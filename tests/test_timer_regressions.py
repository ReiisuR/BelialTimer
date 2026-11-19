"""Regression tests for timer boundaries, skipped ticks and restart behavior."""

import unittest

from app.events import REAL_EVENTS
from app.profile_manager import DEFAULT_PROFILE, build_mechanics
from app.timer_engine import TimerEngine, get_event_state
from app.alert_scheduler import AlertScheduler


class TimerBoundaryRegressionTests(unittest.TestCase):

    def setUp(self):
        self.events = build_mechanics(DEFAULT_PROFILE)

    def test_countdown_switches_at_exact_event_boundary(self):
        before = get_event_state(self.events, 19)
        at_event = get_event_state(self.events, 20)
        self.assertEqual(before.current_event["id"], "real-buffs-005")
        self.assertEqual(before.next_event["id"], "real-laser-020")
        self.assertEqual(before.remaining, 1)
        self.assertEqual(at_event.current_event["id"], "real-laser-020")
        self.assertEqual(at_event.next_event["id"], "real-crest-040")
        self.assertEqual(at_event.remaining, 20)

    def test_large_elapsed_jump_skips_to_correct_event(self):
        state = get_event_state(self.events, 321)
        self.assertEqual(state.current_event["id"], "real-spider-320")
        self.assertEqual(state.next_event["id"], "real-crest-380")
        self.assertEqual(state.remaining, 59)

    def test_after_last_event_remains_at_last_mechanic(self):
        state = get_event_state(self.events, 9999)
        self.assertEqual(state.current_event["id"], REAL_EVENTS[-1]["id"])
        self.assertIsNone(state.next_event)
        self.assertEqual(state.remaining, 0)

    def test_initial_real_countdown_does_not_mark_first_as_started(self):
        state = get_event_state(
            self.events, 0, show_first_during_countdown=True
        )
        self.assertEqual(state.current_event["id"], "real-buffs-005")
        self.assertEqual(state.last_started_index, -1)
        self.assertEqual(state.remaining, 5)


class AlertRegressionTests(unittest.TestCase):

    def test_skipped_seconds_trigger_available_warning_once(self):
        scheduler = AlertScheduler()
        self.assertEqual(
            scheduler.alerts_for_state(-1, 0, True, 1),
            ["warning", "countdown", "critical"]
        )
        self.assertEqual(
            scheduler.alerts_for_state(-1, 0, True, 1), []
        )

    def test_reset_rearms_all_alerts(self):
        scheduler = AlertScheduler()
        first = scheduler.alerts_for_state(0, 1, True, 1)
        scheduler.reset()
        self.assertEqual(scheduler.alerts_for_state(0, 1, True, 1), first)

    def test_no_countdown_alert_after_last_event(self):
        scheduler = AlertScheduler()
        self.assertEqual(
            scheduler.alerts_for_state(19, 20, False, 0),
            ["mechanic"]
        )


class TimerRestartRegressionTests(unittest.TestCase):

    def test_stop_then_start_emits_zero_again(self):
        engine = TimerEngine(interval=10_000)
        emitted = []
        engine.tick.connect(emitted.append)
        try:
            engine.start()
            engine.stop()
            engine.start()
            self.assertEqual(emitted, [0, 0])
            self.assertTrue(engine.is_running)
        finally:
            engine.stop()


if __name__ == "__main__":
    unittest.main()
