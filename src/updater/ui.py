"""Qt front ends for the two halves of an update.

Worker threads never touch a widget - everything crosses back over a signal, so
the connection is queued onto the GUI thread. The previous updater called
QProgressBar.setValue() straight from a plain thread, which Qt does not permit.
"""

import threading

from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QProgressDialog

import messages
from dialogs.alert import warning
from ui_py.updater_window_ui import Ui_Updater
from .errors import UpdateCancelled
from .log import log

TITLE = "Palenica"


class _Signals(QObject):
    advanced = pyqtSignal(int, int)
    finished = pyqtSignal()


def run_download(url: str, destination, tag: str, timeout: float) -> bool:
    """Download `url` behind a cancellable progress dialog.

    Returns True only if the archive is on disk and complete; a cancellation or
    a failure leaves the installation exactly as it was.
    """
    from . import install  # deferred: install imports requests, ui does not need it

    dialog = QProgressDialog(messages.UPDATE_AVAILABLE.format(tag), messages.UPDATE_CANCEL, 0, 100)
    dialog.setWindowTitle(TITLE)
    dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
    dialog.setMinimumDuration(0)
    dialog.setAutoClose(False)
    dialog.setAutoReset(False)

    signals = _Signals()
    cancelled = threading.Event()
    outcome: dict = {"ok": False, "error": None}

    signals.advanced.connect(lambda done, total: _advance(dialog, done, total))
    signals.finished.connect(lambda: dialog.done(0))

    dialog.canceled.connect(cancelled.set)
    dialog.canceled.connect(lambda: dialog.done(0))

    def work():
        try:
            install.download(
                url,
                destination,
                timeout=timeout,
                progress=signals.advanced.emit,
                is_cancelled=cancelled.is_set,
            )
            outcome["ok"] = True
        except UpdateCancelled:
            pass
        except Exception as exc:
            outcome["error"] = exc
        finally:
            signals.finished.emit()

    # Daemon so that cancelling closes the dialog at once: the worker unwinds on
    # its own and its cleanup still runs, but it can never hold the app open.
    threading.Thread(target=work, daemon=True).start()
    dialog.exec()

    if cancelled.is_set():
        log.info("Update cancelled by the user")
        return False

    if outcome["error"] is not None:
        log.error("Download failed: %s", outcome["error"], exc_info=outcome["error"])
        warning(messages.UPDATE_DOWNLOAD_FAILED.format(outcome["error"]))
        return False

    return outcome["ok"]


def _advance(dialog: QProgressDialog, done: int, total: int) -> None:
    if total:
        dialog.setMaximum(100)
        dialog.setValue(int(done * 100 / total))
    else:
        dialog.setMaximum(0)  # unknown length - show a busy indicator


class UpdaterWindow(Ui_Updater, QMainWindow):
    """The updater binary's window: a label, a progress bar and an OK button."""

    advanced = pyqtSignal(str, int, int)
    failed = pyqtSignal(str)
    succeeded = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(TITLE)
        self.label.setText(messages.UPDATE_IN_PROGRESS)

        self.advanced.connect(self._on_advanced)
        self.failed.connect(self._on_failed)
        self.succeeded.connect(self._on_succeeded)

    def _on_advanced(self, label: str, done: int, total: int) -> None:
        self.label.setText(label)
        self.progressBar.setMaximum(total or 0)
        self.progressBar.setValue(done)

    def _on_failed(self, reason: str) -> None:
        self.label.setText(messages.UPDATE_FAILED.format(reason))
        self.label.setWordWrap(True)
        self.progressBar.hide()
        self.pushButton.setEnabled(True)

    def _on_succeeded(self) -> None:
        self.label.setText(messages.UPDATE_DONE)
        self.progressBar.hide()
        self.pushButton.setEnabled(True)

    def ok(self) -> None:
        """Connected to the OK button by the generated setupUi()."""
        self.close()
