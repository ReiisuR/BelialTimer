from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget


class BackgroundWidget(QWidget):

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

    def set_background_opacity(self, opacity):

        self.background_opacity = max(0.0, min(1.0, opacity))
        self.update()

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )
        painter.setOpacity(self.background_opacity)

        rect = self.rect()

        gradient = QLinearGradient(
            0,
            0,
            0,
            rect.height()
        )

        gradient.setColorAt(
            0.0,
            QColor("#151515")
        )

        gradient.setColorAt(
            0.55,
            QColor("#0d0d0d")
        )

        gradient.setColorAt(
            1.0,
            QColor("#080808")
        )

        painter.fillRect(
            rect,
            gradient
        )

        center = rect.center()

        radial = QRadialGradient(
            center.x(),
            center.y(),
            max(
                rect.width(),
                rect.height()
            ) * 0.7
        )

        radial.setColorAt(
            0.0,
            QColor(
                100,
                20,
                25,
                25
            )
        )

        radial.setColorAt(
            0.55,
            QColor(
                70,
                10,
                15,
                10
            )
        )

        radial.setColorAt(
            1.0,
            QColor(
                0,
                0,
                0,
                0
            )
        )

        painter.fillRect(
            rect,
            radial
        )

        painter.setPen(
            QPen(
                QColor("#292929"),
                1
            )
        )

        painter.drawRect(
            rect.adjusted(
                0,
                0,
                -1,
                -1
            )
        )

        painter.setPen(
            QPen(
                QColor(
                    100,
                    25,
                    30,
                    90
                ),
                1
            )
        )

        painter.drawRect(
            rect.adjusted(
                5,
                5,
                -6,
                -6
            )
        )
