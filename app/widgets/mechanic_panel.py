import os

from PySide6.QtCore import Qt, QRectF, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

class MainPanelBackground(QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            True
        )
        self.background_opacity = 1.0

        self.image_path = None

        self.pixmap = QPixmap()

        self.old_pixmap = QPixmap()

        self.new_pixmap = QPixmap()

        self.transition_progress = 1.0

        self.transition_timer = QTimer(
            self
        )

        self.transition_timer.setInterval(
            20
        )

        self.transition_timer.timeout.connect(
            self._update_transition
        )

    def set_background_opacity(self, opacity):

        self.background_opacity = max(0.0, min(1.0, opacity))
        self.update()

    def _load_pixmap(
        self,
        image_path
    ):

        if not image_path:
            return QPixmap()

        full_path = os.path.join(
            BASE_DIR,
            "assets",
            image_path
        )

        if not os.path.exists(
            full_path
        ):
            return QPixmap()

        return QPixmap(
            full_path
        )

    def set_background(
        self,
        image_path
    ):

        if image_path == self.image_path:
            return

        self.image_path = image_path

        new_pixmap = self._load_pixmap(
            image_path
        )

        self.old_pixmap = self.pixmap

        self.new_pixmap = new_pixmap

        self.transition_progress = 0.0

        self.transition_timer.start()

        self.update()

    def _update_transition(
        self
    ):

        self.transition_progress += 0.08

        if self.transition_progress >= 1.0:

            self.transition_progress = 1.0

            self.pixmap = self.new_pixmap

            self.old_pixmap = QPixmap()

            self.new_pixmap = QPixmap()

            self.transition_timer.stop()

        self.update()

    def _draw_pixmap_cover(
        self,
        painter,
        pixmap,
        opacity
    ):

        if pixmap.isNull():
            return

        painter.save()

        painter.setOpacity(
            opacity
        )

        source_ratio = (
            pixmap.width()
            / pixmap.height()
        )

        target_ratio = (
            self.width()
            / self.height()
        )

        if source_ratio > target_ratio:

            new_height = pixmap.height()

            new_width = int(
                new_height
                * target_ratio
            )

        else:

            new_width = pixmap.width()

            new_height = int(
                new_width
                / target_ratio
            )

        x = (
            pixmap.width()
            - new_width
        ) // 2

        y = (
            pixmap.height()
            - new_height
        ) // 2

        source = QRectF(
            x,
            y,
            new_width,
            new_height
        )

        target = QRectF(
            0,
            0,
            self.width(),
            self.height()
        )

        painter.drawPixmap(
            target,
            pixmap,
            source
        )

        painter.restore()

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(
            self
        )

        painter.setOpacity(self.background_opacity)
        painter.setRenderHint(
            QPainter.RenderHint.SmoothPixmapTransform
        )

        rect = self.rect()

        # Fundo base
        painter.fillRect(
            rect,
            QColor("#111111")
        )

        # Imagem antiga
        if not self.old_pixmap.isNull():

            self._draw_pixmap_cover(
                painter,
                self.old_pixmap,
                self.background_opacity
                * (1.0 - self.transition_progress)
            )

        # Imagem nova
        if not self.new_pixmap.isNull():

            self._draw_pixmap_cover(
                painter,
                self.new_pixmap,
                self.background_opacity
                * self.transition_progress
            )

        elif (
            not self.pixmap.isNull()
            and self.old_pixmap.isNull()
        ):

            self._draw_pixmap_cover(
                painter,
                self.pixmap,
                self.background_opacity
            )

        # Escurecimento geral
        painter.fillRect(
            rect,
            QColor(
                0,
                0,
                0,
                105
            )
        )

        # Fade vertical
        gradient = QLinearGradient(
            0,
            0,
            0,
            self.height()
        )

        gradient.setColorAt(
            0.0,
            QColor(
                0,
                0,
                0,
                50
            )
        )

        gradient.setColorAt(
            0.5,
            QColor(
                0,
                0,
                0,
                10
            )
        )

        gradient.setColorAt(
            1.0,
            QColor(
                0,
                0,
                0,
                80
            )
        )

        painter.fillRect(
            rect,
            gradient
        )

        # Borda
        painter.setPen(
            QPen(
                QColor("#292929"),
                1
            )
        )

        painter.drawRoundedRect(
            QRectF(
                0.5,
                0.5,
                self.width() - 1,
                self.height() - 1
            ),
            8,
            8
        )


# =========================================================
# TIMELINE
# =========================================================
# MAIN WINDOW
