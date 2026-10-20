from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QFrame,
    QPushButton,
    QVBoxLayout,
    QWidget
)

from .header_widget import BELIAL_ELBOW_ART, HeaderArtWidget


class CompactWindow(QWidget):

    position_changed = Signal()

    def __init__(
        self,
        start_callback,
        restore_callback,
        close_callback
    ):

        super().__init__(
            None,
            Qt.WindowType.Tool
            |
            Qt.WindowType.FramelessWindowHint
            |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            True
        )

        self.setFixedSize(380, 330)

        self.setToolTip(
            "Dê duplo clique para voltar à janela principal."
        )

        self._drag_position = None
        self._build_ui(
            start_callback,
            restore_callback,
            close_callback
        )

        self.installEventFilter(self)

        for child in self.findChildren(QWidget):
            child.installEventFilter(self)

        self.hide()

    def set_background_opacity(self, opacity):

        opacity = max(0, min(100, int(opacity)))
        alpha = opacity / 100
        self.content_panel.setStyleSheet("""
            QWidget#compactPanel {{
                background: rgba(16, 16, 16, {alpha:.2f});
                border: 1px solid rgba(135, 64, 74, {alpha:.2f});
                border-radius: 8px;
            }}
        """.format(alpha=alpha))
        self.character_art.set_background_opacity(alpha)

    def _build_ui(
        self,
        start_callback,
        restore_callback,
        close_callback
    ):

        self.content_panel = QWidget(self)
        self.content_panel.setObjectName("compactPanel")
        self.content_panel.setGeometry(
            8,
            148,
            self.width() - 16,
            self.height() - 156
        )

        self.character_art = HeaderArtWidget(
            self,
            fit_to_height=True,
            image_path=BELIAL_ELBOW_ART
        )
        self.character_art.setGeometry(35, -18, 310, 225)

        layout = QVBoxLayout(self.content_panel)
        layout.setContentsMargins(14, 10, 14, 8)
        layout.setSpacing(4)

        title = QLabel("BELIAL")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #eeeeee;
                background: transparent;
            }
        """)
        title.setFont(QFont("Arial", 11, QFont.Weight.Bold))

        self.close_button = QPushButton("X", self.content_panel)
        self.close_button.setFixedSize(22, 20)
        self.close_button.setToolTip("Fechar o Belial Timer.")
        self.close_button.setStyleSheet("""
            QPushButton {
                color: #f1e6e7;
                background: #35171b;
                border: 1px solid #87404a;
                border-radius: 3px;
                padding: 0;
            }

            QPushButton:hover {
                color: #ffffff;
                background: #6b2027;
                border: 1px solid #e1848c;
            }
        """)
        self.close_button.clicked.connect(close_callback)

        self.restore_button = QPushButton("NORMAL", self.content_panel)
        self.restore_button.setFixedSize(66, 22)
        self.restore_button.setToolTip("Voltar à janela principal.")
        self.restore_button.setStyleSheet("""
            QPushButton {
                color: #f1e6e7;
                background: #35171b;
                border: 1px solid #87404a;
                border-radius: 3px;
                padding: 0 3px;
            }

            QPushButton:hover {
                color: #ffffff;
                background: #542027;
                border: 1px solid #c35a66;
            }
        """)
        self.restore_button.clicked.connect(restore_callback)

        header = QGridLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setHorizontalSpacing(0)
        header.setColumnMinimumWidth(0, self.restore_button.width())
        header.setColumnMinimumWidth(2, self.restore_button.width())
        header.setColumnStretch(1, 1)
        header.addWidget(self.restore_button, 0, 0, Qt.AlignmentFlag.AlignLeft)
        header.addWidget(title, 0, 1, Qt.AlignmentFlag.AlignCenter)
        header.addWidget(self.close_button, 0, 2, Qt.AlignmentFlag.AlignRight)

        self.mechanic_label = QLabel("AGUARDANDO...")
        self.mechanic_label.setParent(self.content_panel)
        self.mechanic_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mechanic_label.setFixedHeight(22)
        self.mechanic_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                background: transparent;
            }
        """)
        self.mechanic_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))

        self.countdown_label = QLabel("--", self.content_panel)
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setFixedHeight(48)
        self.countdown_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: transparent;
            }
        """)
        compact_font = QFont("Consolas", 36)
        compact_font.setBold(True)
        self.countdown_label.setFont(compact_font)

        self.start_button = QPushButton("INICIAR TIMER", self.content_panel)
        self.start_button.setFixedHeight(25)
        self.start_button.setStyleSheet("""
            QPushButton {
                color: #f1e6e7;
                background: #35171b;
                border: 1px solid #87404a;
                border-radius: 3px;
                padding: 0 8px;
            }

            QPushButton:hover {
                color: #ffffff;
                background: #542027;
                border-color: #c35a66;
            }

            QPushButton:disabled {
                color: #a8787d;
                background: #241619;
                border: 1px solid #533037;
            }
        """)
        self.start_button.clicked.connect(start_callback)

        self.next_label = QLabel("PRÓXIMA: --", self.content_panel)
        self.next_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.next_label.setFixedHeight(18)
        self.next_label.setStyleSheet("""
            QLabel {
                color: #777777;
                background: transparent;
            }
        """)
        self.next_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))

        layout.addLayout(header)
        layout.addWidget(self.mechanic_label)
        layout.addWidget(self.countdown_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.next_label)
        layout.addStretch(1)
        divider = QFrame(self.content_panel)
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #4a252b; border: none;")
        layout.insertWidget(1, divider)
        self.set_background_opacity(100)
        self.character_art.raise_()

    def eventFilter(
        self,
        watched,
        event
    ):

        if isinstance(watched, QPushButton):
            return super().eventFilter(watched, event)

        if event.type() == QEvent.Type.MouseButtonDblClick:
            self._drag_position = None
            self.restore_button.click()
            return True

        if (
            event.type() == QEvent.Type.MouseButtonPress
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            return True

        if (
            event.type() == QEvent.Type.MouseMove
            and self._drag_position is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint()
                - self._drag_position
            )
            return True

        if (
            event.type() == QEvent.Type.MouseButtonRelease
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._drag_position = None
            return True

        return super().eventFilter(watched, event)

    def moveEvent(self, event):

        super().moveEvent(event)
        self.position_changed.emit()
