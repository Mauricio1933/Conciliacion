                       
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QFrame, QFileDialog,
                             QMessageBox, QGroupBox, QGridLayout, QHeaderView, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QPixmap
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

from src.gui.widgets.barra_custom import CustomTitleBar

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.abspath(os.path.join(BASE_PATH, "../../assets"))

class VentanaDetalle(QDialog):
    """Ventana emergente para mostrar el detalle de transacciones."""
    windowStateChanged = pyqtSignal(Qt.WindowState)                                        
    windowStateChanged = pyqtSignal(Qt.WindowState)
    
    def __init__(self, df, titulo, ruta_guardado=None):
        super().__init__()
        self.df = df
        self.ruta_guardado = ruta_guardado                               
        self.titulo_reporte = titulo                                                           
        self.ruta_guardado = ruta_guardado
        self.titulo_reporte = titulo
        
                                            
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle(f"Detalle: {titulo}")
        self.resize(1250, 700)                                                    
        self.resize(1250, 700)
        
        self._setup_styles()
        self.init_ui(titulo)
        
                                  
        self.showMaximized()
    
    def changeEvent(self, event):
        """Maneja cambios de estado de la ventana (maximizar/restaurar)."""
        super().changeEvent(event)
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.WindowStateChange:
            self.windowStateChanged.emit(self.windowState())

    def _setup_styles(self):
        self.setFont(QFont("Inter", 10))
        
                                                                                          
        qss_files = ["main_estilos.qss", "reportes_especificos.qss"]
        combined_styles = ""
        
        for filename in qss_files:
            style_path = os.path.join(ASSETS_PATH, "styles", filename)
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    combined_styles += f.read() + "\n"
            except FileNotFoundError:
                print(f"Advertencia: No se encontró el archivo de estilos en la ruta: {style_path}")
        
        if combined_styles:
            self.setStyleSheet(combined_styles)

    def init_ui(self, titulo):
                          
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
                              
        content_widget = QWidget()
        content_widget.setObjectName("ReporteContentWidget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
                                       
        title_bar = CustomTitleBar(self, show_maximize=True, show_minimize=True)
        title_bar.setFixedHeight(40)
        content_layout.addWidget(title_bar)
        
                            
        interior = QWidget()
        layout = QVBoxLayout(interior)
        layout.setContentsMargins(15, 15, 15, 15)
        
                
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("TituloDetalle")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)
        
               
        self.tabla = QTableWidget()
        self.tabla.setObjectName("TablaDetalle")
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Referencia", "Descripción", "Monto", "Estado", "Control"])
        
                                                          
        self.tabla.verticalHeader().setVisible(False)
        
                                    
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.llenar_tabla()
        layout.addWidget(self.tabla)
        
                
        btn_layout = QHBoxLayout()
        lbl_info = QLabel(f"Total Registros: {len(self.df)}")
        lbl_info.setObjectName("LabelInfo")
        
                                
        btn_imprimir = QPushButton(" Imprimir")
        btn_imprimir.setObjectName("BtnImprimirDetalle")
        btn_imprimir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_imprimir.clicked.connect(self.imprimir_detalle)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setObjectName("BtnCerrarDetalle")
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.clicked.connect(self.close)
        
        btn_layout.addWidget(lbl_info)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_imprimir)
        btn_layout.addWidget(btn_cerrar)
        layout.addLayout(btn_layout)
        
        content_layout.addWidget(interior)
        main_layout.addWidget(content_widget)

    def llenar_tabla(self):
        self.tabla.setRowCount(len(self.df))
        
                                                      
        header = self.tabla.horizontalHeader()
        
                                 
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)         
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)              
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)         
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)          
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)           
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
                                                                                      
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        for r, row in self.df.reset_index().iterrows():
                                                                       
            monto = row['Abono'] if row['Abono'] > 0 else row['Cargo']
            if monto == 0 and row['SAE (Debe)'] > 0: monto = row['SAE (Debe)']
            if monto == 0 and row['SAINT (Haber)'] > 0: monto = row['SAINT (Haber)']
            
            vals = [
                row['Fecha'], 
                row['Referencia'], 
                row['Descripción'], 
                self.formatear_monto(monto),
                row['Estado'],
                row['Nro_Control']
            ]
            
            for c, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                if c == 3:        
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.tabla.setItem(r, c, item)

    def formatear_monto(self, monto):
        try:
            return f"{float(monto):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except: return str(monto)



    def imprimir_detalle(self):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            painter = QPainter(printer)
            
                                                          
            rect = printer.pageRect(QPrinter.Unit.DevicePixel)
            scale = rect.width() / self.tabla.width()
            
            painter.scale(scale, scale)
            self.tabla.render(painter)
            painter.end()

class VentanaReporte(QDialog):
    """Ventana modal para mostrar el reporte general bancario con opción de exportar a PDF."""
    windowStateChanged = pyqtSignal(Qt.WindowState)
    
    def __init__(self, df_resultado, resumen_bancario, ruta_guardado=None):
        super().__init__()
        self.df_resultado = df_resultado
        self.resumen_bancario = resumen_bancario
        self.ruta_guardado = ruta_guardado                                 
        self.ruta_guardado = ruta_guardado
        
                                            
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("VentanaReporte")
        self.setWindowTitle("Reporte General Bancario")
        self.resize(1280, 720)
        
        self._setup_styles()
        self.init_ui()
               
        self.showMaximized()
    
    def _setup_styles(self):
        self.setFont(QFont("Inter", 11))
        
        qss_files = ["main_estilos.qss", "reportes_especificos.qss"]
        combined_styles = ""
        
        for filename in qss_files:
            style_path = os.path.join(ASSETS_PATH, "styles", filename)
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    combined_styles += f.read() + "\n"
            except FileNotFoundError:
                print(f"Advertencia: No se encontró el archivo de estilos en la ruta: {style_path}")
        
        if combined_styles:
            self.setStyleSheet(combined_styles)

    def init_ui(self):
                          
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
                                        
        content_widget = QWidget()
        content_widget.setObjectName("ReporteContentWidget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
                                       
        title_bar = CustomTitleBar(self, show_maximize=True, show_minimize=True)
        title_bar.setFixedHeight(40)
        content_layout.addWidget(title_bar)
        
                                               
        interior = QWidget()
        layout = QVBoxLayout(interior)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
                
        titulo = QLabel("REPORTE GENERAL BANCARIO")
        titulo.setObjectName("TituloReporte")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
                                                                      
        tablas_layout = QVBoxLayout()
        tablas_layout.setSpacing(20)
        tablas_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)                           
        tablas_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
                                               
        resultado_widget = self.crear_seccion_resultados()
        resultado_widget.setMinimumWidth(1100)                                  
        resultado_widget.setMaximumWidth(1400)                          
        resultado_widget.setMinimumWidth(1100)
        resultado_widget.setMaximumWidth(1400)
        tablas_layout.addWidget(resultado_widget, 0, Qt.AlignmentFlag.AlignHCenter)
        
                                                         
        banco_widget = self.crear_seccion_resumen_banco()
        banco_widget.setMinimumWidth(1100)                                  
        banco_widget.setMaximumWidth(1400)                          
        banco_widget.setMinimumWidth(1100)
        banco_widget.setMaximumWidth(1400)
        tablas_layout.addWidget(banco_widget, 0, Qt.AlignmentFlag.AlignHCenter)
        
        layout.addLayout(tablas_layout)
        layout.addStretch()                                  
        layout.addStretch()
        
                         
        botones_layout = QHBoxLayout()
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setObjectName("BtnCerrarReporte")
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.clicked.connect(self.close)
        
                                
        btn_imprimir = QPushButton("Imprimir")
        btn_imprimir.setObjectName("BtnImprimirReporte")
        btn_imprimir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_imprimir.clicked.connect(self.imprimir_reporte)
        
        botones_layout.addStretch()
        botones_layout.addWidget(btn_imprimir)
        botones_layout.addWidget(btn_cerrar)
        
        layout.addLayout(botones_layout)
        
        content_layout.addWidget(interior)
        main_layout.addWidget(content_widget)
    
    def changeEvent(self, event):
        super().changeEvent(event)
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.WindowStateChange:
            self.windowStateChanged.emit(self.windowState())
    
    def crear_seccion_resultados(self):
      
        group = QGroupBox("Resultados de la Conciliación")
        group.setObjectName("GroupResultados")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 15, 10, 10)
        
                                          
        self.stats = self.calcular_estadisticas()
        
                                                        
        tabla = QTableWidget(8, 4)
        tabla.setObjectName("TablaResultados")
        tabla.setHorizontalHeaderLabels(["", "Cantidad", "Monto", "Detalle"])
        tabla.verticalHeader().setVisible(False)
        
                                                                                          
        tabla.verticalHeader().setDefaultSectionSize(38)
                                                   
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
                                  
        tabla.setItem(0, 0, self.crear_item("Notas de Crédito", bold=True))
        tabla.setItem(0, 1, self.crear_item(str(self.stats['nc_total_cant']), bold=True))
        tabla.setItem(0, 2, self.crear_item(self.formatear_monto(self.stats['nc_total_monto']), bold=True))
        
        tabla.setItem(1, 0, self.crear_item("  Partidas Conciliadas"))
        tabla.setItem(1, 1, self.crear_item(str(self.stats['nc_conciliadas_cant'])))
        tabla.setItem(1, 2, self.crear_item(self.formatear_monto(self.stats['nc_conciliadas_monto'])))
        self.agregar_boton_detalle(tabla, 1, "NC_CONCILIADAS")
        
        tabla.setItem(2, 0, self.crear_item("  Partidas No Conciliadas"))
        tabla.setItem(2, 1, self.crear_item(str(self.stats['nc_no_conciliadas_cant'])))
        tabla.setItem(2, 2, self.crear_item(self.formatear_monto(self.stats['nc_no_conciliadas_monto'])))
        self.agregar_boton_detalle(tabla, 2, "NC_PENDIENTES")
        
        tabla.setItem(3, 0, self.crear_item(f"Total Notas de Crédito", bold=True))
        tabla.setItem(3, 1, self.crear_item(str(self.stats['nc_total_cant']), bold=True))
        tabla.setItem(3, 2, self.crear_item(self.formatear_monto(self.stats['nc_total_monto']), bold=True))
        
                                 
        tabla.setItem(4, 0, self.crear_item("Notas de Débito", bold=True))
        tabla.setItem(4, 1, self.crear_item(str(self.stats['nd_total_cant']), bold=True))
        tabla.setItem(4, 2, self.crear_item(self.formatear_monto(self.stats['nd_total_monto']), bold=True))
        
        tabla.setItem(5, 0, self.crear_item("  Partidas Conciliadas"))
        tabla.setItem(5, 1, self.crear_item(str(self.stats['nd_conciliadas_cant'])))
        tabla.setItem(5, 2, self.crear_item(self.formatear_monto(self.stats['nd_conciliadas_monto'])))
        self.agregar_boton_detalle(tabla, 5, "ND_CONCILIADAS")
        
        tabla.setItem(6, 0, self.crear_item("  Partidas No Conciliadas"))
        tabla.setItem(6, 1, self.crear_item(str(self.stats['nd_no_conciliadas_cant'])))
        tabla.setItem(6, 2, self.crear_item(self.formatear_monto(self.stats['nd_no_conciliadas_monto'])))
        self.agregar_boton_detalle(tabla, 6, "ND_PENDIENTES")
        
        tabla.setItem(7, 0, self.crear_item(f"Total Notas de Débito", bold=True))
        tabla.setItem(7, 1, self.crear_item(str(self.stats['nd_total_cant']), bold=True))
        tabla.setItem(7, 2, self.crear_item(self.formatear_monto(self.stats['nd_total_monto']), bold=True))
        
                                                               
        tabla.horizontalHeader().setStretchLastSection(True)
        tabla.setColumnWidth(0, 480)                   
        tabla.setColumnWidth(1, 110)            
        tabla.setColumnWidth(2, 170)         
                                                          
        tabla.setColumnWidth(0, 480)
        tabla.setColumnWidth(1, 110)
        tabla.setColumnWidth(2, 170)
        
                                                                                
        altura_filas = tabla.verticalHeader().defaultSectionSize() * 8
        altura_header = tabla.horizontalHeader().height()
        tabla.setMinimumHeight(altura_filas + altura_header + 20)
        tabla.setMaximumHeight(altura_filas + altura_header + 20)
        
        layout.addWidget(tabla)
        layout.addStretch()                                    
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def agregar_boton_detalle(self, tabla, fila, tipo):
                                                          
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn = QPushButton("Ver Detalle")
        btn.setObjectName("BtnVerDetalle")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedWidth(110)                            
        btn.setFixedHeight(28)               
        btn.setFixedWidth(110)
        btn.setFixedHeight(28)
        btn.clicked.connect(lambda: self.abrir_detalle(tipo))
        
        layout.addWidget(btn)
        tabla.setCellWidget(fila, 3, container)

    def abrir_detalle(self, tipo):
        df_filtrado = pd.DataFrame()
        titulo = ""
        
        if tipo == "NC_CONCILIADAS":
            df_filtrado = self.stats['df_nc_conciliadas']
            titulo = "Notas de Crédito Conciliadas"
        elif tipo == "NC_PENDIENTES":
            df_filtrado = self.stats['df_nc_no_conciliadas']
            titulo = "Notas de Crédito NO Conciliadas"
        elif tipo == "ND_CONCILIADAS":
            df_filtrado = self.stats['df_nd_conciliadas']
            titulo = "Notas de Débito Conciliadas"
        elif tipo == "ND_PENDIENTES":
            df_filtrado = self.stats['df_nd_no_conciliadas']
            titulo = "Notas de Débito NO Conciliadas"
            
        if not df_filtrado.empty:
          
            ventana = VentanaDetalle(df_filtrado, titulo, ruta_guardado=self.ruta_guardado)
            ventana.setWindowModality(Qt.WindowModality.ApplicationModal)
      
            self.setEnabled(False)
            ventana.finished.connect(lambda _=None: self.setEnabled(True))
            ventana.show()
            ventana.raise_()
            try:
                ventana.activateWindow()
            except Exception:
                pass
        else:
            QMessageBox.information(self, "Info", "No hay registros para mostrar.")

    def crear_seccion_resumen_banco(self):
        """Crea la sección de resumen del estado de cuenta del banco."""
        group = QGroupBox("Resumen del Estado de Cuenta (Banco)")
        group.setObjectName("GroupBanco")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 15, 10, 10)
        
        if not self.resumen_bancario:
            label = QLabel("⚠️ No se encontró el resumen bancario del JSON")
            label.setObjectName("LabelWarning")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
        else:
            tabla = QTableWidget(4, 3)
            tabla.setObjectName("TablaBanco")
            tabla.setHorizontalHeaderLabels(["", "Cantidad", "Monto"])
            tabla.verticalHeader().setVisible(False)
            
                                                                                              
            tabla.verticalHeader().setDefaultSectionSize(38)
                                                       
            tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            
                                
            tabla.setItem(0, 0, self.crear_item("Saldo Mes Anterior"))
            tabla.setItem(0, 1, self.crear_item(""))
            tabla.setItem(0, 2, self.crear_item(self.resumen_bancario.get('saldo_mes_anterior', '0,00')))
            
                              
            tabla.setItem(1, 0, self.crear_item("Notas de Crédito"))
            tabla.setItem(1, 1, self.crear_item(str(self.resumen_bancario.get('notas_credito_cantidad', 0))))
            tabla.setItem(1, 2, self.crear_item(self.resumen_bancario.get('notas_credito_monto', '0,00')))
            
                             
            tabla.setItem(2, 0, self.crear_item("Notas de Débito"))
            tabla.setItem(2, 1, self.crear_item(str(self.resumen_bancario.get('notas_debito_cantidad', 0))))
            tabla.setItem(2, 2, self.crear_item(self.resumen_bancario.get('notas_debito_monto', '0,00')))
            
                         
            tabla.setItem(3, 0, self.crear_item("Saldo Final del Mes", bold=True))
            tabla.setItem(3, 1, self.crear_item(""))
            tabla.setItem(3, 2, self.crear_item(self.resumen_bancario.get('saldo_final_mes', '0,00'), bold=True))
            
                                                                   
            tabla.horizontalHeader().setStretchLastSection(True)
            tabla.setColumnWidth(0, 700)                             
            tabla.setColumnWidth(1, 150)            
                                                            
            tabla.setColumnWidth(0, 700)
            tabla.setColumnWidth(1, 150)
            
                                                                                    
            altura_filas = tabla.verticalHeader().defaultSectionSize() * 4
            altura_header = tabla.horizontalHeader().height()
            tabla.setMinimumHeight(altura_filas + altura_header + 20)
            tabla.setMaximumHeight(altura_filas + altura_header + 20)
            
            layout.addWidget(tabla)
        
        layout.addStretch()                                    
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def calcular_estadisticas(self):
        df = self.df_resultado
                            
        nc = df[df['Abono'] > 0].copy()
        nc_conciliadas = nc[nc['Estado'].str.contains('Conciliado', na=False)]
        nc_no_conciliadas = nc[~nc['Estado'].str.contains('Conciliado', na=False)]
        
                        
        nd = df[df['Cargo'] > 0].copy()
        nd_conciliadas = nd[nd['Estado'].str.contains('Conciliado', na=False)]
        nd_no_conciliadas = nd[~nd['Estado'].str.contains('Conciliado', na=False)]
        
        return {
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
            
                                              
            'df_nc_conciliadas': nc_conciliadas,
            'df_nc_no_conciliadas': nc_no_conciliadas,
            'df_nd_conciliadas': nd_conciliadas,
            'df_nd_no_conciliadas': nd_no_conciliadas
        }
    
    def crear_item(self, texto, bold=False):
        item = QTableWidgetItem(str(texto))
                                                                                               
                                                                                        
        if isinstance(texto, str) and texto.startswith('  '):
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        if bold:
            font = item.font()
            font.setBold(True)
            item.setFont(font)
        return item
    
    def formatear_monto(self, monto):

        try:
            return f"{monto:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            return "0,00"
    
    def guardar_todos_reportes(self):

        if not self.ruta_guardado:
            print("⚠️ No hay ruta de guardado configurada. No se guardarán reportes automáticamente.")
            return
        
        try:
                                                 
            meses = {
                1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
                5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
                9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
            }
            
            ahora = datetime.now()
            dia = ahora.day
            mes = meses[ahora.month]
            anio = ahora.year
            hora = ahora.strftime("%H%M%S")
            
            nombre_pdf = f"Reporte {dia} de {mes} {anio} - {hora}.pdf"
            ruta_pdf = os.path.join(self.ruta_guardado, nombre_pdf)
            
            reportes_guardados = []
            
                                               
            self.generar_pdf(ruta_pdf)
            reportes_guardados.append(f"📄 {nombre_pdf}")
            
                                                            
            reportes_especificos = [
                (self.stats['df_nc_conciliadas'], "Notas de Crédito Conciliadas"),
                (self.stats['df_nc_no_conciliadas'], "Notas de Crédito NO Conciliadas"),
                (self.stats['df_nd_conciliadas'], "Notas de Débito Conciliadas"),
                (self.stats['df_nd_no_conciliadas'], "Notas de Débito NO Conciliadas")
            ]
            
            for df, titulo in reportes_especificos:
                if not df.empty:
                                                
                    nombre_limpio = "".join(c for c in titulo if c.isalnum() or c in (' ', '_', '-')).strip()
                    nombre_excel = f"{nombre_limpio}.xlsx"
                    ruta_excel = os.path.join(self.ruta_guardado, nombre_excel)
                    df.to_excel(ruta_excel, index=False)
                    reportes_guardados.append(f"📊 {nombre_excel}")
            
            print(f" Reportes guardados automáticamente: {', '.join(reportes_guardados)}")
            print(f" Ubicación: {self.ruta_guardado}")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ Error al guardar reportes automáticamente: {e}")
    
    def exportar_pdf(self):

        try:
                                              
            fecha = datetime.now().strftime("%Y%m%d")
            nombre_archivo = f"Reporte_Conciliacion_{fecha}.pdf"
            
            ruta, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Reporte PDF",
                nombre_archivo,
                "PDF Files (*.pdf)"
            )
            
            if not ruta:
                return                   
                return
            
                         
            self.generar_pdf(ruta)
            
            QMessageBox.information(self, "Éxito", f"PDF generado correctamente:\n{ruta}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar PDF:\n{str(e)}")
    
    def generar_pdf(self, ruta):

        doc = SimpleDocTemplate(ruta, pagesize=letter)
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
        
                                               
        elementos.append(Paragraph("<b>Resultados de la Conciliación</b>", estilos['Heading2']))
        elementos.append(Spacer(1, 0.2 * inch))
        
                                                
        estadisticas = self.stats
        
                                                                                      
        datos_conciliacion = [
            ['', 'Cantidad', 'Monto'],
            ['Notas de Crédito', str(estadisticas['nc_total_cant']), 
             self.formatear_monto(estadisticas['nc_total_monto'])],
            ['  Partidas Conciliadas', str(estadisticas['nc_conciliadas_cant']), 
             self.formatear_monto(estadisticas['nc_conciliadas_monto'])],
            ['  Partidas No Conciliadas', str(estadisticas['nc_no_conciliadas_cant']), 
             self.formatear_monto(estadisticas['nc_no_conciliadas_monto'])],
            ['Total Notas de Crédito', str(estadisticas['nc_total_cant']), 
             self.formatear_monto(estadisticas['nc_total_monto'])],
            ['', '', ''],
            ['Notas de Débito', str(estadisticas['nd_total_cant']), 
             self.formatear_monto(estadisticas['nd_total_monto'])],
            ['  Partidas Conciliadas', str(estadisticas['nd_conciliadas_cant']), 
             self.formatear_monto(estadisticas['nd_conciliadas_monto'])],
            ['  Partidas No Conciliadas', str(estadisticas['nd_no_conciliadas_cant']), 
             self.formatear_monto(estadisticas['nd_no_conciliadas_monto'])],
            ['Total Notas de Débito', str(estadisticas['nd_total_cant']), 
             self.formatear_monto(estadisticas['nd_total_monto'])],
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
            f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>",
            estilos['Normal']
        ))
        
        doc.build(elementos)

    def imprimir_reporte(self):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                                                                         
                                                                             
            widget_a_imprimir = self.findChild(QWidget, "ReporteContentWidget")
            
            if not widget_a_imprimir:
                widget_a_imprimir = self
                
                                                                       
            pixmap = QPixmap(widget_a_imprimir.size())
            widget_a_imprimir.render(pixmap)
            
            painter = QPainter(printer)
            
                                                     
            rect = printer.pageRect(QPrinter.Unit.DevicePixel)
            
                                                           
            scale_x = rect.width() / pixmap.width()
            scale_y = rect.height() / pixmap.height()
            scale = min(scale_x, scale_y)
            
                                  
            x_offset = (rect.width() - (pixmap.width() * scale)) / 2
            y_offset = (rect.height() - (pixmap.height() * scale)) / 2
            
            painter.translate(rect.x() + x_offset, rect.y() + y_offset)
            painter.scale(scale, scale)
            
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
