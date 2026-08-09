"""Filesystem locations, resolved against the installation rather than the CWD.

Every writable file the application owns - config.toml, version.txt, the update
log - lives next to the executable. Resolving them against the current working
directory (the previous behaviour) meant a desktop shortcut with a "Start in"
field, or a drag-and-drop launch, silently produced a second config and let the
updater unpack a new build over the wrong directory.
"""

from pathlib import Path
import sys

CONFIG_FILE = "config.toml"
VERSION_FILE = "version.txt"
LOG_FILE = "palenica-update.log"

# Downloads and extraction staging live here. Keeping them under the install
# directory means os.replace() into the target never crosses a filesystem, and
# cleanup is a single rmtree instead of hunting for stray archives - the 42 MB
# 1.0.3.zip in the repository root is what the old CWD-relative download left
# behind.
WORK_DIR = ".palenica-update"


def install_dir() -> Path:
    """Directory the application is installed in.

    Frozen builds resolve against the executable, since PyInstaller puts
    Palenica and updater side by side in the collected directory. Running from
    source resolves against the repository root, which is where config.toml has
    always lived.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def config_file() -> Path:
    return install_dir() / CONFIG_FILE


def version_file() -> Path:
    return install_dir() / VERSION_FILE


def log_file() -> Path:
    return install_dir() / LOG_FILE


def work_dir(target: Path | None = None) -> Path:
    return (target or install_dir()) / WORK_DIR
