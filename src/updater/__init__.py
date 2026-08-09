"""Self-update from GitHub Releases.

The application calls check_and_perform_update() once at startup. Every failure
mode - offline, rate limited, no build for this platform, a cancelled download -
resolves to "carry on and start normally"; nothing here may stop the app from
running.

When an update is available the archive is downloaded here and the separate
updater binary takes over, because on Windows a running executable cannot
overwrite itself. Everything that binary needs travels in argv; see
install.spawn_updater().
"""

import sys

import paths

from . import install as _install
from . import version as _version
from .errors import UpdateError
from .install import cleanup_stale, read_version, write_version
from .log import configure, log
from .release import DEFAULT_TIMEOUT, Release, asset_names

__all__ = [
    "check_and_perform_update",
    "cleanup_stale",
    "read_version",
    "write_version",
    "UpdateError",
]


def check_and_perform_update(on_download_start=None) -> bool:
    """Update if there is one to apply.

    Returns True when the updater binary has been started and the caller must
    exit without opening the main window.

    `on_download_start` runs just before the modal download dialog appears -
    the startup splash uses it to get out of the way, since it is always on top
    and would otherwise cover the dialog. It is not called when there is
    nothing to download, so an ordinary start never flickers.
    """
    configure()

    try:
        return _check_and_perform_update(on_download_start)
    except Exception:
        # An update must never be the reason the application fails to start.
        log.exception("Update check failed")
        return False


def _check_and_perform_update(on_download_start=None) -> bool:
    # Deferred so that the updater binary, which only needs install.py, does not
    # depend on a readable config or on Qt being importable.
    from config import config

    from . import ui

    install_root = paths.install_dir()

    # Unconditional, so leftovers from a past update still get swept once
    # someone switches updates off.
    cleanup_stale(install_root)

    if not config.get("updater", "allow_updates", default=True):
        log.info("Updates are disabled in config")
        return False

    if not getattr(sys, "frozen", False) and not config.get("updater", "allow_source_updates", default=False):
        # Unpacking a packaged build over a git checkout would be destructive.
        log.info("Running from source, skipping the update check")
        return False

    url = config.get("updater", "url")
    if not url:
        log.warning("No [updater] url configured")
        return False

    timeout = config.get("updater", "timeout", default=DEFAULT_TIMEOUT)
    release = Release.fetch(url, timeout)
    current = read_version()
    log.info("Latest version: %s, current version: %s", release.tag, current or "unknown")

    if not _version.is_newer(release.tag, current):
        return False

    names = _asset_names(config)
    if not names:
        log.info("No build is published for this platform (%s)", sys.platform)
        return False

    asset_url = release.find_asset(names)
    if asset_url is None:
        return False

    if on_download_start is not None:
        on_download_start()

    archive = _install.archive_path(install_root)
    if not ui.run_download(asset_url, archive, release.tag, timeout):
        return False

    _install.spawn_updater(install_root, archive, release.tag)
    return True


def _asset_names(config) -> list[str]:
    """Assets to look for, honouring the [updater] asset override.

    The override is what makes this path exercisable from a machine with no
    published build of its own: name any asset in the release and the download,
    unpack and swap all run for real.
    """
    override = config.get("updater", "asset")
    return [override] if override else asset_names()
