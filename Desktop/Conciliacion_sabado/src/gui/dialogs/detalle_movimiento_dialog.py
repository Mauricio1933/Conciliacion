import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QFrame, 
                             QPushButton, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.gui.widgets.barra_custom import CustomTitleBar

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.abspath(os.path.join(BASE_PATH, "../../../assets"))


class DetalleMovimientoDialog(QDialog):

    windowStateChanged = pyqtSignal(Qt.WindowState)

    def __init__(self, datos: dict, parent=None):
        super().__init__(parent)
        
        self.datos = datos
                                        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("DetalleMovimientoDialog")
        self.resize(500, 580)
        self.setMinimumWidth(450)
        
        self._setup_styles()
        self._init_ui()
        
    def _setup_styles(self):
        self.setFont(QFont("Inter", 10))
        
                        
        qss_files = ["main_estilos.qss"]
        combined_styles = ""
        for filename in qss_files:
            style_path = os.path.join(ASSETS_PATH, "styles", filename)
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    combined_styles += f.read() + "\n"
            except FileNotFoundError:
                pass
        
                                         
        dialog_styles = """
            #DetalleContentWidget {
                background-color: #1E1E1E;
                border-radius: 10px;
            }
            #TituloDetalle {
                color: #C9A227;
                font-size: 16px;
                font-weight: bold;
                padding: 4px;
            }
            #CampoNombre {
                color: #C9A227;
                font-weight: bold;
                font-size: 12px;
                background: transparent;
            }
            #CampoValor {
                background-color: #2D2D2D;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 5px 8px;
                font-size: 11px;
                color: white;
            }
            #BotonCerrar {
                background-color: #C9A227;
                color: #1E1E1E;
                border: none;
                border-radius: 5px;
                padding: 8px 25px;
                font-weight: bold;
                font-size: 12px;
            }
            #BotonCerrar:hover {
                background-color: #E0B82F;
            }
        """
        
        if combined_styles:
            self.setStyleSheet(combined_styles + dialog_styles)
        else:
            self.setStyleSheet(dialog_styles)
    
    def _init_ui(self):
                          
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
                                                
        content_widget = QWidget()
        content_widget.setObjectName("DetalleContentWidget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
                                       
        self.setWindowTitle("Detalle del Movimiento")
        title_bar = CustomTitleBar(self, show_maximize=False, show_minimize=False)
        title_bar.setFixedHeight(32)
        content_layout.addWidget(title_bar)
        
                            
        interior = QWidget()
        interior_layout = QVBoxLayout(interior)
        interior_layout.setContentsMargins(15, 10, 15, 15)
        interior_layout.setSpacing(10)
        
                
        titulo = QLabel(" Detalle del Movimiento")
        titulo.setObjectName("TituloDetalle")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        interior_layout.addWidget(titulo)
        
                                                
        from PyQt6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")
        
                                                
        campos_widget = QWidget()
        campos_widget.setStyleSheet("background: transparent;")
        form_layout = QVBoxLayout(campos_widget)
        form_layout.setSpacing(8)
        form_layout.setContentsMargins(0, 0, 5, 0)                                   
        
                            
        for campo, valor in self.datos.items():
            campo_frame = QFrame()
            campo_frame.setStyleSheet("background: transparent;")
            campo_layout = QVBoxLayout(campo_frame)
            campo_layout.setContentsMargins(0, 0, 0, 0)
            campo_layout.setSpacing(2)
            
            lbl_nombre = QLabel(campo + ":")
            lbl_nombre.setObjectName("CampoNombre")
            
                                                                           
            val_str = str(valor).strip() if valor is not None else ""
            lbl_valor = QLabel(val_str if val_str else "-")
            lbl_valor.setObjectName("CampoValor")
            lbl_valor.setWordWrap(True)
            lbl_valor.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            
            campo_layout.addWidget(lbl_nombre)
            campo_layout.addWidget(lbl_valor)
            form_layout.addWidget(campo_frame)
            
                                                                               
        from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
        form_layout.addItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        scroll_area.setWidget(campos_widget)
        interior_layout.addWidget(scroll_area)
        
                      
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setObjectName("BotonCerrar")
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.clicked.connect(self.close)
        interior_layout.addWidget(btn_cerrar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addWidget(interior)
        main_layout.addWidget(content_widget)

    def changeEvent(self, event):
        super().changeEvent(event)
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.WindowStateChange:
            self.windowStateChanged.emit(self.windowState())
