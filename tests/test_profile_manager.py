import copy
import unittest

from app.profile_manager import (
    DEFAULT_PROFILE,
    build_mechanics,
    format_mmss,
    parse_mmss,
    validate_profile
)
from app.timer_engine import get_event_state


class ProfileManagerTests(unittest.TestCase):

    def test_default_profile_preserves_sequence_and_exact_start_times(self):
        events = build_mechanics(DEFAULT_PROFILE)

        self.assertEqual(len(events), 20)
        self.assertEqual(events[0]["time"], 5)
        self.assertEqual(events[1]["time"], 20)
        self.assertEqual(events[1]["name"], "LASER")
        self.assertTrue(all(
            "duration_seconds" not in event
            for event in events
        ))
        self.assertNotIn("skills", DEFAULT_PROFILE)

    def test_custom_mechanic_name_is_used_in_both_display_labels(self):
        profile = copy.deepcopy(DEFAULT_PROFILE)
        profile["mechanics"][1]["name"] = "LASER AJUSTADO"
        event = build_mechanics(profile)[1]

        self.assertEqual(event["name"], "LASER AJUSTADO")
        self.assertEqual(event["short"], "LASER AJUSTADO")

    def test_mmss_parser(self):
        self.assertEqual(parse_mmss("02:18"), 138)
        self.assertEqual(format_mmss(138), "02:18")

        with self.assertRaises(ValueError):
            parse_mmss("02:60")

    def test_profile_rejects_invalid_or_unknown_mechanics(self):
        profile = copy.deepcopy(DEFAULT_PROFILE)
        profile["mechanics"][1]["start_time"] = -1
        normalized, error = validate_profile(profile)
        self.assertIsNone(normalized)
        self.assertIsNotNone(error)

        profile = copy.deepcopy(DEFAULT_PROFILE)
        profile["mechanics"][0]["id"] = "unknown"
        normalized, error = validate_profile(profile)
        self.assertIsNone(normalized)
        self.assertIsNotNone(error)

    def test_first_mechanic_uses_its_exact_start_time(self):
        profile = copy.deepcopy(DEFAULT_PROFILE)
        events = build_mechanics(profile)
        state = get_event_state(
            events,
            0,
            show_first_during_countdown=True
        )

        self.assertEqual(events[0]["time"], 5)
        self.assertEqual(state.current_index, 0)
        self.assertEqual(state.current_event["id"], "real-buffs-005")
        self.assertEqual(state.next_index, 1)
        self.assertEqual(
            state.next_event["id"],
            "real-laser-020"
        )
        self.assertEqual(state.remaining, 5)

        at_buffs = get_event_state(events, 5)
        self.assertEqual(at_buffs.current_index, 0)
        self.assertEqual(
            at_buffs.current_event["id"],
            "real-buffs-005"
        )
        self.assertEqual(at_buffs.next_index, 1)
        self.assertEqual(at_buffs.next_event["id"], "real-laser-020")
        self.assertEqual(at_buffs.remaining, 15)

        self.assertTrue(all(
            set(mechanic) == {"id", "name", "start_time"}
            for mechanic in DEFAULT_PROFILE["mechanics"]
        ))


if __name__ == "__main__":
    unittest.main()
