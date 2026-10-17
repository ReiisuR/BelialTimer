class AlertScheduler:

    def __init__(self):

        self.reset()

    def reset(self):

        self.last_warning_event = -1
        self.last_mechanic_event = -1
        self.last_countdown_second = -1
        self.last_critical_event = -1

    def alerts_for_state(
        self,
        current_index,
        next_index,
        has_next_event,
        remaining
    ):

        alerts = []

        if (
            current_index >= 0
            and current_index != self.last_mechanic_event
        ):
            self.last_mechanic_event = current_index
            alerts.append("mechanic")

        if (
            has_next_event
            and 0 < remaining <= 3
            and next_index != self.last_warning_event
        ):
            self.last_warning_event = next_index
            alerts.append("warning")

        if (
            has_next_event
            and 0 < remaining <= 2
            and remaining != self.last_countdown_second
        ):
            self.last_countdown_second = remaining
            alerts.append("countdown")

        if (
            has_next_event
            and 0 < remaining <= 1
            and next_index != self.last_critical_event
        ):
            self.last_critical_event = next_index
            alerts.append("critical")

        if not has_next_event or remaining > 3:
            self.last_countdown_second = -1

        return alerts
