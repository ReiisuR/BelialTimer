from PySide6.QtCore import Qt, QRectF, QPoint, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


class TimelineWidget(QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.setFixedHeight(
            58
        )

        self.events = []

        self.start_index = 0

        self.current_index = None

        self.next_index = None
        self.last_started_index = -1

        self.visual_alerts_enabled = True

        self.entry_animation_ticks = 0

        self.entry_animation_timer = QTimer(
            self
        )

        self.entry_animation_timer.setInterval(
            60
        )

        self.entry_animation_timer.timeout.connect(
            self._advance_entry_animation
        )

    def set_visual_alerts_enabled(
        self,
        enabled
    ):

        self.visual_alerts_enabled = enabled

        if not enabled:

            self.entry_animation_ticks = 0

            self.entry_animation_timer.stop()

        self.update()

    def set_events(
        self,
        events,
        current_index=None,
        next_index=None,
        start_index=0,
        last_started_index=None
    ):

        if last_started_index is None:
            last_started_index = (
                current_index
                if current_index is not None
                else -1
            )

        self.events = events

        self.start_index = start_index

        if not self.visual_alerts_enabled:

            self.entry_animation_ticks = 0

            self.entry_animation_timer.stop()

        if current_index is None or current_index < 0:

            self.entry_animation_ticks = 0

            self.entry_animation_timer.stop()

        elif (
            self.visual_alerts_enabled
            and
            current_index is not None
            and current_index != self.current_index
        ):

            self.entry_animation_ticks = 8

            self.entry_animation_timer.start()

        self.current_index = current_index

        self.next_index = next_index
        self.last_started_index = last_started_index

        self.update()

    def _advance_entry_animation(
        self
    ):

        self.entry_animation_ticks -= 1

        if self.entry_animation_ticks <= 0:

            self.entry_animation_ticks = 0

            self.entry_animation_timer.stop()

        self.update()

    def event_state(
        self,
        event_index
    ):

        if event_index == self.current_index:
            return "current"

        if event_index == self.next_index:
            return "next"

        if (
            event_index <= self.last_started_index
            and event_index != self.current_index
        ):
            return "past"

        return "upcoming"

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        width = self.width()

        if not self.events:
            return

        center_y = 22

        left = 35
        right = width - 35

        # Linha
        painter.setPen(
            QPen(
                QColor("#454545"),
                2
            )
        )

        painter.drawLine(
            left,
            center_y,
            right,
            center_y
        )

        count = len(
            self.events
        )

        if count == 1:

            positions = [
                width / 2
            ]

        elif count == 2:

            positions = [
                left + 25,
                right - 25
            ]

        else:

            step = (
                right - left
            ) / (count - 1)

            positions = [
                left + (
                    step * i
                )
                for i in range(count)
            ]

        for i, event_data in enumerate(
            self.events
        ):

            event_index = (
                self.start_index + i
            )

            state = self.event_state(
                event_index
            )

            if state == "current":

                node_color = QColor(
                    "#c94450"
                )

                radius = 7

            elif state == "next":

                node_color = QColor(
                    "#d28c93"
                )

                radius = 6

            else:

                node_color = QColor(
                    "#555555"
                    if state == "past"
                    else "#686868"
                )

                radius = 4

            if (
                state == "current"
                and self.entry_animation_ticks > 0
            ):

                progress = (
                    self.entry_animation_ticks
                    / 8
                )

                pulse_color = QColor(
                    201,
                    68,
                    80,
                    int(150 * progress)
                )

                painter.setBrush(
                    Qt.BrushStyle.NoBrush
                )

                painter.setPen(
                    QPen(
                        pulse_color,
                        1.5
                    )
                )

                painter.drawEllipse(
                    QPoint(
                        int(positions[i]),
                        center_y
                    ),
                    9 + self.entry_animation_ticks // 4,
                    9 + self.entry_animation_ticks // 4
                )

            self.draw_mechanic_icon(
                painter,
                int(positions[i]),
                center_y,
                event_data,
                node_color,
                radius
            )

            # Nome
            name = event_data.get(
                "short",
                ""
            )

            painter.setPen(
                QColor(
                    "#dedede"
                    if state == "current"
                    else (
                        "#c99ba1"
                        if state == "next"
                        else "#777777"
                    )
                )
            )

            font = QFont(
                "Arial",
                8
            )

            if state in ("current", "next"):
                font.setBold(True)

            painter.setFont(
                font
            )

            painter.drawText(
                QRectF(
                    positions[i] - 55,
                    29,
                    110,
                    16
                ),
                Qt.AlignmentFlag.AlignCenter,
                name
            )

            # Tempo
            painter.setPen(
                QColor("#686868")
            )

            painter.setFont(
                QFont(
                    "Consolas",
                    7
                )
            )

            time_text = self.format_time(
                event_data.get(
                    "time",
                    0
                )
            )

            painter.drawText(
                QRectF(
                    positions[i] - 55,
                    44,
                    110,
                    12
                ),
                Qt.AlignmentFlag.AlignCenter,
                time_text
            )

    @staticmethod
    def draw_mechanic_icon(
        painter,
        center_x,
        center_y,
        event_data,
        node_color,
        radius
    ):

        painter.save()

        center = QPoint(
            center_x,
            center_y
        )

        icon_radius = max(
            6,
            radius + 2
        )

        painter.setBrush(
            QColor("#171717")
        )

        painter.setPen(
            QPen(
                node_color,
                1.2
            )
        )

        painter.drawEllipse(
            center,
            icon_radius,
            icon_radius
        )

        mechanic_name = event_data.get(
            "name",
            event_data.get("short", "")
        ).upper()

        symbol_color = QColor("#d8d8d8")

        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )

        if "SILENCE" in mechanic_name:

            painter.setPen(
                QPen(
                    symbol_color,
                    1.2
                )
            )

            painter.drawEllipse(
                center,
                3,
                3
            )

            painter.drawLine(
                center_x - 5,
                center_y + 5,
                center_x + 5,
                center_y - 5
            )

        elif "LASER" in mechanic_name:

            painter.setPen(
                QPen(
                    QColor("#e45a63"),
                    1.5
                )
            )

            painter.drawLine(
                center_x - 5,
                center_y - 3,
                center_x + 5,
                center_y - 3
            )

            painter.setPen(
                QPen(
                    QColor("#5aa7e4"),
                    1.5
                )
            )

            painter.drawLine(
                center_x - 5,
                center_y + 3,
                center_x + 5,
                center_y + 3
            )

        elif "BRAS" in mechanic_name:

            shield = QPainterPath()

            shield.moveTo(
                center_x - 4,
                center_y - 4
            )

            shield.lineTo(
                center_x + 4,
                center_y - 4
            )

            shield.lineTo(
                center_x + 3,
                center_y + 1
            )

            shield.lineTo(
                center_x,
                center_y + 5
            )

            shield.lineTo(
                center_x - 3,
                center_y + 1
            )

            shield.closeSubpath()

            painter.setPen(
                QPen(
                    QColor("#e2b76b"),
                    1
                )
            )

            painter.setBrush(
                QColor("#6b2027")
            )

            painter.drawPath(
                shield
            )

        elif "CIRCULO" in mechanic_name:

            painter.setPen(
                QPen(
                    QColor("#a58ad3"),
                    1.2
                )
            )

            painter.setBrush(
                QColor("#09070d")
            )

            painter.drawEllipse(
                center,
                4,
                4
            )

        elif "ARANHA" in mechanic_name:

            painter.setPen(
                QPen(
                    symbol_color,
                    1
                )
            )

            painter.drawLine(
                center_x - 2,
                center_y - 1,
                center_x - 5,
                center_y - 4
            )

            painter.drawLine(
                center_x - 2,
                center_y + 1,
                center_x - 5,
                center_y + 4
            )

            painter.drawLine(
                center_x + 2,
                center_y - 1,
                center_x + 5,
                center_y - 4
            )

            painter.drawLine(
                center_x + 2,
                center_y + 1,
                center_x + 5,
                center_y + 4
            )

            painter.setBrush(
                symbol_color
            )

            painter.drawEllipse(
                QPoint(
                    center_x,
                    center_y
                ),
                2,
                3
            )

        elif "HITKILL" in mechanic_name:

            warning = QPainterPath()

            warning.moveTo(
                center_x,
                center_y - 5
            )

            warning.lineTo(
                center_x + 5,
                center_y + 4
            )

            warning.lineTo(
                center_x - 5,
                center_y + 4
            )

            warning.closeSubpath()

            painter.setPen(
                QPen(
                    QColor("#e2b76b"),
                    1
                )
            )

            painter.drawPath(
                warning
            )

            painter.drawLine(
                center_x,
                center_y - 2,
                center_x,
                center_y + 1
            )

            painter.drawPoint(
                center_x,
                center_y + 3
            )

        painter.restore()

    @staticmethod
    def format_time(
        seconds
    ):

        minutes = seconds // 60

        secs = seconds % 60

        return (
            f"{minutes:02d}:"
            f"{secs:02d}"
        )
