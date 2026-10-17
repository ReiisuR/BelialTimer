import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.widgets.header_widget import HeaderWidget


class HeaderWidgetTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.header = HeaderWidget(lambda: None)

    def tearDown(self):
        self.header.close()

    def test_header_keeps_dimensions_and_status_labels(self):
        self.assertEqual(self.header.height(), 95)
        self.assertEqual(self.header.header_timer_label.text(), "00:00")
        self.assertEqual(
            self.header.status_label.text(),
            "○  AGUARDANDO INÍCIO"
        )

    def test_header_image_is_loaded_from_project_assets(self):
        from app.widgets.header_widget import HeaderArtWidget

        image_widget = self.header.findChild(HeaderArtWidget)
        self.assertIsNotNone(image_widget)
        self.assertFalse(image_widget.pixmap.isNull())


if __name__ == "__main__":
    unittest.main()
