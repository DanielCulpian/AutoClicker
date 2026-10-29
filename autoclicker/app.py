"""Punto de entrada de la aplicacion Qt y configuracion de identidad."""
import sys
from PySide6.QtWidgets import QApplication
from .main_window import MainWindow

def main() -> int:
    """Inicializa Qt, crea la ventana principal y arranca el event loop."""
    app = QApplication(sys.argv)
    app.setApplicationName("AutoclickerModerno")
    app.setOrganizationName("DanielCulpian")
    window = MainWindow()
    window.show()
    return app.exec()
