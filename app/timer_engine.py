from dataclasses import dataclass

from PySide6.QtCore import QObject, QElapsedTimer, QTimer, Signal


@dataclass(frozen=True)
class EventState:
    current_index: int
    next_index: int
    current_event: dict | None
    next_event: dict | None
    remaining: int
    last_started_index: int


def get_event_state(events, elapsed_time, show_first_during_countdown=False):

    if not events:
        return EventState(
            current_index=-1,
            next_index=0,
            current_event=None,
            next_event=None,
            remaining=0,
            last_started_index=-1
        )

    start_times = [
        (
            event["start_time"]
            if "start_time" in event
            else event["time"]
        )
        for event in events
    ]
    last_started_index = -1

    for index, start_time in enumerate(start_times):
        if start_time > elapsed_time:
            break
        last_started_index = index

    next_index = last_started_index + 1
    next_event = (
        events[next_index]
        if next_index < len(events)
        else None
    )
    current_index = -1
    current_event = None
    showing_first_during_countdown = (
        last_started_index < 0
        and show_first_during_countdown
        and bool(events)
    )

    if showing_first_during_countdown:
        current_index = 0
        current_event = events[0]
        next_index = 1
        next_event = events[next_index] if next_index < len(events) else None
        remaining = max(0, start_times[0] - elapsed_time)
    elif last_started_index >= 0:
        current_index = last_started_index
        current_event = events[last_started_index]

    if not showing_first_during_countdown:
        remaining = (
            max(0, start_times[next_index] - elapsed_time)
            if next_event is not None
            else 0
        )

    return EventState(
        current_index=current_index,
        next_index=next_index,
        current_event=current_event,
        next_event=next_event,
        remaining=remaining,
        last_started_index=last_started_index
    )


class TimerEngine(QObject):

    tick = Signal(int)

    def __init__(
        self,
        parent=None,
        interval=100
    ):

        super().__init__(parent)

        self._elapsed_timer = QElapsedTimer()
        self._timer = QTimer(self)
        self._timer.setInterval(interval)
        self._timer.timeout.connect(self._emit_elapsed)
        self.is_running = False

    def start(self):

        if self.is_running:
            return

        self._elapsed_timer.start()
        self.is_running = True
        self._timer.start()
        self._emit_elapsed()

    def stop(self):

        self._timer.stop()
        self.is_running = False

    def _emit_elapsed(self):

        if self.is_running:
            self.tick.emit(
                self._elapsed_timer.elapsed() // 1000
            )
