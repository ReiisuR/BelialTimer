import sys

from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow


def main():

    application = QApplication(sys.argv)
    application.setApplicationName("Belial Timer")

    window = MainWindow()
    window.show_startup_mode()

    return application.exec()


if __name__ == "__main__":
    sys.exit(main())
