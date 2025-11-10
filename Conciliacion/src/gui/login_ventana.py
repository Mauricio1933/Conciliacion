from PyQt6.QtWidgets import (QWidget, QLineEdit, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QCheckBox, QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QAction
import os

class CustomTitleBar(QWidget):
    def __init__(self, parent_window: QWidget):
        super().__init__(parent_window)
        
        self.parent_window = parent_window
        self.setObjectName("CustomTitleBar")
        self.start_pos = None
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

class LoginWindow(QWidget):
    show_register_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) 
        self.setObjectName("LoginWindow")
        self.setWindowTitle("Acceso de Usuario")
        self.setFixedSize(380, 380) 
        
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
            "../../assets/styles/login_estilos.qss",
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

        self.titulo = QLabel("Inicio de Sesión")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titulo.setObjectName("titulo")
        content_layout.addWidget(self.titulo)
        content_layout.addSpacing(20)

        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path_user = os.path.join(base_path, "../../assets/icons/user_light.svg")
        icon_path_lock = os.path.join(base_path, "../../assets/icons/lock_red.svg")

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Usuario")
        user_action = QAction(QIcon(icon_path_user), "", self)
        user_action.setObjectName("icon_action")
        self.nombre_input.addAction(user_action, QLineEdit.ActionPosition.LeadingPosition) 
        self.nombre_input.setObjectName("input_usuario")
        self.nombre_input.setFixedHeight(40)
        content_layout.addWidget(self.nombre_input)
        content_layout.addSpacing(5)

        self.contraseña_input = QLineEdit()
        self.contraseña_input.setPlaceholderText("Contraseña")
        lock_action = QAction(QIcon(icon_path_lock), "", self)
        lock_action.setObjectName("icon_action")
        self.contraseña_input.addAction(lock_action, QLineEdit.ActionPosition.LeadingPosition)
        self.contraseña_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.contraseña_input.setObjectName("input_contrasena")
        self.contraseña_input.setFixedHeight(40)
        content_layout.addWidget(self.contraseña_input)

        fila_opciones = QHBoxLayout()
        self.guardar_checkbox = QCheckBox("Guardar contraseña")
        self.guardar_checkbox.setObjectName("checkbox_guardar")
        fila_opciones.addWidget(self.guardar_checkbox)
        fila_opciones.addStretch()
        content_layout.addLayout(fila_opciones)
        content_layout.addSpacing(20)

        self.btn_login = QPushButton("Iniciar sesión")
        self.btn_login.setObjectName("btn_login")
        self.btn_login.setFixedHeight(35)
        self.btn_login.clicked.connect(self.on_login_click)
        content_layout.addWidget(self.btn_login)
        content_layout.addSpacing(5)

        self.btn_register = QPushButton("Registrarse")
        self.btn_register.clicked.connect(self.show_register_requested.emit)
        self.btn_register.setObjectName("btn_register")
        self.btn_register.setFixedHeight(35)
        content_layout.addWidget(self.btn_register)

        content_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def on_login_click(self):
        user = self.nombre_input.text()
        password = self.contraseña_input.text()
        
        if not user or not password:
             QMessageBox.warning(self, "Error", "Por favor, introduce usuario y contraseña.")
             return

        QMessageBox.information(self, "Intento de Login", f"Intentando iniciar sesión con Usuario: {user}")