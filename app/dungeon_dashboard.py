"""Central de DGs: ponto de entrada para os módulos do aplicativo."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
)


class DungeonDashboard(QWidget):
    belial_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BelialTimer | Central de DGs")
        self.setMinimumSize(540, 380)

        self.setStyleSheet("""
            QWidget { background: #17151c; color: #f3edf0; }
            QLabel#heading { font-size: 24px; font-weight: bold; }
            QLabel#description { color: #b7aab3; font-size: 12px; }
            QFrame#dungeonCard {
                background: #27202b; border: 1px solid #67414f;
                border-radius: 10px;
            }
            QPushButton {
                background: #743747; border: 1px solid #aa6074;
                border-radius: 6px; padding: 10px 16px;
                color: white; font-weight: bold;
            }
            QPushButton:hover { background: #93485d; }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(14)

        heading = QLabel("CENTRAL DE DGs")
        heading.setObjectName("heading")
        root.addWidget(heading)

        description = QLabel(
            "Escolha uma DG para abrir seu timer ou guia de mecânicas."
        )
        description.setObjectName("description")
        description.setWordWrap(True)
        root.addWidget(description)

        card = QFrame()
        card.setObjectName("dungeonCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(10)

        name = QLabel("BELIAL")
        name.setStyleSheet("font-size: 18px; font-weight: bold;")
        card_layout.addWidget(name)
        detail = QLabel(
            "Timer de mecânicas com contagem regressiva e alertas."
        )
        detail.setObjectName("description")
        detail.setWordWrap(True)
        card_layout.addWidget(detail)

        actions = QHBoxLayout()
        self.open_belial_button = QPushButton("ABRIR TIMER")
        self.open_belial_button.clicked.connect(self.belial_requested.emit)
        actions.addWidget(self.open_belial_button)
        actions.addStretch()
        card_layout.addLayout(actions)
        root.addWidget(card)

        note = QLabel(
            "Outras DGs e guias de habilidades serão adicionados aqui."
        )
        note.setObjectName("description")
        note.setWordWrap(True)
        root.addWidget(note)
        root.addStretch()
