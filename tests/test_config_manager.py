import json
import os
import tempfile
import unittest
from copy import deepcopy

from app.config_manager import (
    DEFAULT_CONFIG,
    load_config,
    save_config
)
from app.profile_manager import DEFAULT_PROFILE


class ConfigManagerTests(unittest.TestCase):

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(
            self.temporary_directory.name,
            "config.json"
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_missing_file_uses_defaults_without_warning(self):
        config, warning = load_config(self.config_path)

        self.assertEqual(config, DEFAULT_CONFIG)
        self.assertFalse(config["test_mode"])
        self.assertIsNone(warning)

    def test_saved_preferences_are_loaded(self):
        preferences = {
            "sound_enabled": False,
            "visual_alerts_enabled": False,
            "compact_mode": True,
            "test_mode": False
        }

        save_config(preferences, self.config_path)
        config, warning = load_config(self.config_path)

        expected = deepcopy(DEFAULT_CONFIG)
        expected.update(preferences)
        self.assertEqual(config, expected)
        self.assertIsNone(warning)

    def test_custom_profile_is_persisted_and_validated(self):
        profile = deepcopy(DEFAULT_PROFILE)
        profile["mechanics"][1]["start_time"] = 21
        profile["skills"][0]["associations"] = {
            "real-laser-020": 8
        }
        save_config({
            "sound_enabled": True,
            "visual_alerts_enabled": True,
            "compact_mode": False,
            "test_mode": False,
            "custom_profile": profile
        }, self.config_path)

        config, warning = load_config(self.config_path)

        self.assertIsNone(warning)
        self.assertEqual(
            config["custom_profile"]["mechanics"][1]["start_time"],
            21
        )
        self.assertEqual(
            config["custom_profile"]["skills"][0]["associations"],
            {"real-laser-020": 8}
        )

    def test_legacy_skill_durations_are_ignored(self):
        profile = deepcopy(DEFAULT_PROFILE)
        profile["skills"][0]["duration_seconds"] = 8
        profile["skills"][0]["associations"] = {
            "real-laser-020": 3
        }
        save_config({
            "custom_profile": profile
        }, self.config_path)

        config, warning = load_config(self.config_path)
        skill = config["custom_profile"]["skills"][0]

        self.assertIsNone(warning)
        self.assertNotIn("duration_seconds", skill)
        self.assertEqual(
            skill["associations"],
            {"real-laser-020": 3}
        )

    def test_corrupt_json_uses_defaults_and_reports_warning(self):
        with open(self.config_path, "w", encoding="utf-8") as config_file:
            config_file.write("{invalid")

        config, warning = load_config(self.config_path)

        self.assertEqual(config, DEFAULT_CONFIG)
        self.assertIsNotNone(warning)

    def test_invalid_value_only_resets_that_preference(self):
        with open(self.config_path, "w", encoding="utf-8") as config_file:
            json.dump({
                "sound_enabled": "off",
                "test_mode": False
            }, config_file)

        config, warning = load_config(self.config_path)

        expected = deepcopy(DEFAULT_CONFIG)
        expected["test_mode"] = False
        self.assertEqual(config, expected)
        self.assertIn("sound_enabled", warning)


if __name__ == "__main__":
    unittest.main()
