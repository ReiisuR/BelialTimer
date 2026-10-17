from copy import deepcopy

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)

from ..events import REAL_EVENTS
from .header_widget import BELIAL_ART_OPTIONS
from ..profile_manager import (
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
        background_opacity=85,
        text_opacity=85,
        opacities_linked=True,
        header_art="sentada",
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

            QSlider::groove:horizontal {
                height: 4px;
                background: #303030;
                border-radius: 2px;
            }

            QSlider::sub-page:horizontal {
                background: #6b2027;
                border-radius: 2px;
            }

            QSlider::handle:horizontal {
                width: 14px;
                margin: -5px 0;
                background: #c94450;
                border: 1px solid #e28b91;
                border-radius: 7px;
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
                test_mode,
                background_opacity,
                text_opacity,
                opacities_linked,
                header_art
            ),
            "Geral"
        )
        self.tabs.addTab(
            self._build_mechanics_page(),
            "Mecânicas"
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
        test_mode,
        background_opacity,
        text_opacity,
        opacities_linked,
        header_art
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

        self.header_art_combo = QComboBox()
        self.header_art_combo.addItem("Belial sentada", "sentada")
        self.header_art_combo.addItem("Belial deitada", "deitada")
        self.header_art_combo.setCurrentIndex(
            0 if header_art == "sentada" else 1
        )
        self.header_art_preview = QLabel()
        self.header_art_preview.setFixedSize(240, 140)
        self.header_art_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_art_preview.setStyleSheet(
            "background: #171717; border: 1px solid #303030; border-radius: 4px;"
        )
        self.header_art_combo.currentIndexChanged.connect(
            self._update_header_art_preview
        )
        art_row = QHBoxLayout()
        art_row.addWidget(self.header_art_combo)
        art_row.addWidget(self.header_art_preview)
        art_row.addStretch(1)
        form.addRow("Imagem do modo normal:", art_row)
        self._update_header_art_preview()

        self.background_opacity_slider = QSlider(
            Qt.Orientation.Horizontal
        )
        self.background_opacity_slider.setRange(0, 100)
        self.background_opacity_slider.setValue(background_opacity)
        self.background_opacity_value_label = QLabel(
            "{}%".format(self.background_opacity_slider.value())
        )
        self.background_opacity_slider.valueChanged.connect(
            self._on_background_opacity_changed
        )
        background_row = QHBoxLayout()
        background_row.addWidget(self.background_opacity_slider, 1)
        background_row.addWidget(self.background_opacity_value_label)
        form.addRow("Opacidade do fundo:", background_row)

        self.text_opacity_slider = QSlider(
            Qt.Orientation.Horizontal
        )
        self.text_opacity_slider.setRange(0, 100)
        self.text_opacity_slider.setValue(text_opacity)
        self.text_opacity_value_label = QLabel(
            "{}%".format(self.text_opacity_slider.value())
        )
        self.text_opacity_slider.valueChanged.connect(
            self._on_text_opacity_changed
        )
        text_row = QHBoxLayout()
        text_row.addWidget(self.text_opacity_slider, 1)
        text_row.addWidget(self.text_opacity_value_label)
        form.addRow("Opacidade das letras:", text_row)

        self.link_opacities_button = QPushButton()
        self.link_opacities_button.setCheckable(True)
        self.link_opacities_button.setChecked(opacities_linked)
        self.link_opacities_button.toggled.connect(
            self._on_opacities_linked_changed
        )
        self._update_link_button_text(opacities_linked)
        if opacities_linked:
            self._set_text_opacity_value(
                self.background_opacity_slider.value()
            )
        form.addRow(self.link_opacities_button)

        opacity_note = QLabel(
            "A opacidade do fundo também afeta as imagens; "
            "os botões mantêm contraste para continuarem legíveis. "
            "0% = invisível; 100% = totalmente opaco. "
            "Os ajustes valem nos modos normal e compacto. "
            "Ctrl+Shift+O restaura fundo e letras a 100%."
        )
        opacity_note.setWordWrap(True)
        form.addRow(opacity_note)
        layout.addLayout(form)

        note = QLabel(
            "As preferências e o perfil personalizado são salvos "
            "localmente para as próximas execuções."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch(1)
        return page

    def _update_header_art_preview(self):

        art_name = self.header_art_combo.currentData()
        image_path = BELIAL_ART_OPTIONS[art_name]
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            self.header_art_preview.clear()
            self.header_art_preview.setText(
                "Imagem indisponível:\n{}".format(image_path)
            )
            return

        if art_name == "deitada":
            mirrored_pixmap = QPixmap(pixmap.size())
            mirrored_pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(mirrored_pixmap)
            try:
                painter.translate(pixmap.width(), 0)
                painter.scale(-1, 1)
                painter.drawPixmap(0, 0, pixmap)
            finally:
                painter.end()
            pixmap = mirrored_pixmap

        self.header_art_preview.setText("")
        self.header_art_preview.setPixmap(
            pixmap.scaled(
                self.header_art_preview.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def _on_background_opacity_changed(self, value):

        self.background_opacity_value_label.setText(
            "{}%".format(value)
        )
        if self.link_opacities_button.isChecked():
            self._set_text_opacity_value(value)

    def _on_text_opacity_changed(self, value):

        self.text_opacity_value_label.setText(
            "{}%".format(value)
        )
        if self.link_opacities_button.isChecked():
            blocker = QSignalBlocker(self.background_opacity_slider)
            self.background_opacity_slider.setValue(value)
            del blocker
            self.background_opacity_value_label.setText(
                "{}%".format(value)
            )

    def _set_text_opacity_value(self, value):

        blocker = QSignalBlocker(self.text_opacity_slider)
        self.text_opacity_slider.setValue(value)
        del blocker
        self.text_opacity_value_label.setText(
            "{}%".format(value)
        )

    def _on_opacities_linked_changed(self, linked):

        if linked:
            self._set_text_opacity_value(
                self.background_opacity_slider.value()
            )
        self._update_link_button_text(linked)

    def _update_link_button_text(self, linked):

        self.link_opacities_button.setText(
            "OPACIDADES VINCULADAS"
            if linked
            else "VINCULAR OPACIDADES"
        )

    def _build_mechanics_page(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        note = QLabel(
            "Edite o horário exato de início de cada mecânica. "
            "Ao chegar nele, a contagem passa para a próxima ocorrência."
        )
        note.setWordWrap(True)
        layout.addWidget(note)

        self.mechanics_table = QTableWidget(
            len(self.profile["mechanics"]),
            3
        )
        self.mechanics_table.setHorizontalHeaderLabels([
            "N.º",
            "Mecânica",
            "Início (MM:SS)"
        ])
        self.mechanics_table.verticalHeader().hide()
        self.mechanics_table.setAlternatingRowColors(True)
        self.mechanics_table.setColumnWidth(0, 45)
        self.mechanics_table.setColumnWidth(1, 330)
        self.mechanics_table.setColumnWidth(2, 150)

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

        layout.addWidget(self.mechanics_table)
        return page

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
        self.tabs.insertTab(
            1,
            self._build_mechanics_page(),
            "Mecânicas"
        )
        self.tabs.setCurrentIndex(0)

    def _read_profile(self):

        mechanics = []
        for row, template in enumerate(REAL_EVENTS):
            name_input = self.mechanics_table.cellWidget(row, 1)
            start_input = self.mechanics_table.cellWidget(row, 2)

            try:
                start_time = parse_mmss(start_input.text())
            except ValueError as error:
                raise ValueError(
                    "Mecânica {:02d}: {}".format(row + 1, error)
                ) from error

            mechanics.append({
                "id": template["id"],
                "name": name_input.text(),
                "start_time": start_time
            })

        profile, error = validate_profile({
            "mechanics": mechanics
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
