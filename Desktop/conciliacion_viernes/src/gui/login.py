import sys
import os  
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QApplication,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
from src.gui.widgets.barra_custom import CustomTitleBar
from src.logic.database import verify_user, add_user

class LoginWindow(QMainWindow):
    login_success = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        qss_file_path = os.path.join(project_root, "assets", "styles", "login_estilos.qss")

        try:
            with open(qss_file_path, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"ADVERTENCIA: No se pudo encontrar el archivo de estilos en la ruta esperada: {qss_file_path}")

        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, show_maximize=False)
        main_layout.addWidget(self.title_bar)

        self.create_main_content(main_layout)

        self.resize(400, 500)
        
        self._load_saved_credentials()

    def create_main_content(self, main_layout):
        self.login_widget = self.create_login_section()
        main_layout.addWidget(self.login_widget)

    def create_login_section(self):
        login_frame = QWidget()
        login_frame.setObjectName("LoginFrame")
        layout = QVBoxLayout(login_frame)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)

        title = QLabel("Inicio de Sesión")
        title.setObjectName("SectionTitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        icons_path = os.path.join(project_root, "assets", "icons")

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")
        self.user_input.setFixedHeight(40)
        self.user_input.setObjectName("LoginUserInput")

        user_icon_path = os.path.join(icons_path, "user_light.svg")
        if os.path.exists(user_icon_path):
            self.user_input.addAction(QIcon(user_icon_path), QLineEdit.ActionPosition.LeadingPosition)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.setObjectName("LoginPasswordInput")
        self.password_input.setPlaceholderText("Contraseña")

        lock_icon_path = os.path.join(icons_path, "lock_red.svg")
        if os.path.exists(lock_icon_path):
            self.password_input.addAction(QIcon(lock_icon_path), QLineEdit.ActionPosition.LeadingPosition)

        self.remember_checkbox = QCheckBox("Recordar usuario y contraseña")
        self.remember_checkbox.setObjectName("RememberMeCheckbox")

        login_button = QPushButton("Iniciar Sesión")
        login_button.setObjectName("LoginButton")
        login_button.setFixedHeight(40)
        login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        login_button.clicked.connect(self.handle_login)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        form_layout.addWidget(self.user_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.remember_checkbox)

        layout.addWidget(title)
        layout.addStretch(1)
        layout.addLayout(form_layout)
        layout.addStretch(1)
        layout.addWidget(login_button)

        return login_frame

    def handle_login(self):
        username = self.user_input.text()
        password = self.password_input.text()

        from src.logic.settings import save_credentials, clear_credentials

        if verify_user(username, password):
            if self.remember_checkbox.isChecked():
                save_credentials(username, password)
            else:
                clear_credentials()

            self.login_success.emit() 
            self.close() 
        else:
            QMessageBox.warning(
                self, "Error de Autenticación",
                "El nombre de usuario o la contraseña son incorrectos."
            )

    def _load_saved_credentials(self):
        from src.logic.settings import load_credentials, clear_credentials
        from src.logic.database import verify_user

        username, password = load_credentials()
        if username and password:
            if verify_user(username, password):
                self.user_input.setText(username)
                self.password_input.setText(password)
                self.remember_checkbox.setChecked(True)
            else:
                clear_credentials()