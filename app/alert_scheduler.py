class AlertScheduler:

    def __init__(self):

        self.reset()

    def reset(self):

        self.last_warning_event = -1
        self.last_mechanic_event = -1
        self.last_countdown_second = -1
        self.last_critical_event = -1
        self.alerted_reminders = set()

    def new_skill_reminders(
        self,
        reminders,
        elapsed_time
    ):

        due_reminders = {
            reminder["id"]
            for reminder in reminders
            if (
                reminder["reminder_time"] <= elapsed_time
                and reminder["id"] not in self.alerted_reminders
            )
        }

        self.alerted_reminders.update(
            due_reminders
        )

        return due_reminders

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
