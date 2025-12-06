import shutil
import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QSizePolicy, QSpacerItem, 
    QPushButton, QMessageBox, QFileDialog, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QEvent, QThreadPool
from PyQt6.QtGui import QIcon, QFont, QPixmap, QCursor
import sys
import pandas as pd
import os

from src.gui.widgets.barra_custom import CustomTitleBar
from src.gui.widgets.nav_custom import NavBar
from src.gui.usuarios_ventana import UsersView
from src.gui.registros_ventana import RegistrosWindow
from src.gui.ventana_conciliacion import VentanaConciliacion
from src.gui.resultados_ventana import VentanaResultados 
from src.logic.workers.pdf_worker import PdfConverterWorker
from src.logic.workers.libro_ventas_worker import LibroVentasWorker
from src.logic.workers.saint_worker import SaintWorker
from src.logic.workers.conciliacion_worker import ConciliacionWorker
from src.logic.reporte_pdf_generator import ReportePDFGenerator

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

    def set_enabled_import(self, enabled: bool):
        """Habilita o deshabilita la interacción con la tarjeta."""
        self.card_widget.setEnabled(enabled)

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

class MainWindow(QWidget): 
    windowStateChanged = pyqtSignal(Qt.WindowState) 
    logout_triggered = pyqtSignal()
    
    ICON_MAP = {
        "Estado de Cuenta": ("pdf_icon.svg", "pdf_import.svg"),
        "Libro de Venta": ("excel_icon.svg", "excel_import.svg"),
         "Registro SAINT": ("csv_icon.svg", "csv_import.svg")
    }
    
    FILE_FILTERS = {
        "Estado de Cuenta": "Archivos PDF (*.pdf);;Todos los Archivos (*.*)",
        "Libro de Venta": "Archivos Excel (*.xlsx *.xls);;Todos los Archivos (*.*)",
        "Registro SAINT": "Archivos Excel (*.xlsx *.xls);;Todos los Archivos (*.*)"
    }


    def __init__(self, logged_username: str | None = None):
        super().__init__()
        self.logged_username = logged_username
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) 
        self.setObjectName("MainWindow")
        self.resize(1100, 700)
        
        self.main_layout = QVBoxLayout(self) 
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0) 
        
        self.thread_pool = QThreadPool()
        
        self.ruta_csv_estado_cuenta = None
        self.ruta_csv_libro_ventas = None 
        self.ruta_csv_registro_saint = None
        
                                                               
        self.ruta_original_estado_cuenta = None
        self.ruta_original_libro_ventas = None
        self.ruta_original_registro_saint = None
        
        self.resumen_bancario = None                                             
        
                                                                                      
        self.ventana_resultados_actual = None
        
                                                               
        self.df_resultado_conciliacion = None
        self.ultimo_timestamp = None
        
        self.files_recorded = False

        self._setup_styles() 
        self._init_ui()
        
                             
        self.showMaximized()

    def _init_ui(self):
        title_bar = CustomTitleBar(self) 
        title_bar.setFixedHeight(40)     
        self.main_layout.addWidget(title_bar)

        self.nav_bar = NavBar(self) 
        self.main_layout.addWidget(self.nav_bar)
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        self.vista_principal_conciliacion = self._create_registros_view() 
        self.usuarios_view = UsersView()
        self.registros_window_new = RegistrosWindow()

        self.stacked_widget.addWidget(self.vista_principal_conciliacion)
        self.stacked_widget.addWidget(self.usuarios_view)
        self.stacked_widget.addWidget(self.registros_window_new)

        self.nav_bar.conciliacion_clicked.connect(self._show_conciliacion_view)
        self.nav_bar.registros_clicked.connect(self._show_registros_window_new)
        self.nav_bar.usuarios_clicked.connect(self._show_usuarios_view)
        self.nav_bar.logout_clicked.connect(self._handle_logout)
        
        base_storage_path = os.path.join(BASE_PATH, "../../data_files/conciliaciones")
        self.registros_window_new.load_records_from_disk(base_storage_path)

        self.check_permissions()

    def check_permissions(self):
        from src.logic.settings import load_credentials
        from src.logic.database import get_user_by_username
        # Prefer the username passed at construction (user who just authenticated).
        if getattr(self, 'logged_username', None):
            saved_username = self.logged_username
        else:
            saved_username, _ = load_credentials()

        self.current_user = None
        if saved_username:
            self.current_user = get_user_by_username(saved_username)
            
                                                                              
        user_role = self.current_user.get('rol', '').lower() if self.current_user else ''
        
        if user_role != 'admin':
            self.nav_bar.hide_users_button()
            self.nav_bar.hide_conciliacion_button()
            
                                                
            if hasattr(self, 'import_card_1'): self.import_card_1.set_enabled_import(False)
            if hasattr(self, 'import_card_2'): self.import_card_2.set_enabled_import(False)
            if hasattr(self, 'import_card_3'): self.import_card_3.set_enabled_import(False)

            self.stacked_widget.setCurrentIndex(2)                  

    def _handle_logout(self):
        self.logout_triggered.emit()
                                                                              
                                                                   

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self.windowStateChanged.emit(self.windowState())

    def _show_conciliacion_view(self):
        self.stacked_widget.setCurrentWidget(self.vista_principal_conciliacion)
        
    def _show_registros_window_new(self):
        self.stacked_widget.setCurrentWidget(self.registros_window_new)

    def _show_usuarios_view(self):
        self.stacked_widget.setCurrentWidget(self.usuarios_view)

    def _setup_styles(self):
        self.setFont(QFont("Inter", 11))

        qss_files = ["main_estilos.qss", "usuarios_estilos.qss", "registros_estilos.qss"]
        
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

    def _handle_import_logic(self, file_path: str, card_widget: QWidget, icon_label: QLabel, title_label: QLabel, card_title: str, card_instance: 'ImportFileCard'):
        self.files_recorded = False
        
        if card_title == "Estado de Cuenta":
            if not file_path.lower().endswith('.pdf'):
                QMessageBox.warning(self, "Archivo no válido", "Por favor, seleccione un archivo PDF para el Estado de Cuenta.")
                return
            self.ruta_original_estado_cuenta = file_path
            card_instance.set_enabled_import(False)
            worker = PdfConverterWorker(pdf_path=file_path)

            worker.signals.finished.connect(
                lambda csv_path, resumen: self._on_conversion_finished(
                    csv_path, card_widget, icon_label, title_label, card_title, card_instance, resumen
                )
            )
            worker.signals.error.connect(
                lambda error_msg: self._on_conversion_error(error_msg, card_instance)
            )
            self.thread_pool.start(worker)

        elif card_title == "Libro de Venta":
            if not file_path.lower().endswith(('.xlsx', '.xls')):
                QMessageBox.warning(self, "Archivo no válido", "Por favor, seleccione un archivo Excel (.xlsx, .xls).")
                return
            self.ruta_original_libro_ventas = file_path
            card_instance.set_enabled_import(False)
            worker = LibroVentasWorker(excel_path=file_path)

            worker.signals.finished.connect(
                lambda csv_path: self._on_conversion_finished(
                    csv_path, card_widget, icon_label, title_label, card_title, card_instance
                )
            )
            worker.signals.error.connect(
                lambda error_msg: self._on_conversion_error(error_msg, card_instance)
            )

            self.thread_pool.start(worker)

        elif card_title == "Registro SAINT":
            if not file_path.lower().endswith(('.xlsx', '.xls')):
                QMessageBox.warning(self, "Archivo no válido", "Por favor, seleccione un archivo Excel (.xlsx, .xls) para el Registro SAINT.")
                return
            self.ruta_original_registro_saint = file_path
            card_instance.set_enabled_import(False)
            worker = SaintWorker(file_path=file_path)

            worker.signals.finished.connect(
                lambda csv_path: self._on_conversion_finished(
                    csv_path, card_widget, icon_label, title_label, card_title, card_instance
                )
            )
            worker.signals.error.connect(
                lambda error_msg: self._on_conversion_error(error_msg, card_instance)
            )

            self.thread_pool.start(worker)
        
        else:
            print(f"Importación simple para: {card_title}")
            self._update_card_ui_to_success(card_widget, icon_label, title_label, card_title)

    def _on_conversion_finished(self, csv_path: str, card_widget: QWidget, icon_label: QLabel, title_label: QLabel, card_title: str, card_instance: 'ImportFileCard', resumen: dict = None):
        card_instance.set_enabled_import(True) 
        if card_title == "Estado de Cuenta":
            self.ruta_csv_estado_cuenta = csv_path
            if resumen:
                self.resumen_bancario = resumen
        elif card_title == "Libro de Venta":
            self.ruta_csv_libro_ventas = csv_path
        elif card_title == "Registro SAINT":
            self.ruta_csv_registro_saint = csv_path

        self._actualizar_estado_boton_conciliar()
        self._update_card_ui_to_success(card_widget, icon_label, title_label, card_title)

    def _on_conversion_error(self, error_msg: str, card_instance: 'ImportFileCard'):
        card_instance.set_enabled_import(True) 
        self._actualizar_estado_boton_conciliar()
        QMessageBox.critical(self, "Error de Conversión", error_msg)

    def _update_card_ui_to_success(self, card_widget: QWidget, icon_label: QLabel, title_label: QLabel, card_title: str):
        card_widget.setObjectName("ImportCardWidgetSuccess") 
        title_label.setObjectName("title_label_success") 
        card_widget.style().polish(card_widget)
        title_label.style().polish(title_label)

        icon_size = QSize(80, 80)
        icon_pair = self.ICON_MAP.get(card_title, ("default.svg", "check_circle.svg"))
        success_icon_name = icon_pair[1]
        success_icon_path = os.path.join(ASSETS_PATH, "icons", f"{success_icon_name}")
        pixmap = QPixmap(success_icon_path)
        icon_label.setPixmap(pixmap.scaled(icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def _create_import_card(self, title):
        icon_pair = self.ICON_MAP.get(title, ("default.svg", "check_circle.svg"))
        file_filter = self.FILE_FILTERS.get(title, "Todos los Archivos (*.*)")
        
        card = ImportFileCard(
            title=title, 
            icon_pair=icon_pair, 
            file_filter=file_filter,
            parent=self 
        )
        
        card.import_triggered.connect(
            lambda file_path, widget, icon, title_lbl, card_title: 
            self._handle_import_logic(file_path, widget, icon, title_lbl, card_title, card)
        )
        return card

    def _actualizar_estado_boton_conciliar(self):
        archivos_listos = (self.ruta_csv_estado_cuenta is not None and 
                          self.ruta_csv_registro_saint is not None and 
                          self.ruta_csv_libro_ventas is not None)
        
        self.btn_conciliar.setEnabled(archivos_listos)
        
        if archivos_listos:
            self.btn_conciliar.setText("Conciliar")
            self.btn_conciliar.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_conciliar.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFD700, stop:1 #FFC107);
                    color: #000000;
                    border: 2px solid #FFFFFF;
                    border-radius: 12px;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 10px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4CAF50, stop:1 #45a049);
                    color: white;
                    border: 2px solid #81C784;
                }
                QPushButton:pressed {
                    background-color: #388E3C;
                    color: white;
                }
            """)
        else:
            self.btn_conciliar.setText("Conciliar")
            self.btn_conciliar.setCursor(Qt.CursorShape.ForbiddenCursor)
            self.btn_conciliar.setStyleSheet("""
                QPushButton {
                    background-color: #2C2C2C;
                    color: #7F7F7F;
                    border: 1px solid #444444;
                    border-radius: 12px;
                    font-size: 16px;
                    padding: 10px;
                }
            """)

    def _create_registros_view(self) -> QWidget:
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget) 
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_widget.setObjectName("MainContentWidget") 
        
        # Title for the conciliación view (matches RecordsTitle style used elsewhere)
        title = QLabel("Conciliación")
        title.setObjectName("RecordsTitle")
        title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)

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
        
        self.btn_conciliar = QPushButton("Conciliar")
        self.btn_conciliar.setObjectName("ConciliarButton")
        self.btn_conciliar.setFixedSize(200, 45) 
        self.btn_conciliar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_conciliar.setEnabled(False) 
        self.btn_conciliar.clicked.connect(self._iniciar_proceso_conciliacion)

        conciliar_container = QWidget()
        conciliar_layout = QHBoxLayout(conciliar_container)
        conciliar_layout.setContentsMargins(0, 0, 0, 0)
        conciliar_layout.addStretch()
        conciliar_layout.addWidget(self.btn_conciliar)
        conciliar_layout.addStretch()
        content_layout.addWidget(conciliar_container)
        content_layout.addStretch()
        return content_widget

    def _iniciar_proceso_conciliacion(self):
        """
        Verifica, carga los archivos CSV, ejecuta la conciliación en segundo plano
        y muestra los resultados directamente.
        """
        if not all([self.ruta_csv_estado_cuenta, self.ruta_csv_registro_saint, self.ruta_csv_libro_ventas]):
            QMessageBox.warning(self, "Archivos Faltantes", "Asegúrese de haber importado correctamente los tres archivos: 'Estado de Cuenta', 'Libro de Venta' y 'Registro SAINT'.")
            return

        try:
                                                                                        
            saved_files_data = self._save_conciliation_files()
                                                                                                                  
            self.registros_window_new.add_conciliation_record(saved_files_data)

                                                                
            df_banco = pd.read_csv(self.ruta_csv_estado_cuenta, encoding='utf-8-sig')
            df_ventas = pd.read_csv(self.ruta_csv_libro_ventas, encoding='utf-8-sig', sep=';')
            df_saint = pd.read_csv(self.ruta_csv_registro_saint, encoding='utf-8-sig')

                                               
                                                       
            self.btn_conciliar.setEnabled(False)
            self.btn_conciliar.setText("Procesando...")
            
            worker = ConciliacionWorker(df_banco, df_ventas, df_saint)
            worker.signals.finished.connect(self._on_conciliacion_finished)
            worker.signals.error.connect(self._on_conciliacion_error)
            
            self.thread_pool.start(worker)

        except Exception as e:
            self.btn_conciliar.setEnabled(True)
            self.btn_conciliar.setText("Conciliar")
            QMessageBox.critical(self, "Error en Conciliación", f"Ocurrió un error al iniciar el proceso:\n\n{e}")
            import traceback
            traceback.print_exc()

    def _on_conciliacion_finished(self, df_resultado):
        self.btn_conciliar.setEnabled(True)
        self.btn_conciliar.setText("Conciliar")
                                                  
        self.df_resultado_conciliacion = df_resultado
                                                                       
        ruta_guardado = None
        if self.ultimo_timestamp:
            try:
                base_storage_path = os.path.join(BASE_PATH, "../../data_files/conciliaciones", self.ultimo_timestamp)
                os.makedirs(base_storage_path, exist_ok=True)
                                        
                reportes_path = os.path.join(base_storage_path, "reportes")
                os.makedirs(reportes_path, exist_ok=True)
                                                                                          
                excel_path = os.path.join(reportes_path, "Conciliacion_Completa.xlsx")
                                                  
                df_resultado.to_excel(excel_path, index=False)
                print(f"✅ Conciliación guardada automáticamente en: {excel_path}")
                ruta_guardado = base_storage_path
                                                  
                self._guardar_reportes_automaticamente(df_resultado, reportes_path)
                
            except Exception as e:
                print(f"❌ Error al guardar Excel automático: {e}")
                import traceback
                traceback.print_exc()
                                                                     
            try:
                updated_files_data = {
                    "timestamp": self.ultimo_timestamp,
                    "estado_cuenta": os.path.abspath(os.path.join(base_storage_path, "archivos_procesados", "Estado_Cuenta.csv")) if os.path.exists(os.path.join(base_storage_path, "archivos_procesados", "Estado_Cuenta.csv")) else None,
                    "libro_ventas": os.path.abspath(os.path.join(base_storage_path, "archivos_procesados", "Libro_Ventas.csv")) if os.path.exists(os.path.join(base_storage_path, "archivos_procesados", "Libro_Ventas.csv")) else None,
                    "registro_saint": os.path.abspath(os.path.join(base_storage_path, "archivos_procesados", "Registro_Saint.csv")) if os.path.exists(os.path.join(base_storage_path, "archivos_procesados", "Registro_Saint.csv")) else None,
                    "informe": os.path.abspath(os.path.join(base_storage_path, "reportes", "Conciliacion_Completa.xlsx")) if os.path.exists(os.path.join(base_storage_path, "reportes", "Conciliacion_Completa.xlsx")) else None,
                    "path_root": os.path.abspath(base_storage_path),
                    "notas": os.path.abspath(os.path.join(base_storage_path, "notas", "Notas_Conciliacion.pdf")) if os.path.exists(os.path.join(base_storage_path, "notas", "Notas_Conciliacion.pdf")) else None
                }
                                                                                          
                if hasattr(self.registros_window_new, 'update_conciliation_record'):
                    self.registros_window_new.update_conciliation_record(updated_files_data)
                else:
                                                                                 
                    self.registros_window_new.add_conciliation_record(updated_files_data)
            except Exception:
                pass

        # Nota: ya no mostramos un diálogo de éxito. Si la conciliación fue
        # exitosa, se pasa directamente a la ventana de resultados.
        
        self.ventana_resultados_actual = VentanaResultados(df_resultado, self.resumen_bancario, ruta_guardado=ruta_guardado)
        self.ventana_resultados_actual.closed.connect(self.show)
        self.ventana_resultados_actual.showMaximized()
        self.hide()

    def _on_conciliacion_error(self, error_msg):
        self.btn_conciliar.setEnabled(True)
        self.btn_conciliar.setText("Conciliar")
        QMessageBox.critical(self, "Error de Conciliación", error_msg)

    def _save_conciliation_files(self) -> dict:
        from src.logic.settings import load_credentials
        
        saved_username, _ = load_credentials()
        username_str = saved_username if saved_username else "desconocido"
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder_name = f"{timestamp}_{username_str}"
        
        base_storage_path = os.path.join(BASE_PATH, "../../data_files/conciliaciones", folder_name)
        
                                      
        procesados_path = os.path.join(base_storage_path, "archivos_procesados")
        originales_path = os.path.join(base_storage_path, "archivos_originales")
        
        os.makedirs(base_storage_path, exist_ok=True)
        os.makedirs(procesados_path, exist_ok=True)
        os.makedirs(originales_path, exist_ok=True)
        
                                                                    
        dest_estado = shutil.copy2(self.ruta_csv_estado_cuenta, os.path.join(procesados_path, "Estado_Cuenta.csv"))
        dest_ventas = shutil.copy2(self.ruta_csv_libro_ventas, os.path.join(procesados_path, "Libro_Ventas.csv"))
        dest_saint = shutil.copy2(self.ruta_csv_registro_saint, os.path.join(procesados_path, "Registro_Saint.csv"))
        
                                                                         
        if self.ruta_original_estado_cuenta and os.path.exists(self.ruta_original_estado_cuenta):
            nombre_orig = os.path.basename(self.ruta_original_estado_cuenta)
            shutil.copy2(self.ruta_original_estado_cuenta, os.path.join(originales_path, nombre_orig))
            
        if self.ruta_original_libro_ventas and os.path.exists(self.ruta_original_libro_ventas):
            nombre_orig = os.path.basename(self.ruta_original_libro_ventas)
            shutil.copy2(self.ruta_original_libro_ventas, os.path.join(originales_path, nombre_orig))
            
        if self.ruta_original_registro_saint and os.path.exists(self.ruta_original_registro_saint):
            nombre_orig = os.path.basename(self.ruta_original_registro_saint)
            shutil.copy2(self.ruta_original_registro_saint, os.path.join(originales_path, nombre_orig))
        
                                                                                
        self.ultimo_timestamp = folder_name

        return {
            "timestamp": folder_name,
            "estado_cuenta": dest_estado,
            "libro_ventas": dest_ventas,
            "registro_saint": dest_saint,
            "path_root": base_storage_path,
            "user": username_str
        }

    def _guardar_reportes_automaticamente(self, df_resultado, ruta_guardado):

        try:
            reportes_guardados = []
            
                                                                                 
            nc = df_resultado[df_resultado['Abono'] > 0].copy()
            nc_conciliadas = nc[nc['Estado'].str.contains('Conciliado', na=False)]
            nc_no_conciliadas = nc[~nc['Estado'].str.contains('Conciliado', na=False)]
            
            nd = df_resultado[df_resultado['Cargo'] > 0].copy()
            nd_conciliadas = nd[nd['Estado'].str.contains('Conciliado', na=False)]
            nd_no_conciliadas = nd[~nd['Estado'].str.contains('Conciliado', na=False)]
                                                                                                               
            meses = {
                1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
                5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
                9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
            }
            
            ahora = datetime.datetime.now()
            dia = ahora.day
            mes = meses[ahora.month]
            anio = ahora.year
            hora = ahora.strftime("%H%M%S")
            
            nombre_pdf = f"Reporte {dia} de {mes} {anio} - {hora}.pdf"
            ruta_pdf = os.path.join(ruta_guardado, nombre_pdf)
            
                                                                                                   
            from src.gui.ventana_reportes import VentanaReporte
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.units import inch
            
                                                                      
            doc = SimpleDocTemplate(ruta_pdf, pagesize=letter)
            elementos = []
            estilos = getSampleStyleSheet()
            
                                
            estilo_titulo = ParagraphStyle(
                'CustomTitle',
                parent=estilos['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#0078D4'),
                spaceAfter=30,
                alignment=1
            )
            
                    
            elementos.append(Paragraph("REPORTE GENERAL BANCARIO", estilo_titulo))
            elementos.append(Spacer(1, 0.3 * inch))
            
                                   
            stats = {
                'nc_conciliadas_cant': len(nc_conciliadas),
                'nc_conciliadas_monto': nc_conciliadas['Abono'].sum(),
                'nc_no_conciliadas_cant': len(nc_no_conciliadas),
                'nc_no_conciliadas_monto': nc_no_conciliadas['Abono'].sum(),
                'nc_total_cant': len(nc),
                'nc_total_monto': nc['Abono'].sum(),
                'nd_conciliadas_cant': len(nd_conciliadas),
                'nd_conciliadas_monto': nd_conciliadas['Cargo'].sum(),
                'nd_no_conciliadas_cant': len(nd_no_conciliadas),
                'nd_no_conciliadas_monto': nd_no_conciliadas['Cargo'].sum(),
                'nd_total_cant': len(nd),
                'nd_total_monto': nd['Cargo'].sum(),
            }
            
            def formatear_monto(monto):
                try:
                    return f"{monto:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                except:
                    return "0,00"
            
                                                   
            elementos.append(Paragraph("<b>Resultados de la Conciliación</b>", estilos['Heading2']))
            elementos.append(Spacer(1, 0.2 * inch))
            
            datos_conciliacion = [
                ['', 'Cantidad', 'Monto'],
                ['Notas de Crédito', str(stats['nc_total_cant']), 
                 formatear_monto(stats['nc_total_monto'])],
                ['  Partidas Conciliadas', str(stats['nc_conciliadas_cant']), 
                 formatear_monto(stats['nc_conciliadas_monto'])],
                ['  Partidas No Conciliadas', str(stats['nc_no_conciliadas_cant']), 
                 formatear_monto(stats['nc_no_conciliadas_monto'])],
                ['Total Notas de Crédito', str(stats['nc_total_cant']), 
                 formatear_monto(stats['nc_total_monto'])],
                ['', '', ''],
                ['Notas de Débito', str(stats['nd_total_cant']), 
                 formatear_monto(stats['nd_total_monto'])],
                ['  Partidas Conciliadas', str(stats['nd_conciliadas_cant']), 
                 formatear_monto(stats['nd_conciliadas_monto'])],
                ['  Partidas No Conciliadas', str(stats['nd_no_conciliadas_cant']), 
                 formatear_monto(stats['nd_no_conciliadas_monto'])],
                ['Total Notas de Débito', str(stats['nd_total_cant']), 
                 formatear_monto(stats['nd_total_monto'])],
            ]
            
            tabla_conc = Table(datos_conciliacion, colWidths=[4*inch, 1.2*inch, 1.5*inch])
            tabla_conc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C2C2C')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#D4AF37')),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('ALIGN', (1, 1), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
                ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold'),
                ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
                ('FONTNAME', (0, 9), (-1, 9), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F5F5F5')),
                ('BACKGROUND', (0, 2), (-1, 2), colors.white),
                ('BACKGROUND', (0, 3), (-1, 3), colors.white),
                ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#F5F5F5')),
                ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor('#F5F5F5')),
                ('BACKGROUND', (0, 7), (-1, 7), colors.white),
                ('BACKGROUND', (0, 8), (-1, 8), colors.white),
                ('BACKGROUND', (0, 9), (-1, 9), colors.HexColor('#F5F5F5')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elementos.append(tabla_conc)
            elementos.append(Spacer(1, 0.4 * inch))
            
                                                             
            elementos.append(Paragraph("<b>Resumen del Estado de Cuenta (Banco)</b>", estilos['Heading2']))
            elementos.append(Spacer(1, 0.2 * inch))
            
            if self.resumen_bancario:
                datos_banco = [
                    ['', 'Cantidad', 'Monto'],
                    ['Saldo Mes Anterior', '', self.resumen_bancario.get('saldo_mes_anterior', '0,00')],
                    ['Notas de Crédito', str(self.resumen_bancario.get('notas_credito_cantidad', 0)), 
                     self.resumen_bancario.get('notas_credito_monto', '0,00')],
                    ['Notas de Débito', str(self.resumen_bancario.get('notas_debito_cantidad', 0)), 
                     self.resumen_bancario.get('notas_debito_monto', '0,00')],
                    ['Saldo Final del Mes', '', self.resumen_bancario.get('saldo_final_mes', '0,00')],
                ]
                
                tabla_banco = Table(datos_banco, colWidths=[4*inch, 1*inch, 1.5*inch])
                tabla_banco.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C2C2C')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#D4AF37')),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('ALIGN', (1, 1), (2, -1), 'CENTER'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, 1), colors.white),
                    ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F5F5F5')),
                    ('BACKGROUND', (0, 3), (-1, 3), colors.white),
                    ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#F5F5F5')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                elementos.append(tabla_banco)
            
                           
            elementos.append(Spacer(1, 0.5 * inch))
            elementos.append(Paragraph(
                f"<i>Reporte generado el {dia} de {mes} de {anio}</i>",
                estilos['Normal']
            ))
            
            # Try to draw the provided logo on each page (top-right corner).
            logo_path = os.path.join(ASSETS_PATH, "icons", "pio_12_icon.png")

            def _draw_logo(canvas_obj, doc_obj):
                try:
                    page_w, page_h = doc_obj.pagesize
                    margin = 36

                    # Draw header text (left/top)
                    try:
                        from reportlab.pdfbase.pdfmetrics import stringWidth
                        title = "Unidad Educativa Colegio Salesiano Pio XII"
                        rif = "RIF: 309755188"
                        title_font = "Helvetica-Bold"
                        title_size = 14
                        rif_font = "Helvetica"
                        rif_size = 10

                        # y coordinate for header text (a bit below top edge)
                        header_y = page_h - margin / 2

                        canvas_obj.setFont(title_font, title_size)
                        canvas_obj.setFillColorRGB(0, 0, 0)
                        x_title = margin
                        canvas_obj.drawString(x_title, header_y, title)

                        # draw RIF to the right of title
                        title_w = stringWidth(title, title_font, title_size)
                        x_rif = x_title + title_w + 12
                        canvas_obj.setFont(rif_font, rif_size)
                        canvas_obj.drawString(x_rif, header_y + 2, rif)
                    except Exception:
                        # If any failure drawing text, continue (non-fatal)
                        pass

                    # Draw logo at top-right
                    if os.path.exists(logo_path):
                        # size in points (72 pts = 1 inch)
                        logo_w = 72
                        logo_h = 72
                        x = page_w - logo_w - margin
                        y = page_h - logo_h - margin
                        canvas_obj.drawImage(logo_path, x, y, width=logo_w, height=logo_h, mask='auto')
                except Exception as e:
                    print(f"Advertencia al dibujar logo/encabezado en PDF: {e}")

            doc.build(elementos, onFirstPage=_draw_logo, onLaterPages=_draw_logo)
            reportes_guardados.append(f"📄 {nombre_pdf}")
            print(f"✅ PDF general guardado: {nombre_pdf}")
            
                                                            
            reportes_especificos = [
                (nc_conciliadas, "Notas de Crédito Conciliadas"),
                (nc_no_conciliadas, "Notas de Crédito NO Conciliadas"),
                (nd_conciliadas, "Notas de Débito Conciliadas"),
                (nd_no_conciliadas, "Notas de Débito NO Conciliadas")
            ]
            
            for df, titulo in reportes_especificos:
                if not df.empty:
                                                
                    nombre_limpio = "".join(c for c in titulo if c.isalnum() or c in (' ', '_', '-')).strip()
                    nombre_excel = f"{nombre_limpio}.xlsx"
                    ruta_excel = os.path.join(ruta_guardado, nombre_excel)
                    df.to_excel(ruta_excel, index=False)
                    reportes_guardados.append(f"📊 {nombre_excel}")
                    print(f"✅ Excel guardado: {nombre_excel}")
            
            print(f"✅ TOTAL: {len(reportes_guardados)} reportes guardados automáticamente")
            print(f"📁 Ubicación: {ruta_guardado}")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ Error al guardar reportes automáticamente: {e}")


    def _generar_pdf_reporte(self):
        """Genera el reporte PDF de la conciliación."""
        try:
            if self.df_resultado_conciliacion is None or self.ultimo_timestamp is None:
                return
            
                                       
            base_storage_path = os.path.join(BASE_PATH, "../../data_files/conciliaciones", self.ultimo_timestamp)
            pdf_path = os.path.join(base_storage_path, "Reporte_Conciliacion.pdf")
            
                            
            generador = ReportePDFGenerator(
                df_resultado=self.df_resultado_conciliacion,
                output_path=pdf_path,
                timestamp=self.ultimo_timestamp
            )
            
            if generador.generar():
                pass
                
        except Exception as e:
            import traceback
            traceback.print_exc()
