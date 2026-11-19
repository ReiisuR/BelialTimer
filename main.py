import sys

from PySide6.QtWidgets import QApplication

from app.dungeon_dashboard import DungeonDashboard
from app.main_window import MainWindow


def main():
    application = QApplication(sys.argv)
    application.setApplicationName("Belial Timer")

    dashboard = DungeonDashboard()
    active_timer = None

    def return_to_dashboard():
        # Mostrar antes de esconder o timer evita encerrar a aplicacao
        # quando a ultima janela visivel desaparece.
        dashboard.show()
        dashboard.raise_()
        dashboard.activateWindow()

    def open_belial():
        nonlocal active_timer
        if active_timer is None:
            active_timer = MainWindow()
            active_timer.dashboard_return_callback = return_to_dashboard
            # NORMAL e X agora retornam para a Central de DGs.
            button = active_timer.compact_widget.restore_button
            button.clicked.disconnect()
            button.clicked.connect(active_timer.close_app)
            button.setText("CENTRAL")
            button.setToolTip("Voltar à Central de DGs.")
            active_timer.compact_widget.close_button.setToolTip(
                "Fechar o timer e voltar à Central de DGs."
            )
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
