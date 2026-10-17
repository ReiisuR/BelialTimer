import unittest

from app.alert_scheduler import AlertScheduler


class AlertSchedulerTests(unittest.TestCase):

    def setUp(self):
        self.scheduler = AlertScheduler()

    def test_countdown_alerts_fire_once_at_each_threshold(self):
        self.assertEqual(
            self.scheduler.alerts_for_state(-1, 0, True, 3),
            ["warning"]
        )
        self.assertEqual(
            self.scheduler.alerts_for_state(-1, 0, True, 3),
            []
        )
        self.assertEqual(
            self.scheduler.alerts_for_state(-1, 0, True, 2),
            ["countdown"]
        )
        self.assertEqual(
            self.scheduler.alerts_for_state(-1, 0, True, 2),
            []
        )
        self.assertEqual(
            self.scheduler.alerts_for_state(-1, 0, True, 1),
            ["countdown", "critical"]
        )
        self.assertEqual(
            self.scheduler.alerts_for_state(-1, 0, True, 1),
            []
        )

    def test_skipped_updates_still_emit_current_thresholds_once(self):
        self.assertEqual(
            self.scheduler.alerts_for_state(-1, 0, True, 1),
            ["warning", "countdown", "critical"]
        )
        self.assertEqual(
            self.scheduler.alerts_for_state(-1, 0, True, 1),
            []
        )

    def test_repeated_event_names_use_distinct_event_indices(self):
        self.assertEqual(
            self.scheduler.alerts_for_state(11, 12, True, 1),
            ["mechanic", "warning", "countdown", "critical"]
        )
        self.assertEqual(
            self.scheduler.alerts_for_state(12, 13, False, 0),
            ["mechanic"]
        )

    def test_reset_allows_alerts_to_fire_again(self):
        self.scheduler.alerts_for_state(0, 1, True, 1)
        self.scheduler.reset()

        self.assertEqual(
            self.scheduler.alerts_for_state(0, 1, True, 1),
            ["mechanic", "warning", "countdown", "critical"]
        )

    def test_skill_reminders_fire_once_per_association(self):
        reminders = [
            {"id": "guard:laser", "reminder_time": 17},
            {"id": "protection:laser", "reminder_time": 17},
            {"id": "guard:hitkill", "reminder_time": 25}
        ]

        self.assertEqual(
            self.scheduler.new_skill_reminders(reminders, 16),
            set()
        )
        self.assertEqual(
            self.scheduler.new_skill_reminders(reminders, 17),
            {"guard:laser", "protection:laser"}
        )
        self.assertEqual(
            self.scheduler.new_skill_reminders(reminders, 17),
            set()
        )
        self.assertEqual(
            self.scheduler.new_skill_reminders(reminders, 25),
            {"guard:hitkill"}
        )

    def test_reset_allows_skill_reminders_to_fire_again(self):
        reminders = [{"id": "guard:laser", "reminder_time": 17}]
        self.scheduler.new_skill_reminders(reminders, 17)
        self.scheduler.reset()

        self.assertEqual(
            self.scheduler.new_skill_reminders(reminders, 17),
            {"guard:laser"}
        )


if __name__ == "__main__":
    unittest.main()
