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
    build_mechanics,
    build_skill_reminders
)
from .widgets.timeline_widget import TimelineWidget
from .widgets.mechanic_panel import MainPanelBackground
from .widgets.header_widget import HeaderWidget
from .widgets.background_widget import BackgroundWidget
from .widgets.compact_window import CompactWindow
from .widgets.settings_dialog import SettingsDialog

from PySide6.QtCore import (
    Qt,
    QTimer,
)

from PySide6.QtGui import (
    QFont,
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

        self.compact = False

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

        # -------------------------------------------------
        # UI
        # -------------------------------------------------

        self._build_ui()

        self._update_timer_running_ui()

        self.update_sound_button()

        self.apply_visual_alerts_state()

        self.update_timer_display()

        if config_warning:
            QMessageBox.warning(
                self,
                "Configurações",
                config_warning
            )

        if self.config["compact_mode"]:
            self.toggle_compact_mode()

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
            self.close_app
        )

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

        # Configurações
        settings_button = QPushButton(
            "CONFIG"
        )

        settings_button.clicked.connect(
            self.open_settings
        )

        # Compacto
        compact_button = QPushButton(
            "COMPACTO"
        )

        compact_button.clicked.connect(
            self.toggle_compact_mode
        )

        # Reset
        reset_button = QPushButton(
            "RESETAR"
        )

        reset_button.clicked.connect(
            lambda: self.reset_timer()
        )

        # Fechar
        close_button = QPushButton(
            "FECHAR"
        )

        close_button.clicked.connect(
            self.close_app
        )

        buttons = [
            self.start_button,
            self.sound_button,
            self.alerts_button,
            settings_button,
            compact_button,
            reset_button,
            close_button
        ]

        for button in buttons:

            button.setFixedHeight(
                29
            )

            button.setStyleSheet("""
                QPushButton {
                    color: #aaaaaa;
                    background: #171717;
                    border: 1px solid #303030;
                    border-radius: 4px;
                    padding: 0 9px;
                }

                QPushButton:hover {
                    color: #eeeeee;
                    background: #202020;
                    border: 1px solid #6b2027;
                }

                QPushButton:pressed {
                    background: #101010;
                }

                QPushButton:disabled {
                    color: #7c464b;
                    background: #151515;
                    border: 1px solid #292020;
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

        self.compact_mechanic_label = self.compact_widget.mechanic_label
        self.compact_countdown_label = self.compact_widget.countdown_label
        self.compact_start_button = self.compact_widget.start_button
        self.compact_next_label = self.compact_widget.next_label

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
            current_time
        )

        current_index = event_state.current_index
        next_index = event_state.next_index
        last_started_index = event_state.last_started_index
        current_event = event_state.current_event
        next_event = event_state.next_event
        remaining = event_state.remaining

        new_skill_reminders = set()
        if not self.test_mode and self.timer_running:
            skill_reminders = build_skill_reminders(
                self.custom_profile,
                self.events
            )
            new_skill_reminders = self.alert_scheduler.new_skill_reminders(
                skill_reminders,
                current_time
            )

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

        if (
            self.timer_running
            and new_skill_reminders
            and not scheduled_alerts
        ):
            self.alert_system.mechanic()

        # -------------------------------------------------
        # MECÂNICA ATUAL
        # -------------------------------------------------

        if current_event is not None:

            self.main_panel.set_background(
                current_event.get(
                    "background"
                )
            )

            self.mechanic_label.setText(
                current_event["name"]
            )

            self.compact_mechanic_label.setText(
                current_event["short"]
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

        if next_event is not None:

            self.next_label.setText(
                "PRÓXIMA: "
                + next_event["name"]
            )

            self.compact_next_label.setText(
                "PRÓXIMA: "
                + next_event["short"]
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
            current_index,
            next_index,
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

        if last_started_index < 0:

            start_index = 0

        else:

            start_index = max(
                0,
                min(
                    last_started_index - 1,
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
            current_time
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
                    color: #aaaaaa;
                    background: #171717;
                    border: 1px solid #303030;
                    border-radius: 4px;
                    padding: 0 9px;
                }

                QPushButton:hover {
                    color: #eeeeee;
                    background: #202020;
                    border: 1px solid #6b2027;
                }
            """)

        else:

            self.sound_button.setText(
                "○ SOM DESATIVADO"
            )

            self.sound_button.setStyleSheet("""
                QPushButton {
                    color: #777777;
                    background: #121212;
                    border: 1px solid #292929;
                    border-radius: 4px;
                    padding: 0 9px;
                }

                QPushButton:hover {
                    color: #aaaaaa;
                    background: #1b1b1b;
                    border: 1px solid #444444;
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
                background: #171717;
                border: 1px solid #303030;
                border-radius: 4px;
                padding: 0 9px;
            }

            QPushButton:hover {
                color: #eeeeee;
                background: #202020;
                border: 1px solid #6b2027;
            }
            """
            % (
                "#aaaaaa"
                if self.visual_alerts_enabled
                else "#777777"
            )
        )

        event_state = get_event_state(
            self.events,
            self.game_time
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
            parent=self
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self.alert_system.enabled = (
            dialog.sound_checkbox.isChecked()
        )

        self.visual_alerts_enabled = (
            dialog.visual_alerts_checkbox.isChecked()
        )

        self.update_sound_button()

        self.apply_visual_alerts_state()

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

    def _save_user_config(
        self
    ):

        self.config.update({
            "sound_enabled": self.alert_system.enabled,
            "visual_alerts_enabled": self.visual_alerts_enabled,
            "compact_mode": self.compact,
            "test_mode": self.test_mode,
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

    # =====================================================
    # RESET
    # =====================================================

    def reset_timer(
        self,
        start_after_reset=True
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

        self.compact = (
            not self.compact
        )

        self._save_user_config()

        if self.compact:

            self.hide()

            self.compact_widget.move(
                20,
                20
            )

            self.compact_widget.show()

            self.compact_widget.raise_()

        else:

            self.compact_widget.hide()

            self.show()

            self.raise_()

            self.activateWindow()

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

        self.timer_engine.stop()

        self.countdown_pulse_timer.stop()

        self.compact_widget.hide()

        self.close()

        application = QApplication.instance()

        if application is not None:

            application.quit()
