import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon 
from src.gui.login_ventana import LoginWindow
from src.gui.register_ventana import RegisterWindow

class WindowManager:
    def __init__(self):
        self.login_win = LoginWindow()
        self.register_win = RegisterWindow()

        self.login_win.show_register_requested.connect(self.show_register)
        self.register_win.show_login_requested.connect(self.show_login)

    def show_login(self):
        self.register_win.hide()
        self.login_win.show()

    def show_register(self):
        self.login_win.hide()
        self.register_win.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_path, "assets/icons/app_icon.svg")
    app.setWindowIcon(QIcon(icon_path))

    manager = WindowManager()
    manager.show_login()
    sys.exit(app.exec())