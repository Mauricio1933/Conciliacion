import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from src.gui.login import LoginWindow
from src.gui.main_ventana import MainWindow

def main():
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
    app = QApplication(sys.argv)
    font = QFont("Inter")
    app.setFont(font)

    main_window = None
    login_window = None

    def show_login_window():
        nonlocal login_window, main_window
        if main_window:
            main_window.close()
            
        login_window = LoginWindow()
        login_window.login_success.connect(show_main_window)
        login_window.show()

    def show_main_window(username: str):
        nonlocal main_window, login_window
        if login_window:
            login_window.close()
            
        main_window = MainWindow(logged_username=username)
        main_window.logout_triggered.connect(show_login_window)
        main_window.show()
        
        screen = app.primaryScreen()
        if screen:
            center_point = screen.availableGeometry().center()
            frame_geometry = main_window.frameGeometry()
            frame_geometry.moveCenter(center_point)
            main_window.move(frame_geometry.topLeft())

    show_login_window()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()