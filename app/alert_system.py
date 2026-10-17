import threading
import winsound


class AlertSystem:

    def __init__(self):

        self.enabled = True

    def _beep(
        self,
        frequency,
        duration
    ):

        if not self.enabled:
            return

        def play():

            try:

                winsound.Beep(
                    frequency,
                    duration
                )

            except Exception:

                try:

                    winsound.MessageBeep(
                        winsound.MB_OK
                    )

                except Exception:
                    pass

        threading.Thread(
            target=play,
            daemon=True
        ).start()

    def warning(self):

        self._beep(
            650,
            100
        )

    def mechanic(self):

        self._beep(
            900,
            140
        )

    def countdown(self):

        self._beep(
            1100,
            80
        )

    def critical(self):

        self._beep(
            1400,
            180
        )
