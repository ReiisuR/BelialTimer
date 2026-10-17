import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

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
        self.assertEqual(self.window.size().width(), 220)
        self.assertEqual(self.window.size().height(), 190)
        self.assertEqual(self.window.start_button.text(), "INICIAR TIMER")
        self.assertEqual(self.window.restore_button.text(), "NORMAL")
        self.assertEqual(self.window.close_button.text(), "X")

    def test_controls_call_their_callbacks(self):
        self.window.start_button.click()
        self.window.restore_button.click()
        self.window.close_button.click()

        self.assertEqual(self.calls, ["start", "restore", "close"])


if __name__ == "__main__":
    unittest.main()
