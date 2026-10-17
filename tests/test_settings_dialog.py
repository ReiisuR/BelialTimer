import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QCheckBox, QLabel

from app.widgets.settings_dialog import SettingsDialog


class SettingsDialogTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def test_dialog_initializes_controls_from_current_preferences(self):
        dialog = SettingsDialog(
            sound_enabled=False,
            visual_alerts_enabled=True,
            test_mode=False
        )

        self.assertEqual(dialog.width(), 760)
        self.assertFalse(dialog.sound_checkbox.isChecked())
        self.assertTrue(dialog.visual_alerts_checkbox.isChecked())
        self.assertFalse(dialog.event_mode_combo.currentData())
        notes = [
            label.text()
            for label in dialog.findChildren(QLabel)
        ]
        self.assertTrue(
            any("salvos localmente" in note for note in notes)
        )
        self.assertEqual(dialog.tabs.count(), 3)
        self.assertEqual(dialog.mechanics_table.rowCount(), 20)

        dialog.close()

    def test_dialog_contains_test_and_real_modes(self):
        dialog = SettingsDialog(True, True, True)

        self.assertEqual(dialog.event_mode_combo.count(), 2)
        self.assertTrue(dialog.event_mode_combo.itemData(0))
        self.assertFalse(dialog.event_mode_combo.itemData(1))

        dialog.close()

    def test_editor_reads_mechanic_and_skill_profile_changes(self):
        dialog = SettingsDialog(True, True, False)
        dialog.mechanics_table.cellWidget(1, 2).setText("00:21")
        dialog.skill_target_tables["guard"].cellWidget(2, 0).findChild(
            QCheckBox
        ).setChecked(True)
        dialog.skill_target_tables["guard"].cellWidget(2, 2).setText("00:08")

        profile = dialog._read_profile()

        self.assertEqual(profile["mechanics"][1]["start_time"], 21)
        self.assertEqual(
            profile["skills"][0]["associations"]["real-crest-040"],
            8
        )

        dialog.close()

    def test_restore_button_returns_editor_to_default_profile(self):
        dialog = SettingsDialog(True, True, False)
        dialog.mechanics_table.cellWidget(1, 2).setText("00:21")

        dialog.restore_profile_defaults()
        profile = dialog._read_profile()

        self.assertEqual(profile["mechanics"][1]["start_time"], 20)
        self.assertTrue(all(
            "duration_seconds" not in skill
            for skill in profile["skills"]
        ))
        self.assertNotIn("skill_duration_inputs", dialog.__dict__)
        dialog.close()

    def test_invalid_time_shows_inline_error_without_closing_dialog(self):
        dialog = SettingsDialog(True, True, False)
        dialog.mechanics_table.cellWidget(0, 2).setText("invalid")

        dialog.accept()

        self.assertFalse(dialog.validation_label.isHidden())
        self.assertIn("MM:SS", dialog.validation_label.text())
        self.assertIsNone(dialog.custom_profile)
        dialog.close()


if __name__ == "__main__":
    unittest.main()
