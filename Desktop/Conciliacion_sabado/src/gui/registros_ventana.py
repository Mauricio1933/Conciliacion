from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy,
    QPushButton, QHBoxLayout, QMessageBox, QScrollArea, QStackedWidget, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QCursor
import os
import datetime
import subprocess
try:
    import win32com.client
except ImportError:
    win32com = None

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.abspath(os.path.join(BASE_PATH, "../../assets"))

class RegistrosWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ContentArea")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QWidget#ContentArea { border-radius: 0px; }")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        self.grid_page = self._create_grid_page()
        self.details_page = self._create_details_page()
        self.reports_page = self._create_reports_page()
        self.processed_page = self._create_processed_page()
        self.originals_page = self._create_originals_page()
        self.notes_page = self._create_notes_page()
        
        self.stacked_widget.addWidget(self.grid_page)
        self.stacked_widget.addWidget(self.details_page)
        self.stacked_widget.addWidget(self.reports_page)
        self.stacked_widget.addWidget(self.processed_page)
        self.stacked_widget.addWidget(self.originals_page)
        self.stacked_widget.addWidget(self.notes_page)
        
        self.records_data = [] 
        self.current_record_path = None

    def _create_grid_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(15)
        
        title_label = QLabel("Registros")
        title_label.setObjectName("RecordsTitle")
        title_label.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        layout.addSpacing(20)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background: transparent; border: none;")
        
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        
                                                                                   
        container_layout = QVBoxLayout(self.grid_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        self.grid_layout = QGridLayout()
                                                         
        self.grid_layout.setVerticalSpacing(25) 
        self.grid_layout.setHorizontalSpacing(20)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
                                                 
        for col in range(4):
            self.grid_layout.setColumnStretch(col, 1)
            
        container_layout.addLayout(self.grid_layout)
        container_layout.addStretch()                            
        
        scroll_area.setWidget(self.grid_container)
        layout.addWidget(scroll_area)
        
        self.no_records_label = QLabel("")
        self.no_records_label.setObjectName("NoUsersLabel")
        self.no_records_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_records_label.setFont(QFont("Inter", 12))
        layout.addWidget(self.no_records_label)
        
        return page

    def _create_details_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        
        back_btn = QPushButton("← Volver")
        back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 16px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #FFD700;
            }
        """)
        back_btn.clicked.connect(self._show_grid_view)
        header_layout.addWidget(back_btn)
        
        self.details_title = QLabel("Detalle de Conciliación")
        self.details_title.setObjectName("RecordsTitle")
        self.details_title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        header_layout.addWidget(self.details_title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        self.details_content_layout = QVBoxLayout()
        self.details_content_layout.setSpacing(15)
        self.details_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        layout.addLayout(self.details_content_layout)
        layout.addStretch()
        
        return page

    def _create_reports_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        back_btn = QPushButton("← Volver a Detalles")
        back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 16px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #FFD700;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.details_page))
        header_layout.addWidget(back_btn)
        
        title = QLabel("Reportes Guardados")
        title.setObjectName("RecordsTitle")
        title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background: transparent; border: none;")
        
        self.reports_container = QWidget()
        self.reports_container.setStyleSheet("background: transparent;")
        self.reports_layout = QVBoxLayout(self.reports_container)
        self.reports_layout.setSpacing(15)
        self.reports_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.reports_container)
        layout.addWidget(scroll_area)
        
        return page

    def _create_processed_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        back_btn = QPushButton("← Volver a Detalles")
        back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 16px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #FFD700;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.details_page))
        header_layout.addWidget(back_btn)
        
        title = QLabel("Archivos Procesados (CSV)")
        title.setObjectName("RecordsTitle")
        title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background: transparent; border: none;")
        
        self.processed_container = QWidget()
        self.processed_container.setStyleSheet("background: transparent;")
        self.processed_layout = QVBoxLayout(self.processed_container)
        self.processed_layout.setSpacing(15)
        self.processed_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.processed_container)
        layout.addWidget(scroll_area)
        
        return page

    def _create_originals_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        back_btn = QPushButton("← Volver a Detalles")
        back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 16px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #FFD700;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.details_page))
        header_layout.addWidget(back_btn)
        
        title = QLabel("Archivos Originales")
        title.setObjectName("RecordsTitle")
        title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background: transparent; border: none;")
        
        self.originals_container = QWidget()
        self.originals_container.setStyleSheet("background: transparent;")
        self.originals_layout = QVBoxLayout(self.originals_container)
        self.originals_layout.setSpacing(15)
        self.originals_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.originals_container)
        layout.addWidget(scroll_area)
        
        return page

    def add_conciliation_record(self, files_data: dict):
        if self.no_records_label.isVisible():
            self.no_records_label.setVisible(False)
            self.main_layout.removeWidget(self.no_records_label) 

                                                                     
        num_columns = 4
        row = len(self.records_data) // num_columns
        col = len(self.records_data) % num_columns
        
        record_widget = self._create_grid_item(files_data)
        self.grid_layout.addWidget(record_widget, row, col)
        
        self.records_data.append(files_data)

    def update_conciliation_record(self, files_data: dict):
        ts = files_data.get('timestamp')
        if not ts:
                                                   
            self.add_conciliation_record(files_data)
            return

                                 
        found = False
        for i, rec in enumerate(self.records_data):
            if rec.get('timestamp') == ts:
                            
                self.records_data[i] = files_data
                found = True
                break

        if not found:
            self.records_data.append(files_data)

                                                                     
        self._rebuild_grid()

    def _rebuild_grid(self):
                      
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

                                              
        num_columns = 4
        for idx, files_data in enumerate(self.records_data):
            row = idx // num_columns
            col = idx % num_columns
            record_widget = self._create_grid_item(files_data)
            self.grid_layout.addWidget(record_widget, row, col)

    def _convertir_fecha_texto(self, timestamp_str):
        try:
                                        
            clean_ts = timestamp_str.replace("-", "").replace("_", "").replace(" ", "")
                                                      
            if len(clean_ts) >= 8:
                year = int(clean_ts[0:4])
                month = int(clean_ts[4:6])
                day = int(clean_ts[6:8])
                
                meses = {
                    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
                    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
                    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
                }
                
                return f"{day} de {meses.get(month, 'mes')}"
        except:
            pass
        return timestamp_str           

    def _create_grid_item(self, files_data: dict) -> QWidget:
        container = QFrame()
        container.setObjectName("RecordGridItem")
        container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        container.setFrameShape(QFrame.Shape.NoFrame)
                                                                             
        container.setFixedSize(320, 100)
        container.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        container.setStyleSheet("""
            QFrame#RecordGridItem {
                background-color: #181A20;
                border: 2px solid #F2CD55;
                border-radius: 12px;
            }
            QFrame#RecordGridItem:hover {
                background-color: #1E242E;
                border: 2px solid #FFD700;
            }
        """)
        
                                                            
        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
                                 
        icon_label = QLabel()
        icon_label.setObjectName("CardIconLabel")
        icon_path = os.path.join(ASSETS_PATH, "icons", "conciliacion_icon.svg")
        
                                  
        icon_size = 50
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(QSize(icon_size, icon_size), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setText("📊")
            icon_label.setFont(QFont("Inter", 30))
        layout.addWidget(icon_label)
        
                                              
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
                                                        
        title_label = QLabel("Registro de conciliacion:")
        title_label.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #FFD700;")         

                                                                              
        timestamp = files_data.get("timestamp", "")
        user_name = files_data.get("user")
        if not user_name and timestamp and "_" in timestamp:
                                                          
            try:
                user_name = timestamp.split("_")[-1]
            except:
                user_name = "desconocido"

        admin_label = QLabel(user_name if user_name else "desconocido")
        admin_label.setFont(QFont("Inter", 11, QFont.Weight.Normal))
        admin_label.setStyleSheet("color: #FFFFFF;")

                                         
        fecha_texto = self._convertir_fecha_texto(timestamp)
        date_label = QLabel(fecha_texto)
        date_label.setFont(QFont("Inter", 13, QFont.Weight.Normal))
        date_label.setStyleSheet("color: #FFFFFF;")         

        text_layout.addWidget(title_label)
        text_layout.addWidget(admin_label)
        text_layout.addWidget(date_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()                              
        
        container.mousePressEvent = lambda event: self._show_details_view(files_data)
        
        return container

    def _show_grid_view(self):
        self.stacked_widget.setCurrentWidget(self.grid_page)

    def _show_details_view(self, files_data: dict):
        while self.details_content_layout.count():
            item = self.details_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        timestamp = files_data.get("timestamp", "")
        self.details_title.setText(f"Conciliación: {timestamp}")
        
                              
        self.current_record_path = files_data.get("path_root")
        
        if not self.current_record_path:
            for key in ["informe", "estado_cuenta", "libro_ventas", "registro_saint"]:
                p = files_data.get(key)
                if p and os.path.exists(p):
                    d = os.path.dirname(p)
                    basename = os.path.basename(d)
                    if basename in ["reportes", "archivos_procesados", "archivos_originales", "notas"]:
                        self.current_record_path = os.path.dirname(d)
                    else:
                        self.current_record_path = d
                    break
        
                  
        if not self.current_record_path or not os.path.exists(self.current_record_path):
            base_storage = os.path.join(BASE_PATH, "../../data_files/conciliaciones", timestamp)
            if os.path.exists(base_storage):
                self.current_record_path = os.path.abspath(base_storage)
        
        if self.current_record_path and os.path.exists(self.current_record_path):
                                    
            originales_dir = os.path.join(self.current_record_path, "archivos_originales")
            if os.path.exists(originales_dir) and os.listdir(originales_dir):
            
                self._add_submenu_button("Archivos Originales", "Ver archivos fuente (PDF/Excel)", "file_icon.svg", self._show_original_files_view)
            
                                           
            procesados_dir = os.path.join(self.current_record_path, "archivos_procesados")
            legacy_csvs = ["Estado_Cuenta.csv", "Libro_Ventas.csv", "Registro_Saint.csv"]
            has_legacy_csvs = any(os.path.exists(os.path.join(self.current_record_path, f)) for f in legacy_csvs)
            
            if (os.path.exists(procesados_dir) and os.listdir(procesados_dir)) or has_legacy_csvs:
           
                self._add_submenu_button("Archivos Procesados", "Ver archivos convertidos a CSV", "gear_icon.svg", self._show_processed_files_view)

                                                             
            notas_dir = os.path.join(self.current_record_path, "notas")
            notas_pdf_path = os.path.join(notas_dir, "Notas_Conciliacion.pdf")
            legacy_notas = os.path.join(self.current_record_path, "Notas_Conciliacion.pdf")
            
            final_notas_path = None
            if os.path.exists(notas_pdf_path):
                final_notas_path = notas_pdf_path
            elif os.path.exists(legacy_notas):
                final_notas_path = legacy_notas
                
            if final_notas_path:
                self._add_submenu_button("Notas", "Ver notas (PDF + TXT)", "note_icon.svg", self._show_notes_view)
            
                                   
            reportes_dir = os.path.join(self.current_record_path, "reportes")
            has_reports = False
            
            if os.path.exists(reportes_dir):
                if any(f.endswith(".xlsx") or f.endswith(".pdf") for f in os.listdir(reportes_dir)):
                    has_reports = True
            
                                              
            if not has_reports:
                ignored_files = ["Estado_Cuenta.csv", "Libro_Ventas.csv", "Registro_Saint.csv", "Notas_Conciliacion.pdf"]
                try:
                    for f in os.listdir(self.current_record_path):
                         if os.path.isfile(os.path.join(self.current_record_path, f)):
                            if (f.endswith(".xlsx") or f.endswith(".pdf")) and f not in ignored_files:
                                has_reports = True
                                break
                except: pass

            if has_reports:
              
                self._add_submenu_button("Reportes Guardados", "Ver reportes generados", "folder_icon.svg", self._show_reports_view)
        
        self.stacked_widget.setCurrentWidget(self.details_page)

    def _add_submenu_button(self, title, description, icon_char, callback):
        widget = QWidget()
        widget.setObjectName("ThinRectangle")
        widget.setFixedHeight(80)
        widget.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 10, 20, 10)
        
 
        icon_label = QLabel()
        if isinstance(icon_char, str) and icon_char.lower().endswith('.svg'):
            icon_path = os.path.join(ASSETS_PATH, "icons", icon_char)
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                icon_label.setPixmap(pixmap.scaled(QSize(36, 36), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                icon_label.setText(icon_char)
                icon_label.setFont(QFont("Inter", 24))
        else:
            icon_label.setText(icon_char)
            icon_label.setFont(QFont("Inter", 24))
        layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 14px;")
        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(desc_lbl)
        layout.addLayout(text_layout)
        
        layout.addStretch()
        
        arrow_lbl = QLabel("➜")
        arrow_lbl.setFont(QFont("Inter", 16))
        arrow_lbl.setStyleSheet("color: white;")
        layout.addWidget(arrow_lbl)
        
        widget.mousePressEvent = lambda event: callback()
        
        self.details_content_layout.addWidget(widget)

    def _show_reports_view(self):
        while self.reports_layout.count():
            item = self.reports_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if not self.current_record_path or not os.path.exists(self.current_record_path):
            lbl = QLabel("No se encontró la carpeta de registros.")
            lbl.setStyleSheet("color: white; font-size: 14px;")
            self.reports_layout.addWidget(lbl)
            self.stacked_widget.setCurrentWidget(self.reports_page)
            return

        found_any = False
        
                                        
        reportes_dir = os.path.join(self.current_record_path, "reportes")
        if os.path.exists(reportes_dir):
            try:
                files = os.listdir(reportes_dir)
                files.sort()
                for f in files:
                    if f.endswith(".xlsx") or f.endswith(".pdf"):
                        full_path = os.path.join(reportes_dir, f)
                        self._add_report_item(f, full_path)
                        found_any = True
            except Exception as e:
                print(f"Error scanning reportes dir: {e}")

                                                   
        ignored_files = [
            "Estado_Cuenta.csv", 
            "Libro_Ventas.csv", 
            "Registro_Saint.csv", 
            "Notas_Conciliacion.pdf"
        ]
        
        try:
            files_root = os.listdir(self.current_record_path)
            files_root.sort()
            for f in files_root:
                if (f.endswith(".xlsx") or f.endswith(".pdf")) and f not in ignored_files:
                    full_path = os.path.join(self.current_record_path, f)
                    self._add_report_item(f, full_path)
                    found_any = True
        except Exception as e:
            print(f"Error scanning root dir: {e}")
            
        if not found_any:
            lbl = QLabel("No hay reportes adicionales guardados.")
            lbl.setStyleSheet("color: #AAAAAA; font-size: 14px; font-style: italic;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.reports_layout.addWidget(lbl)
            
        self.stacked_widget.setCurrentWidget(self.reports_page)

    def _create_notes_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        back_btn = QPushButton("← Volver a Detalles")
        back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 16px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #FFD700;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.details_page))
        header_layout.addWidget(back_btn)

        title = QLabel("Notas")
        title.setObjectName("RecordsTitle")
        title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background: transparent; border: none;")

        self.notes_container = QWidget()
        self.notes_container.setStyleSheet("background: transparent;")
        self.notes_layout = QVBoxLayout(self.notes_container)
        self.notes_layout.setSpacing(15)
        self.notes_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(self.notes_container)
        layout.addWidget(scroll_area)

        return page

    def _show_notes_view(self):
       
        while self.notes_layout.count():
            item = self.notes_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.current_record_path or not os.path.exists(self.current_record_path):
            lbl = QLabel("No se encontró la carpeta de registros.")
            lbl.setStyleSheet("color: white; font-size: 14px;")
            self.notes_layout.addWidget(lbl)
            self.stacked_widget.setCurrentWidget(self.notes_page)
            return

        notas_dir = os.path.join(self.current_record_path, "notas")
        notas_pdf_path = os.path.join(notas_dir, "Notas_Conciliacion.pdf")
        notas_txt_path = os.path.join(notas_dir, "notas_conciliacion.txt")

        legacy_pdf = os.path.join(self.current_record_path, "Notas_Conciliacion.pdf")
        legacy_txt = os.path.join(self.current_record_path, "notas_conciliacion.txt")

        items_found = False

 
        final_pdf = None
        if os.path.exists(notas_pdf_path):
            final_pdf = notas_pdf_path
        elif os.path.exists(legacy_pdf):
            final_pdf = legacy_pdf

        if final_pdf:
            self._add_note_item(os.path.basename(final_pdf), final_pdf)
            items_found = True

    
        final_txt = None
        if os.path.exists(notas_txt_path):
            final_txt = notas_txt_path
        elif os.path.exists(legacy_txt):
            final_txt = legacy_txt

        if final_txt:
            self._add_note_item(os.path.basename(final_txt), final_txt)
            items_found = True

        if not items_found:
            lbl = QLabel("No hay notas guardadas para este registro.")
            lbl.setStyleSheet("color: #AAAAAA; font-size: 14px; font-style: italic;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.notes_layout.addWidget(lbl)

        self.stacked_widget.setCurrentWidget(self.notes_page)

    def _add_note_item(self, filename, full_path):
    
        widget = QWidget()
        widget.setObjectName("ThinRectangle")
        widget.setFixedHeight(80)
        widget.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        widget.setStyleSheet("""
            QWidget#ThinRectangle {
                background-color: #181A20;
                border-radius: 15px;
                border: 1px solid #F2CD55;
            }
            QWidget#ThinRectangle:hover {
                background-color: #1E242E;
                border: 2px solid #FFD700;
            }
        """)

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 10, 20, 10)

        icon_label = QLabel()
        if filename.endswith('.pdf'):
            icon_name = "pdf_icon.svg"
        elif filename.endswith('.txt'):
            icon_name = "txt_icon.svg"
        else:
            icon_name = "conciliacion_icon.svg"

        icon_path = os.path.join(ASSETS_PATH, "icons", icon_name)
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(QSize(40, 40), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setText("📄" if filename.endswith('.pdf') else "📄")
            icon_label.setFont(QFont("Inter", 20))
        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        title = os.path.splitext(filename)[0].replace("_", " ")
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 14px;")

        path_lbl = QLabel(filename)
        path_lbl.setStyleSheet("color: #CCCCCC; font-size: 12px;")

        text_layout.addWidget(title_lbl)
        text_layout.addWidget(path_lbl)
        layout.addLayout(text_layout)

        layout.addStretch()

        print_btn = QPushButton()
        print_btn.setFixedSize(40, 40)
        print_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        print_btn.setToolTip("Imprimir archivo")
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: white;
                border: 1px solid #555;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                border: 1px solid #4CAF50;
            }
        """)
        # set svg icon if available
        print_icon_path = os.path.join(ASSETS_PATH, "icons", "print_icon.svg")
        if os.path.exists(print_icon_path):
            print_btn.setIcon(QIcon(print_icon_path))
            print_btn.setIconSize(QSize(20, 20))

        print_btn.clicked.connect(lambda checked=False: self._print_file(full_path))
        layout.addWidget(print_btn)

        open_lbl = QLabel()
        open_icon_path = os.path.join(ASSETS_PATH, "icons", "open_folder_icon.svg")
        if os.path.exists(open_icon_path):
            pixmap = QPixmap(open_icon_path)
            open_lbl.setPixmap(pixmap.scaled(QSize(20, 20), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            open_lbl.setText("📂")
            open_lbl.setFont(QFont("Inter", 16))
        layout.addWidget(open_lbl)

        widget.mousePressEvent = lambda event: self._open_file(full_path)

        self.notes_layout.addWidget(widget)

    def _add_report_item(self, filename, full_path):
        widget = QWidget()
        widget.setObjectName("ThinRectangle")
        widget.setFixedHeight(80)
        widget.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        widget.setStyleSheet("""
            QWidget#ThinRectangle {
                background-color: #181A20;
                border-radius: 15px;
                border: 1px solid #F2CD55;
            }
            QWidget#ThinRectangle:hover {
                background-color: #1E242E;
                border: 2px solid #FFD700;
            }
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 10, 20, 10)
        
        icon_label = QLabel()
        if filename.endswith('.pdf'):
            icon_name = "pdf_icon.svg"
        elif filename.endswith('.xlsx'):
            icon_name = "excel_icon.svg"
        else:
            icon_name = "conciliacion_icon.svg"
            
        icon_path = os.path.join(ASSETS_PATH, "icons", icon_name)
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(QSize(40, 40), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            if filename.endswith('.pdf'):
                icon_label.setText("📄")
            else:
                icon_label.setText("📊")
            icon_label.setFont(QFont("Inter", 20))
        layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        title = os.path.splitext(filename)[0].replace("_", " ")
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 14px;")
        
        path_lbl = QLabel(filename)
        path_lbl.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(path_lbl)
        layout.addLayout(text_layout)
        
        layout.addStretch()
        
                           
        print_btn = QPushButton()
        print_btn.setFixedSize(40, 40)
        print_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        print_btn.setToolTip("Imprimir archivo")
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: white;
                border: 1px solid #555;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                border: 1px solid #4CAF50;
            }
        """)
        # set svg icon if available
        print_icon_path = os.path.join(ASSETS_PATH, "icons", "print_icon.svg")
        if os.path.exists(print_icon_path):
            print_btn.setIcon(QIcon(print_icon_path))
            print_btn.setIconSize(QSize(20, 20))

        print_btn.clicked.connect(lambda checked=False: self._print_file(full_path))
        layout.addWidget(print_btn)
        
        open_lbl = QLabel()
        open_icon_path = os.path.join(ASSETS_PATH, "icons", "open_folder_icon.svg")
        if os.path.exists(open_icon_path):
            pixmap = QPixmap(open_icon_path)
            open_lbl.setPixmap(pixmap.scaled(QSize(20, 20), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            open_lbl.setText("📂")
            open_lbl.setFont(QFont("Inter", 16))
        layout.addWidget(open_lbl)
        
        widget.mousePressEvent = lambda event: self._open_file(full_path)
        
        self.reports_layout.addWidget(widget)

    def _print_file(self, file_path):
        """
        Abre el archivo e intenta mostrar el cuadro de diálogo de impresión 'de una'.
        Para Excel: Usa automatización COM.
        Para PDF/Otros: Abre el archivo y envía Ctrl+P mediante un script VBS temporal.
        """
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", "El archivo no existe.")
            return

        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == '.xlsx' and win32com:
                self._print_excel_with_dialog(file_path)
            else:
                self._print_generic_with_dialog_attempt(file_path)
                
        except Exception as e:
                                                                    
            print(f"Error al intentar abrir diálogo de impresión: {e}")
            os.startfile(file_path)

    def _print_excel_with_dialog(self, file_path):
        try:
                                                                               
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = True                                       
            
            wb = excel.Workbooks.Open(file_path)
                                                                                                               
            excel.Dialogs(8).Show()
                                                                                                                                                                                   
        except Exception as e:
            raise Exception(f"Error COM Excel: {e}")

    def _print_generic_with_dialog_attempt(self, file_path):
                                                                                            
        os.startfile(file_path)
                                                                                                                                                                     
        vbs_script = """
        WScript.Sleep 2000 
        Set WshShell = WScript.CreateObject("WScript.Shell")
        WshShell.SendKeys "^p"
        """
        
        vbs_path = os.path.join(os.environ["TEMP"], "print_shortcut_temp.vbs")
        
        try:
            with open(vbs_path, "w") as f:
                f.write(vbs_script)
            
                                                                                  
            subprocess.Popen(["wscript", vbs_path], shell=True)
            
        except Exception as e:
            print(f"No se pudo enviar el comando Ctrl+P: {e}")

    def _show_processed_files_view(self):
        while self.processed_layout.count():
            item = self.processed_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if not self.current_record_path or not os.path.exists(self.current_record_path):
            return

        found_any = False
        procesados_dir = os.path.join(self.current_record_path, "archivos_procesados")
        
                                                   
        if os.path.exists(procesados_dir):
            try:
                files = os.listdir(procesados_dir)
                files.sort()
                for f in files:
                    if f.endswith(".csv"):
                        self._add_file_item(f, os.path.join(procesados_dir, f), self.processed_layout, "csv_icon.svg")
                        found_any = True
            except Exception as e:
                print(f"Error scanning procesados dir: {e}")
        
                                 
        legacy_files = ["Estado_Cuenta.csv", "Libro_Ventas.csv", "Registro_Saint.csv"]
        for f in legacy_files:
            p = os.path.join(self.current_record_path, f)
            if os.path.exists(p):
                                                              
                if not os.path.exists(os.path.join(procesados_dir, f)):
                    self._add_file_item(f, p, self.processed_layout, "csv_icon.svg")
                    found_any = True
        
        if not found_any:
            lbl = QLabel("No hay archivos procesados.")
            lbl.setStyleSheet("color: #AAAAAA; font-size: 14px; font-style: italic;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.processed_layout.addWidget(lbl)
        
        self.stacked_widget.setCurrentWidget(self.processed_page)

    def _show_original_files_view(self):
        while self.originals_layout.count():
            item = self.originals_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if not self.current_record_path or not os.path.exists(self.current_record_path):
            return

        found_any = False
        originales_dir = os.path.join(self.current_record_path, "archivos_originales")
        
        if os.path.exists(originales_dir):
            try:
                files = os.listdir(originales_dir)
                files.sort()
                for f in files:
                    icon = "pdf_icon.svg" if f.endswith(".pdf") else "excel_icon.svg"
                    self._add_file_item(f, os.path.join(originales_dir, f), self.originals_layout, icon)
                    found_any = True
            except Exception as e:
                print(f"Error scanning originales dir: {e}")
        
        if not found_any:
            lbl = QLabel("No hay archivos originales guardados.")
            lbl.setStyleSheet("color: #AAAAAA; font-size: 14px; font-style: italic;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.originals_layout.addWidget(lbl)
            
        self.stacked_widget.setCurrentWidget(self.originals_page)

    def _add_file_item(self, filename, full_path, target_layout, icon_name="conciliacion_icon.svg"):
        widget = QWidget()
        widget.setObjectName("ThinRectangle")
        widget.setFixedHeight(80)
        widget.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        widget.setStyleSheet("""
            QWidget#ThinRectangle {
                background-color: #181A20;
                border-radius: 15px;
                border: 1px solid #F2CD55;
            }
            QWidget#ThinRectangle:hover {
                background-color: #1E242E;
                border: 2px solid #FFD700;
            }
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 10, 20, 10)
        
        icon_label = QLabel()
        icon_path = os.path.join(ASSETS_PATH, "icons", icon_name)
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(QSize(40, 40), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setText("📄")
            icon_label.setFont(QFont("Inter", 20))
        layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        title = os.path.splitext(filename)[0].replace("_", " ")
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 14px;")
        
        path_lbl = QLabel(filename)
        path_lbl.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(path_lbl)
        layout.addLayout(text_layout)
        
        layout.addStretch()
        
        open_lbl = QLabel()
        open_icon_path = os.path.join(ASSETS_PATH, "icons", "open_folder_icon.svg")
        if os.path.exists(open_icon_path):
            pixmap = QPixmap(open_icon_path)
            open_lbl.setPixmap(pixmap.scaled(QSize(20, 20), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            open_lbl.setText("📂")
            open_lbl.setFont(QFont("Inter", 16))
        layout.addWidget(open_lbl)
        
        widget.mousePressEvent = lambda event: self._open_file(full_path)
        
        target_layout.addWidget(widget)

    def _add_file_widget(self, title, file_path, icon_name):
        widget = QWidget()
        widget.setObjectName("ThinRectangle")
        widget.setFixedHeight(80)
        widget.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 10, 20, 10)
        
        icon_label = QLabel()
        if "pdf" in icon_name:
             real_icon = "pdf_icon.svg" 
        elif "excel" in icon_name:
             real_icon = "excel_icon.svg"
        else:
             real_icon = "conciliacion_icon.svg"

        icon_path = os.path.join(ASSETS_PATH, "icons", real_icon)
        if not os.path.exists(icon_path):
             icon_path = os.path.join(ASSETS_PATH, "icons", "conciliacion_icon.svg")

        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(QSize(40, 40), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setText("📄")
            icon_label.setFont(QFont("Inter", 20))
            
        layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 14px;")
        path_lbl = QLabel(os.path.basename(file_path) if file_path else "No disponible")
        path_lbl.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(path_lbl)
        layout.addLayout(text_layout)
        
        layout.addStretch()
        
        open_lbl = QLabel()
        open_icon_path = os.path.join(ASSETS_PATH, "icons", "open_folder_icon.svg")
        if os.path.exists(open_icon_path):
            pixmap = QPixmap(open_icon_path)
            open_lbl.setPixmap(pixmap.scaled(QSize(20, 20), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            open_lbl.setText("📂")
            open_lbl.setFont(QFont("Inter", 16))
        layout.addWidget(open_lbl)
        
        widget.mousePressEvent = lambda event: self._open_file(file_path)
        
        self.details_content_layout.addWidget(widget)

    def _open_file(self, file_path):
        if file_path and os.path.exists(file_path):
            try:
                os.startfile(file_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo abrir el archivo: {e}")
        else:
            QMessageBox.warning(self, "Error", "El archivo no existe o no se encuentra.")

    def load_records_from_disk(self, storage_path: str):
        if not os.path.exists(storage_path):
            return

        try:
            subdirs = [d for d in os.listdir(storage_path) if os.path.isdir(os.path.join(storage_path, d))]
            subdirs.sort(reverse=True)

            for timestamp in subdirs:
                record_path = os.path.abspath(os.path.join(storage_path, timestamp))
                
                estado_path = os.path.join(record_path, "Estado_Cuenta.csv")
                ventas_path = os.path.join(record_path, "Libro_Ventas.csv")
                saint_path = os.path.join(record_path, "Registro_Saint.csv")
                
                                                               
                reporte_path_root = os.path.join(record_path, "Conciliacion_Completa.xlsx")
                reporte_path_subdir = os.path.join(record_path, "reportes", "Conciliacion_Completa.xlsx")
                
                reporte_path = None
                if os.path.exists(reporte_path_subdir):
                    reporte_path = reporte_path_subdir
                elif os.path.exists(reporte_path_root):
                    reporte_path = reporte_path_root
                
                                                                           
                if any(os.path.exists(p) for p in [estado_path, ventas_path, saint_path]) or reporte_path:
                    files_data = {
                        "timestamp": timestamp,
                        "estado_cuenta": os.path.abspath(estado_path) if os.path.exists(estado_path) else None,
                        "libro_ventas": os.path.abspath(ventas_path) if os.path.exists(ventas_path) else None,
                        "registro_saint": os.path.abspath(saint_path) if os.path.exists(saint_path) else None,
                        "informe": os.path.abspath(reporte_path) if reporte_path else None
                    }
                    self.add_conciliation_record(files_data)
                    
        except Exception as e:
            print(f"Error loading records from disk: {e}")
