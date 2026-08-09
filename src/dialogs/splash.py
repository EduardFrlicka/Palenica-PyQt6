from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QSplashScreen

TITLE = "Pálenica"

BACKGROUND_COLOR = "#1e2a36"
BORDER_COLOR = "#3d5468"
TITLE_COLOR = "#f2f6fa"
MESSAGE_COLOR = "#cfd9e2"


class StartupSplash(QSplashScreen):
    """Splash screen shown while the database connection is established and the
    tabs load their data. Startup is synchronous, so every stage has to call
    ``message()``, which repaints the splash before the slow work starts."""

    WIDTH = 420
    HEIGHT = 220

    def __init__(self):
        super().__init__(self._background())
        self.setWindowTitle(TITLE)

    @classmethod
    def _background(cls) -> QPixmap:
        ratio = QApplication.instance().devicePixelRatio()
        pixmap = QPixmap(int(cls.WIDTH * ratio), int(cls.HEIGHT * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(QColor(BACKGROUND_COLOR))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(QColor(BORDER_COLOR))
        painter.drawRect(0, 0, cls.WIDTH - 1, cls.HEIGHT - 1)

        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.setPen(QColor(TITLE_COLOR))
        painter.drawText(
            QRect(0, 50, cls.WIDTH, 60),
            Qt.AlignmentFlag.AlignCenter,
            TITLE,
        )

        painter.end()
        return pixmap

    def message(self, text: str):
        """Show a stage message and repaint immediately."""
        print(text)
        self.showMessage(
            f"\n{text}\n",
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
            QColor(MESSAGE_COLOR),
        )
        QApplication.processEvents()
