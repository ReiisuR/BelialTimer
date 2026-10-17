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
        self.assertNotIn("skills", config["custom_profile"])

    def test_legacy_profile_removes_duration_and_restores_buff_start(self):
        profile = deepcopy(DEFAULT_PROFILE)
        profile["mechanics"][0]["start_time"] = 0
        profile["mechanics"][0]["duration_seconds"] = 5
        save_config({
            "custom_profile": profile
        }, self.config_path)

        config, warning = load_config(self.config_path)

        self.assertIsNone(warning)
        self.assertEqual(
            config["custom_profile"]["mechanics"][0]["start_time"],
            5
        )
        self.assertNotIn(
            "duration_seconds",
            config["custom_profile"]["mechanics"][0]
        )

    def test_legacy_skill_settings_are_discarded_without_warning(self):
        profile = deepcopy(DEFAULT_PROFILE)
        profile["skills"] = [{
            "id": "impenetrability",
            "name": "IMPENETRABILIDADE",
            "associations": {"real-laser-020": 3}
        }]
        save_config({
            "custom_profile": profile
        }, self.config_path)

        config, warning = load_config(self.config_path)

        self.assertIsNone(warning)
        self.assertNotIn("skills", config["custom_profile"])

    def test_background_and_text_opacity_accept_full_range(self):
        for key in ("background_opacity", "text_opacity"):
            for opacity in (0, 100):
                save_config({
                    key: opacity,
                    "opacities_linked": False
                }, self.config_path)
                config, warning = load_config(self.config_path)

                self.assertIsNone(warning)
                self.assertEqual(config[key], opacity)

    def test_linked_opacities_are_persisted(self):
        save_config({
            "background_opacity": 43,
            "text_opacity": 76,
            "opacities_linked": False
        }, self.config_path)
        config, warning = load_config(self.config_path)

        self.assertIsNone(warning)
        self.assertEqual(config["background_opacity"], 43)
        self.assertEqual(config["text_opacity"], 76)
        self.assertFalse(config["opacities_linked"])

    def test_legacy_window_opacity_migrates_to_background_only(self):
        save_config({"window_opacity": 35}, self.config_path)
        config, warning = load_config(self.config_path)

        self.assertIsNone(warning)
        self.assertEqual(config["background_opacity"], 35)
        self.assertEqual(config["text_opacity"], 100)
        self.assertFalse(config["opacities_linked"])

    def test_invalid_background_opacity_uses_default_and_reports_warning(self):
        save_config({"background_opacity": 101}, self.config_path)

        config, warning = load_config(self.config_path)

        self.assertEqual(config["background_opacity"], 85)
        self.assertIn("background_opacity", warning)

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

    def test_header_art_selection_is_persisted_and_validated(self):
        save_config({"header_art": "deitada"}, self.config_path)
        config, warning = load_config(self.config_path)

        self.assertIsNone(warning)
        self.assertEqual(config["header_art"], "deitada")

        save_config({"header_art": "unknown"}, self.config_path)
        config, warning = load_config(self.config_path)

        self.assertEqual(config["header_art"], "sentada")
        self.assertIn("header_art", warning)

    def test_window_positions_are_persisted_and_validated(self):
        positions = {
            "normal": [240, 180],
            "compact": [-120, 75]
        }
        save_config({"window_positions": positions}, self.config_path)
        config, warning = load_config(self.config_path)

        self.assertIsNone(warning)
        self.assertEqual(config["window_positions"], positions)

        save_config({
            "window_positions": {
                "normal": [True, 10],
                "compact": [100001, 0]
            }
        }, self.config_path)
        config, warning = load_config(self.config_path)

        self.assertEqual(
            config["window_positions"],
            DEFAULT_CONFIG["window_positions"]
        )
        self.assertIn("window_positions.normal", warning)
        self.assertIn("window_positions.compact", warning)


if __name__ == "__main__":
    unittest.main()
