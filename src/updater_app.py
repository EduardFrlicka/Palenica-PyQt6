"""The updater binary.

Started by the application when a new release has finished downloading, and
never run on its own. Everything it needs arrives in argv:

    updater --archive <zip> --target <install-dir> --version <tag>
            [--wait-pid <pid>] -- <command to relaunch>

The previous version instead imported the update module and let it re-query the
GitHub API to rediscover all of that, which cost a second round trip, opened a
window in which a freshly published release desynchronised the two processes,
and failed outright with a NameError whenever updates were disabled in config.
"""

import argparse
import sys
import threading
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

import messages
from updater import install
from updater.log import configure, log
from updater.ui import UpdaterWindow


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Applies a downloaded Palenica update.")
    parser.add_argument("--archive", required=True, type=Path, help="downloaded release archive")
    parser.add_argument("--target", required=True, type=Path, help="installation directory to update")
    parser.add_argument("--version", required=True, help="tag being installed")
    parser.add_argument("--wait-pid", type=int, help="wait for this process to exit first")
    parser.add_argument("relaunch", nargs="*", help="command to run once the update lands")

    args = parser.parse_args(argv)

    if not args.archive.is_file():
        parser.error(f"archive not found: {args.archive}")
    if not args.target.is_dir():
        parser.error(f"target is not a directory: {args.target}")

    return args


def _work(window: UpdaterWindow, args: argparse.Namespace) -> None:
    """Unpack and install, off the GUI thread. Reports back over signals only."""
    try:
        if args.wait_pid:
            install.wait_for_exit(args.wait_pid)

        staging = install.staging_dir(args.target)

        install.extract(
            args.archive,
            staging,
            progress=lambda done, total: window.advanced.emit(messages.UPDATE_EXTRACTING, done, total),
        )
        install.apply(
            staging,
            args.target,
            progress=lambda done, total: window.advanced.emit(messages.UPDATE_INSTALLING, done, total),
        )

        # Only once every file has landed. A partial install keeps the old
        # marker, so the next start retries instead of believing it is current.
        install.write_version(args.version, args.target)
        install.cleanup_stale(args.target)

        log.info("Updated to %s", args.version)
        window.succeeded.emit()
    except Exception as exc:
        log.exception("Update failed")
        window.failed.emit(str(exc))


def _finish(window: UpdaterWindow, args: argparse.Namespace) -> None:
    """Runs on the GUI thread once the install succeeds."""
    if args.relaunch:
        try:
            install.relaunch(args.relaunch, args.target)
        except OSError:
            log.exception("Could not relaunch %s", args.relaunch)

    # Long enough for "Hotovo" to register, short enough not to sit in front of
    # the application window that is already coming up.
    QTimer.singleShot(1200, window.close)


def main(argv=None) -> int:
    args = parse_args(argv)
    configure()
    log.info("Updater starting: archive=%s target=%s version=%s", args.archive, args.target, args.version)

    app = QApplication(sys.argv[:1])
    window = UpdaterWindow()
    window.succeeded.connect(lambda: _finish(window, args))
    window.show()

    threading.Thread(target=_work, args=(window, args), daemon=True).start()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
