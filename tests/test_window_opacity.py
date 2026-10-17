import copy
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QDialog

import app.main_window as main_window_module
from app.config_manager import DEFAULT_CONFIG
from app.widgets.settings_dialog import SettingsDialog


class WindowOpacityTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        config = copy.deepcopy(DEFAULT_CONFIG)
        config["background_opacity"] = 65
        config["text_opacity"] = 92
        config["opacities_linked"] = False
        self.config_patch = patch.object(
            main_window_module,
            "load_config",
            return_value=(config, None)
        )
        self.path_patch = patch.object(
            main_window_module,
            "get_config_path",
            return_value="C:/temporary-belial-config.json"
        )
        self.save_patch = patch.object(
            main_window_module,
            "save_config"
        )
        self.config_patch.start()
        self.path_patch.start()
        self.save_patch.start()
        self.window = main_window_module.MainWindow()

    def tearDown(self):
        self.window.close()
        self.config_patch.stop()
        self.path_patch.stop()
        self.save_patch.stop()

    def test_background_and_text_opacity_are_independent(self):
        self.assertEqual(
            self.window.background.background_opacity,
            0.65
        )
        self.assertEqual(
            self.window.main_panel.background_opacity,
            0.65
        )
        self.assertEqual(
            self.window.header_widget.background_opacity,
            0.65
        )
        self.assertEqual(
            self.window._text_opacity_effects[0].opacity(),
            0.92
        )
        self.assertIn(
            "rgba(16, 16, 16, 0.65)",
            self.window.compact_widget.content_panel.styleSheet()
        )

    def test_character_art_overlaps_header_and_mechanic_panel(self):
        self.window.show()
        self.application.processEvents()

        art = self.window.header_widget.header_art
        panel = self.window.main_panel
        panel_origin = panel.mapTo(self.window, QPoint(0, 0))
        panel_geometry = QRect(panel_origin, panel.size())

        self.assertIs(art.parentWidget(), self.window)
        self.assertTrue(
            art.geometry().intersects(
                panel_geometry
            )
        )
        self.assertTrue(
            art.testAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents
            )
        )

    def test_lying_art_is_mirrored_and_enters_from_above_window(self):
        self.window.show()
        self.application.processEvents()
        self.window.apply_header_art("deitada")
        art = self.window.header_widget.header_art
        overlay = self.window.lying_art_overlay
        self.application.processEvents()

        self.assertTrue(art.mirror_horizontally)
        self.assertTrue(overlay.mirror_horizontally)
        self.assertEqual(overlay.size(), QSize(360, 270))
        self.assertTrue(overlay.isVisible())
        self.assertFalse(art.isVisible())
        self.assertEqual(
            overlay.mapToGlobal(QPoint(0, 0)),
            self.window.mapToGlobal(QPoint(-95, -80))
        )
        self.assertTrue(
            overlay.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
        )
        self.assertEqual(art.image_path, main_window_module.BELIAL_ART_OPTIONS["deitada"])

        self.window.apply_header_art("sentada")

        self.assertFalse(art.mirror_horizontally)
        self.assertEqual(art.geometry(), QRect(26, -4, 260, 195))
        self.assertFalse(overlay.isVisible())

    def test_saved_lying_art_appears_on_initial_window_show(self):
        self.window.config["header_art"] = "deitada"
        self.window.apply_header_art("deitada")

        self.assertFalse(self.window.lying_art_overlay.isVisible())

        self.window.show()
        self.application.processEvents()
        self.application.processEvents()

        self.assertTrue(self.window.lying_art_overlay.isVisible())
        self.assertFalse(self.window.header_widget.header_art.isVisible())
        self.assertEqual(
            self.window.lying_art_overlay.mapToGlobal(QPoint(0, 0)),
            self.window.mapToGlobal(QPoint(-95, -80))
        )

    def test_lying_art_overlay_hides_when_minimized_and_returns(self):
        self.window.config["header_art"] = "deitada"
        self.window.apply_header_art("deitada")
        self.window.show()
        self.application.processEvents()
        overlay = self.window.lying_art_overlay
        self.assertTrue(overlay.isVisible())

        self.window.showMinimized()
        self.application.processEvents()
        self.assertFalse(overlay.isVisible())

        self.window.showNormal()
        self.application.processEvents()
        self.application.processEvents()
        self.assertTrue(overlay.isVisible())

    def test_normal_and_compact_positions_are_saved_and_restored(self):
        self.window.move(240, 180)
        self.window.show()
        self.application.processEvents()

        self.window.toggle_compact_mode()
        self.application.processEvents()
        self.assertEqual(
            self.window.compact_widget.pos(),
            QPoint(240, 180)
        )
        self.assertEqual(
            self.window.config["window_positions"]["normal"],
            [240, 180]
        )

        self.window.compact_widget.move(200, 150)
        self.window._save_active_window_position()
        self.window.toggle_compact_mode()
        self.application.processEvents()
        self.assertEqual(self.window.pos(), QPoint(240, 180))
        self.assertEqual(
            self.window.config["window_positions"]["compact"],
            [200, 150]
        )

        self.window.toggle_compact_mode()
        self.application.processEvents()
        self.assertEqual(
            self.window.compact_widget.pos(),
            QPoint(200, 150)
        )

    def test_saved_window_position_is_clamped_to_available_screen(self):
        self.window.config["window_positions"]["normal"] = [100000, 100000]

        self.assertTrue(
            self.window._restore_window_position("normal", self.window)
        )
        screen = main_window_module.QGuiApplication.screenAt(self.window.pos())
        self.assertIsNotNone(screen)
        self.assertTrue(screen.availableGeometry().adjusted(
            -self.window.width() + 48,
            -self.window.height() + 48,
            0,
            0
        ).contains(self.window.pos()))

    def test_opacities_update_both_modes_independently(self):
        self.window.apply_display_opacities(0, 100, False)
        self.assertEqual(self.window.config["background_opacity"], 0)
        self.assertEqual(self.window.config["text_opacity"], 100)
        self.assertEqual(self.window.background.background_opacity, 0.0)
        self.assertEqual(self.window.main_panel.background_opacity, 0.0)
        self.assertEqual(self.window.header_widget.background_opacity, 0.0)
        self.assertEqual(self.window._text_opacity_effects[0].opacity(), 1.0)

        self.window.apply_display_opacities(100, 0, False)
        self.assertEqual(self.window.background.background_opacity, 1.0)
        self.assertEqual(self.window._text_opacity_effects[0].opacity(), 0.0)

    def test_buttons_remain_high_contrast_at_zero_opacity(self):
        self.window.apply_display_opacities(0, 0, False)

        for button in (
            self.window.start_button,
            self.window.sound_button,
            self.window.alerts_button,
            self.window.compact_start_button,
            self.window.compact_widget.restore_button,
            self.window.compact_widget.close_button
        ):
            self.assertIsNone(button.graphicsEffect())
            self.assertIn("#35171b", button.styleSheet())

    def test_compact_character_opacity_tracks_background_opacity(self):
        self.window.apply_display_opacities(42, 100, False)

        self.assertEqual(
            self.window.compact_widget.character_art.background_opacity,
            0.42
        )

    def test_compact_mode_opens_at_normal_window_position(self):
        self.window.move(240, 180)
        self.window.show()
        self.application.processEvents()

        self.window.toggle_compact_mode()
        self.application.processEvents()

        self.assertEqual(
            self.window.compact_widget.pos(),
            self.window.pos()
        )
        self.assertTrue(self.window.compact_widget.isVisible())
        self.assertFalse(self.window.isVisible())

        self.window.toggle_compact_mode()
        self.application.processEvents()
        self.assertTrue(self.window.isVisible())
        self.assertEqual(self.window.pos(), QPoint(240, 180))

    def test_compact_background_renders_transparent(self):
        self.window.compact_widget.set_background_opacity(0)
        image = QImage(
            self.window.compact_widget.size(),
            QImage.Format.Format_ARGB32
        )
        image.fill(0)
        self.window.compact_widget.render(image)

        self.assertEqual(
            image.pixelColor(5, 80).alpha(),
            0
        )

    def test_opacity_reset_shortcut_restores_both_windows(self):
        self.window.apply_display_opacities(0, 0, False)

        self.assertEqual(
            self.window.opacity_reset_shortcut.key().toString(),
            "Ctrl+Shift+O"
        )
        self.window.restore_full_opacity()

        self.assertEqual(self.window.config["background_opacity"], 100)
        self.assertEqual(self.window.config["text_opacity"], 100)
        self.assertTrue(self.window.config["opacities_linked"])
        self.assertEqual(self.window.background.background_opacity, 1.0)
        self.assertEqual(self.window._text_opacity_effects[0].opacity(), 1.0)
        main_window_module.save_config.assert_called_once()

    def test_settings_apply_and_persist_opacity_to_both_modes(self):
        dialog = SettingsDialog(
            sound_enabled=True,
            visual_alerts_enabled=True,
            test_mode=False,
            profile=self.window.custom_profile,
            background_opacity=65,
            text_opacity=65,
            opacities_linked=True
        )
        dialog.link_opacities_button.setChecked(False)
        dialog.background_opacity_slider.setValue(42)
        dialog.text_opacity_slider.setValue(87)
        dialog.custom_profile = self.window.custom_profile

        with patch.object(
            main_window_module,
            "SettingsDialog",
            return_value=dialog
        ), patch.object(
            dialog,
            "exec",
            return_value=QDialog.DialogCode.Accepted
        ):
            self.window.open_settings()

        self.assertEqual(self.window.config["background_opacity"], 42)
        self.assertEqual(self.window.config["text_opacity"], 87)
        self.assertFalse(self.window.config["opacities_linked"])
        self.assertEqual(self.window.background.background_opacity, 0.42)
        self.assertEqual(self.window._text_opacity_effects[0].opacity(), 0.87)
        main_window_module.save_config.assert_called_once()
        dialog.close()

    def test_footer_buttons_follow_requested_order(self):
        footer = self.window.start_button.parentWidget()
        footer_buttons = footer.findChildren(
            main_window_module.QPushButton
        )

        self.assertEqual(
            [button.text() for button in footer_buttons],
            [
                "INICIAR",
                "RESETAR",
                "● SOM ATIVO",
                "ALERTAS ON",
                "COMPACTO"
            ]
        )
        self.assertEqual(self.window.settings_button.text(), "⚙")
        self.assertEqual(self.window.close_button.text(), "×")

    def test_reset_stops_timer_zeros_time_and_restores_start_button(self):
        self.window.start_timer()
        self.window.game_time = 37
        self.window.update_timer_display()

        self.window.reset_button.click()

        self.assertFalse(self.window.timer_running)
        self.assertFalse(self.window.timer_engine.is_running)
        self.assertEqual(self.window.game_time, 0)
        self.assertEqual(self.window.header_timer_label.text(), "00:00")
        self.assertEqual(self.window.start_button.text(), "INICIAR")
        self.assertTrue(self.window.start_button.isEnabled())

    def test_real_buff_mechanic_is_displayed_during_initial_five_second_countdown(self):
        self.window.update_timer_display()

        self.assertEqual(self.window.game_time, 0)
        self.assertEqual(
            self.window.mechanic_label.text(),
            "REMOÇÃO DOS BUFFS"
        )
        self.assertEqual(
            self.window.compact_mechanic_label.text(),
            "BUFFS"
        )
        self.assertEqual(self.window.countdown_label.text(), "00:05")
        self.assertEqual(self.window.compact_countdown_label.text(), "00:05")
        self.assertEqual(self.window.next_label.text(), "PRÓXIMA: LASER")
        self.assertEqual(
            self.window.compact_next_label.text(),
            "PRÓXIMA: LASER"
        )
        self.assertEqual(self.window.timeline.event_state(0), "current")
        self.assertEqual(self.window.timeline.event_state(1), "next")

        self.window.start_timer()
        self.window.update_timer_display()

        self.assertEqual(
            self.window.mechanic_label.text(),
            "REMOÇÃO DOS BUFFS"
        )
        self.assertNotEqual(
            self.window.mechanic_label.text(),
            "AGUARDANDO..."
        )

        self.window.game_time = 5
        self.window.update_timer_display()

        self.assertEqual(self.window.mechanic_label.text(), "LASER")
        self.assertEqual(self.window.compact_mechanic_label.text(), "LASER")
        self.assertEqual(self.window.countdown_label.text(), "00:15")
        self.assertEqual(self.window.compact_countdown_label.text(), "00:15")
        self.assertEqual(self.window.next_label.text(), "PRÓXIMA: BRASÃO")
        self.assertEqual(
            self.window.compact_next_label.text(),
            "PRÓXIMA: BRASÃO"
        )
        self.assertEqual(self.window.timeline.event_state(0), "past")
        self.assertEqual(self.window.timeline.event_state(1), "current")
        self.assertEqual(self.window.timeline.event_state(2), "next")

        self.window.game_time = 20
        self.window.update_timer_display()
        self.assertEqual(self.window.mechanic_label.text(), "BRASÃO")
        self.assertEqual(self.window.compact_mechanic_label.text(), "BRASÃO")
        self.assertEqual(self.window.countdown_label.text(), "00:20")
        self.assertEqual(self.window.next_label.text(), "PRÓXIMA: BRASÃO")
        self.assertEqual(
            [event["id"] for event in self.window.timeline.events],
            [
                "real-laser-020",
                "real-crest-040",
                "real-crest-095"
            ]
        )
        self.assertEqual(self.window.timeline.current_index, 2)
        self.assertEqual(self.window.timeline.next_index, 3)

        self.window.game_time = 40
        self.window.update_timer_display()
        self.assertEqual(self.window.mechanic_label.text(), "BRASÃO")
        self.assertEqual(self.window.countdown_label.text(), "00:55")

        self.window.game_time = 95
        self.window.update_timer_display()
        self.assertEqual(
            self.window.mechanic_label.text(),
            "CÍRCULO PRETO"
        )
        self.assertEqual(self.window.countdown_label.text(), "00:43")
        self.assertEqual(
            self.window.next_label.text(),
            "PRÓXIMA: LASER"
        )


if __name__ == "__main__":
    unittest.main()
