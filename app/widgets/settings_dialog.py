from copy import deepcopy

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)

from ..events import REAL_EVENTS
from ..profile_manager import (
    SKILL_NAMES,
    clone_default_profile,
    format_mmss,
    parse_mmss,
    validate_profile
)


class SettingsDialog(QDialog):

    def __init__(
        self,
        sound_enabled,
        visual_alerts_enabled,
        test_mode,
        profile=None,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.setWindowTitle(
            "CONFIGURAÇÕES"
        )

        self.setFixedSize(
            760,
            650
        )

        self.setStyleSheet("""
            QDialog {
                color: #dddddd;
                background: #101010;
            }

            QLabel {
                color: #aaaaaa;
            }

            QCheckBox, QComboBox, QLineEdit, QTableWidget {
                color: #dddddd;
                background: #171717;
                border: 1px solid #303030;
                border-radius: 3px;
                padding: 4px;
            }

            QTableWidget {
                gridline-color: #303030;
            }

            QHeaderView::section {
                color: #aaaaaa;
                background: #151515;
                border: 1px solid #303030;
                padding: 5px;
            }

            QComboBox QAbstractItemView {
                color: #dddddd;
                background: #171717;
                selection-background-color: #6b2027;
            }

            QPushButton {
                color: #dddddd;
                background: #171717;
                border: 1px solid #303030;
                border-radius: 3px;
                padding: 6px 12px;
            }

            QPushButton:hover {
                border-color: #6b2027;
            }

            QTabWidget::pane {
                border: 1px solid #303030;
            }

            QTabBar::tab {
                color: #aaaaaa;
                background: #151515;
                padding: 7px 14px;
            }

            QTabBar::tab:selected {
                color: #eeeeee;
                background: #202020;
                border-bottom: 2px solid #6b2027;
            }

            QGroupBox {
                color: #dddddd;
                border: 1px solid #303030;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)

        self.profile = deepcopy(
            profile
            if profile is not None
            else clone_default_profile()
        )
        self.custom_profile = None

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 12)
        root.setSpacing(10)

        self.tabs = QTabWidget()
        self.tabs.addTab(
            self._build_general_page(
                sound_enabled,
                visual_alerts_enabled,
                test_mode
            ),
            "Geral"
        )
        self.tabs.addTab(
            self._build_mechanics_page(),
            "Mecânicas"
        )
        self.tabs.addTab(
            self._build_skills_page(),
            "Skills"
        )
        root.addWidget(self.tabs, 1)

        self.validation_label = QLabel()
        self.validation_label.setStyleSheet("color: #d77b83;")
        self.validation_label.setWordWrap(True)
        self.validation_label.hide()
        root.addWidget(self.validation_label)

        footer = QHBoxLayout()
        self.restore_defaults_button = QPushButton(
            "Restaurar perfil padrão"
        )
        self.restore_defaults_button.clicked.connect(
            self.restore_profile_defaults
        )
        footer.addWidget(self.restore_defaults_button)
        footer.addStretch(1)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        footer.addWidget(self.button_box)
        root.addLayout(footer)

    def _build_general_page(
        self,
        sound_enabled,
        visual_alerts_enabled,
        test_mode
    ):

        page = QWidget()
        layout = QVBoxLayout(page)
        form = QFormLayout()

        self.sound_checkbox = QCheckBox(
            "Ativar alertas sonoros"
        )
        self.sound_checkbox.setChecked(sound_enabled)

        self.visual_alerts_checkbox = QCheckBox(
            "Ativar alertas visuais"
        )
        self.visual_alerts_checkbox.setChecked(
            visual_alerts_enabled
        )

        form.addRow(self.sound_checkbox)
        form.addRow(self.visual_alerts_checkbox)

        self.event_mode_combo = QComboBox()
        self.event_mode_combo.addItem(
            "Sequência de teste",
            True
        )
        self.event_mode_combo.addItem(
            "Sequência real do Belial",
            False
        )
        self.event_mode_combo.setCurrentIndex(
            0 if test_mode else 1
        )
        form.addRow("Eventos:", self.event_mode_combo)
        layout.addLayout(form)

        note = QLabel(
            "As preferências e o perfil personalizado são salvos "
            "localmente para as próximas execuções."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch(1)
        return page

    def _build_mechanics_page(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        note = QLabel(
            "Edite os horários de início e a duração visual. "
            "Uma duração vazia mantém a mecânica ativa até outra regra."
        )
        note.setWordWrap(True)
        layout.addWidget(note)

        self.mechanics_table = QTableWidget(
            len(self.profile["mechanics"]),
            4
        )
        self.mechanics_table.setHorizontalHeaderLabels([
            "N.º",
            "Mecânica",
            "Início (MM:SS)",
            "Duração (MM:SS)"
        ])
        self.mechanics_table.verticalHeader().hide()
        self.mechanics_table.setAlternatingRowColors(True)
        self.mechanics_table.setColumnWidth(0, 45)
        self.mechanics_table.setColumnWidth(1, 245)
        self.mechanics_table.setColumnWidth(2, 135)
        self.mechanics_table.setColumnWidth(3, 145)

        for row, mechanic in enumerate(self.profile["mechanics"]):
            number = QTableWidgetItem(
                "{:02d}".format(row + 1)
            )
            number.setFlags(
                number.flags()
                & ~Qt.ItemFlag.ItemIsEditable
            )
            self.mechanics_table.setItem(row, 0, number)

            name_input = QLineEdit(mechanic["name"])
            self.mechanics_table.setCellWidget(row, 1, name_input)

            start_input = self._time_input(
                format_mmss(mechanic["start_time"])
            )
            self.mechanics_table.setCellWidget(row, 2, start_input)
            name_input.textChanged.connect(
                self._refresh_skill_target_labels
            )
            start_input.textChanged.connect(
                self._refresh_skill_target_labels
            )

            duration_input = self._time_input(
                format_mmss(mechanic["duration_seconds"])
            )
            duration_input.setPlaceholderText("MM:SS")
            self.mechanics_table.setCellWidget(row, 3, duration_input)

        layout.addWidget(self.mechanics_table)
        return page

    def _build_skills_page(self):

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)

        self.skill_target_tables = {}
        self.skill_target_labels = {}

        mechanics_by_id = {
            mechanic["id"]: mechanic
            for mechanic in self.profile["mechanics"]
        }

        for skill in self.profile["skills"]:
            group = QGroupBox(skill["name"])
            group_layout = QVBoxLayout(group)
            group_layout.addWidget(QLabel(
                "Marque cada ocorrência-alvo e informe quantos segundos "
                "antes deseja receber o lembrete. Deixe desmarcado ou "
                "sem antecedência para não agendar aviso."
            ))

            table = QTableWidget(len(REAL_EVENTS), 3)
            table.setHorizontalHeaderLabels([
                "Usar",
                "Mecânica-alvo",
                "Aviso antes (MM:SS)"
            ])
            table.verticalHeader().hide()
            table.setColumnWidth(0, 55)
            table.setColumnWidth(1, 380)
            table.setColumnWidth(2, 160)
            table.setFixedHeight(250)

            associations = skill["associations"]
            self.skill_target_labels[skill["id"]] = {}
            for row, event in enumerate(REAL_EVENTS):
                checkbox = QCheckBox()
                checkbox.setChecked(
                    event["id"] in associations
                )
                checkbox_cell = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_cell)
                checkbox_layout.setContentsMargins(6, 0, 0, 0)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                table.setCellWidget(row, 0, checkbox_cell)

                mechanic = mechanics_by_id[event["id"]]
                target_label = QTableWidgetItem(
                    "{}  {}".format(
                        format_mmss(mechanic["start_time"]),
                        mechanic["name"]
                    )
                )
                target_label.setFlags(
                    target_label.flags()
                    & ~Qt.ItemFlag.ItemIsEditable
                )
                table.setItem(row, 1, target_label)
                self.skill_target_labels[skill["id"]][event["id"]] = (
                    target_label
                )

                lead_time = associations.get(event["id"])
                lead_input = self._time_input(
                    format_mmss(lead_time)
                )
                lead_input.setPlaceholderText("MM:SS")
                table.setCellWidget(row, 2, lead_input)

            self.skill_target_tables[skill["id"]] = table
            group_layout.addWidget(table)
            layout.addWidget(group)

        self._refresh_skill_target_labels()
        layout.addStretch(1)
        scroll.setWidget(content)
        return scroll

    def _refresh_skill_target_labels(self):

        if not hasattr(self, "skill_target_labels"):
            return

        for row, event in enumerate(REAL_EVENTS):
            name_input = self.mechanics_table.cellWidget(row, 1)
            start_input = self.mechanics_table.cellWidget(row, 2)
            name = name_input.text().strip() or event["name"]
            try:
                start_time = format_mmss(
                    parse_mmss(start_input.text())
                )
            except ValueError:
                start_time = start_input.text().strip() or "??:??"

            label_text = "{}  {}".format(start_time, name)
            for labels in self.skill_target_labels.values():
                labels[event["id"]].setText(label_text)

    @staticmethod
    def _time_input(value):

        line_edit = QLineEdit(value)
        line_edit.setMaxLength(6)
        line_edit.setPlaceholderText("MM:SS")
        line_edit.setFixedWidth(125)
        return line_edit

    def restore_profile_defaults(self):

        self.profile = clone_default_profile()
        self.tabs.removeTab(1)
        self.tabs.removeTab(1)
        self.tabs.insertTab(
            1,
            self._build_mechanics_page(),
            "Mecânicas"
        )
        self.tabs.insertTab(
            2,
            self._build_skills_page(),
            "Skills"
        )
        self.tabs.setCurrentIndex(0)

    def _read_profile(self):

        mechanics = []
        for row, template in enumerate(REAL_EVENTS):
            name_input = self.mechanics_table.cellWidget(row, 1)
            start_input = self.mechanics_table.cellWidget(row, 2)
            duration_input = self.mechanics_table.cellWidget(row, 3)

            try:
                start_time = parse_mmss(start_input.text())
                duration = parse_mmss(
                    duration_input.text(),
                    allow_empty=True
                )
            except ValueError as error:
                raise ValueError(
                    "Mecânica {:02d}: {}".format(row + 1, error)
                ) from error

            mechanics.append({
                "id": template["id"],
                "name": name_input.text(),
                "start_time": start_time,
                "duration_seconds": duration
            })

        skills = []
        for skill_id, skill_name in SKILL_NAMES.items():
            associations = {}
            table = self.skill_target_tables[skill_id]
            for row, event in enumerate(REAL_EVENTS):
                checkbox_cell = table.cellWidget(row, 0)
                checkbox = checkbox_cell.findChild(QCheckBox)

                if not checkbox.isChecked():
                    continue

                lead_input = table.cellWidget(row, 2)
                try:
                    lead_time = parse_mmss(
                        lead_input.text(),
                        allow_empty=True
                    )
                except ValueError as error:
                    raise ValueError(
                        "{} → {}: {}".format(
                            skill_name,
                            event["name"],
                            error
                        )
                    ) from error

                associations[event["id"]] = lead_time

            skills.append({
                "id": skill_id,
                "name": skill_name,
                "associations": associations
            })

        profile, error = validate_profile({
            "mechanics": mechanics,
            "skills": skills
        })

        if error:
            raise ValueError(error)

        return profile

    def accept(self):

        try:
            self.custom_profile = self._read_profile()
        except ValueError as error:
            self.validation_label.setText(str(error))
            self.validation_label.show()
            return

        self.validation_label.clear()
        super().accept()
