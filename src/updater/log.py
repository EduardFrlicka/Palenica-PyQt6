"""Update logging.

Both binaries are built with console=False, so the print() calls the updater
used to rely on go nowhere - a failed update was completely invisible. Write to
a file next to the executable instead, and keep stderr for source runs.
"""

import logging

import paths

LOGGER_NAME = "palenica.updater"
MAX_BYTES = 512 * 1024

log = logging.getLogger(LOGGER_NAME)
_configured = False


def configure() -> logging.Logger:
    """Attach handlers once. Safe to call from either binary."""
    global _configured
    if _configured:
        return log

    _configured = True
    log.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")

    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    log.addHandler(stream)

    try:
        _truncate_if_large(paths.log_file())
        handler = logging.FileHandler(paths.log_file(), encoding="utf-8")
        handler.setFormatter(formatter)
        log.addHandler(handler)
    except OSError as exc:
        # A read-only or missing install directory must not stop the app from
        # starting; the stream handler still carries the messages.
        log.warning("Cannot write %s: %s", paths.log_file(), exc)

    return log


def _truncate_if_large(path) -> None:
    """Keep the log from growing without bound.

    RotatingFileHandler would need both processes to agree on the rollover,
    which they cannot - they run one after the other. A size check at startup
    is enough for a file that gains a handful of lines per launch.
    """
    if path.exists() and path.stat().st_size > MAX_BYTES:
        path.unlink()
