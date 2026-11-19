import sys

from PySide6.QtWidgets import QApplication

from app.dungeon_dashboard import DungeonDashboard
from app.main_window import MainWindow


def main():
    application = QApplication(sys.argv)
    application.setApplicationName("Belial Timer")

    dashboard = DungeonDashboard()
    active_timer = None

    def open_belial():
        nonlocal active_timer
        if active_timer is None:
            active_timer = MainWindow()
        # O painel é o ponto de entrada; o timer abre na interface compacta.
        if not active_timer.compact:
            active_timer.compact = True
        active_timer.show_startup_mode()
        dashboard.hide()

    dashboard.belial_requested.connect(open_belial)
    dashboard.show()

    return application.exec()


if __name__ == "__main__":
    sys.exit(main())
