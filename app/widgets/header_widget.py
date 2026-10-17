import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget
)

BELIAL_ART = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    ),
    "assets",
    "belial_sentada.png"
)
BELIAL_ART_OPTIONS = {
    "sentada": BELIAL_ART,
    "deitada": os.path.join(
        os.path.dirname(BELIAL_ART),
        "belial_deitada.png"
    )
}
BELIAL_ELBOW_ART = os.path.join(
    os.path.dirname(BELIAL_ART),
    "belial_cotovelo.png"
)


# =========================================================

class HeaderArtWidget(QWidget):

    def __init__(
        self,
        parent=None,
        fit_to_height=False,
        image_path=BELIAL_ART
    ):

        super().__init__(
            parent
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True
        )

        self.image_path = image_path
        self.pixmap = QPixmap(image_path)
        self.fit_to_height = fit_to_height
        self.mirror_horizontally = False
        self.background_opacity = 1.0

    def set_image_path(self, image_path):

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            raise ValueError(
                "Não foi possível carregar a imagem: {}".format(image_path)
            )

        self.image_path = image_path
        self.pixmap = pixmap
        self.update()

    def set_mirrored_horizontally(self, mirrored):

        self.mirror_horizontally = bool(mirrored)
        self.update()

    def set_background_opacity(self, opacity):

        self.background_opacity = max(0.0, min(1.0, opacity))
        self.update()

    def paintEvent(
        self,
        event
    ):

        if self.pixmap.isNull():
            return

        target_size = self.size()
        if self.fit_to_height:
            target_width = round(
                self.pixmap.width()
                * self.height()
                / self.pixmap.height()
            )
            target_size.setWidth(target_width)

        scaled = self.pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        painter = QPainter(self)
        try:
            painter.setRenderHint(
                QPainter.RenderHint.SmoothPixmapTransform
            )
            painter.setOpacity(self.background_opacity)
            if self.mirror_horizontally:
                painter.translate(self.width(), 0)
                painter.scale(-1, 1)

            painter.drawPixmap(
                (self.width() - scaled.width()) // 2,
                (self.height() - scaled.height()) // 2,
                scaled
            )
        finally:
            painter.end()


# =========================================================
# HEADER
# =========================================================

class HeaderWidget(QWidget):

    def __init__(
        self,
        close_callback,
        settings_callback=None,
        artwork_parent=None,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.setFixedHeight(
            95
        )

        self.close_callback = close_callback
        self.settings_callback = settings_callback
        self.artwork_parent = artwork_parent

        self.header_timer_label = None
        self.header_art = None
        self.background_opacity = 1.0

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
            self.artwork_parent or self
        )
        self.header_art = art

        if self.artwork_parent is None:
            art.setFixedWidth(
                260
            )
            layout.addWidget(art)
        else:
            art_space = QWidget(self)
            art_space.setFixedWidth(260)
            layout.addWidget(art_space)

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
        self.header_divider = divider

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

        self.status_label = QLabel(
            "○  AGUARDANDO INÍCIO",
            title_container
        )
        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
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
        title_layout.addWidget(self.status_label)
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
            5,
            5,
            4
        )

        timer_layout.setSpacing(
            0
        )

        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 1)
        actions_layout.setSpacing(4)
        actions_layout.addStretch()

        self.settings_button = QPushButton("⚙")
        self.settings_button.setFixedSize(24, 22)
        self.settings_button.setToolTip("Configurações")
        self.settings_button.setEnabled(
            self.settings_callback is not None
        )
        self.settings_button.setStyleSheet("""
            QPushButton {
                color: #f1e6e7;
                background: #35171b;
                border: 1px solid #87404a;
                border-radius: 4px;
            }

            QPushButton:hover {
                color: #ffffff;
                background: #542027;
                border-color: #c35a66;
            }
        """)
        if self.settings_callback is not None:
            self.settings_button.clicked.connect(
                self.settings_callback
            )
        actions_layout.addWidget(self.settings_button)

        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(24, 22)
        self.close_button.setToolTip("Fechar")
        self.close_button.setStyleSheet("""
            QPushButton {
                color: #f1e6e7;
                background: #35171b;
                border: 1px solid #87404a;
                border-radius: 4px;
                font-size: 16px;
            }

            QPushButton:hover {
                color: #ffffff;
                background: #6b2027;
                border-color: #e1848c;
            }
        """)
        self.close_button.clicked.connect(self.close_callback)
        actions_layout.addWidget(self.close_button)

        timer_layout.addLayout(actions_layout)

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
            timer_label
        )

        layout.addWidget(
            timer_container
        )

    def set_background_opacity(self, opacity):

        self.background_opacity = max(0.0, min(1.0, opacity))
        self.header_art.set_background_opacity(opacity)
        self.update()

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(
            self
        )

        painter.setOpacity(self.background_opacity)
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
