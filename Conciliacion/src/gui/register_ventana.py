from PyQt6.QtWidgets import (QWidget, QLineEdit, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QAction
import os
from typing import Optional 

class CustomTitleBar(QWidget):
    def __init__(self, parent_window: QWidget):
        super().__init__(parent_window)
        
        self.parent_window = parent_window
        self.setObjectName("CustomTitleBar")
        self.start_pos: Optional[QPoint] = None
        self.setFixedHeight(30)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 0, 0)
        layout.setSpacing(5)
        layout.setObjectName("layout")
        self.setLayout(layout) 
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True) 

        icon_label = QLabel()
        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "../../assets/icons/app_icon.svg")
        pixmap = QPixmap(icon_path)
        icon_label.setPixmap(pixmap.scaled(QSize(20, 20), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(icon_label)

        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addItem(spacer) 
        
        self.btn_minimize = QPushButton("—") 
        self.btn_close = QPushButton("✕")
        
        self.btn_minimize.setObjectName("btnMinimize")
        self.btn_close.setObjectName("btnClose")
        
        self.btn_minimize.setFixedWidth(30)
        self.btn_close.setFixedWidth(30)

        self.btn_minimize.clicked.connect(self.parent_window.showMinimized)
        self.btn_close.clicked.connect(self.parent_window.close)
        
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_close)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()
            self.diff = self.start_pos - self.parent_window.pos()
            self.parent_window.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()

    def mouseMoveEvent(self, event):
        if self.start_pos is not None and not self.parent_window.isMaximized():
            self.parent_window.move(event.globalPosition().toPoint() - self.diff)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.start_pos = None
        self.parent_window.setCursor(Qt.CursorShape.ArrowCursor)
        event.accept()

class RegisterWindow(QWidget):
    show_login_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) 
        self.setObjectName("RegisterWindow") 
        self.setWindowTitle("Registro de Nuevo Usuario")
        self.setFixedSize(550, 460) 
        
        self.main_layout = QVBoxLayout(self) 
        self.main_layout.setObjectName("main_layout")
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        background_widget = QWidget()
        background_widget.setObjectName("BackgroundWidget")
        self.main_layout.addWidget(background_widget)

        background_layout = QVBoxLayout(background_widget)
        background_layout.setContentsMargins(0, 0, 0, 0)
        background_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self)
        background_layout.addWidget(self.title_bar)
        
        self._setup_styles() 
        self._init_ui()
        
        background_layout.addWidget(self.content_widget)

    def _setup_styles(self):
        self.setFont(QFont("sans serif", 10))
        archivos_qss = [
            "../../assets/styles/register_estilos.qss", 
            "../../assets/styles/estilos_generales.qss", 
        ]
        
        estilos_combinados = ""
        
        for filename in archivos_qss:
            style_path = os.path.join(os.path.dirname(__file__), filename)
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    estilos_combinados += f.read() + "\n"
            except (FileNotFoundError, Exception):
                pass
        self.setStyleSheet(estilos_combinados)
    
    def _init_ui(self):
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget) 
        content_layout.setContentsMargins(30, 20, 30, 30)
        self.content_widget.setObjectName("ContentWidget") 

        self.titulo = QLabel("Crear Cuenta")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titulo.setObjectName("titulo")
        content_layout.addWidget(self.titulo)
        content_layout.addSpacing(20)
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path_user = os.path.join(base_path, "../../assets/icons/user_light.svg")
        icon_path_mail = os.path.join(base_path, "../../assets/icons/email.svg")
        icon_path_lock = os.path.join(base_path, "../../assets/icons/lock_red.svg")
        
        nombre_apellido_layout = QHBoxLayout()
        nombre_apellido_layout.setSpacing(10)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre")
        user_action1 = QAction(QIcon(icon_path_user), "", self)
        user_action1.setObjectName("icon_action")
        self.nombre_input.addAction(user_action1, QLineEdit.ActionPosition.LeadingPosition) 
        self.nombre_input.setObjectName("input_nombre")
        self.nombre_input.setFixedHeight(45)
        nombre_apellido_layout.addWidget(self.nombre_input)

        self.apellido_input = QLineEdit()
        self.apellido_input.setPlaceholderText("Apellido")
        user_action2 = QAction(QIcon(icon_path_user), "", self)
        user_action2.setObjectName("icon_action")
        self.apellido_input.addAction(user_action2, QLineEdit.ActionPosition.LeadingPosition)
        self.apellido_input.setObjectName("input_apellido")
        self.apellido_input.setFixedHeight(45)
        nombre_apellido_layout.addWidget(self.apellido_input)

        content_layout.addLayout(nombre_apellido_layout)
        content_layout.addSpacing(10)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        mail_action = QAction(QIcon(icon_path_mail), "", self)
        mail_action.setObjectName("icon_action")
        self.email_input.addAction(mail_action, QLineEdit.ActionPosition.LeadingPosition)
        self.email_input.setObjectName("input_email")
        self.email_input.setFixedHeight(45)
        content_layout.addWidget(self.email_input)
        content_layout.addSpacing(10)
        
        contrasena_confirmar_layout = QHBoxLayout()
        contrasena_confirmar_layout.setSpacing(10)

        self.contraseña_input = QLineEdit()
        self.contraseña_input.setPlaceholderText("Contraseña")
        lock_action1 = QAction(QIcon(icon_path_lock), "", self)
        lock_action1.setObjectName("icon_action")
        self.contraseña_input.addAction(lock_action1, QLineEdit.ActionPosition.LeadingPosition)
        self.contraseña_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.contraseña_input.setObjectName("input_registro_contrasena")
        self.contraseña_input.setFixedHeight(45)
        contrasena_confirmar_layout.addWidget(self.contraseña_input)

        self.confirmar_contraseña_input = QLineEdit()
        self.confirmar_contraseña_input.setPlaceholderText("Confirmar Contraseña")
        lock_action2 = QAction(QIcon(icon_path_lock), "", self)
        lock_action2.setObjectName("icon_action")
        self.confirmar_contraseña_input.addAction(lock_action2, QLineEdit.ActionPosition.LeadingPosition)
        self.confirmar_contraseña_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirmar_contraseña_input.setObjectName("input_registro_confirmar")
        self.confirmar_contraseña_input.setFixedHeight(45)
        contrasena_confirmar_layout.addWidget(self.confirmar_contraseña_input)

        content_layout.addLayout(contrasena_confirmar_layout)
        content_layout.addSpacing(25)

        botones_layout = QVBoxLayout()
        botones_layout.setSpacing(5)

        BUTTON_WIDTH = 300 
        BUTTON_HEIGHT = 35
        
        self.btn_register = QPushButton("Registrarse")
        self.btn_register.setObjectName("btn_registro_final") 
        self.btn_register.setFixedHeight(BUTTON_HEIGHT) 
        self.btn_register.setFixedWidth(BUTTON_WIDTH)
        self.btn_register.clicked.connect(self.on_register_click)
        
        h_reg = QHBoxLayout()
        h_reg.addStretch()
        h_reg.addWidget(self.btn_register)
        h_reg.addStretch()
        botones_layout.addLayout(h_reg)

        self.btn_back_to_login = QPushButton("Volver a Iniciar Sesión")
        self.btn_back_to_login.clicked.connect(self.show_login_requested.emit)
        self.btn_back_to_login.setObjectName("btn_volver_login") 
        self.btn_back_to_login.setFixedHeight(BUTTON_HEIGHT) 
        self.btn_back_to_login.setFixedWidth(BUTTON_WIDTH)
        
        h_back = QHBoxLayout()
        h_back.addStretch()
        h_back.addWidget(self.btn_back_to_login)
        h_back.addStretch()
        botones_layout.addLayout(h_back)

        content_layout.addLayout(botones_layout) 

        content_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def on_register_click(self):
        nombre = self.nombre_input.text()
        apellido = self.apellido_input.text()
        email = self.email_input.text()
        password = self.contraseña_input.text()
        confirm_password = self.confirmar_contraseña_input.text()
        
        campos_llenos = nombre and apellido and email and password and confirm_password
        
        if not campos_llenos:
             QMessageBox.warning(self, "Error de Validación", "Por favor, completa todos los campos.")
             return

        if password != confirm_password:
             QMessageBox.warning(self, "Error de Contraseña", "Las contraseñas no coinciden.")
             return

        QMessageBox.information(self, "Registro Exitoso", f"Usuario {nombre} {apellido} registrado con email: {email}.")
        self.show_login_requested.emit()