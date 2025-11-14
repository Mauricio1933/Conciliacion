import sys
import os  
from PyQt6.QtWidgets import (
     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QSizePolicy, QCheckBox, QApplication,
    QMessageBox
)
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QIcon, QFont
from src.gui.widgets.barra_custom import CustomTitleBar
from src.logic.database import verify_user, add_user

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(400, 250)
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

        self.title_bar = CustomTitleBar(self, show_maximize=False, show_icon=False)
        main_layout.addWidget(self.title_bar)

        self.create_main_content(main_layout)

        self.overlay_on_right = True

        self.resize(800, 500)
        
        self._load_saved_credentials()

    def create_main_content(self, main_layout):
        content_frame = QFrame()
        content_frame.setObjectName("ContentFrame")
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.login_widget = self.create_login_section()
        content_layout.addWidget(self.login_widget)

        self.register_widget = self.create_register_section()
        content_layout.addWidget(self.register_widget)

        self.overlay = QWidget(self.central_widget)
        self.overlay.setObjectName("OverlayWidget")
        self.create_overlay_content()

        main_layout.addWidget(content_frame)

    def create_overlay_content(self):
        overlay_layout = QVBoxLayout(self.overlay)
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.setSpacing(0)
        self.overlay_title_bar = QWidget()
        self.overlay_title_bar.setObjectName("OverlayTitleBar")
        self.overlay_title_bar.setFixedHeight(30)
        overlay_title_layout = QHBoxLayout(self.overlay_title_bar)
        overlay_title_layout.setContentsMargins(0, 0, 0, 0)
        overlay_title_layout.setSpacing(0)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        icons_path = os.path.join(project_root, "assets", "icons")

        self.overlay_minimize_button = QPushButton()
        self.overlay_minimize_button.setObjectName("MinimizeButton")
        mini_light_path = os.path.join(icons_path, "mini_white.svg")
        if os.path.exists(mini_light_path):
            self.overlay_minimize_button.setIcon(QIcon(mini_light_path))
        self.overlay_minimize_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.overlay_minimize_button.clicked.connect(self.showMinimized)

        self.overlay_close_button = QPushButton()
        self.overlay_close_button.setObjectName("CloseButton")
        exit_light_path = os.path.join(icons_path, "exit_white.svg")
        if os.path.exists(exit_light_path):
            self.overlay_close_button.setIcon(QIcon(exit_light_path))
        self.overlay_close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.overlay_close_button.clicked.connect(QApplication.instance().quit)

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(10, 0, 10, 0)
        buttons_layout.setSpacing(10)
        buttons_layout.addWidget(self.overlay_minimize_button)
        buttons_layout.addWidget(self.overlay_close_button)

        overlay_title_layout.addStretch()
        overlay_title_layout.addLayout(buttons_layout)

        self.overlay_title_bar.setVisible(True)

        self.overlay_title = QLabel()
        self.overlay_title.setObjectName("OverlayTitleLabel")
        self.overlay_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlay_title.setWordWrap(True)

        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("ToggleButton")
        self.toggle_button.setFixedSize(150, 40)
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_button.clicked.connect(self.toggle_overlay_position)

        overlay_layout.addWidget(self.overlay_title_bar)
        overlay_layout.addStretch(1)
        overlay_layout.addWidget(self.overlay_title)
        overlay_layout.addStretch(1)
        overlay_layout.addWidget(self.toggle_button, alignment=Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addStretch(2)

    def create_login_section(self):
        login_frame = QFrame()
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

    def create_register_section(self):
        register_frame = QFrame()
        register_frame.setObjectName("RegisterFrame")
        layout = QVBoxLayout(register_frame)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)

        title = QLabel("Registrarse")
        title.setObjectName("SectionTitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        icons_path = os.path.join(project_root, "assets", "icons")

        name_layout = QHBoxLayout()
        
        self.reg_name_input = QLineEdit()
        self.reg_name_input.setPlaceholderText("Nombre")
        self.reg_name_input.setFixedHeight(40)
        self.reg_name_input.setObjectName("RegisterNameInput")
        user_icon_path = os.path.join(icons_path, "user_light.svg")
        if os.path.exists(user_icon_path):
            self.reg_name_input.addAction(QIcon(user_icon_path), QLineEdit.ActionPosition.LeadingPosition)

        self.reg_lastname_input = QLineEdit()
        self.reg_lastname_input.setPlaceholderText("Apellido")
        self.reg_lastname_input.setFixedHeight(40)
        self.reg_lastname_input.setObjectName("RegisterLastNameInput")
        if os.path.exists(user_icon_path):
            self.reg_lastname_input.addAction(QIcon(user_icon_path), QLineEdit.ActionPosition.LeadingPosition)

        name_layout.addWidget(self.reg_name_input)
        name_layout.addWidget(self.reg_lastname_input)

        self.reg_username_input = QLineEdit()
        self.reg_username_input.setPlaceholderText("Nombre de usuario")
        self.reg_username_input.setFixedHeight(40)
        self.reg_username_input.setObjectName("RegisterUsernameInput")
        if os.path.exists(user_icon_path):
            self.reg_username_input.addAction(QIcon(user_icon_path), QLineEdit.ActionPosition.LeadingPosition)

        self.reg_email_input = QLineEdit()
        self.reg_email_input.setPlaceholderText("Email")
        self.reg_email_input.setFixedHeight(40)
        self.reg_email_input.setObjectName("RegisterEmailInput")
        email_icon_path = os.path.join(icons_path, "email_icon.svg")
        if os.path.exists(email_icon_path):
            self.reg_email_input.addAction(QIcon(email_icon_path), QLineEdit.ActionPosition.LeadingPosition)

        password_layout = QHBoxLayout()

        self.reg_password_input = QLineEdit()
        self.reg_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_password_input.setFixedHeight(40)
        self.reg_password_input.setPlaceholderText("Contraseña")
        self.reg_password_input.setObjectName("RegisterPasswordInput")
        lock_icon_path = os.path.join(icons_path, "lock_red.svg")
        if os.path.exists(lock_icon_path):
            self.reg_password_input.addAction(QIcon(lock_icon_path), QLineEdit.ActionPosition.LeadingPosition)

        self.reg_confirm_password_input = QLineEdit()
        self.reg_confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_confirm_password_input.setFixedHeight(40)
        self.reg_confirm_password_input.setPlaceholderText("Confirmar contraseña")
        self.reg_confirm_password_input.setObjectName("RegisterConfirmPasswordInput")
        if os.path.exists(lock_icon_path):
            self.reg_confirm_password_input.addAction(QIcon(lock_icon_path), QLineEdit.ActionPosition.LeadingPosition)

        password_layout.addWidget(self.reg_password_input)
        password_layout.addWidget(self.reg_confirm_password_input)

        register_button = QPushButton("Registrarse")
        register_button.setObjectName("RegisterButton")
        register_button.setFixedHeight(40)
        register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        register_button.clicked.connect(self.handle_register)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        form_layout.addLayout(name_layout)
        form_layout.addWidget(self.reg_username_input)
        form_layout.addWidget(self.reg_email_input)
        form_layout.addLayout(password_layout)

        layout.addWidget(title)
        layout.addStretch(1)
        layout.addLayout(form_layout)
        layout.addStretch(1)
        layout.addWidget(register_button)

        return register_frame

    def handle_login(self):
        username = self.user_input.text()
        password = self.password_input.text()

        from src.logic.settings import save_credentials, clear_credentials

        if verify_user(username, password):
            if self.remember_checkbox.isChecked():
                save_credentials(username, password)
            else:
                clear_credentials()

            from src.gui.main_ventana import MainWindow
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(
                self, "Error de Autenticación",
                "El nombre de usuario o la contraseña son incorrectos."
            )

    def handle_register(self):
        first_name = self.reg_name_input.text()
        last_name = self.reg_lastname_input.text()
        username = self.reg_username_input.text()
        email = self.reg_email_input.text()
        password = self.reg_password_input.text()
        confirm_password = self.reg_confirm_password_input.text()

        if not all([first_name, last_name, username, email, password, confirm_password]):
            QMessageBox.warning(self, "Campos Incompletos", "Por favor, rellene todos los campos.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error de Contraseña", "Las contraseñas no coinciden.")
            return

        success, message = add_user(first_name, last_name, username, email, password)

        if success:
            QMessageBox.information(self, "Registro Exitoso", message)
            self.reg_name_input.clear()
            self.reg_lastname_input.clear()
            self.reg_username_input.clear()
            self.reg_email_input.clear()
            self.reg_password_input.clear()
            self.reg_confirm_password_input.clear()
            self.toggle_overlay_position()
        else:
            QMessageBox.critical(self, "Error de Registro", message)

    def toggle_overlay_position(self):
        overlay_width = self.width() // 2
        start_x = self.width() // 2 if self.overlay_on_right else 0
        end_x = 0 if self.overlay_on_right else self.width() // 2

        self.animation = QPropertyAnimation(self.overlay, b"geometry")
        self.animation.setDuration(500)
        self.animation.setStartValue(QRect(start_x, 0, overlay_width, self.height()))
        self.animation.setEndValue(QRect(end_x, 0, overlay_width, self.height()))
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.start()

        self.overlay_on_right = not self.overlay_on_right
        self._update_overlay_content()

    def _update_overlay_content(self):
        from src.logic.settings import load_credentials

        if self.overlay_on_right:
            self.toggle_button.setText("Registrarse")
            self.overlay_title_bar.setVisible(True)
            username, _ = load_credentials()
            if username:
                self.overlay_title.setText(f"¡Bienvenido de nuevo,\n{username}!")
            else:
                self.overlay_title.setText("¿Aún no tienes una cuenta?")
        else:
            self.toggle_button.setText("Iniciar Sesion")
            self.overlay_title_bar.setVisible(False)
            self.overlay_title.setText("¿Ya tienes una cuenta?")
            

    def resizeEvent(self, event):
        super().resizeEvent(event) 
        overlay_width = self.width() // 2
        overlay_height = self.height()
        start_x = self.width() // 2 if self.overlay_on_right else 0
        self.overlay.setGeometry(start_x, 0, overlay_width, overlay_height)
        self.overlay.raise_() 

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
        self._update_overlay_content()