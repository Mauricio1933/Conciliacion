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

#================================================================================
# IMPORTACIONES PARA CONCILIACIÓN
#================================================================================
from src.gui.conciliacion_view import ConciliacionView
from src.logic.conciliacion_maestra import ConciliacionMaestra
from src.logic.convert_pdf_csv import EstadoDeCuentaPdfToCsv
from src.logic.libro_ventas_processor import LibroVentasCsv
from src.logic.Registro_saint_to_csv import RegistroSaintCsv
import pandas as pd

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
        "Registro SAINT": "Archivos Excel (*.xlsx *.xls);;Todos los Archivos (*.*)"  # Cambiado a Excel
    }


    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Comentado para evitar transparencia
        self.setObjectName("MainWindow")
        self.resize(1100, 700)
        
        #================================================================================
        # TRACKING DE ARCHIVOS IMPORTADOS
        #================================================================================
        self.archivos_importados = {
            "Estado de Cuenta": None,
            "Libro de Venta": None,
            "Registro SAINT": None
        }
        
        self.btn_conciliar = None  # Referencia al botón Conciliar
        
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
        
        #================================================================================
        # VISTA DE CONCILIACIÓN
        #================================================================================
        self.conciliacion_view = ConciliacionView()

        self.stacked_widget.addWidget(self.registros_view)
        self.stacked_widget.addWidget(self.usuarios_view)
        self.stacked_widget.addWidget(self.conciliacion_view)

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

        #================================================================================
        # CARGAR ESTILOS INCLUYENDO CONCILIACIÓN
        #================================================================================
        qss_files = ["main_estilos.qss", "usuarios_estilos.qss", "conciliacion_estilos.qss"]
        
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
        #================================================================================
        # GUARDAR RUTA DEL ARCHIVO IMPORTADO
        #================================================================================
        self.archivos_importados[card_title] = file_path
        
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
        
        #================================================================================
        # VERIFICAR SI TODOS LOS ARCHIVOS ESTÁN IMPORTADOS
        #================================================================================
        self._verificar_archivos_completos()
        
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
        
        #================================================================================
        # BOTÓN CONCILIAR CON LÓGICA COMPLETA
        #================================================================================
        self.btn_conciliar = QPushButton("Conciliar")
        self.btn_conciliar.setObjectName("ConciliarButton")
        self.btn_conciliar.setFixedSize(200, 45) 
        self.btn_conciliar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_conciliar.setEnabled(False)  # Deshabilitado hasta que se importen los 3 archivos
        self.btn_conciliar.clicked.connect(self._ejecutar_conciliacion)

        conciliar_container = QWidget()
        conciliar_layout = QHBoxLayout(conciliar_container)
        conciliar_layout.setContentsMargins(0, 0, 0, 0)
        conciliar_layout.addStretch()
        conciliar_layout.addWidget(self.btn_conciliar)
        conciliar_layout.addStretch()
        content_layout.addWidget(conciliar_container)
        content_layout.addStretch()
        return content_widget
    
    #================================================================================
    # MÉTODOS DE CONCILIACIÓN
    #================================================================================
    
    def _verificar_archivos_completos(self):
        """Verifica si los 3 archivos están importados y habilita el botón Conciliar"""
        todos_importados = all(ruta is not None for ruta in self.archivos_importados.values())
        
        if self.btn_conciliar:
            self.btn_conciliar.setEnabled(todos_importados)
            
            if todos_importados:
                self.btn_conciliar.setToolTip("Ejecutar conciliación completa")
            else:
                archivos_faltantes = [nombre for nombre, ruta in self.archivos_importados.items() if ruta is None]
                self.btn_conciliar.setToolTip(f"Faltan archivos: {', '.join(archivos_faltantes)}")
    
    def _ejecutar_conciliacion(self):
        """Ejecuta la conciliación completa y muestra resultados"""
        try:
            # Cargar archivos
            print("\n🔄 Cargando archivos...")
            
            #================================================================================
            # PROCESAR ARCHIVOS CON LOS PROCESADORES EXISTENTES
            #================================================================================
            
            # Estado de Cuenta (PDF → CSV)
            ruta_estado = self.archivos_importados["Estado de Cuenta"]
            print(f"📄 Procesando Estado de Cuenta: {ruta_estado}")
            try:
                procesador_estado = EstadoDeCuentaPdfToCsv(ruta_estado)
                csv_estado = procesador_estado.ejecutar()
                df_estado = pd.read_csv(csv_estado)
                print(f"✅ Estado de Cuenta procesado: {len(df_estado)} movimientos\n")
            except Exception as e:
                raise Exception(f"Error al procesar Estado de Cuenta (PDF):\n{str(e)}\n\nVerifique que el PDF no esté corrupto o protegido.")
            
            # Libro de Ventas (Excel → CSV)
            ruta_libro = self.archivos_importados["Libro de Venta"]
            print(f"📊 Procesando Libro de Ventas: {ruta_libro}")
            try:
                procesador_libro = LibroVentasCsv(ruta_libro, banco_filtro='BANCARIBE')
                csv_libro = procesador_libro.ejecutar()
                df_libro = pd.read_csv(csv_libro, sep=';')
                print(f"✅ Libro de Ventas procesado: {len(df_libro)} facturas\n")
            except Exception as e:
                raise Exception(f"Error al procesar Libro de Ventas (Excel):\n{str(e)}")
            
            # Registro SAINT (Excel → CSV)
            ruta_saint = self.archivos_importados["Registro SAINT"]
            print(f"📋 Procesando Registro SAINT: {ruta_saint}")
            try:
                procesador_saint = RegistroSaintCsv(ruta_saint)
                csv_saint = procesador_saint.ejecutar()
                df_saint = pd.read_csv(csv_saint)
                print(f"✅ Registro SAINT procesado: {len(df_saint)} registros\n")
            except Exception as e:
                raise Exception(f"Error al procesar Registro SAINT (Excel):\n{str(e)}")
            
            # Crear conciliador maestro
            conciliador = ConciliacionMaestra(df_estado, df_libro)
            
            # Ejecutar conciliación
            resultados = conciliador.ejecutar_conciliacion_completa()
            
            # Mostrar resultados en la vista
            self.conciliacion_view.cargar_resultados(resultados)
            self.stacked_widget.setCurrentWidget(self.conciliacion_view)
            
            QMessageBox.information(
                self,
                "Conciliación Exitosa",
                f"Se procesaron {len(resultados)} transacciones.\n\nRevise los resultados en la tabla.",
                QMessageBox.StandardButton.Ok
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error en Conciliación",
                f"Ocurrió un error durante la conciliación:\n\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
