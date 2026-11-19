"""Central de DGs com cartões temáticos e navegação por pesquisa."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QScrollArea, QVBoxLayout, QWidget
)

from .design_system.tokens import BASE_QSS
from .design_system.theme_manager import get_dungeon_theme
from .dungeon_catalog import filter_dungeons


class DungeonCard(QFrame):
    selected = Signal(str)

    def __init__(self, dungeon, parent=None):
        super().__init__(parent)
        self.dungeon = dungeon
        self.setObjectName("dungeonCard")
        self.setMinimumHeight(226)
        self.setMaximumWidth(420)
        theme = get_dungeon_theme(dungeon["theme"])

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        self.banner = QLabel()
        self.banner.setFixedHeight(74)
        self.banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.banner.setStyleSheet(
            "background: %s; border-radius: 7px; color: %s;"
            % (theme["banner"], theme["accent"])
        )
        image_path = theme.get("image")
        if image_path:
            image = QPixmap(image_path)
            if not image.isNull():
                self.banner.setPixmap(image.scaled(
                    400, 74,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                ))
        if self.banner.pixmap() is None or self.banner.pixmap().isNull():
            self.banner.setText("◆  " + (dungeon["acronym"] or dungeon["name"]).upper())
        root.addWidget(self.banner)

        title = dungeon["name"]
        if dungeon["acronym"]:
            title += " (" + dungeon["acronym"] + ")"
        name = QLabel(title)
        name.setObjectName("cardTitle")
        name.setWordWrap(True)
        root.addWidget(name)

        access = " • ".join(filter(None, (dungeon["npc"], dungeon["location"])))
        detail = QLabel(access or "Timer de mecânicas")
        detail.setObjectName("cardDetail")
        detail.setWordWrap(True)
        root.addWidget(detail)

        variants = QLabel(
            "  ·  ".join(dungeon["difficulties"]) if dungeon["difficulties"]
            else ("Timer" if dungeon["type"] == "timer" else "Dificuldades a definir")
        )
        variants.setObjectName("cardDetail")
        variants.setWordWrap(True)
        root.addWidget(variants)

        button = QPushButton(
            "ABRIR TIMER" if dungeon["type"] == "timer" else "VER INFORMAÇÕES"
        )
        button.clicked.connect(lambda: self.selected.emit(dungeon["id"]))
        if dungeon["type"] != "timer":
            button.setStyleSheet("background: #39313E; border-color: #574251;")
        root.addWidget(button)
        self.action_button = button


class DungeonDashboard(QWidget):
    belial_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("dashboard")
        self.setWindowTitle("BelialTimer | Central de DGs")
        self.resize(920, 660)
        self.setMinimumSize(650, 470)
        self.setStyleSheet(BASE_QSS)
        self.cards = []

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(154)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(14, 24, 14, 18)
        side_layout.setSpacing(12)
        brand = QLabel("BELIAL TIMER")
        brand.setStyleSheet("color: #C6A16B; font-weight: bold; font-size: 14px;")
        side_layout.addWidget(brand)
        nav = QLabel("◆  DGs")
        nav.setStyleSheet("color: #F4EDF1; font-weight: bold; padding: 12px 4px;")
        side_layout.addWidget(nav)
        side_layout.addStretch()
        root.addWidget(sidebar)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 22, 24, 22)
        content_layout.setSpacing(14)
        heading = QLabel("CENTRAL DE DGs")
        heading.setObjectName("heading")
        content_layout.addWidget(heading)
        description = QLabel("Escolha uma DG para consultar informações ou abrir o timer.")
        description.setObjectName("subheading")
        content_layout.addWidget(description)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText("Buscar por DG, sigla ou NPC...")
        self.search_input.textChanged.connect(self.refresh_cards)
        content_layout.addWidget(self.search_input)

        filters = QHBoxLayout()
        filters.setSpacing(7)
        self.filter_buttons = {}
        for difficulty in ("Todas", "Normal", "Difícil", "Fácil"):
            button = QPushButton(difficulty)
            button.setObjectName("filter")
            button.setCheckable(True)
            button.setChecked(difficulty == "Todas")
            button.clicked.connect(
                lambda checked=False, name=difficulty: self.set_difficulty(name)
            )
            self.filter_buttons[difficulty] = button
            filters.addWidget(button)
        filters.addStretch()
        content_layout.addLayout(filters)
        self.active_difficulty = "Todas"

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(12)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.grid_container)
        content_layout.addWidget(scroll, 1)
        root.addWidget(content, 1)

        self.refresh_cards()

    def set_difficulty(self, difficulty):
        self.active_difficulty = difficulty
        for name, button in self.filter_buttons.items():
            button.setChecked(name == difficulty)
        self.refresh_cards()

    def refresh_cards(self, *_):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.cards = []
        matches = filter_dungeons(
            self.search_input.text(), self.active_difficulty
        )
        for index, dungeon in enumerate(matches):
            card = DungeonCard(dungeon, self.grid_container)
            card.selected.connect(self.open_dungeon)
            self.grid.addWidget(card, index // 2, index % 2)
            self.cards.append(card)
        if not matches:
            empty = QLabel("Nenhuma DG encontrada para os filtros selecionados.")
            empty.setObjectName("subheading")
            self.grid.addWidget(empty, 0, 0)

    def open_dungeon(self, dungeon_id):
        if dungeon_id == "belial":
            self.belial_requested.emit()
            return
        from .dungeon_catalog import DUNGEONS
        dungeon = next(d for d in DUNGEONS if d["id"] == dungeon_id)
        difficulty = ", ".join(dungeon["difficulties"]) or "A definir"
        QMessageBox.information(
            self,
            dungeon["name"],
            "NPC: {}\nAcesso: {}\nDificuldades: {}\n\n"
            "Guia de mecânicas em preparação.".format(
                dungeon["npc"], dungeon["location"], difficulty
            ),
        )
