import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication

from app.widgets.compact_window import CompactWindow


class CompactWindowTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.calls = []
        self.window = CompactWindow(
            start_callback=lambda: self.calls.append("start"),
            restore_callback=lambda: self.calls.append("restore"),
            close_callback=lambda: self.calls.append("close")
        )

    def tearDown(self):
        self.window.close()

    def test_compact_window_keeps_size_and_controls(self):
        self.window.show()
        self.application.processEvents()

        self.assertEqual(self.window.size().width(), 380)
        self.assertEqual(self.window.size().height(), 330)
        self.assertEqual(self.window.start_button.text(), "INICIAR TIMER")
        self.assertEqual(self.window.restore_button.text(), "NORMAL")
        self.assertGreaterEqual(self.window.restore_button.width(), 64)
        self.assertGreater(
            self.window.mechanic_label.font().pointSize(),
            9
        )
        self.assertGreater(
            self.window.next_label.font().pointSize(),
            7
        )
        self.assertEqual(self.window.close_button.text(), "X")
        self.assertFalse(self.window.character_art.pixmap.isNull())
        self.assertTrue(self.window.character_art.pixmap.hasAlphaChannel())
        self.assertTrue(self.window.character_art.fit_to_height)
        self.assertEqual(
            os.path.basename(self.window.character_art.image_path),
            "belial_cotovelo.png"
        )
        self.assertEqual(self.window.character_art.geometry(), QRect(35, -18, 310, 225))
        self.assertEqual(
            self.window.content_panel.geometry(),
            QRect(8, 148, 364, 174)
        )
        self.assertIs(self.window.start_button.parentWidget(), self.window.content_panel)
        self.assertEqual(
            self.window.restore_button.geometry().center().y(),
            self.window.close_button.geometry().center().y()
        )
        self.assertEqual(
            self.window.start_button.geometry().center().x(),
            self.window.content_panel.rect().center().x()
        )

    def test_controls_call_their_callbacks(self):
        self.window.start_button.click()
        self.window.restore_button.click()
        self.window.close_button.click()

        self.assertEqual(self.calls, ["start", "restore", "close"])


if __name__ == "__main__":
    unittest.main()
