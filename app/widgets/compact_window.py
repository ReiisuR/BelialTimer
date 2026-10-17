from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget
)


class CompactWindow(QWidget):

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

        self.setFixedSize(
            220,
            190
        )

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

    def _build_ui(
        self,
        start_callback,
        restore_callback,
        close_callback
    ):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(2)

        title = QLabel("BELIAL")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #eeeeee;
                background: transparent;
            }
        """)
        title.setFont(QFont("Arial", 11, QFont.Weight.Bold))

        self.close_button = QPushButton("X", self)
        self.close_button.setFixedSize(22, 20)
        self.close_button.setToolTip("Fechar o Belial Timer.")
        self.close_button.setStyleSheet("""
            QPushButton {
                color: #aaaaaa;
                background: #171717;
                border: 1px solid #303030;
                border-radius: 3px;
                padding: 0;
            }

            QPushButton:hover {
                color: #ffffff;
                background: #6b2027;
                border: 1px solid #8a3038;
            }
        """)
        self.close_button.clicked.connect(close_callback)

        self.restore_button = QPushButton("NORMAL", self)
        self.restore_button.setFixedSize(48, 20)
        self.restore_button.setToolTip("Voltar à janela principal.")
        self.restore_button.setStyleSheet("""
            QPushButton {
                color: #aaaaaa;
                background: #171717;
                border: 1px solid #303030;
                border-radius: 3px;
                padding: 0 3px;
            }

            QPushButton:hover {
                color: #ffffff;
                background: #202020;
                border: 1px solid #6b2027;
            }
        """)
        self.restore_button.clicked.connect(restore_callback)

        header = QHBoxLayout()
        header.addWidget(self.restore_button)
        header.addStretch()
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.close_button)

        self.mechanic_label = QLabel("AGUARDANDO...")
        self.mechanic_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mechanic_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                background: transparent;
            }
        """)
        self.mechanic_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))

        self.countdown_label = QLabel("--")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: transparent;
            }
        """)
        compact_font = QFont("Consolas", 36)
        compact_font.setBold(True)
        self.countdown_label.setFont(compact_font)

        self.start_button = QPushButton("INICIAR TIMER", self)
        self.start_button.setFixedHeight(22)
        self.start_button.setStyleSheet("""
            QPushButton {
                color: #dddddd;
                background: #171717;
                border: 1px solid #303030;
                border-radius: 3px;
                padding: 0 8px;
            }

            QPushButton:hover {
                border-color: #6b2027;
            }

            QPushButton:disabled {
                color: #7c464b;
                background: #151515;
                border: 1px solid #292020;
            }
        """)
        self.start_button.clicked.connect(start_callback)

        self.next_label = QLabel("PRÓXIMA: --")
        self.next_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.next_label.setStyleSheet("""
            QLabel {
                color: #777777;
                background: transparent;
            }
        """)
        self.next_label.setFont(QFont("Arial", 7))

        layout.addLayout(header)
        layout.addWidget(self.mechanic_label)
        layout.addWidget(self.countdown_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.next_label)
        self.setStyleSheet("""
            QWidget {
                background: #101010;
                border: 1px solid #4a1d22;
                border-radius: 8px;
            }
        """)

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
