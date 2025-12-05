import sys
import pandas as pd
import json
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableWidget, QTableWidgetItem, QPushButton, QLabel, QFrame, 
                             QFileDialog, QMessageBox, QHeaderView, QAbstractItemView,
                             QComboBox, QLineEdit, QDateEdit, QCheckBox)
from PyQt6.QtCore import Qt, QEvent, pyqtSignal, QSize, QDate
from PyQt6.QtGui import QColor, QFont, QIcon

from src.gui.widgets.barra_custom import CustomTitleBar

from src.gui.dialogs.detalle_movimiento_dialog import DetalleMovimientoDialog
from src.gui.dialogs.tomar_nota_dialog import TomarNotaDialog

try:
    from src.logic.CONCILIACIONMAESTRA import ConciliacionMaestra
except ImportError:
    print("❌ ERROR CRÍTICO: No se encontró 'CONCILIACIONMAESTRA.py' en src/logic.")

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.abspath(os.path.join(BASE_PATH, "../../assets"))

class VentanaResultados(QWidget):
    windowStateChanged = pyqtSignal(Qt.WindowState)
    closed = pyqtSignal()

    def __init__(self, df_resultado, resumen_bancario=None, parent=None, ruta_guardado=None):
        super().__init__(parent)

                                                       
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("VentanaResultados")
        self.resize(1400, 900)
        
        self.df_banco = None
        self.df_ventas = None
        self.df_saint = None
        self.df_resultado = df_resultado
        self.resumen_bancario = resumen_bancario

        self.ruta_guardado = ruta_guardado
        
        self.modo_tomar_nota = False

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self._setup_styles()
        self.init_ui()
        
        if self.df_resultado is not None and not self.df_resultado.empty:
            self.aplicar_filtros()
        else:
            self.lbl_stats.setText("No se recibieron datos para mostrar.")
        
        self.showMaximized()

    def generar_reporte(self):
        if self.df_resultado is None:
            QMessageBox.warning(self, "Sin Datos", "No hay datos de conciliación para generar un reporte.")
            return

        try:
            resumen_bancario = self.resumen_bancario
            
            from src.gui.ventana_reportes import VentanaReporte
            ventana = VentanaReporte(self.df_resultado, resumen_bancario, ruta_guardado=self.ruta_guardado)
            ventana.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Reporte", f"No se pudo generar el reporte:\n\n{e}")

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self.windowStateChanged.emit(self.windowState())

    def _setup_styles(self):
        self.setFont(QFont("Inter", 11))

        qss_files = ["main_estilos.qss", "resultados_estilos.qss"]
        
        combined_styles = ""
        for filename in qss_files:
            style_path = os.path.join(ASSETS_PATH, "styles", filename)
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    combined_styles += f.read() + "\n" 
            except FileNotFoundError:
                print(f"Advertencia: No se encontro el archivo de estilos en la ruta: {style_path}")

        if combined_styles:
            self.setStyleSheet(combined_styles)

    def init_ui(self):
        title_bar = CustomTitleBar(self)
        title_bar.setFixedHeight(40)
        self.main_layout.addWidget(title_bar)

        content_widget = QWidget()
        content_widget.setObjectName("ResultadosContentWidget")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.addWidget(content_widget)

        self.setWindowTitle("Resultados de la Conciliación")

        header_layout = QHBoxLayout()

        btn_volver = QPushButton()
        icon_path = os.path.join(ASSETS_PATH, "icons", "logout_icon.svg")
        btn_volver.setIcon(QIcon(icon_path))
        btn_volver.setIconSize(QSize(30, 30))
        btn_volver.setToolTip("Volver a Principal")
        btn_volver.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_volver.setObjectName("BotonVolver")
        btn_volver.setStyleSheet("background-color: transparent; border: none;")
        btn_volver.clicked.connect(self.close)
        header_layout.addWidget(btn_volver, 0, Qt.AlignmentFlag.AlignLeft)

        title_container = QVBoxLayout()
        lbl_titulo = QLabel("Unidad Educativa Colegio Salesiano Pio XII")
        lbl_titulo.setObjectName("HeaderTitulo")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet("color: #FFD700; font-family: 'Inter'; font-size: 22px; font-weight: bold;")
        
        title_container.addWidget(lbl_titulo)
        header_layout.addLayout(title_container)

        header_layout.addWidget(QLabel(), 0, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(header_layout)

        filters_frame = QFrame()
        filters_frame.setStyleSheet("""
            QFrame#FiltrosFrame {
                background-color: #252525; 
                border-radius: 5px; 
                margin-bottom: 5px; 
                margin-top: 10px;
            }
            QLabel {
                color: #FFD700;
                font-weight: bold;
                font-family: 'Inter';
            }
            QComboBox, QDateEdit {
                background-color: #1E1E1E;
                color: #FFD700;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 4px;
                min-width: 100px;
            }
            QComboBox::drop-down, QDateEdit::drop-down {
                border: none;
                width: 20px;
            }
            QDateEdit::down-arrow {
                 border: none;
            }
            QLineEdit {
                background-color: #1E1E1E;
                color: #FFD700;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 4px;
            }
            /* Calendario popup */
            QCalendarWidget QWidget {
                background-color: #2C2C2C;
                color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: white;
                background-color: #2C2C2C;
                selection-background-color: #FFD700;
                selection-color: black;
            }
        """)
        filters_frame.setObjectName("FiltrosFrame")
        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setContentsMargins(10, 5, 10, 5)

        lbl_tipo = QLabel("Ver:")
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos los Movimientos", "Ingresos (SAE/Ventas)", "Egresos (SAINT/Gastos)"])
        self.combo_tipo.currentIndexChanged.connect(self.aplicar_filtros)

        lbl_estado = QLabel("Estado:")
        self.combo_estado = QComboBox()
        self.combo_estado.addItems([
            "Todos los Estados", 
            "Conciliado", 
            "Pendiente en Banco", 
            "Pendiente en Libro/SAINT", 
            "Requiere Revisión",
            "En Transcurso"
        ])
        self.combo_estado.currentIndexChanged.connect(self.aplicar_filtros)

                                
        self.chk_usar_fecha = QCheckBox()
        self.chk_usar_fecha.setToolTip("Activar filtro por fechas")
        self.chk_usar_fecha.setChecked(False)
        self.chk_usar_fecha.stateChanged.connect(self.aplicar_filtros)
        
        lbl_desde = QLabel("Desde:")
        self.date_desde = QDateEdit()
        self.date_desde.setCalendarPopup(True)
        self.date_desde.setDate(QDate(QDate.currentDate().year(), 1, 1))
        self.date_desde.setDisplayFormat("dd/MM/yyyy")
        self.date_desde.setEnabled(False) 
        self.date_desde.dateChanged.connect(self.aplicar_filtros)

        lbl_hasta = QLabel("Hasta:")
        self.date_hasta = QDateEdit()
        self.date_hasta.setCalendarPopup(True)
        self.date_hasta.setDate(QDate.currentDate())
        self.date_hasta.setDisplayFormat("dd/MM/yyyy")
        self.date_hasta.setEnabled(False)
        self.date_hasta.dateChanged.connect(self.aplicar_filtros)

        self.chk_usar_fecha.toggled.connect(lambda checked: self.date_desde.setEnabled(checked))
        self.chk_usar_fecha.toggled.connect(lambda checked: self.date_hasta.setEnabled(checked))
                                



        lbl_buscar = QLabel("Buscar:")
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Referencia, Monto, Descripción...")
        self.txt_buscar.textChanged.connect(self.aplicar_filtros)

        self.btn_reporte = QPushButton("Ver Reporte")
        self.btn_reporte.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reporte.setObjectName("BotonReporte")
        self.btn_reporte.setFixedSize(140, 40)
        self.btn_reporte.clicked.connect(self.generar_reporte)

        self.btn_tomar_nota = QPushButton("Tomar Nota")
        self.btn_tomar_nota.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tomar_nota.setObjectName("BotonTomarNota")
        self.btn_tomar_nota.setFixedSize(140, 40)
        self.btn_tomar_nota.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                border-radius: 5px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:checked {
                background-color: #FFD700;
                color: black;
                border: 2px solid #FFA000;
            }
        """)
        self.btn_tomar_nota.setCheckable(True)
        self.btn_tomar_nota.clicked.connect(self.toggle_modo_nota)

        self.lbl_stats = QLabel("Listo.")

        filters_layout.addWidget(lbl_tipo)
        filters_layout.addWidget(self.combo_tipo)
        filters_layout.addWidget(lbl_estado)
        filters_layout.addWidget(self.combo_estado)
        
                          
        filters_layout.addSpacing(15)
        filters_layout.addWidget(self.chk_usar_fecha)
        filters_layout.addWidget(lbl_desde)
        filters_layout.addWidget(self.date_desde)
        filters_layout.addWidget(lbl_hasta)
        filters_layout.addWidget(self.date_hasta)
        


        filters_layout.addSpacing(15)
        filters_layout.addWidget(lbl_buscar)
        filters_layout.addWidget(self.txt_buscar)
        filters_layout.addStretch()

        filters_layout.addWidget(self.lbl_stats)
        
        layout.addWidget(filters_frame)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Referencia", "Descripción", 
            "Cargo", "Abono", "SAE (Debe)", "SAINT (Haber)", "Estado"
        ])
        self.estilizar_tabla()
        layout.addWidget(self.tabla)

                                  
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 10, 0, 0)
        bottom_layout.addStretch() 
        bottom_layout.addWidget(self.btn_tomar_nota)
        bottom_layout.addSpacing(15)
        bottom_layout.addWidget(self.btn_reporte)
        
        layout.addLayout(bottom_layout)

    def estilizar_tabla(self):
        header = self.tabla.horizontalHeader()
        self.tabla.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(False)
        
        self.tabla.setColumnWidth(0, 120)
        self.tabla.setColumnWidth(1, 170)
        self.tabla.setColumnWidth(2, 510)
        self.tabla.setColumnWidth(3, 110)
        self.tabla.setColumnWidth(4, 110)
        self.tabla.setColumnWidth(5, 110)
        self.tabla.setColumnWidth(6, 110)
        
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch) 
        
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.cellDoubleClicked.connect(self.mostrar_detalle_fila)

    def aplicar_filtros(self):
        if self.df_resultado is None: return
        
        df = self.df_resultado.copy()
        
                                     
        if self.chk_usar_fecha.isChecked() and 'Fecha' in df.columns:
            try:
                                                                               
                def clean_date(val):
                    if not isinstance(val, str): return val
                    v = val.upper().strip()
                                                  
                    v = v.replace('-', '/')
                    v = v.replace('.', '')                                        

                                                                                
                    meses_num = {
                        'ENE': '01', 'JAN': '01', 
                        'FEB': '02', 
                        'MAR': '03', 
                        'ABR': '04', 'APR': '04', 
                        'MAY': '05', 
                        'JUN': '06', 
                        'JUL': '07', 
                        'AGO': '08', 'AUG': '08', 
                        'SEP': '09', 'SET': '09', 
                        'OCT': '10', 
                        'NOV': '11', 
                        'DIC': '12', 'DEC': '12'
                    }
                    
                    found_month = False
                    for mes_txt, mes_num in meses_num.items():
                        if mes_txt in v:
                            v = v.replace(mes_txt, mes_num)
                            found_month = True
                                                                              
                            break 
                    
                    return v

                                                                                               
                temp_series = df['Fecha'].astype(str).apply(clean_date)
                
                                                                            
                df['Fecha_dt'] = pd.to_datetime(temp_series, dayfirst=True, errors='coerce')
                
                fecha_inicio = self.date_desde.date().toPyDate()
                fecha_fin = self.date_hasta.date().toPyDate()
                
                                                                           
                df = df[
                    (df['Fecha_dt'].dt.date >= fecha_inicio) & 
                    (df['Fecha_dt'].dt.date <= fecha_fin)
                ]
            except Exception as e:
                print(f"Error filtro fecha (formato español): {e}")
                                     

        tipo = self.combo_tipo.currentText()
        if "Ingresos" in tipo:
            df = df[(df['Abono'] > 0) | (df['SAE (Debe)'] > 0)]
        elif "Egresos" in tipo:
            df = df[(df['Cargo'] > 0) | (df['SAINT (Haber)'] > 0)]
            
        est = self.combo_estado.currentText()
        if est == "Conciliado":
            df = df[df['Estado'] == 'Conciliado']
        elif est == "Pendiente en Banco":
            df = df[df['Estado'] == 'Pendiente en Banco']
        elif "Pendiente en Libro" in est:
            df = df[df['Estado'].str.contains('Pendiente en Libro|Pendiente en SAINT')]
        elif "Revisión" in est:
            df = df[df['Estado'].str.contains('Revisión|Error')]
        elif "En Transcurso" in est:
            df = df[df['Estado'].str.contains('Transcurso')]

        txt = self.txt_buscar.text().lower()
        if txt:
            mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(txt).any(), axis=1)
            df = df[mask]

        self.mostrar_datos(df)

    def formatear_moneda(self, valor):
        try:
            v = float(str(valor).replace(',', '.'))
            if v == 0: return "-"
            return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except: return str(valor)

    def mostrar_datos(self, df):
        self.tabla.setRowCount(0)
        self.tabla.setRowCount(len(df))
        
        c_conciliado = 0
        c_pendiente = 0
        c_revision = 0
        
        for r_idx, (df_idx, row) in enumerate(df.iterrows()):
            st = str(row['Estado'])
            
            bg = QColor("#1E1E1E") 
            if 'Conciliado' in st: 
                bg = QColor("#1B5E20")
                c_conciliado += 1
            elif 'Pendiente en Banco' in st: 
                bg = QColor("#5D4037")
                c_pendiente += 1
            elif 'Pendiente en Libro' in st:
                bg = QColor("#004D40")
                c_pendiente += 1
            elif 'Pendiente en SAINT' in st:
                bg = QColor("#E65100")
                c_pendiente += 1
            elif 'Transcurso' in st:
                bg = QColor("#0D47A1")
            elif 'Revisión' in st or 'Error' in st:
                bg = QColor("#B71C1C")
                c_revision += 1
            
            vals = [
                row['Fecha'], row['Referencia'], row['Descripción'], 
                row['Cargo'], row['Abono'], row['SAE (Debe)'], row['SAINT (Haber)'], st
            ]
            
            for c, val in enumerate(vals):
                txt = str(val)
                if c in [3,4,5,6]: txt = self.formatear_moneda(val)
                
                item = QTableWidgetItem(txt)
                item.setBackground(bg)
                item.setForeground(QColor("white"))
                
                if c in [3,4,5,6]: 
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                
                if c == 1 and "[NO ENCONTRADA]" in txt:
                    item.setForeground(QColor("#FF5252"))
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)

                self.tabla.setItem(r_idx, c, item)
        
        self.lbl_stats.setText(f"Viendo: {len(df)} filas | ✅: {c_conciliado} | ⚠️: {c_pendiente} | 🔍: {c_revision}")

    def mostrar_detalle_fila(self, row, column):
        datos = {}
        headers = ["Fecha", "Referencia", "Descripción", "Cargo", "Abono", "SAE (Debe)", "SAINT (Haber)", "Estado"]
        for col, header in enumerate(headers):
            item = self.tabla.item(row, col)
            if item:
                datos[header] = item.text()
            else:
                datos[header] = "-"
        
        if self.modo_tomar_nota:
            dialog = TomarNotaDialog(datos, self, ruta_notas=self.ruta_guardado)
            dialog.exec()
        else:
            dialog = DetalleMovimientoDialog(datos, self)
            dialog.exec()

    def toggle_modo_nota(self):
        self.modo_tomar_nota = self.btn_tomar_nota.isChecked()
        
        if self.modo_tomar_nota:
            self.setCursor(Qt.CursorShape.WhatsThisCursor) 
            self.tabla.setCursor(Qt.CursorShape.WhatsThisCursor)
            self.btn_tomar_nota.setText("Modo Notas ON")
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.tabla.setCursor(Qt.CursorShape.ArrowCursor)
            self.btn_tomar_nota.setText("Tomar Nota")

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()


if __name__ == "__main__":
    data_ejemplo = {
        'Fecha': ['01/01/2024', '01/01/2024', '02/01/2024', '03/01/2024'],
        'Referencia': ['12345', '67890', '[NO ENCONTRADA]', '54321'],
        'Descripción': ['Pago de prueba', 'Comisión', 'Venta pendiente', 'Gasto X'],
        'Cargo': [0, 1.50, 0, 50.0],
        'Abono': [100.0, 0, 0, 0],
        'SAE (Debe)': [100.0, 0, 150.0, 0],
        'SAINT (Haber)': [0, 0, 0, 50.0],
        'Estado': ['Conciliado', 'Conciliado', 'Pendiente en Banco', 'Requiere Revisión']
    }
    df_ejemplo = pd.DataFrame(data_ejemplo)

    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = VentanaResultados(df_ejemplo)
    window.show()
    
    sys.exit(app.exec())
