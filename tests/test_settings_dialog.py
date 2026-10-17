import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel

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
        self.assertEqual(dialog.header_art_combo.currentData(), "sentada")
        self.assertFalse(dialog.header_art_preview.pixmap().isNull())
        notes = [
            label.text()
            for label in dialog.findChildren(QLabel)
        ]
        self.assertTrue(
            any("salvos localmente" in note for note in notes)
        )
        self.assertEqual(dialog.tabs.count(), 2)
        self.assertEqual(
            [dialog.tabs.tabText(index) for index in range(dialog.tabs.count())],
            ["Geral", "Mecânicas"]
        )
        self.assertEqual(dialog.mechanics_table.rowCount(), 20)
        self.assertEqual(dialog.background_opacity_slider.minimum(), 0)
        self.assertEqual(dialog.background_opacity_slider.maximum(), 100)
        self.assertEqual(dialog.background_opacity_slider.value(), 85)
        self.assertEqual(dialog.text_opacity_slider.value(), 85)
        self.assertTrue(dialog.link_opacities_button.isChecked())
        self.assertEqual(dialog.mechanics_table.columnCount(), 3)
        self.assertEqual(
            dialog.mechanics_table.horizontalHeaderItem(2).text(),
            "Início (MM:SS)"
        )
        self.assertFalse(
            dialog.mechanics_table.cellWidget(0, 2).isReadOnly()
        )

        dialog.close()

    def test_linked_sliders_update_together(self):
        dialog = SettingsDialog(
            True,
            True,
            False,
            background_opacity=65,
            text_opacity=65,
            opacities_linked=True
        )

        dialog.background_opacity_slider.setValue(38)
        self.assertEqual(dialog.text_opacity_slider.value(), 38)
        dialog.text_opacity_slider.setValue(71)
        self.assertEqual(dialog.background_opacity_slider.value(), 71)
        self.assertEqual(dialog.background_opacity_value_label.text(), "71%")
        self.assertEqual(dialog.text_opacity_value_label.text(), "71%")

        dialog.close()

    def test_unlinked_sliders_are_independent_and_can_be_relinked(self):
        dialog = SettingsDialog(
            True,
            True,
            False,
            background_opacity=30,
            text_opacity=90,
            opacities_linked=False
        )

        dialog.background_opacity_slider.setValue(20)
        self.assertEqual(dialog.text_opacity_slider.value(), 90)

        dialog.link_opacities_button.setChecked(True)
        self.assertEqual(dialog.text_opacity_slider.value(), 20)
        dialog.text_opacity_slider.setValue(0)
        self.assertEqual(dialog.background_opacity_slider.value(), 0)
        self.assertEqual(dialog.background_opacity_value_label.text(), "0%")

        dialog.close()

    def test_dialog_contains_test_and_real_modes(self):
        dialog = SettingsDialog(True, True, True)

        self.assertEqual(dialog.event_mode_combo.count(), 2)
        self.assertTrue(dialog.event_mode_combo.itemData(0))
        self.assertFalse(dialog.event_mode_combo.itemData(1))

        dialog.close()

    def test_header_art_selection_is_stored_as_option_data(self):
        dialog = SettingsDialog(True, True, False, header_art="deitada")

        self.assertEqual(dialog.header_art_combo.currentData(), "deitada")
        dialog.header_art_combo.setCurrentIndex(0)
        self.assertEqual(dialog.header_art_combo.currentData(), "sentada")
        self.assertFalse(dialog.header_art_preview.pixmap().isNull())

        dialog.close()

    def test_editor_reads_mechanic_profile_changes(self):
        dialog = SettingsDialog(True, True, False)
        dialog.mechanics_table.cellWidget(1, 2).setText("00:21")

        profile = dialog._read_profile()

        self.assertEqual(profile["mechanics"][1]["start_time"], 21)
        self.assertNotIn("skills", profile)

        dialog.close()

    def test_restore_button_returns_editor_to_default_profile(self):
        dialog = SettingsDialog(True, True, False)
        dialog.mechanics_table.cellWidget(0, 2).setText("00:07")

        dialog.restore_profile_defaults()
        profile = dialog._read_profile()

        self.assertEqual(profile["mechanics"][0]["start_time"], 5)
        self.assertEqual(profile["mechanics"][1]["start_time"], 20)
        self.assertNotIn("skills", profile)
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
