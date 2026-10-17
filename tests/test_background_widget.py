import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from app.widgets.background_widget import BackgroundWidget


class BackgroundWidgetTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def test_widget_renders_without_errors(self):
        widget = BackgroundWidget()
        widget.resize(680, 420)

        image = QImage(
            widget.size(),
            QImage.Format.Format_ARGB32
        )
        image.fill(0)

        widget.render(image)

        self.assertFalse(image.isNull())
        self.assertNotEqual(image.pixelColor(10, 10).alpha(), 0)

        widget.close()


if __name__ == "__main__":
    unittest.main()
