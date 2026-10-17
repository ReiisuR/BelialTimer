import os

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

BELIAL_ART = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    ),
    "assets",
    "belial_header.jpg"
)


# =========================================================

class HeaderArtWidget(QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.pixmap = QPixmap(
            BELIAL_ART
        )

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.RenderHint.SmoothPixmapTransform
        )

        if self.pixmap.isNull():
            return

        target_height = self.height()

        scaled = self.pixmap.scaled(
            self.pixmap.width(),
            target_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        painter.drawPixmap(
            0,
            0,
            scaled
        )

        # Fade lateral
        fade_width = 65

        gradient = QLinearGradient(
            self.width() - fade_width,
            0,
            self.width(),
            0
        )

        gradient.setColorAt(
            0.0,
            QColor(
                10,
                10,
                10,
                0
            )
        )

        gradient.setColorAt(
            1.0,
            QColor(
                10,
                10,
                10,
                255
            )
        )

        painter.fillRect(
            QRectF(
                self.width() - fade_width,
                0,
                fade_width,
                self.height()
            ),
            gradient
        )


# =========================================================
# HEADER
# =========================================================

class HeaderWidget(QWidget):

    def __init__(
        self,
        close_callback,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.setFixedHeight(
            95
        )

        self.close_callback = close_callback

        self.header_timer_label = None

        self._build_ui()

    def _build_ui(self):

        layout = QHBoxLayout(
            self
        )

        layout.setContentsMargins(
            18,
            0,
            18,
            0
        )

        layout.setSpacing(
            0
        )

        # -------------------------------------------------
        # ARTE
        # -------------------------------------------------

        art = HeaderArtWidget(
            self
        )

        art.setFixedWidth(
            260
        )

        layout.addWidget(
            art
        )

        # -------------------------------------------------
        # TITULO
        # -------------------------------------------------

        title_container = QWidget(
            self
        )

        title_layout = QVBoxLayout(
            title_container
        )

        title_layout.setContentsMargins(
            12,
            14,
            0,
            10
        )

        title_layout.setSpacing(
            1
        )

        title = QLabel(
            "BELIAL"
        )

        title.setStyleSheet("""
            QLabel {
                color: #eeeeee;
                background: transparent;
            }
        """)

        title.setFont(
            QFont(
                "Arial",
                19,
                QFont.Weight.Bold
            )
        )

        subtitle = QLabel(
            "DUNGEON TIMER"
        )

        subtitle.setStyleSheet("""
            QLabel {
                color: #8f8f8f;
                background: transparent;
                letter-spacing: 2px;
            }
        """)

        subtitle.setFont(
            QFont(
                "Arial",
                9
            )
        )

        divider = QFrame()

        divider.setFixedHeight(
            1
        )

        divider.setStyleSheet("""
            QFrame {
                background: #6b2027;
                border: none;
            }
        """)

        title_layout.addWidget(
            title
        )

        title_layout.addWidget(
            subtitle
        )

        title_layout.addSpacing(
            7
        )

        title_layout.addWidget(
            divider
        )

        title_layout.addStretch()

        layout.addWidget(
            title_container,
            1
        )

        # -------------------------------------------------
        # STATUS + TIMER
        # -------------------------------------------------

        timer_container = QWidget(
            self
        )

        timer_layout = QVBoxLayout(
            timer_container
        )

        timer_layout.setContentsMargins(
            0,
            12,
            5,
            7
        )

        timer_layout.setSpacing(
            0
        )

        self.status_label = QLabel(
            "○  AGUARDANDO INÍCIO"
        )

        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        self.status_label.setStyleSheet("""
            QLabel {
                color: #a34a53;
                background: transparent;
            }
        """)

        self.status_label.setFont(
            QFont(
                "Arial",
                8,
                QFont.Weight.Bold
            )
        )

        timer_label = QLabel(
            "00:00"
        )

        timer_label.setAlignment(
            Qt.AlignmentFlag.AlignRight |
            Qt.AlignmentFlag.AlignVCenter
        )

        timer_label.setStyleSheet("""
            QLabel {
                color: #eeeeee;
                background: transparent;
            }
        """)

        timer_label.setFont(
            QFont(
                "Consolas",
                35,
                QFont.Weight.Bold
            )
        )

        self.header_timer_label = timer_label

        timer_layout.addWidget(
            self.status_label
        )

        timer_layout.addWidget(
            timer_label
        )

        layout.addWidget(
            timer_container
        )

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(
            self
        )

        painter.fillRect(
            self.rect(),
            QColor("#101010")
        )

        painter.setPen(
            QPen(
                QColor("#252525"),
                1
            )
        )

        painter.drawLine(
            15,
            self.height() - 1,
            self.width() - 15,
            self.height() - 1
        )


# =========================================================
# MAIN WINDOW
