from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QApplication, QSizePolicy, QSpacerItem, 
    QPushButton, QHBoxLayout, QMessageBox, QFileDialog, QStackedWidget
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QSize, QEvent
from PyQt6.QtGui import QIcon, QFont, QPixmap, QCursor
import sys
import os

from src.gui.widgets.barra_custom import CustomTitleBar
from src.gui.widgets.nav_custom import NavBar
from src.gui.usuarios_ventana import UsersView

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.abspath(os.path.join(BASE_PATH, "../../assets"))

class ImportFileCard(QWidget):
    import_triggered = pyqtSignal(str, QWidget, QLabel, QLabel, str) 

    def __init__(self, title: str, icon_pair: tuple, file_filter: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.icon_pair = icon_pair
        self.file_filter = file_filter
        self.setAcceptDrops(True)
        self.setObjectName("ImportCardContainer") 
        self._setup_ui()
    
    def _setup_ui(self):
        v_layout = QVBoxLayout(self)
        v_layout.setContentsMargins(5, 5, 5, 5)
        v_layout.setSpacing(10)
        v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) 

        self.card_widget = QWidget()
        self.card_widget.setObjectName("ImportCardWidget") 
        self.card_widget.setFixedSize(230, 270) 
        
        card_layout = QVBoxLayout(self.card_widget) 
        card_layout.setSpacing(10)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_name = self.icon_pair[0]
        icon_path = os.path.join(ASSETS_PATH, f"icons/{icon_name}")
        self.icon_label = QLabel()
        self.icon_label.setObjectName("CardIconLabel")
        icon_size = QSize(80, 80)

        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.icon_label.setPixmap(pixmap.scaled(icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.icon_label.setText(f"<{self.title}>")
            self.icon_label.setFont(QFont("sans serif", 18))

        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("sans serif", 11, QFont.Weight.Bold))
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_import = QPushButton("Importar")
        btn_import.setObjectName("ImportButton")
        btn_import.setFixedSize(100,35)
        btn_import.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        btn_import.clicked.connect(self._handle_button_click)
        v_layout.addWidget(self.card_widget)
        v_layout.addWidget(btn_import, alignment=Qt.AlignmentFlag.AlignCenter)

    def _handle_button_click(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            f"Importar Archivo - {self.title}", 
            "", 
            self.file_filter
        )
        if file_path:
            self.import_triggered.emit(file_path, self.card_widget, self.icon_label, self.title_label, self.title)
        else:
            QMessageBox.warning(
                self, 
                "Importación Cancelada", 
                "La importación para fue cancelada.",
                QMessageBox.StandardButton.Ok
            )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            file_path = urls[0].toLocalFile()
            self.import_triggered.emit(file_path, self.card_widget, self.icon_label, self.title_label, self.title)
            
            event.acceptProposedAction()
        else:
            event.ignore()

class MainWindow(QWidget): # MainWindow
    windowStateChanged = pyqtSignal(Qt.WindowState) 
    
    ICON_MAP = {
        "Estado de Cuenta": ("pdf_icon.svg", "pdf_import.svg"),
        "Libro de Venta": ("excel_icon.svg", "excel_import.svg"),
        "Registro SAINT": ("csv_icon.svg", "csv_import.svg")
    }
    
    FILE_FILTERS = {
        "Estado de Cuenta": "Archivos PDF (*.pdf);;Todos los Archivos (*.*)",
        "Libro de Venta": "Archivos Excel (*.xlsx *.xls);;Todos los Archivos (*.*)",
        "Registro SAINT": "Archivos CSV (*.csv);;Archivos de Texto (*.txt);;Todos los Archivos (*.*)"
    }


    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) 
        self.setObjectName("MainWindow")
        self.resize(1100, 700)
        
        self.main_layout = QVBoxLayout(self) 
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0) 
        
        self._setup_styles() 
        self._init_ui()

    def _init_ui(self):
        title_bar = CustomTitleBar(self) 
        title_bar.setFixedHeight(40)     
        self.main_layout.addWidget(title_bar)

        self.nav_bar = NavBar(self) 
        self.main_layout.addWidget(self.nav_bar)
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        self.registros_view = self._create_registros_view()
        self.usuarios_view = UsersView()

        self.stacked_widget.addWidget(self.registros_view)
        self.stacked_widget.addWidget(self.usuarios_view)

        self.nav_bar.registros_clicked.connect(self._show_registros_view)
        self.nav_bar.usuarios_clicked.connect(self._show_usuarios_view)
        
    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self.windowStateChanged.emit(self.windowState())

    def _show_registros_view(self):
        self.stacked_widget.setCurrentWidget(self.registros_view)

    def _show_usuarios_view(self):
        self.stacked_widget.setCurrentWidget(self.usuarios_view)

    def _setup_styles(self):
        self.setFont(QFont("Inter", 11))

        qss_files = ["main_estilos.qss", "usuarios_estilos.qss"]
        
        combined_styles = ""
        for filename in qss_files:
            style_path = os.path.join(ASSETS_PATH, "styles", filename)
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    combined_styles += f.read() + "\n" 
            except FileNotFoundError:
                print(f"Advertencia: No se encontro el archivo de estilos en la ruta: {style_path}")
            except Exception as e:
                print(f"Error al cargar {filename}: {e}")

        if combined_styles:
            self.setStyleSheet(combined_styles)
        else:
            print("Advertencia: No se pudo cargar ningun estilo QSS.")

    def _handle_import_logic(self, file_path: str, card_widget: QWidget, icon_label: QLabel, title_label: QLabel, card_title: str):
        icon_size = QSize(80, 80)
        
        icon_pair = self.ICON_MAP.get(card_title, ("default.svg", "check_circle.svg"))
        success_icon_name = icon_pair[1]
        success_icon_path = os.path.join(ASSETS_PATH, f"icons/{success_icon_name}")
        
        if os.path.exists(success_icon_path):
            pixmap = QPixmap(success_icon_path)
            icon_label.setPixmap(pixmap.scaled(icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setText("✅")
            icon_label.setFont(QFont("sans serif", 24))
            print(f"Advertencia: No se encontró el icono de éxito específico: {success_icon_name}")

        card_widget.setObjectName("ImportCardWidgetSuccess") 
        
        title_label.setObjectName("title_label_success") 
        
        card_widget.style().polish(card_widget)
        title_label.style().polish(title_label)
        
        QMessageBox.information(
            self, 
            "Importación Exitosa", 
            f"El archivo para '{card_title}' ha sido seleccionado exitosamente",
            QMessageBox.StandardButton.Ok
        )

    def _create_import_card(self, title):
        icon_pair = self.ICON_MAP.get(title, ("default.svg", "check_circle.svg"))
        file_filter = self.FILE_FILTERS.get(title, "Todos los Archivos (*.*)")
        
        card = ImportFileCard(
            title=title, 
            icon_pair=icon_pair, 
            file_filter=file_filter,
            parent=self 
        )
        
        card.import_triggered.connect(self._handle_import_logic)
        return card

    def _create_registros_view(self) -> QWidget:
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget) 
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_widget.setObjectName("MainContentWidget") 
        
        content_layout.addStretch() 

        center_h_container = QWidget()
        center_h_layout = QHBoxLayout(center_h_container)
        center_h_layout.setContentsMargins(0, 0, 0, 0)
        center_h_layout.addStretch() 
        
        cards_h_layout = QHBoxLayout()
        cards_h_layout.setSpacing(25) 
        cards_h_layout.setContentsMargins(0, 0, 0, 0) 

        card_1 = self._create_import_card("Estado de Cuenta")
        card_2 = self._create_import_card("Libro de Venta")
        card_3 = self._create_import_card("Registro SAINT")

        cards_h_layout.addWidget(card_1)
        cards_h_layout.addWidget(card_2)
        cards_h_layout.addWidget(card_3)
        
        center_h_layout.addLayout(cards_h_layout)
        center_h_layout.addStretch() 
        content_layout.addWidget(center_h_container)

        spacer_gap = QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        content_layout.addItem(spacer_gap)
        
        btn_conciliar = QPushButton("Conciliar")
        btn_conciliar.setObjectName("ConciliarButton")
        btn_conciliar.setFixedSize(200, 45) 
        btn_conciliar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_conciliar.clicked.connect(lambda: QMessageBox.information(self, "Acción", "Función 'Conciliar' activada."))

        conciliar_container = QWidget()
        conciliar_layout = QHBoxLayout(conciliar_container)
        conciliar_layout.setContentsMargins(0, 0, 0, 0)
        conciliar_layout.addStretch()
        conciliar_layout.addWidget(btn_conciliar)
        conciliar_layout.addStretch()
        content_layout.addWidget(conciliar_container)
        content_layout.addStretch()
        return content_widget
