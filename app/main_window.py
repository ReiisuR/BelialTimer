from .config_manager import (
    get_config_path,
    load_config,
    save_config
)
from .alert_system import AlertSystem
from .alert_scheduler import AlertScheduler
from .events import TEST_EVENTS
from .timer_engine import (
    TimerEngine,
    get_event_state
)
from .profile_manager import (
    build_mechanics
)
from .opacity import apply_background_opacity
from .widgets.timeline_widget import TimelineWidget
from .widgets.mechanic_panel import MainPanelBackground
from .widgets.header_widget import (
    BELIAL_ART_OPTIONS,
    HeaderArtWidget,
    HeaderWidget
)
from .widgets.background_widget import BackgroundWidget
from .widgets.compact_window import CompactWindow
from .widgets.settings_dialog import SettingsDialog

from PySide6.QtCore import (
    Qt,
    QTimer,
    QPoint,
    QEvent
)

from PySide6.QtGui import (
    QFont,
    QKeySequence,
    QShortcut,
    QGuiApplication
)

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QDialog,
    QGraphicsOpacityEffect,
    QMessageBox
)


class MainWindow(QWidget):

    def __init__(
        self
    ):

        super().__init__()

        # -------------------------------------------------
        # ESTADO
        # -------------------------------------------------

        self.config_path = get_config_path()

        self.config, config_warning = load_config(
            self.config_path
        )

        self.compact = self.config["compact_mode"]

        self.timer_running = False

        self.game_time = 0

        self.test_mode = self.config["test_mode"]

        self.custom_profile = self.config["custom_profile"]

        self.events = (
            TEST_EVENTS
            if self.test_mode
            else build_mechanics(self.custom_profile)
        )

        self.visual_alerts_enabled = self.config[
            "visual_alerts_enabled"
        ]

        self.start_button = None

        # -------------------------------------------------
        # ALERTAS
        # -------------------------------------------------

        self.alert_system = AlertSystem()

        self.alert_system.enabled = self.config[
            "sound_enabled"
        ]

        self.alert_scheduler = AlertScheduler()

        # -------------------------------------------------
        # MARCO 4
        # Pulso do countdown
        # -------------------------------------------------

        self.countdown_pulse_timer = QTimer(
            self
        )

        self.countdown_pulse_timer.setInterval(
            450
        )

        self.countdown_pulse_timer.timeout.connect(
            self.pulse_countdown
        )

        self.countdown_pulse_active = False

        self.countdown_pulse_phase = False

        # -------------------------------------------------
        # TIMER
        # -------------------------------------------------

        self.timer_engine = TimerEngine(
            self
        )

        self.timer_engine.tick.connect(
            self.update_timer
        )

        # -------------------------------------------------
        # JANELA
        # -------------------------------------------------

        self.setFixedSize(
            680,
            420
        )

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            |
            Qt.WindowType.WindowStaysOnTopHint
            |
            Qt.WindowType.Tool
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self._drag_position = None
        self._position_tracking_ready = False
        self._position_save_timer = QTimer(self)
        self._position_save_timer.setSingleShot(True)
        self._position_save_timer.setInterval(400)
        self._position_save_timer.timeout.connect(
            self._save_active_window_position
        )

        # -------------------------------------------------
        # UI
        # -------------------------------------------------

        self._build_ui()
        self.lying_art_overlay = None
        self.apply_header_art(self.config["header_art"])
        self._text_opacity_effects = []
        self._background_style_widgets = []
        self.apply_display_opacities(
            self.config["background_opacity"],
            self.config["text_opacity"],
            self.config["opacities_linked"]
        )

        self._update_timer_running_ui()

        self.update_sound_button()

        self.apply_visual_alerts_state()

        self.update_timer_display()
        self._restore_window_position("normal", self)
        self._position_tracking_ready = True

        if config_warning:
            QMessageBox.warning(
                self,
                "Configurações",
                config_warning
            )

        if self.compact:
            self._restore_window_position("compact", self.compact_widget)

    def show_startup_mode(self):

        if self.compact:
            self.hide()
            self.compact_widget.show()
            self.compact_widget.raise_()
        else:
            self.show()

    # =====================================================
    # BUILD UI
    # =====================================================

    def _build_ui(
        self
    ):

        self.background = BackgroundWidget(
            self
        )

        self.background.setGeometry(
            self.rect()
        )

        root = QVBoxLayout(
            self.background
        )

        root.setContentsMargins(
            8,
            8,
            8,
            8
        )

        root.setSpacing(
            0
        )

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header = HeaderWidget(
            close_callback=self.close_app,
            settings_callback=self.open_settings,
            artwork_parent=self
        )
        self.header_widget = header
        self.settings_button = header.settings_button
        self.close_button = header.close_button

        self.header_timer_label = (
            header.header_timer_label
        )

        self.header_status_label = (
            header.status_label
        )

        root.addWidget(
            header
        )

        # -------------------------------------------------
        # MAIN PANEL
        # -------------------------------------------------

        self.main_panel = MainPanelBackground()

        self.main_panel.setMinimumHeight(
            240
        )
        header.header_art.setGeometry(
            26,
            -4,
            260,
            195
        )

        panel_layout = QVBoxLayout(
            self.main_panel
        )

        panel_layout.setContentsMargins(
            24,
            17,
            24,
            10
        )

        panel_layout.setSpacing(
            0
        )

        # -------------------------------------------------
        # MECÂNICA ATUAL
        # -------------------------------------------------

        mechanic_title = QLabel(
            "MECÂNICA ATUAL"
        )

        mechanic_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        mechanic_title.setStyleSheet("""
            QLabel {
                color: #9b9b9b;
                background: transparent;
                letter-spacing: 2px;
            }
        """)

        mechanic_title.setFont(
            QFont(
                "Arial",
                8,
                QFont.Weight.Bold
            )
        )

        panel_layout.addWidget(
            mechanic_title
        )

        panel_layout.addSpacing(
            4
        )

        # -------------------------------------------------
        # NOME DA MECÂNICA
        # -------------------------------------------------

        self.mechanic_label = QLabel(
            "AGUARDANDO..."
        )

        self.mechanic_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.mechanic_label.setStyleSheet("""
            QLabel {
                color: #eeeeee;
                background: transparent;
            }
        """)

        self.mechanic_label.setFont(
            QFont(
                "Arial",
                20,
                QFont.Weight.Bold
            )
        )

        panel_layout.addWidget(
            self.mechanic_label
        )

        panel_layout.addSpacing(
            0
        )

        # -------------------------------------------------
        # COUNTDOWN
        # -------------------------------------------------

        self.countdown_label = QLabel(
            "--"
        )

        self.countdown_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.countdown_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: transparent;
                border: none;
            }
        """)

        countdown_font = QFont(
            "Consolas",
            58
        )

        countdown_font.setBold(
            True
        )

        self.countdown_label.setFont(
            countdown_font
        )

        panel_layout.addWidget(
            self.countdown_label
        )

        # -------------------------------------------------
        # PRÓXIMA
        # -------------------------------------------------

        self.next_label = QLabel(
            "PRÓXIMA: --"
        )

        self.next_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.next_label.setStyleSheet("""
            QLabel {
                color: #a0a0a0;
                background: transparent;
            }
        """)

        self.next_label.setFont(
            QFont(
                "Arial",
                8
            )
        )

        panel_layout.addWidget(
            self.next_label
        )

        panel_layout.addStretch()

        # -------------------------------------------------
        # TIMELINE
        # -------------------------------------------------

        self.timeline = TimelineWidget()

        panel_layout.addWidget(
            self.timeline
        )

        root.addWidget(
            self.main_panel,
            1
        )

        # -------------------------------------------------
        # FOOTER
        # -------------------------------------------------

        footer = QWidget()

        footer.setFixedHeight(
            48
        )

        footer_layout = QHBoxLayout(
            footer
        )

        footer_layout.setContentsMargins(
            8,
            7,
            8,
            0
        )

        footer_layout.setSpacing(
            6
        )

        # Início manual
        self.start_button = QPushButton(
            "INICIAR"
        )

        self.start_button.clicked.connect(
            self.start_timer
        )

        # Reset
        self.reset_button = QPushButton(
            "RESETAR"
        )

        self.reset_button.clicked.connect(
            self.reset_timer
        )

        # Som
        self.sound_button = QPushButton(
            "● SOM ATIVO"
        )

        self.sound_button.clicked.connect(
            self.toggle_sound
        )

        # Alertas
        self.alerts_button = QPushButton(
            "ALERTAS ON"
        )

        self.alerts_button.clicked.connect(
            self.toggle_visual_alerts
        )

        # Compacto
        self.compact_button = QPushButton(
            "COMPACTO"
        )

        self.compact_button.clicked.connect(
            self.toggle_compact_mode
        )

        buttons = [
            self.start_button,
            self.reset_button,
            self.sound_button,
            self.alerts_button,
            self.compact_button
        ]

        for button in buttons:

            button.setFixedHeight(
                29
            )

            button.setStyleSheet("""
                QPushButton {
                    color: #f1e6e7;
                    background: #35171b;
                    border: 1px solid #87404a;
                    border-radius: 4px;
                    padding: 0 9px;
                }

                QPushButton:hover {
                    color: #ffffff;
                    background: #542027;
                    border: 1px solid #c35a66;
                }

                QPushButton:pressed {
                    background: #6b2027;
                    border-color: #e1848c;
                }

                QPushButton:disabled {
                    color: #a8787d;
                    background: #241619;
                    border: 1px solid #533037;
                }
            """)

            button.setFont(
                QFont(
                    "Arial",
                    7,
                    QFont.Weight.Bold
                )
            )

            footer_layout.addWidget(
                button
            )

        root.addWidget(
            footer
        )

        # -------------------------------------------------
        self.compact_widget = CompactWindow(
            start_callback=self.start_timer,
            restore_callback=self.toggle_compact_mode,
            close_callback=self.close_app
        )
        self.compact_widget.position_changed.connect(
            self._schedule_position_save
        )

        self.compact_mechanic_label = self.compact_widget.mechanic_label
        self.compact_countdown_label = self.compact_widget.countdown_label
        self.compact_start_button = self.compact_widget.start_button
        self.compact_next_label = self.compact_widget.next_label
        self.opacity_reset_shortcut = QShortcut(
            QKeySequence("Ctrl+Shift+O"),
            self
        )
        self.opacity_reset_shortcut.activated.connect(
            self.restore_full_opacity
        )
        self.compact_opacity_reset_shortcut = QShortcut(
            QKeySequence("Ctrl+Shift+O"),
            self.compact_widget
        )
        self.compact_opacity_reset_shortcut.activated.connect(
            self.restore_full_opacity
        )
        self.header_widget.header_art.raise_()

    # =====================================================
    # LABEL HELPER
    # =====================================================

    def _label(
        self,
        text,
        size=10,
        color="#ffffff"
    ):

        label = QLabel(
            text
        )

        label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        label.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background: transparent;
            }}
            """
        )

        label.setFont(
            QFont(
                "Arial",
                size
            )
        )

        return label

    # =====================================================
    # START TIMER
    # =====================================================

    def start_timer(
        self
    ):

        if self.timer_running:
            return

        self.timer_running = True

        self._update_timer_running_ui()

        self.timer_engine.start()

    def _update_timer_running_ui(
        self
    ):

        if self.timer_running:

            self.header_status_label.setText(
                "●  EM ANDAMENTO"
            )

            self.start_button.setText(
                "RODANDO"
            )

            self.compact_start_button.setText(
                "EM ANDAMENTO"
            )

        else:

            self.header_status_label.setText(
                "○  AGUARDANDO INÍCIO"
            )

            self.start_button.setText(
                "INICIAR"
            )

            self.compact_start_button.setText(
                "INICIAR TIMER"
            )

        self.start_button.setEnabled(
            not self.timer_running
        )

        self.compact_start_button.setEnabled(
            not self.timer_running
        )

    # =====================================================
    # UPDATE TIMER
    # =====================================================

    def update_timer(
        self,
        elapsed_seconds
    ):

        if not self.timer_running:
            return

        self.game_time = elapsed_seconds

        self.update_timer_display()

    # =====================================================
    # UPDATE DISPLAY
    # =====================================================

    def update_timer_display(
        self
    ):

        current_time = self.game_time

        # -------------------------------------------------
        # TIMER PRINCIPAL
        # -------------------------------------------------

        formatted_time = self.format_time(
            current_time
        )

        self.header_timer_label.setText(
            formatted_time
        )

        # -------------------------------------------------
        # ENCONTRA EVENTO ATUAL
        # -------------------------------------------------

        event_state = get_event_state(
            self.events,
            current_time,
            show_first_during_countdown=not self.test_mode
        )

        current_index = event_state.current_index
        next_index = event_state.next_index
        last_started_index = event_state.last_started_index
        current_event = event_state.current_event
        next_event = event_state.next_event
        remaining = event_state.remaining
        if last_started_index < 0:
            display_event = current_event
            display_current_index = current_index
            display_next_index = next_index
            display_next_event = next_event
        elif next_event is not None:
            display_event = next_event
            display_current_index = next_index
            display_next_index = next_index + 1
            display_next_event = (
                self.events[display_next_index]
                if display_next_index < len(self.events)
                else None
            )
        else:
            display_event = current_event
            display_current_index = current_index
            display_next_index = next_index
            display_next_event = None

        # -------------------------------------------------
        # INTERROMPE O PULSO AO INICIAR UMA MECÂNICA
        # -------------------------------------------------

        mechanic_changed = (
            last_started_index >= 0
            and last_started_index
            != self.alert_scheduler.last_mechanic_event
        )

        if mechanic_changed:

            self.countdown_pulse_timer.stop()

            self.countdown_pulse_active = False

            self.countdown_pulse_phase = False

        # -------------------------------------------------
        # ALERTAS
        # -------------------------------------------------

        scheduled_alerts = []

        if self.timer_running:
            scheduled_alerts = self.update_alerts(
                last_started_index,
                next_index,
                next_event,
                remaining
            )

        # -------------------------------------------------
        # MECÂNICA ATUAL
        # -------------------------------------------------

        if display_event is not None:

            self.main_panel.set_background(
                display_event.get(
                    "background"
                )
            )

            self.mechanic_label.setText(
                display_event["name"]
            )

            self.compact_mechanic_label.setText(
                display_event["short"]
            )

        else:

            self.main_panel.set_background(
                None
            )

            self.mechanic_label.setText(
                "AGUARDANDO..."
            )

            self.compact_mechanic_label.setText(
                "AGUARDANDO..."
            )

        # -------------------------------------------------
        # PRÓXIMA
        # -------------------------------------------------

        if display_next_event is not None:

            self.next_label.setText(
                "PRÓXIMA: "
                + display_next_event["name"]
            )

            self.compact_next_label.setText(
                "PRÓXIMA: "
                + display_next_event["short"]
            )

        else:

            self.next_label.setText(
                "PRÓXIMA: --"
            )

            self.compact_next_label.setText(
                "PRÓXIMA: --"
            )

        # -------------------------------------------------
        # COUNTDOWN
        # -------------------------------------------------

        countdown_text = self.format_time(
            max(
                0,
                remaining
            )
        )

        self.countdown_label.setText(
            countdown_text
        )

        self.compact_countdown_label.setText(
            countdown_text
        )

        # -------------------------------------------------
        # ESTILO COUNTDOWN
        # -------------------------------------------------

        self.update_countdown_style(
            remaining
        )

        self.update_compact_countdown_style(
            remaining
        )

        # -------------------------------------------------
        # MARCO 4 — PULSO
        # -------------------------------------------------

        if (
            self.visual_alerts_enabled
            and
            remaining <= 2
            and remaining > 0
            and not mechanic_changed
        ):

            if not self.countdown_pulse_timer.isActive():

                self.countdown_pulse_active = True

                self.countdown_pulse_timer.start()

        else:

            self.countdown_pulse_timer.stop()

            self.countdown_pulse_active = False

            self.countdown_pulse_phase = False

        # -------------------------------------------------
        # TIMELINE
        # -------------------------------------------------

        self.update_timeline(
            display_current_index,
            display_next_index,
            last_started_index
        )

    def update_timeline(
        self,
        current_index,
        next_index,
        last_started_index=None
    ):

        if last_started_index is None:
            last_started_index = current_index

        max_start = max(
            0,
            len(self.events) - 3
        )

        if current_index < 0:

            start_index = 0

        else:

            start_index = max(
                0,
                min(
                    current_index - 1,
                    max_start
                )
            )

        timeline_events = self.events[
            start_index:start_index + 3
        ]

        self.timeline.set_events(
            timeline_events,
            current_index=current_index,
            next_index=(
                next_index
                if next_index < len(self.events)
                else None
            ),
            start_index=start_index,
            last_started_index=last_started_index
        )

    # =====================================================
    # ALERTAS
    # =====================================================

    def update_alerts(
        self,
        current_index,
        next_index,
        next_event,
        remaining
    ):

        alerts = self.alert_scheduler.alerts_for_state(
            current_index=current_index,
            next_index=next_index,
            has_next_event=next_event is not None,
            remaining=remaining
        )

        alert_methods = {
            "mechanic": self.alert_system.mechanic,
            "warning": self.alert_system.warning,
            "countdown": self.alert_system.countdown,
            "critical": self.alert_system.critical
        }

        for alert_name in alerts:
            alert_methods[alert_name]()

        return alerts

    # =====================================================
    # COUNTDOWN STYLE
    # =====================================================

    def update_countdown_style(
        self,
        remaining
    ):

        if not self.visual_alerts_enabled:

            color = "#ffffff"

            size = 58

        elif remaining > 3:

            color = "#ffffff"

            size = 58

        elif remaining == 3:

            color = "#e4aeb5"

            size = 60

        elif remaining == 2:

            pulse_active = (
                self.countdown_pulse_timer.isActive()
                and not self.compact
                and 0 < remaining <= 2
            )

            color = (
                "#ff9ba3"
                if pulse_active
                and self.countdown_pulse_phase
                else "#ff858f"
            )

            size = 63

        elif remaining == 1:

            pulse_active = (
                self.countdown_pulse_timer.isActive()
                and not self.compact
                and 0 < remaining <= 2
            )

            color = (
                "#ffb0b6"
                if pulse_active
                and self.countdown_pulse_phase
                else "#ff707d"
            )

            size = 66

        else:

            color = "#ffffff"

            size = 58

        self.countdown_label.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background: transparent;
                border: none;
            }}
            """
        )

        font = QFont(
            "Consolas",
            size
        )

        font.setBold(
            True
        )

        self.countdown_label.setFont(
            font
        )

    # =====================================================
    # MARCO 4 — PULSO DO COUNTDOWN
    # =====================================================

    def pulse_countdown(
        self
    ):

        if not self.timer_running:

            self.countdown_pulse_timer.stop()

            return

        if not self.visual_alerts_enabled:

            self.countdown_pulse_timer.stop()

            return

        # Não interfere no modo compacto
        if self.compact:

            return

        # Descobre o tempo restante atual
        current_time = self.game_time

        event_state = get_event_state(
            self.events,
            current_time,
            show_first_during_countdown=not self.test_mode
        )

        if event_state.next_event is None:

            self.countdown_pulse_timer.stop()

            return

        remaining = event_state.remaining

        if remaining > 2:

            self.countdown_pulse_timer.stop()

            self.countdown_pulse_active = False

            self.countdown_pulse_phase = False

            self.update_countdown_style(
                remaining
            )

            return

        # Alterna a cor sem redimensionar o texto durante o pulso.
        self.countdown_pulse_phase = (
            not self.countdown_pulse_phase
        )

        self.update_countdown_style(
            remaining
        )

    # =====================================================
    # COMPACT COUNTDOWN
    # =====================================================

    def update_compact_countdown_style(
        self,
        remaining
    ):

        if not self.visual_alerts_enabled:

            color = "#ffffff"

            size = 36

        elif remaining > 3:

            color = "#ffffff"

            size = 36

        elif remaining == 3:

            color = "#e4aeb5"

            size = 38

        else:

            color = "#ff707d"

            size = 40

        self.compact_countdown_label.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background: transparent;
            }}
            """
        )

        font = QFont(
            "Consolas",
            size
        )

        font.setBold(
            True
        )

        self.compact_countdown_label.setFont(
            font
        )

    # =====================================================
    # SOM
    # =====================================================

    def toggle_sound(
        self
    ):

        self.alert_system.enabled = (
            not self.alert_system.enabled
        )

        self.update_sound_button()

        self._save_user_config()

    def update_sound_button(
        self
    ):

        if self.alert_system.enabled:

            self.sound_button.setText(
                "● SOM ATIVO"
            )

            self.sound_button.setStyleSheet("""
                QPushButton {
                    color: #f1e6e7;
                    background: #35171b;
                    border: 1px solid #87404a;
                    border-radius: 4px;
                    padding: 0 9px;
                }

                QPushButton:hover {
                    color: #ffffff;
                    background: #542027;
                    border: 1px solid #c35a66;
                }
            """)

        else:

            self.sound_button.setText(
                "○ SOM DESATIVADO"
            )

            self.sound_button.setStyleSheet("""
                QPushButton {
                    color: #cbb8bb;
                    background: #241619;
                    border: 1px solid #533037;
                    border-radius: 4px;
                    padding: 0 9px;
                }

                QPushButton:hover {
                    color: #ffffff;
                    background: #3b2024;
                    border: 1px solid #87404a;
                }
            """)

    def toggle_visual_alerts(
        self
    ):

        self.visual_alerts_enabled = (
            not self.visual_alerts_enabled
        )

        self.apply_visual_alerts_state()

        self._save_user_config()

    def apply_visual_alerts_state(
        self
    ):

        self.timeline.set_visual_alerts_enabled(
            self.visual_alerts_enabled
        )

        if not self.visual_alerts_enabled:

            self.countdown_pulse_timer.stop()

            self.countdown_pulse_active = False

            self.countdown_pulse_phase = False

        self.alerts_button.setText(
            "ALERTAS ON"
            if self.visual_alerts_enabled
            else "ALERTAS OFF"
        )

        self.alerts_button.setStyleSheet(
            """
            QPushButton {
                color: %s;
                background: %s;
                border: 1px solid %s;
                border-radius: 4px;
                padding: 0 9px;
            }

            QPushButton:hover {
                color: #ffffff;
                background: #542027;
                border: 1px solid #c35a66;
            }
            """
            % (
                "#f1e6e7"
                if self.visual_alerts_enabled
                else "#cbb8bb",
                "#35171b"
                if self.visual_alerts_enabled
                else "#241619",
                "#87404a"
                if self.visual_alerts_enabled
                else "#533037"
            )
        )

        event_state = get_event_state(
            self.events,
            self.game_time,
            show_first_during_countdown=not self.test_mode
        )

        self.update_countdown_style(
            event_state.remaining
        )

        self.update_compact_countdown_style(
            event_state.remaining
        )

    def open_settings(
        self
    ):

        dialog = SettingsDialog(
            sound_enabled=self.alert_system.enabled,
            visual_alerts_enabled=self.visual_alerts_enabled,
            test_mode=self.test_mode,
            profile=self.custom_profile,
            background_opacity=self.config["background_opacity"],
            text_opacity=self.config["text_opacity"],
            opacities_linked=self.config["opacities_linked"],
            header_art=self.config["header_art"],
            parent=self
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self.alert_system.enabled = (
            dialog.sound_checkbox.isChecked()
        )
        self.config["header_art"] = dialog.header_art_combo.currentData()
        self.apply_header_art(self.config["header_art"])

        self.visual_alerts_enabled = (
            dialog.visual_alerts_checkbox.isChecked()
        )
        self.update_sound_button()

        self.apply_visual_alerts_state()
        self.apply_display_opacities(
            dialog.background_opacity_slider.value(),
            dialog.text_opacity_slider.value(),
            dialog.link_opacities_button.isChecked()
        )

        selected_test_mode = bool(
            dialog.event_mode_combo.currentData()
        )
        updated_profile = dialog.custom_profile
        profile_changed = updated_profile != self.custom_profile
        mode_changed = selected_test_mode != self.test_mode
        was_running = self.timer_running

        self.custom_profile = updated_profile
        self.config["custom_profile"] = updated_profile
        self.test_mode = selected_test_mode

        self.events = (
            TEST_EVENTS
            if self.test_mode
            else build_mechanics(self.custom_profile)
        )

        if mode_changed or profile_changed:
            self.reset_timer(
                start_after_reset=was_running
            )

        self._save_user_config()

    def apply_header_art(self, art_name):

        art = self.header_widget.header_art
        art.set_image_path(BELIAL_ART_OPTIONS[art_name])
        is_lying = art_name == "deitada"
        art.set_mirrored_horizontally(is_lying)

        if is_lying:
            if self.lying_art_overlay is None:
                self.lying_art_overlay = HeaderArtWidget(
                    self,
                    image_path=BELIAL_ART_OPTIONS["deitada"]
                )
                self.lying_art_overlay.setWindowFlags(
                    Qt.WindowType.Tool
                    | Qt.WindowType.FramelessWindowHint
                    | Qt.WindowType.WindowStaysOnTopHint
                    | Qt.WindowType.WindowDoesNotAcceptFocus
                )
                self.lying_art_overlay.setAttribute(
                    Qt.WidgetAttribute.WA_TranslucentBackground,
                    True
                )
                self.lying_art_overlay.setAttribute(
                    Qt.WidgetAttribute.WA_ShowWithoutActivating,
                    True
                )
                self.lying_art_overlay.setStyleSheet(
                    "background: transparent; border: none;"
                )

            art.hide()
            self.lying_art_overlay.set_image_path(
                BELIAL_ART_OPTIONS["deitada"]
            )
            self.lying_art_overlay.set_mirrored_horizontally(True)
            self.lying_art_overlay.set_background_opacity(
                self.config["background_opacity"] / 100
            )
            self._position_lying_art_overlay()
            if self.isVisible() and not self.compact:
                self.lying_art_overlay.show()
                self.lying_art_overlay.raise_()
                QTimer.singleShot(0, self._raise_lying_art_overlay)
        else:
            if self.lying_art_overlay is not None:
                self.lying_art_overlay.hide()
            art.show()
            art.setGeometry(26, -4, 260, 195)

    def moveEvent(self, event):

        super().moveEvent(event)
        self._position_lying_art_overlay()
        if (
            self._position_tracking_ready
            and not self.compact
            and self.isVisible()
        ):
            self._schedule_position_save()

    def showEvent(self, event):

        super().showEvent(event)
        self._position_lying_art_overlay()
        if (
            self.lying_art_overlay is not None
            and self.config["header_art"] == "deitada"
            and not self.compact
        ):
            self.lying_art_overlay.show()
            self.lying_art_overlay.raise_()
            QTimer.singleShot(0, self._raise_lying_art_overlay)

    def changeEvent(self, event):

        super().changeEvent(event)
        if event.type() != QEvent.Type.WindowStateChange:
            return

        overlay = getattr(self, "lying_art_overlay", None)
        if overlay is None:
            return

        if self.isMinimized():
            overlay.hide()
        elif (
            self.isVisible()
            and not self.compact
            and self.config["header_art"] == "deitada"
        ):
            QTimer.singleShot(0, self._raise_lying_art_overlay)

    def hideEvent(self, event):

        super().hideEvent(event)
        if self.lying_art_overlay is not None:
            self.lying_art_overlay.hide()

    def _position_lying_art_overlay(self):

        overlay = getattr(self, "lying_art_overlay", None)
        if overlay is None:
            return

        position = self.mapToGlobal(QPoint(-95, -80))
        overlay.setGeometry(
            position.x(),
            position.y(),
            360,
            270
        )

    def _raise_lying_art_overlay(self):

        overlay = getattr(self, "lying_art_overlay", None)
        if (
            overlay is not None
            and self.isVisible()
            and not self.compact
            and self.config["header_art"] == "deitada"
        ):
            self._position_lying_art_overlay()
            overlay.show()
            overlay.raise_()

    def _restore_window_position(self, mode, window, fallback=None):

        positions = self.config.get("window_positions", {})
        saved_position = positions.get(mode)
        position = saved_position if saved_position is not None else fallback
        if position is None:
            return False

        point = QPoint(position[0], position[1])
        screen = QGuiApplication.screenAt(point)
        if screen is None:
            screen = QGuiApplication.primaryScreen()
        if screen is None:
            window.move(point)
            return True

        bounds = screen.availableGeometry()
        margin = 48
        min_x = bounds.left() - window.width() + margin
        max_x = bounds.right() - margin
        min_y = bounds.top() - window.height() + margin
        max_y = bounds.bottom() - margin
        if min_x > max_x:
            min_x = max_x = bounds.left()
        if min_y > max_y:
            min_y = max_y = bounds.top()

        window.move(
            max(min_x, min(point.x(), max_x)),
            max(min_y, min(point.y(), max_y))
        )
        return True

    def _store_window_position(self, mode, window):

        positions = self.config.setdefault(
            "window_positions",
            {"normal": None, "compact": None}
        )
        position = window.pos()
        positions[mode] = [position.x(), position.y()]

    def _schedule_position_save(self):

        if self._position_tracking_ready:
            self._position_save_timer.start()

    def _save_active_window_position(self):

        if self.compact:
            if self.compact_widget.isVisible():
                self._store_window_position("compact", self.compact_widget)
        elif self.isVisible():
            self._store_window_position("normal", self)

        self._save_user_config()

    def _save_user_config(
        self
    ):

        self.config.update({
            "sound_enabled": self.alert_system.enabled,
            "visual_alerts_enabled": self.visual_alerts_enabled,
            "compact_mode": self.compact,
            "test_mode": self.test_mode,
            "background_opacity": self.config["background_opacity"],
            "text_opacity": self.config["text_opacity"],
            "opacities_linked": self.config["opacities_linked"],
            "header_art": self.config["header_art"],
            "window_positions": self.config["window_positions"],
            "custom_profile": self.custom_profile
        })

        try:
            save_config(
                self.config,
                self.config_path
            )
        except OSError as error:
            QMessageBox.warning(
                self,
                "Configurações",
                "Não foi possível salvar as configurações em:\n{}\n\n{}".format(
                    self.config_path,
                    error
                )
            )

    def apply_display_opacities(
        self,
        background_opacity,
        text_opacity,
        opacities_linked
    ):

        background_opacity = max(0, min(100, int(background_opacity)))
        text_opacity = max(0, min(100, int(text_opacity)))
        self.config["background_opacity"] = background_opacity
        self.config["text_opacity"] = text_opacity
        self.config["opacities_linked"] = bool(opacities_linked)
        background_value = background_opacity / 100
        text_value = text_opacity / 100

        self.background.set_background_opacity(background_value)
        self.main_panel.set_background_opacity(background_value)
        self.header_widget.set_background_opacity(background_value)
        self.compact_widget.set_background_opacity(background_opacity)
        if self.lying_art_overlay is not None:
            self.lying_art_overlay.set_background_opacity(background_value)

        styled_widgets = [
            *self.findChildren(QWidget),
            self.compact_widget,
            *self.compact_widget.findChildren(QWidget)
        ]
        for widget in styled_widgets:
            if widget.styleSheet() and not isinstance(widget, QPushButton):
                apply_background_opacity(widget, background_opacity)

        if not self._text_opacity_effects:
            text_widgets = [
                *self.findChildren(QLabel),
                *self.compact_widget.findChildren(QLabel),
                self.timeline
            ]
            seen_widgets = set()
            for widget in text_widgets:
                if widget in seen_widgets:
                    continue
                seen_widgets.add(widget)
                effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(effect)
                self._text_opacity_effects.append(effect)

        for effect in self._text_opacity_effects:
            effect.setOpacity(text_value)

    def restore_full_opacity(self):

        self.apply_display_opacities(100, 100, True)
        self._save_user_config()

    # =====================================================
    # RESET
    # =====================================================

    def reset_timer(
        self,
        start_after_reset=False
    ):

        self.timer_engine.stop()

        self.countdown_pulse_timer.stop()

        self.timer_running = False

        self.game_time = 0

        self.countdown_pulse_active = False

        self.countdown_pulse_phase = False

        # -------------------------------------------------
        # RESET ALERTAS
        # -------------------------------------------------

        self.alert_scheduler.reset()

        # -------------------------------------------------
        # RESET DISPLAY
        # -------------------------------------------------

        self.header_timer_label.setText(
            "00:00"
        )

        self.mechanic_label.setText(
            "AGUARDANDO..."
        )

        self.next_label.setText(
            "PRÓXIMA: --"
        )

        self.countdown_label.setText(
            "--"
        )

        self.compact_mechanic_label.setText(
            "AGUARDANDO..."
        )

        self.compact_next_label.setText(
            "PRÓXIMA: --"
        )

        self.compact_countdown_label.setText(
            "--"
        )

        self.main_panel.set_background(
            None
        )

        self.update_countdown_style(
            99
        )

        self.update_compact_countdown_style(
            99
        )

        self.update_timeline(
            -1,
            0,
            -1
        )

        self._update_timer_running_ui()

        self.update_timer_display()

        if start_after_reset:

            self.start_timer()

    # =====================================================
    # FORMAT TIME
    # =====================================================

    @staticmethod
    def format_time(
        seconds
    ):

        seconds = max(
            0,
            int(seconds)
        )

        minutes = (
            seconds // 60
        )

        secs = (
            seconds % 60
        )

        return (
            f"{minutes:02d}:"
            f"{secs:02d}"
        )

    # =====================================================
    # COMPACT MODE
    # =====================================================

    def toggle_compact_mode(
        self
    ):

        if not self.compact:
            self._store_window_position("normal", self)
            normal_position = self.pos()
            self.compact = True
            self._restore_window_position(
                "compact",
                self.compact_widget,
                fallback=[normal_position.x(), normal_position.y()]
            )

            self.hide()
            self.compact_widget.show()
            self.compact_widget.raise_()
        else:
            self._store_window_position("compact", self.compact_widget)
            self.compact = False

            self.compact_widget.hide()
            self._restore_window_position("normal", self)
            self.show()
            self.raise_()
            self.activateWindow()
            QTimer.singleShot(0, self._raise_lying_art_overlay)

        self._position_save_timer.stop()
        self._save_user_config()

    # ARRASTAR JANELA
    # =====================================================

    def mousePressEvent(
        self,
        event
    ):

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):

            self._drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

            event.accept()

    def mouseMoveEvent(
        self,
        event
    ):

        if (
            self._drag_position is not None
            and event.buttons()
            & Qt.MouseButton.LeftButton
        ):

            self.move(
                event.globalPosition().toPoint()
                - self._drag_position
            )

            event.accept()

    def mouseReleaseEvent(
        self,
        event
    ):

        self._drag_position = None

        event.accept()

    # =====================================================
    # FECHAR
    # =====================================================

    def close_app(
        self
    ):

        if self.compact and self.compact_widget.isVisible():
            self._store_window_position("compact", self.compact_widget)
        elif self.isVisible():
            self._store_window_position("normal", self)
        self._position_save_timer.stop()
        self._save_user_config()

        self.timer_engine.stop()

        self.countdown_pulse_timer.stop()

        self.compact_widget.hide()

        self.close()

        application = QApplication.instance()

        if application is not None:

            application.quit()
