"""Tests for the parts of the updater that used to fail silently.

Each one pins a bug the previous implementation shipped with: string version
ordering, a hardcoded Windows asset name, unvalidated archive members, and no
answer at all for a file Windows will not let you overwrite.
"""

import os
import stat
import sys
import time
import zipfile
from pathlib import Path

import pytest
import requests

from updater import install, release, version
from updater.errors import UpdateError


# ---------------------------------------------------------------------------
# version ordering
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "latest, current",
    [
        # The bug that motivated all of this: as strings, "1.10.0" < "1.9.0".
        ("1.10.0", "1.9.0"),
        ("v1.10.0", "v1.9.0"),
        ("2.0.0", "1.99.99"),
        ("1.0.1", "1.0.0"),
        ("1.2.0", "1.2.0-rc1"),
        ("1.2", "1.1.9"),
    ],
)
def test_is_newer(latest, current):
    assert version.is_newer(latest, current)
    assert not version.is_newer(current, latest)


@pytest.mark.parametrize("tag", ["1.0.0", "v1.0.0", "1.0", "1.0.0.0"])
def test_equal_versions_are_not_newer(tag):
    assert not version.is_newer(tag, tag)


def test_trailing_zeros_do_not_count_as_a_new_release():
    assert not version.is_newer("1.2.0", "1.2")
    assert not version.is_newer("1.2", "1.2.0")


def test_a_missing_version_marker_triggers_an_update():
    """An install whose last update failed part way has no version.txt; it has
    to be able to try again."""
    assert version.is_newer("1.0.0", "")


def test_unparseable_tags_fall_back_to_text():
    assert version.is_newer("release-b", "release-a")
    assert not version.is_newer("release-a", "release-b")


def test_prereleases_sort_below_their_release():
    assert version.parse("1.2.0-rc1") < version.parse("1.2.0")


# ---------------------------------------------------------------------------
# asset selection
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "platform_name, machine, expected",
    [
        ("win32", "AMD64", ["palenica-windows-x86_64.zip", "windows-latest.zip"]),
        ("linux", "x86_64", ["palenica-linux-x86_64.zip"]),
        ("darwin", "arm64", ["palenica-macos-arm64.zip"]),
        ("linux", "aarch64", ["palenica-linux-arm64.zip"]),
    ],
)
def test_asset_names(monkeypatch, platform_name, machine, expected):
    monkeypatch.setattr(release.sys, "platform", platform_name)
    monkeypatch.setattr(release.platform, "machine", lambda: machine)
    assert release.asset_names() == expected


def test_an_unknown_platform_asks_for_nothing(monkeypatch):
    """This is how Linux and macOS degrade gracefully: no candidates means the
    caller logs it and the app starts as normal."""
    monkeypatch.setattr(release.sys, "platform", "aix")
    assert release.asset_names() == []


def test_find_asset_prefers_the_first_match():
    rel = release.Release(
        tag="1.0.0",
        assets={
            "windows-latest.zip": "https://example/legacy",
            "palenica-windows-x86_64.zip": "https://example/current",
        },
    )
    assert rel.find_asset(["palenica-windows-x86_64.zip", "windows-latest.zip"]) == "https://example/current"


def test_find_asset_returns_none_when_nothing_matches():
    """The old find_asset_url() fell off the end and returned None implicitly,
    which surfaced as requests.get(None) inside a worker thread."""
    rel = release.Release(tag="1.0.0", assets={"source.tar.gz": "https://example/src"})
    assert rel.find_asset(["palenica-windows-x86_64.zip"]) is None


# ---------------------------------------------------------------------------
# archives
# ---------------------------------------------------------------------------


def _zip(path: Path, members: dict[str, str]) -> Path:
    with zipfile.ZipFile(path, "w") as bundle:
        for name, content in members.items():
            bundle.writestr(name, content)
    return path


def test_extract_rejects_members_that_escape_the_target(tmp_path):
    archive = _zip(tmp_path / "evil.zip", {"../evil.txt": "pwned"})

    with pytest.raises(UpdateError):
        install.extract(archive, tmp_path / "staging")

    assert not (tmp_path / "evil.txt").exists()


def test_extract_rejects_absolute_members(tmp_path):
    archive = _zip(tmp_path / "evil.zip", {"/etc/passwd": "pwned"})

    with pytest.raises(UpdateError):
        install.extract(archive, tmp_path / "staging")


def test_extract_rejects_a_file_that_is_not_a_zip(tmp_path):
    archive = tmp_path / "update.zip"
    archive.write_text("<html>404 Not Found</html>")

    with pytest.raises(UpdateError):
        install.extract(archive, tmp_path / "staging")


def test_extract_writes_the_tree(tmp_path):
    archive = _zip(tmp_path / "build.zip", {"Palenica.exe": "app", "_internal/qt.dll": "lib"})
    staging = tmp_path / "staging"

    seen = []
    install.extract(archive, staging, progress=lambda done, total: seen.append((done, total)))

    assert (staging / "Palenica.exe").read_text() == "app"
    assert (staging / "_internal" / "qt.dll").read_text() == "lib"
    assert seen == [(1, 2), (2, 2)]


def test_extract_starts_from_a_clean_staging_directory(tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "leftover.txt").write_text("from a previous attempt")

    install.extract(_zip(tmp_path / "build.zip", {"Palenica.exe": "app"}), staging)

    assert not (staging / "leftover.txt").exists()


@pytest.mark.skipif(sys.platform == "win32", reason="no executable bit on Windows")
def test_extract_preserves_the_executable_bit(tmp_path):
    """ZipFile.extract() drops mode bits, which would leave a Linux or macOS
    build unrunnable after an update."""
    archive = tmp_path / "build.zip"
    info = zipfile.ZipInfo("Palenica")
    info.external_attr = 0o755 << 16

    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr(info, "#!/bin/sh\n")

    staging = tmp_path / "staging"
    install.extract(archive, staging)

    assert stat.S_IMODE((staging / "Palenica").stat().st_mode) == 0o755


# ---------------------------------------------------------------------------
# swapping files in
# ---------------------------------------------------------------------------


def test_apply_replaces_the_installed_files(tmp_path):
    staging, target = tmp_path / "staging", tmp_path / "install"
    (staging / "_internal").mkdir(parents=True)
    (staging / "Palenica.exe").write_text("new")
    (staging / "_internal" / "qt.dll").write_text("new lib")

    target.mkdir()
    (target / "Palenica.exe").write_text("old")

    install.apply(staging, target)

    assert (target / "Palenica.exe").read_text() == "new"
    assert (target / "_internal" / "qt.dll").read_text() == "new lib"


def test_replace_moves_a_locked_file_aside(tmp_path, monkeypatch):
    """Windows will not let us overwrite a running executable, but it will let
    us rename one - which is how the updater replaces itself."""
    destination = tmp_path / "updater.exe"
    destination.write_text("old")
    source = tmp_path / "staged"
    source.write_text("new")

    real_replace = os.replace
    attempts = []

    def fake_replace(src, dst):
        attempts.append((Path(src).name, Path(dst).name))
        if len(attempts) == 1:
            raise PermissionError(13, "used by another process")
        return real_replace(src, dst)

    monkeypatch.setattr(install.os, "replace", fake_replace)
    install._replace(source, destination, deadline=time.monotonic() + 5)

    assert destination.read_text() == "new"

    retired = list(tmp_path.glob(f"updater.exe{install.RETIRED_SUFFIX}*"))
    assert len(retired) == 1
    assert retired[0].read_text() == "old"


def test_replace_gives_up_once_the_deadline_passes(tmp_path, monkeypatch):
    destination = tmp_path / "updater.exe"
    destination.write_text("old")
    source = tmp_path / "staged"
    source.write_text("new")

    def always_locked(src, dst):
        raise PermissionError(13, "used by another process")

    monkeypatch.setattr(install.os, "replace", always_locked)

    with pytest.raises(UpdateError):
        install._replace(source, destination, deadline=time.monotonic())

    assert destination.read_text() == "old"


def test_cleanup_stale_removes_retired_files_and_the_work_directory(tmp_path):
    (tmp_path / f"updater.exe{install.RETIRED_SUFFIX}0").write_text("retired")
    work = install.paths.work_dir(tmp_path)
    work.mkdir(parents=True)
    (work / "update.zip").write_text("downloaded")
    (tmp_path / "Palenica.exe").write_text("keep me")

    install.cleanup_stale(tmp_path)

    assert not list(tmp_path.glob(f"*{install.RETIRED_SUFFIX}*"))
    assert not work.exists()
    assert (tmp_path / "Palenica.exe").exists()


# ---------------------------------------------------------------------------
# downloading
# ---------------------------------------------------------------------------


class _FakeResponse:
    def __init__(self, chunks, headers=None, status=200):
        self.chunks = chunks
        self.headers = headers or {}
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def raise_for_status(self):
        if self.status >= 400:
            raise requests.HTTPError(f"{self.status}")

    def iter_content(self, chunk_size):
        yield from self.chunks


def _serve(monkeypatch, response):
    monkeypatch.setattr(install.requests, "get", lambda *a, **kw: response)


def test_download_writes_the_body(tmp_path, monkeypatch):
    _serve(monkeypatch, _FakeResponse([b"abc", b"def"], {"Content-Length": "6"}))
    destination = tmp_path / "update.zip"

    seen = []
    install.download("https://example/asset", destination, progress=lambda d, t: seen.append((d, t)))

    assert destination.read_bytes() == b"abcdef"
    assert seen == [(3, 6), (6, 6)]
    assert not list(tmp_path.glob("*.part"))


def test_download_refuses_an_error_response(tmp_path, monkeypatch):
    """response.raw was previously copied to disk without checking the status,
    so a 404 page was saved as though it were the archive."""
    _serve(monkeypatch, _FakeResponse([b"<html>"], status=404))
    destination = tmp_path / "update.zip"

    with pytest.raises(requests.HTTPError):
        install.download("https://example/missing", destination)

    assert not destination.exists()


def test_download_rejects_a_truncated_body(tmp_path, monkeypatch):
    _serve(monkeypatch, _FakeResponse([b"abc"], {"Content-Length": "6"}))
    destination = tmp_path / "update.zip"

    with pytest.raises(UpdateError):
        install.download("https://example/asset", destination)

    assert not destination.exists()
    assert not list(tmp_path.glob("*.part"))


def test_download_ignores_the_length_when_the_body_is_encoded(tmp_path, monkeypatch):
    """With a Content-Encoding the header describes the compressed size, not
    what iter_content hands us."""
    _serve(monkeypatch, _FakeResponse([b"abcdef"], {"Content-Length": "3", "Content-Encoding": "gzip"}))
    destination = tmp_path / "update.zip"

    install.download("https://example/asset", destination)

    assert destination.read_bytes() == b"abcdef"


def test_download_can_be_cancelled(tmp_path, monkeypatch):
    from updater.errors import UpdateCancelled

    _serve(monkeypatch, _FakeResponse([b"abc", b"def"], {"Content-Length": "6"}))
    destination = tmp_path / "update.zip"

    with pytest.raises(UpdateCancelled):
        install.download("https://example/asset", destination, is_cancelled=lambda: True)

    assert not destination.exists()
    assert not list(tmp_path.glob("*.part"))


# ---------------------------------------------------------------------------
# handoff
# ---------------------------------------------------------------------------


def test_spawn_updater_passes_everything_in_argv(tmp_path, monkeypatch):
    """The child must not need a second GitHub call, or a config file, to know
    what it is installing."""
    recorded = {}

    def fake_popen(command, **kwargs):
        recorded["command"] = command
        recorded["kwargs"] = kwargs

    monkeypatch.setattr(install.subprocess, "Popen", fake_popen)
    install.spawn_updater(tmp_path, tmp_path / "update.zip", "v1.2.3")

    command = recorded["command"]
    assert "--version" in command and command[command.index("--version") + 1] == "v1.2.3"
    assert "--target" in command and command[command.index("--target") + 1] == str(tmp_path)
    assert "--wait-pid" in command and command[command.index("--wait-pid") + 1] == str(os.getpid())
    # Everything after the separator is the command that brings the app back.
    assert command[command.index("--") + 1 :] == install.app_command(tmp_path)


def test_wait_for_exit_returns_once_the_process_is_gone(monkeypatch):
    alive = iter([True, True, False])
    monkeypatch.setattr(install, "_is_running", lambda pid: next(alive))
    assert install.wait_for_exit(1234, timeout=5)


def test_wait_for_exit_gives_up(monkeypatch):
    monkeypatch.setattr(install, "_is_running", lambda pid: True)
    assert not install.wait_for_exit(1234, timeout=0.2)


def test_this_process_is_running():
    assert install._is_running(os.getpid())
