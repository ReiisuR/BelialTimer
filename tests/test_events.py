import unittest

from app.events import REAL_EVENTS, TEST_EVENTS
from app.profile_manager import DEFAULT_PROFILE, build_mechanics
from app.timer_engine import TimerEngine, get_event_state


class EventSequenceTests(unittest.TestCase):

    def test_real_sequence_matches_reference_times(self):
        self.assertEqual(
            [
                (event["time"], event["name"])
                for event in REAL_EVENTS
            ],
            [
                (5, "REMOÇÃO DOS BUFFS"),
                (20, "LASER"),
                (40, "BRASÃO"),
                (95, "BRASÃO"),
                (138, "CÍRCULO PRETO"),
                (157, "LASER"),
                (225, "BRASÃO"),
                (300, "CÍRCULO PRETO"),
                (315, "SILENCE"),
                (320, "ARANHA"),
                (380, "BRASÃO"),
                (445, "LASER"),
                (456, "CÍRCULO PRETO"),
                (469, "LASER"),
                (560, "BRASÃO"),
                (579, "CÍRCULO PRETO"),
                (593, "LASER"),
                (621, "BRASÃO"),
                (715, "HITKILL"),
                (728, "HITKILL")
            ]
        )
        self.assertEqual(len(REAL_EVENTS), 20)
        self.assertEqual(
            [event["id"] for event in REAL_EVENTS if event["time"] in (5, 20)],
            [
                "real-buffs-005",
                "real-laser-020"
            ]
        )
        self.assertEqual(
            [event["time"] for event in REAL_EVENTS],
            [
                5, 20, 40, 95, 138, 157, 225, 300, 315, 320,
                380, 445, 456, 469, 560, 579, 593, 621, 715, 728
            ]
        )
        self.assertEqual(
            len({event["id"] for event in REAL_EVENTS}),
            len(REAL_EVENTS)
        )

    def test_sequences_are_separate_and_chronological(self):
        self.assertIsNot(TEST_EVENTS, REAL_EVENTS)

        for sequence in (TEST_EVENTS, REAL_EVENTS):
            times = [event["time"] for event in sequence]
            self.assertEqual(times, sorted(times))
            event_ids = [event["id"] for event in sequence]

            for event in sequence:
                self.assertEqual(
                    set(event),
                    {"id", "type", "time", "name", "short", "background"}
                )
                self.assertEqual(event["type"], "mechanic")

            self.assertEqual(len(event_ids), len(set(event_ids)))

    def test_state_waits_for_first_test_event(self):
        before_first = get_event_state(TEST_EVENTS, 0)

        self.assertEqual(before_first.current_index, -1)
        self.assertIsNone(before_first.current_event)
        self.assertEqual(before_first.next_index, 0)
        self.assertIs(before_first.next_event, TEST_EVENTS[0])
        self.assertEqual(before_first.remaining, 5)

        at_first = get_event_state(TEST_EVENTS, 5)

        self.assertEqual(at_first.current_index, 0)
        self.assertIs(at_first.current_event, TEST_EVENTS[0])
        self.assertEqual(at_first.next_index, 1)
        self.assertIs(at_first.next_event, TEST_EVENTS[1])
        self.assertEqual(at_first.remaining, 5)

    def test_repeated_mechanic_names_remain_distinct_events(self):
        state = get_event_state(TEST_EVENTS, 55)

        self.assertEqual(state.current_index, 10)
        self.assertEqual(state.current_event["name"], "BRASÃO")
        self.assertEqual(state.next_index, 11)
        self.assertEqual(state.next_event["name"], "HITKILL")
        self.assertEqual(state.remaining, 5)

        at_boundary = get_event_state(TEST_EVENTS, 60)
        self.assertEqual(at_boundary.current_index, 11)
        self.assertEqual(at_boundary.current_event["id"], "test-hitkill-060")
        self.assertEqual(at_boundary.next_event["id"], "test-hitkill-065")
        self.assertEqual(at_boundary.remaining, 5)

    def test_state_after_last_event_has_no_next_event(self):
        state = get_event_state(REAL_EVENTS, 728)

        self.assertEqual(state.current_index, 19)
        self.assertIs(state.current_event, REAL_EVENTS[-1])
        self.assertEqual(state.next_index, 20)
        self.assertIsNone(state.next_event)
        self.assertEqual(state.remaining, 0)

    def test_real_profile_counts_each_exact_start_time(self):
        events = build_mechanics(DEFAULT_PROFILE)
        state = get_event_state(
            events,
            0,
            show_first_during_countdown=True
        )

        self.assertEqual(state.current_index, 0)
        self.assertEqual(state.current_event["id"], "real-buffs-005")
        self.assertEqual(state.next_index, 1)
        self.assertEqual(state.next_event["id"], "real-laser-020")
        self.assertEqual(state.remaining, 5)
        self.assertEqual(state.last_started_index, -1)

        at_five = get_event_state(
            events,
            5,
            show_first_during_countdown=True
        )
        self.assertEqual(at_five.current_index, 0)
        self.assertEqual(at_five.current_event["id"], "real-buffs-005")
        self.assertEqual(at_five.next_index, 1)
        self.assertEqual(at_five.next_event["id"], "real-laser-020")
        self.assertEqual(at_five.remaining, 15)

        at_buffs = get_event_state(events, 5)
        self.assertEqual(at_buffs.current_index, 0)
        self.assertEqual(at_buffs.current_event["id"], "real-buffs-005")
        self.assertEqual(at_buffs.current_event["name"], "REMOÇÃO DOS BUFFS")
        self.assertEqual(at_buffs.next_index, 1)
        self.assertEqual(at_buffs.next_event["id"], "real-laser-020")
        self.assertEqual(at_buffs.remaining, 15)

        during_wait = get_event_state(events, 6)
        self.assertEqual(during_wait.current_event["id"], "real-buffs-005")
        self.assertEqual(during_wait.next_event["id"], "real-laser-020")
        self.assertEqual(during_wait.remaining, 14)

        at_laser = get_event_state(events, 20)
        self.assertEqual(at_laser.current_event["id"], "real-laser-020")
        self.assertEqual(at_laser.current_event["name"], "LASER")
        self.assertEqual(at_laser.next_event["id"], "real-crest-040")
        self.assertEqual(at_laser.remaining, 20)

    def test_profile_mechanics_start_at_each_configured_time(self):
        events = build_mechanics(DEFAULT_PROFILE)
        for index, event in enumerate(events):
            at_boundary = get_event_state(
                events,
                event["time"]
            )

            self.assertEqual(at_boundary.current_index, index)
            self.assertEqual(
                at_boundary.current_event["id"],
                event["id"]
            )


class TimerEngineTests(unittest.TestCase):

    def test_start_emits_initial_elapsed_time_and_stop_is_idempotent(self):
        engine = TimerEngine(interval=10_000)
        elapsed_values = []
        engine.tick.connect(elapsed_values.append)

        engine.start()
        engine.start()

        self.assertTrue(engine.is_running)
        self.assertEqual(elapsed_values, [0])

        engine.stop()
        engine.stop()

        self.assertFalse(engine.is_running)
