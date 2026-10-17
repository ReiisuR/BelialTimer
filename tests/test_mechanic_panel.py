import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from app.widgets.mechanic_panel import MainPanelBackground


class MainPanelBackgroundTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = MainPanelBackground()
        self.panel.resize(320, 200)

    def tearDown(self):
        self.panel.transition_timer.stop()
        self.panel.close()

    def finish_transition(self):
        for _ in range(13):
            self.panel._update_transition()

    def test_background_asset_transitions_and_renders(self):
        self.panel.set_background("laser.jpg")

        self.assertFalse(self.panel.new_pixmap.isNull())
        self.finish_transition()

        self.assertEqual(self.panel.image_path, "laser.jpg")
        self.assertFalse(self.panel.pixmap.isNull())
        self.assertFalse(self.panel.transition_timer.isActive())

        image = QImage(
            self.panel.size(),
            QImage.Format.Format_ARGB32
        )
        image.fill(0)
        self.panel.render(image)
        self.assertFalse(image.isNull())

    def test_missing_or_empty_background_returns_to_base(self):
        self.panel.set_background("missing-background.png")
        self.finish_transition()
        self.assertTrue(self.panel.pixmap.isNull())

        self.panel.set_background(None)
        self.finish_transition()

        self.assertIsNone(self.panel.image_path)
        self.assertTrue(self.panel.pixmap.isNull())


if __name__ == "__main__":
    unittest.main()
