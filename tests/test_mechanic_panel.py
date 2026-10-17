import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QColor, QImage, QPixmap
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

    def test_background_opacity_applies_to_images(self):
        pixmap = QPixmap(20, 20)
        pixmap.fill(QColor("#ffffff"))
        self.panel.pixmap = pixmap

        self.panel.set_background_opacity(0)
        transparent_image = QImage(
            self.panel.size(),
            QImage.Format.Format_ARGB32
        )
        transparent_image.fill(0)
        self.panel.render(transparent_image)
        self.assertEqual(
            transparent_image.pixelColor(160, 100).alpha(),
            0
        )

        self.panel.set_background_opacity(1)
        opaque_image = QImage(
            self.panel.size(),
            QImage.Format.Format_ARGB32
        )
        opaque_image.fill(0)
        self.panel.render(opaque_image)

        self.assertGreater(
            opaque_image.pixelColor(160, 100).alpha(),
            0
        )
        self.assertGreater(
            opaque_image.pixelColor(160, 100).red(),
            transparent_image.pixelColor(160, 100).red()
        )


if __name__ == "__main__":
    unittest.main()
