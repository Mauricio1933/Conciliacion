import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QCursor, QPixmap, QFont

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.abspath(os.path.join(BASE_PATH, "../../../assets"))


class NavButton(QWidget):
    clicked = pyqtSignal()

    def __init__(self, text: str, icon_name: str, object_name: str, parent=None):
        super().__init__(parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setObjectName(object_name)
        self.setFixedSize(100, 80)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)
        
        self.icon_label = QLabel()
        icon_path = os.path.join(ASSETS_PATH, f"icons/{icon_name}")
        icon_size = QSize(45, 45)
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.icon_label.setPixmap(pixmap.scaled(icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.icon_label.setText("❓")
            self.icon_label.setFont(QFont("sans serif", 12))
            
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.text_label = QLabel(text)
        self.text_label.setObjectName("NavButtonText")
        self.text_label.setFont(QFont("Inter", 8, QFont.Weight.Bold))
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
        
    def enterEvent(self, event):
        self.setProperty("hover", True)
        self.style().polish(self)
        self.style().polish(self.text_label)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setProperty("hover", False)
        self.style().polish(self)
        self.style().polish(self.text_label)
        super().leaveEvent(event)


class NavBar(QWidget):
    usuarios_clicked = pyqtSignal()
    registros_clicked = pyqtSignal()
    ayuda_clicked = pyqtSignal()

    ICON_NAV_MAP = {
        "Usuarios": "users_icon.svg",
        "Registros": "files_icon.svg",
        "Ayuda": "help_icon.svg"
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NavBar")
        self.setFixedHeight(100)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        nav_layout = QHBoxLayout(self)
        nav_layout.setContentsMargins(10, 0, 10, 0)
        nav_layout.setSpacing(10)
        
        spacer_left = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        nav_layout.addItem(spacer_left)
        
        btn_usuarios = NavButton(
            "Usuarios", 
            self.ICON_NAV_MAP["Usuarios"], 
            "navButtonHome" 
        )
        btn_registros = NavButton(
            "Registros", 
            self.ICON_NAV_MAP["Registros"], 
            "navButtonConf" 
        )
        btn_ayuda = NavButton(
            "Ayuda", 
            self.ICON_NAV_MAP["Ayuda"], 
            "navButtonData"
        )

        btn_usuarios.clicked.connect(self.usuarios_clicked)
        btn_registros.clicked.connect(self.registros_clicked)
        btn_ayuda.clicked.connect(self.ayuda_clicked)
        
        nav_layout.addWidget(btn_usuarios)
        nav_layout.addWidget(btn_registros)
        nav_layout.addWidget(btn_ayuda)
        
        spacer_right = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        nav_layout.addItem(spacer_right)