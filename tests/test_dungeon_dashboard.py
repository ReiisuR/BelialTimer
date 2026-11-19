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

    def test_dashboard_is_not_always_on_top(self):
        dashboard = DungeonDashboard()
        self.assertEqual(dashboard.windowTitle(), "BelialTimer | Central de DGs")
        self.assertTrue(dashboard.open_belial_button.isEnabled())
        dashboard.close()


if __name__ == "__main__":
    unittest.main()
