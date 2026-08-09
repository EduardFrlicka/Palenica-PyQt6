"""Downloading, unpacking and swapping in a new build.

The updater runs from inside the directory it is updating, so on Windows the
install directory can be neither moved nor deleted while it works. Files are
therefore replaced one at a time, in place, after being staged somewhere they
can be validated first.
"""

import itertools
import os
import shutil
import stat
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import requests

import messages
import paths
from .errors import UpdateCancelled, UpdateError
from .log import log
from .release import DEFAULT_TIMEOUT, USER_AGENT

ARCHIVE_NAME = "update.zip"
STAGING_NAME = "staging"

# Marks a file moved aside because it was still in use. Swept on the next start.
RETIRED_SUFFIX = ".palenica-old"

CHUNK_SIZE = 256 * 1024

# How long to keep retrying a locked file. The parent normally exits within a
# second of spawning us; this covers a slow shutdown, not an indefinite one.
REPLACE_TIMEOUT = 30.0


def archive_path(target: Path | None = None) -> Path:
    return paths.work_dir(target) / ARCHIVE_NAME


def staging_dir(target: Path | None = None) -> Path:
    return paths.work_dir(target) / STAGING_NAME


def version_file(target: Path | None = None) -> Path:
    return (target / paths.VERSION_FILE) if target else paths.version_file()


def read_version(target: Path | None = None) -> str:
    try:
        return version_file(target).read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def write_version(tag: str, target: Path | None = None) -> None:
    version_file(target).write_text(tag, encoding="utf-8")


# --------------------------------------------------------------------------
# download
# --------------------------------------------------------------------------


def download(url, destination: Path, timeout=DEFAULT_TIMEOUT, progress=None, is_cancelled=None) -> None:
    """Stream `url` into `destination`, atomically.

    Writes to a .part file and renames on success, so an interrupted download
    can never be mistaken for a finished archive. The previous implementation
    piped response.raw straight to disk without checking the status, which
    happily saved a 404 page as a zip.
    """
    partial = destination.with_name(destination.name + ".part")
    partial.parent.mkdir(parents=True, exist_ok=True)
    written = 0

    try:
        with requests.get(url, stream=True, timeout=timeout, headers={"User-Agent": USER_AGENT}) as response:
            response.raise_for_status()

            # Only trust the length when the body arrives verbatim; with a
            # transfer encoding it describes the compressed size, not what we write.
            expected = 0 if response.headers.get("Content-Encoding") else int(response.headers.get("Content-Length") or 0)

            with open(partial, "wb") as handle:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if is_cancelled is not None and is_cancelled():
                        raise UpdateCancelled()

                    handle.write(chunk)
                    written += len(chunk)
                    if progress is not None:
                        progress(written, expected)

        if expected and written != expected:
            raise UpdateError(messages.UPDATE_ARCHIVE_INCOMPLETE)

        os.replace(partial, destination)
    finally:
        # A successful download has already renamed it away, so this only bites
        # on a cancellation or a dropped connection. It has to sit out here:
        # Windows refuses to unlink a file while its handle is still open, so
        # cleaning up inside the write loop fails on the one platform that
        # matters.
        partial.unlink(missing_ok=True)

    log.info("Downloaded %s (%d bytes)", destination, written)


# --------------------------------------------------------------------------
# unpack
# --------------------------------------------------------------------------


def extract(archive: Path, staging: Path, progress=None) -> None:
    """Unpack `archive` into a clean `staging` directory."""
    if not zipfile.is_zipfile(archive):
        raise UpdateError(messages.UPDATE_ARCHIVE_INVALID)

    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)

    with zipfile.ZipFile(archive) as bundle:
        members = _safe_members(bundle, staging)

        for index, (info, destination) in enumerate(members, start=1):
            destination.parent.mkdir(parents=True, exist_ok=True)
            _write_member(bundle, info, destination)
            if progress is not None:
                progress(index, len(members))

    log.info("Extracted %d files to %s", len(members), staging)


def _safe_members(bundle: zipfile.ZipFile, root: Path) -> list[tuple[zipfile.ZipInfo, Path]]:
    """Pair every member with its destination, rejecting paths that escape `root`.

    An archive is allowed to name "../../evil"; resolving before comparing is
    what stops it from being written outside the staging directory.
    """
    root = root.resolve()
    members = []

    for info in bundle.infolist():
        if info.is_dir():
            continue

        destination = (root / info.filename).resolve()
        if root not in destination.parents:
            raise UpdateError(messages.UPDATE_ARCHIVE_UNSAFE.format(info.filename))

        members.append((info, destination))

    if not members:
        raise UpdateError(messages.UPDATE_ARCHIVE_INVALID)

    return members


def _write_member(bundle: zipfile.ZipFile, info: zipfile.ZipInfo, destination: Path) -> None:
    """Write one member, keeping the mode bits ZipFile.extract() throws away.

    Losing the executable bit would leave a Linux or macOS build unrunnable
    after an update; losing a symlink would break the framework layout macOS
    bundles rely on.
    """
    mode = info.external_attr >> 16

    if stat.S_ISLNK(mode):
        destination.unlink(missing_ok=True)
        destination.symlink_to(bundle.read(info).decode("utf-8"))
        return

    with bundle.open(info) as source, open(destination, "wb") as sink:
        shutil.copyfileobj(source, sink)

    if mode & 0o777:
        os.chmod(destination, mode & 0o777)


# --------------------------------------------------------------------------
# swap
# --------------------------------------------------------------------------


def apply(staging: Path, target: Path, progress=None, timeout=REPLACE_TIMEOUT) -> None:
    """Move every staged file into `target`.

    Files removed upstream are left behind rather than tracked in a manifest;
    a stale entry under _internal/ costs disk and nothing else.
    """
    staged = sorted(path for path in staging.rglob("*") if path.is_symlink() or path.is_file())
    deadline = time.monotonic() + timeout

    for index, source in enumerate(staged, start=1):
        destination = target / source.relative_to(staging)
        destination.parent.mkdir(parents=True, exist_ok=True)
        _replace(source, destination, deadline)
        if progress is not None:
            progress(index, len(staged))

    log.info("Installed %d files into %s", len(staged), target)


def _replace(source: Path, destination: Path, deadline: float) -> None:
    delay = 0.1

    while True:
        try:
            os.replace(source, destination)
            return
        except PermissionError:
            pass

        # Windows forbids overwriting a running executable but permits renaming
        # one, which is how the updater replaces itself. The leftover is swept
        # on the next start.
        try:
            retired = _retired_name(destination)
            os.replace(destination, retired)
            log.info("Moved %s aside to %s", destination.name, retired.name)
            os.replace(source, destination)
            return
        except OSError as exc:
            last = exc

        if time.monotonic() >= deadline:
            log.error("Giving up on %s: %s", destination, last)
            raise UpdateError(messages.UPDATE_FILE_LOCKED.format(destination.name))

        time.sleep(delay)
        delay = min(delay * 2, 2.0)


def _retired_name(destination: Path) -> Path:
    for index in itertools.count():
        candidate = destination.with_name(f"{destination.name}{RETIRED_SUFFIX}{index}")
        if not candidate.exists():
            return candidate


def cleanup_stale(target: Path | None = None) -> None:
    """Remove what an earlier update left behind.

    Best effort throughout: anything still held by a live process is simply
    retried on the next start.
    """
    target = target or paths.install_dir()

    for path in target.rglob(f"*{RETIRED_SUFFIX}*"):
        if not path.is_file():
            continue
        try:
            path.unlink()
        except OSError as exc:
            log.info("Leaving %s for later: %s", path.name, exc)

    shutil.rmtree(paths.work_dir(target), ignore_errors=True)


# --------------------------------------------------------------------------
# process handoff
# --------------------------------------------------------------------------


def _detached() -> dict:
    """Popen options that let the child outlive us."""
    if hasattr(subprocess, "DETACHED_PROCESS"):  # Windows
        return {"creationflags": subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def updater_command(install: Path) -> list[str]:
    """argv prefix that starts the updater, frozen or from source."""
    if getattr(sys, "frozen", False):
        name = "updater.exe" if sys.platform == "win32" else "updater"
        return [str(install / name)]
    return [sys.executable, str(Path(__file__).resolve().parent.parent / "updater_app.py")]


def app_command(install: Path) -> list[str]:
    """argv that starts the application again once the update lands."""
    if getattr(sys, "frozen", False):
        name = "Palenica.exe" if sys.platform == "win32" else "Palenica"
        return [str(install / name)]
    return [sys.executable, str(Path(__file__).resolve().parent.parent / "app.py")]


def spawn_updater(install: Path, archive: Path, tag: str) -> None:
    """Hand off to the updater binary and let it take over.

    Everything it needs travels in argv. The old design had it re-query the
    GitHub API to rediscover the same facts, which meant a second network round
    trip, a window in which a newly published release desynchronised the two
    processes, and a hard NameError whenever updates were disabled in config.
    """
    command = updater_command(install) + [
        "--archive", str(archive),
        "--target", str(install),
        "--version", tag,
        "--wait-pid", str(os.getpid()),
        "--",
        *app_command(install),
    ]

    log.info("Starting updater: %s", command)
    subprocess.Popen(command, cwd=str(install), close_fds=True, **_detached())


def relaunch(command: list[str], cwd: Path) -> None:
    log.info("Relaunching: %s", command)
    subprocess.Popen(command, cwd=str(cwd), close_fds=True, **_detached())


def wait_for_exit(pid: int, timeout: float = REPLACE_TIMEOUT) -> bool:
    """Block until `pid` is gone, or the timeout expires.

    An optimisation only - _replace() retries regardless - so a platform where
    liveness cannot be checked just proceeds straight to the retry loop.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if not _is_running(pid):
            return True
        time.sleep(0.1)

    log.warning("Process %d still alive after %.0fs", pid, timeout)
    return False


def _is_running(pid: int) -> bool:
    if sys.platform == "win32":
        return _is_running_windows(pid)

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists, owned by someone else
    return True


def _is_running_windows(pid: int) -> bool:
    import ctypes

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return False

    try:
        code = ctypes.c_ulong()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
            return False
        return code.value == STILL_ACTIVE
    finally:
        kernel32.CloseHandle(handle)
