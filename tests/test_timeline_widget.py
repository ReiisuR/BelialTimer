import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.events import TEST_EVENTS
from app.widgets.timeline_widget import TimelineWidget


class TimelineWidgetTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widget = TimelineWidget()

    def tearDown(self):
        self.widget.entry_animation_timer.stop()
        self.widget.close()

    def test_event_states_use_event_indices_not_names(self):
        self.widget.set_events(
            TEST_EVENTS[10:13],
            current_index=11,
            next_index=12,
            start_index=10
        )

        self.assertEqual(self.widget.event_state(10), "past")
        self.assertEqual(self.widget.event_state(11), "current")
        self.assertEqual(self.widget.event_state(12), "next")

    def test_visual_alert_toggle_stops_entry_animation(self):
        self.widget.set_events(
            TEST_EVENTS,
            current_index=0,
            next_index=1
        )

        self.assertTrue(self.widget.entry_animation_timer.isActive())

        self.widget.set_visual_alerts_enabled(False)

        self.assertFalse(self.widget.entry_animation_timer.isActive())
        self.assertEqual(self.widget.entry_animation_ticks, 0)

    def test_timeline_does_not_track_active_skill_state(self):
        self.assertEqual(self.widget.height(), 58)
        self.assertFalse(hasattr(self.widget, "active_buffs"))


if __name__ == "__main__":
    unittest.main()
