import os
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy, QApplication, QDialog
)
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QCursor

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.abspath(os.path.join(BASE_PATH, "../../../assets"))

class CustomTitleBar(QWidget):
    def __init__(self, parent_window: QWidget, show_maximize: bool = True, show_icon: bool = True, show_minimize: bool = True):
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

        if show_icon:
            icon_label = QLabel()
            app_icon_path = os.path.join(ASSETS_PATH, "icons", "app_icon.svg")
            if os.path.exists(app_icon_path):
                pixmap = QPixmap(app_icon_path)
                icon_label.setPixmap(pixmap.scaled(QSize(27, 27), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                 print(f"Advertencia: No se encontro el icono de la App en la ruta: {app_icon_path}")
            layout.addWidget(icon_label)

        self.title_label = QLabel(self.parent_window.windowTitle() if self.parent_window else "Aplicación")
        self.title_label.setObjectName("TitleLabel")
        layout.addWidget(self.title_label)
        
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        self.btn_close = QPushButton()
        self.btn_close.setObjectName("btnClose")
        self.btn_close.setFixedWidth(30)
        self.btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        self.minimize_icon_path = os.path.join(ASSETS_PATH, "icons/mini_dark.svg") 
        self.maximize_icon_path = os.path.join(ASSETS_PATH, "icons/expand_white.svg")
        self.restore_icon_path = os.path.join(ASSETS_PATH, "icons/minimize_icon.svg")
        self.close_icon_path = os.path.join(ASSETS_PATH, "icons/exit_dark.svg")

        if show_minimize:
            self.btn_minimize = QPushButton()
            self.btn_minimize.setObjectName("btnMinimize")
            self.btn_minimize.setFixedWidth(30)
            self.btn_minimize.setIcon(QIcon(self.minimize_icon_path))
            self.btn_minimize.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.btn_minimize.clicked.connect(self.parent_window.showMinimized)
            layout.addWidget(self.btn_minimize)

        self.btn_close.setIcon(QIcon(self.close_icon_path))
        if isinstance(self.parent_window, QDialog):
            self.btn_close.clicked.connect(self.parent_window.close)
        else:
            self.btn_close.clicked.connect(QApplication.instance().quit)

        if show_maximize:
            self.btn_maximize = QPushButton() 
            self.btn_maximize.setObjectName("btnMaximize")
            self.btn_maximize.setFixedWidth(30)
            self.btn_maximize.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self._update_maximize_button(self.parent_window.windowState()) 
            self.btn_maximize.clicked.connect(self._toggle_maximize)
            layout.addWidget(self.btn_maximize)
            self.parent_window.windowStateChanged.connect(self._update_maximize_button)

        layout.addWidget(self.btn_close)

    def _toggle_maximize(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()

    def _update_maximize_button(self, state=None):
        if self.parent_window.isMaximized():
            self.btn_maximize.setIcon(QIcon(self.restore_icon_path)) 
        else:
            self.btn_maximize.setIcon(QIcon(self.maximize_icon_path))

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()
            self.diff = self.start_pos - self.parent_window.pos() 
            self.parent_window.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        event.accept()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.start_pos is not None and not self.parent_window.isMaximized():
            self.parent_window.move(event.globalPosition().toPoint() - self.diff)
        event.accept()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.start_pos = None
        self.parent_window.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        event.accept()
        
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and hasattr(self, 'btn_maximize'):
            self._toggle_maximize()
            event.accept()