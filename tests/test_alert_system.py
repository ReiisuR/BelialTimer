import unittest
from unittest.mock import patch

from app.alert_system import AlertSystem


class AlertSystemTests(unittest.TestCase):

    def test_disabled_alert_does_not_create_a_thread(self):
        alerts = AlertSystem()
        alerts.enabled = False

        with patch("app.alert_system.threading.Thread") as thread:
            alerts.warning()

        thread.assert_not_called()

    def test_alerts_keep_their_frequency_and_duration(self):
        expected_beeps = {
            "warning": (650, 100),
            "mechanic": (900, 140),
            "countdown": (1100, 80),
            "critical": (1400, 180)
        }

        alerts = AlertSystem()

        for method_name, expected in expected_beeps.items():
            with self.subTest(alert=method_name):
                with patch("app.alert_system.threading.Thread") as thread, \
                        patch("app.alert_system.winsound.Beep") as beep:
                    getattr(alerts, method_name)()
                    thread_target = thread.call_args.kwargs["target"]
                    self.assertTrue(thread.call_args.kwargs["daemon"])
                    thread_target()

                beep.assert_called_once_with(*expected)
