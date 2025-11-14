import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from src.gui.login import LoginWindow

def main():
    app = QApplication(sys.argv)
    font = QFont("Inter")
    app.setFont(font)
    login_window = LoginWindow()
    login_window.show()
    screen = app.primaryScreen()
    if screen:
        center_point = screen.availableGeometry().center()
        frame_geometry = login_window.frameGeometry()
        frame_geometry.moveCenter(center_point)
        login_window.move(frame_geometry.topLeft())
    sys.exit(app.exec())

if __name__ == '__main__':
    main()