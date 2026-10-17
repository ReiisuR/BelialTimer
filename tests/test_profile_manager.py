import copy
import unittest

from app.profile_manager import (
    DEFAULT_PROFILE,
    build_mechanics,
    build_skill_reminders,
    due_skill_reminders,
    format_mmss,
    parse_mmss,
    validate_profile
)


class ProfileManagerTests(unittest.TestCase):

    def test_default_profile_preserves_sequence_and_removal_window(self):
        events = build_mechanics(DEFAULT_PROFILE)

        self.assertEqual(len(events), 20)
        self.assertEqual(events[0]["time"], 0)
        self.assertEqual(events[0]["duration_seconds"], 5)
        self.assertEqual(events[1]["time"], 20)
        self.assertEqual(events[1]["name"], "LASER")
        self.assertIsNone(events[-1]["duration_seconds"])
        self.assertTrue(all(
            "duration_seconds" not in skill
            for skill in DEFAULT_PROFILE["skills"]
        ))

    def test_custom_mechanic_name_is_used_in_both_display_labels(self):
        profile = copy.deepcopy(DEFAULT_PROFILE)
        profile["mechanics"][1]["name"] = "LASER AJUSTADO"
        event = build_mechanics(profile)[1]

        self.assertEqual(event["name"], "LASER AJUSTADO")
        self.assertEqual(event["short"], "LASER AJUSTADO")

    def test_mmss_parser_and_optional_duration(self):
        self.assertEqual(parse_mmss("02:18"), 138)
        self.assertEqual(format_mmss(138), "02:18")
        self.assertIsNone(parse_mmss("", allow_empty=True))

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

    def test_skill_reminder_is_scheduled_before_target_without_changing_it(self):
        profile = copy.deepcopy(DEFAULT_PROFILE)
        profile["skills"][1]["associations"] = {
            "real-laser-020": 3
        }
        events = build_mechanics(profile)

        reminders = build_skill_reminders(profile, events)
        self.assertEqual(len(reminders), 1)
        self.assertEqual(reminders[0]["reminder_time"], 17)
        self.assertEqual(reminders[0]["target_time"], 20)
        self.assertEqual(events[1]["time"], 20)
        self.assertEqual(due_skill_reminders(profile, events, 16), [])
        self.assertEqual(
            [reminder["id"] for reminder in due_skill_reminders(
                profile,
                events,
                17
            )],
            ["impenetrability:real-laser-020"]
        )

    def test_simultaneous_skill_reminders_remain_distinct_associations(self):
        profile = copy.deepcopy(DEFAULT_PROFILE)
        profile["skills"][0]["associations"] = {
            "real-laser-020": 3
        }
        profile["skills"][1]["associations"] = {
            "real-laser-020": 3
        }

        reminders = build_skill_reminders(profile, build_mechanics(profile))
        self.assertEqual(
            {reminder["id"] for reminder in reminders},
            {
                "guard:real-laser-020",
                "impenetrability:real-laser-020"
            }
        )
        self.assertEqual(
            {reminder["reminder_time"] for reminder in reminders},
            {17}
        )


if __name__ == "__main__":
    unittest.main()
