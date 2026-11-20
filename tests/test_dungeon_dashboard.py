import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from app.dungeon_dashboard import DungeonDashboard


class DungeonDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def test_belial_card_emits_open_signal(self):
        dashboard = DungeonDashboard()
        calls = []
        dashboard.belial_requested.connect(lambda: calls.append(True))
        dashboard.open_belial_button.click()
        self.assertEqual(calls, [True])
        dashboard.close()

    def test_settings_navigation_emits_signal(self):
        dashboard = DungeonDashboard()
        calls = []
        dashboard.settings_requested.connect(lambda: calls.append(True))
        dashboard.settings_button.click()
        self.assertEqual(calls, [True])
        dashboard.close()

    def test_search_filters_cards_by_npc(self):
        dashboard = DungeonDashboard()
        dashboard.search_input.setText("Izzy")
        self.assertEqual(len(dashboard.cards), 2)
        self.assertEqual({card.dungeon["id"] for card in dashboard.cards}, {"darkweb", "never"})
        dashboard.close()

    def test_difficulty_filter_shows_only_matching_dungeons(self):
        dashboard = DungeonDashboard()
        dashboard.set_difficulty("Difícil")
        self.assertEqual([card.dungeon["id"] for card in dashboard.cards], ["pesadelo"])
        dashboard.close()

    def test_dashboard_is_not_always_on_top(self):
        dashboard = DungeonDashboard()
        self.assertEqual(dashboard.windowTitle(), "BelialTimer | Central de DGs")
        self.assertTrue(dashboard.open_belial_button.isEnabled())
        dashboard.close()


if __name__ == "__main__":
    unittest.main()
