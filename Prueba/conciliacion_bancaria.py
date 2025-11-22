"""
Sistema de Conciliación Bancaria
Unidad Educativa Colegio Salesiano Pio XII
Concilia Estado de Cuenta vs Registro Saint (Egresos)
"""

import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QComboBox, QHeaderView, QMessageBox, QFileDialog, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon
from pathlib import Path


class ConciliacionBancaria(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df_estado_cuenta = None
        self.df_registro_saint = None
        self.df_conciliacion = None
        
        self.init_ui()
        self.cargar_archivos_automaticamente()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Sistema de Conciliaciones Bancarias")
        self.setMinimumSize(1400, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ===== HEADER =====
        self.crear_header(main_layout)
        
        # ===== CONTROLES =====
        self.crear_controles(main_layout)
        
        # ===== TABLA =====
        self.crear_tabla(main_layout)
        
        # ===== FOOTER CON BOTÓN =====
        self.crear_footer(main_layout)
        
        # Aplicar estilos
        self.aplicar_estilos()
    
    def crear_header(self, parent_layout):
        """Crea el header negro con título"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setFixedHeight(120)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Título principal
        titulo = QLabel("Unidad Educativa Colegio Salesiano Pio XII")
        titulo.setObjectName("tituloHeader")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtítulo
        subtitulo = QLabel("Conciliación Bancaria")
        subtitulo.setObjectName("subtituloHeader")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Mes
        mes = QLabel("Mes [JUNIO]")
        mes.setObjectName("mesHeader")
        mes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(titulo)
        header_layout.addWidget(subtitulo)
        header_layout.addWidget(mes)
        
        parent_layout.addWidget(header_frame)
    
    def crear_controles(self, parent_layout):
        """Crea la sección de controles (búsqueda y filtros)"""
        controles_frame = QFrame()
        controles_frame.setObjectName("controlesFrame")
        controles_layout = QHBoxLayout(controles_frame)
        controles_layout.setContentsMargins(20, 15, 20, 15)
        
        # Búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por referencia, descripción o monto...")
        self.search_input.setMinimumWidth(400)
        self.search_input.textChanged.connect(self.filtrar_tabla)
        
        # Filtro de estado
        self.filtro_estado = QComboBox()
        self.filtro_estado.addItems([
            "Todos los registros",
            "Conciliados",
            "Pendientes en Banco",
            "Descartados"
        ])
        self.filtro_estado.currentTextChanged.connect(self.filtrar_tabla)
        
        # Botón actualizar
        btn_actualizar = QPushButton("🔄 Actualizar")
        btn_actualizar.clicked.connect(lambda: self.cargar_archivos_automaticamente(mostrar_mensaje=True))

        
        # Botón exportar
        btn_exportar = QPushButton("📥 Exportar CSV")
        btn_exportar.clicked.connect(self.exportar_csv)
        
        controles_layout.addWidget(self.search_input)
        controles_layout.addWidget(QLabel("Filtrar:"))
        controles_layout.addWidget(self.filtro_estado)
        controles_layout.addStretch()
        controles_layout.addWidget(btn_actualizar)
        controles_layout.addWidget(btn_exportar)
        
        parent_layout.addWidget(controles_frame)
    
    def crear_tabla(self, parent_layout):
        """Crea la tabla principal de conciliación"""
        tabla_frame = QFrame()
        tabla_frame.setObjectName("tablaFrame")
        tabla_layout = QVBoxLayout(tabla_frame)
        tabla_layout.setContentsMargins(20, 10, 20, 10)
        
        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha",
            "Referencia",
            "Cargo",
            "Descripción",
            "Estado"
        ])
        
        # Configurar tabla
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Descripción
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        
        # Label de estadísticas
        self.stats_label = QLabel()
        self.stats_label.setObjectName("statsLabel")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        tabla_layout.addWidget(self.tabla)
        tabla_layout.addWidget(self.stats_label)
        
        parent_layout.addWidget(tabla_frame)
    
    def crear_footer(self, parent_layout):
        """Crea el footer con el botón Generar Reporte"""
        footer_frame = QFrame()
        footer_frame.setObjectName("footerFrame")
        footer_frame.setFixedHeight(80)
        
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        footer_layout.addStretch()
        
        # Botón Generar Reporte
        btn_generar = QPushButton("Generar Reporte")
        btn_generar.setObjectName("btnGenerar")
        btn_generar.setMinimumSize(200, 50)
        btn_generar.clicked.connect(self.realizar_conciliacion)
        
        footer_layout.addWidget(btn_generar)
        
        parent_layout.addWidget(footer_frame)
    
    def aplicar_estilos(self):
        """Aplica los estilos CSS a la aplicación"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            /* Header */
            #headerFrame {
                background-color: #1a1a1a;
                border-bottom: 3px solid #ff9800;
            }
            
            #tituloHeader {
                color: white;
                font-size: 24px;
                font-weight: bold;
                margin: 5px;
            }
            
            #subtituloHeader {
                color: #ff9800;
                font-size: 18px;
                font-weight: bold;
                margin: 3px;
            }
            
            #mesHeader {
                color: #cccccc;
                font-size: 14px;
                margin: 3px;
            }
            
            /* Controles */
            #controlesFrame {
                background-color: white;
                border-bottom: 1px solid #ddd;
            }
            
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 13px;
            }
            
            QLineEdit:focus {
                border: 2px solid #ff9800;
            }
            
            QComboBox {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                min-width: 180px;
                font-size: 13px;
            }
            
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #1976D2;
            }
            
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            
            /* Tabla */
            #tablaFrame {
                background-color: white;
            }
            
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #e0e0e0;
                font-size: 12px;
            }
            
            QTableWidget::item {
                padding: 8px;
            }
            
            QHeaderView::section {
                background-color: #ff9800;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            
            QTableWidget::item:alternate {
                background-color: #f9f9f9;
            }
            
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
            
            /* Stats */
            #statsLabel {
                font-size: 14px;
                font-weight: bold;
                color: #555;
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 5px;
                margin-top: 10px;
            }
            
            /* Footer */
            #footerFrame {
                background-color: #1a1a1a;
                border-top: 1px solid #333;
            }
            
            #btnGenerar {
                background-color: #ffc107;
                color: #1a1a1a;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                padding: 12px 24px;
            }
            
            #btnGenerar:hover {
                background-color: #ffb300;
            }
            
            #btnGenerar:pressed {
                background-color: #ffa000;
            }
        """)
    
    def cargar_archivos_automaticamente(self, mostrar_mensaje=False):
        """Carga los archivos CSV automáticamente desde el directorio actual"""
        try:
            directorio_actual = Path(__file__).parent
            archivos_cargados = True
            
            # Cargar Estado de Cuenta
            ruta_estado = directorio_actual / "Estado_Cuenta-3_limpio.csv"
            if ruta_estado.exists():
                self.df_estado_cuenta = pd.read_csv(ruta_estado)
                print(f"✅ Estado de Cuenta cargado: {len(self.df_estado_cuenta)} registros")
            else:
                print(f"❌ No se encontró: {ruta_estado.name}")
                archivos_cargados = False
                if mostrar_mensaje:
                    QMessageBox.warning(self, "Archivo no encontrado", 
                                      f"No se encontró: {ruta_estado.name}")
            
            # Cargar Registro Saint
            ruta_saint = directorio_actual / "egresos_saint_bancaribe_junio_mejorado.csv"
            if ruta_saint.exists():
                self.df_registro_saint = pd.read_csv(ruta_saint)
                print(f"✅ Registro Saint cargado: {len(self.df_registro_saint)} registros")
            else:
                print(f"❌ No se encontró: {ruta_saint.name}")
                archivos_cargados = False
                if mostrar_mensaje:
                    QMessageBox.warning(self, "Archivo no encontrado", 
                                      f"No se encontró: {ruta_saint.name}")
            
            # Actualizar label de estado
            if hasattr(self, 'stats_label'):
                if archivos_cargados:
                    self.stats_label.setText("✅ Archivos cargados correctamente. Haz clic en 'Generar Reporte' para comenzar.")
                else:
                    self.stats_label.setText("⚠️ No se pudieron cargar todos los archivos CSV. Verifica que estén en el directorio.")
            
            if mostrar_mensaje and archivos_cargados:
                QMessageBox.information(self, "Archivos Cargados", 
                                      "Los archivos CSV se cargaron correctamente.\n"
                                      "Haz clic en 'Generar Reporte' para realizar la conciliación.")
            
        except Exception as e:
            print(f"❌ Error al cargar archivos: {str(e)}")
            if mostrar_mensaje:
                QMessageBox.critical(self, "Error", f"Error al cargar archivos:\n{str(e)}")
    
    def realizar_conciliacion(self):
        """Realiza la conciliación bancaria"""
        if self.df_estado_cuenta is None or self.df_registro_saint is None:
            QMessageBox.warning(self, "Archivos no cargados", 
                              "Primero debes cargar los archivos CSV.")
            return
        
        try:
            # Normalizar encabezados
            self.df_estado_cuenta.columns = self.df_estado_cuenta.columns.str.upper().str.strip()
            self.df_registro_saint.columns = self.df_registro_saint.columns.str.upper().str.strip()
            
            # Filtrar solo Notas de Débito
            df_banco = self.df_estado_cuenta[self.df_estado_cuenta['TIPO'] == 'ND'].copy()
            
            # Normalizar montos del banco
            df_banco['MONTO'] = df_banco['CARGO'].astype(str)
            df_banco['MONTO'] = df_banco['MONTO'].str.replace('.', '', regex=False)
            df_banco['MONTO'] = df_banco['MONTO'].str.replace(',', '.', regex=False)
            df_banco['MONTO'] = pd.to_numeric(df_banco['MONTO'], errors='coerce')
            
            # Normalizar montos de Saint
            self.df_registro_saint['MONTO'] = pd.to_numeric(self.df_registro_saint['MONTO'], errors='coerce')
            
            # Redondear
            df_banco['MONTO'] = df_banco['MONTO'].round(2)
            self.df_registro_saint['MONTO'] = self.df_registro_saint['MONTO'].round(2)
            
            # ===== MANEJO ESPECIAL DE COMISIONES =====
            comisiones_banco = df_banco[df_banco['DESCRIPCIÓN'].str.contains('COMISION', case=False, na=False)].copy()
            suma_comisiones = comisiones_banco['MONTO'].sum()
            
            # Buscar el registro de comisiones en Saint
            comision_saint = self.df_registro_saint[
                self.df_registro_saint['TIPO_NOTA'].str.contains('COMISION', case=False, na=False)
            ]
            
            monto_comision_saint = 0
            if not comision_saint.empty:
                monto_comision_saint = comision_saint['MONTO'].iloc[0]
            
            # Verificar si las comisiones coinciden
            comisiones_conciliadas = abs(suma_comisiones - monto_comision_saint) < 0.10
            
            # ===== CONCILIACIÓN DE OTROS EGRESOS =====
            df_banco_sin_comisiones = df_banco[~df_banco['DESCRIPCIÓN'].str.contains('COMISION', case=False, na=False)].copy()
            df_saint_sin_comisiones = self.df_registro_saint[
                ~self.df_registro_saint['TIPO_NOTA'].str.contains('COMISION', case=False, na=False)
            ].copy()
            
            # Preparar referencias
            df_banco_sin_comisiones['REF_MATCH'] = df_banco_sin_comisiones['REFERENCIA'].astype(str).str.strip().str[-4:]
            df_saint_sin_comisiones['REF_MATCH'] = df_saint_sin_comisiones['REFERENCIA'].astype(str).str.strip()
            
            # Merge
            conciliacion = pd.merge(
                df_banco_sin_comisiones[['FECHA', 'REFERENCIA', 'MONTO', 'DESCRIPCIÓN', 'REF_MATCH']],
                df_saint_sin_comisiones[['REF_MATCH', 'MONTO', 'NOMBRE']],
                on=['REF_MATCH', 'MONTO'],
                how='outer',
                indicator=True,
                suffixes=('_banco', '_saint')
            )
            
            # Clasificar estados
            conciliacion['ESTADO'] = conciliacion['_merge'].map({
                'both': 'Conciliado',
                'left_only': 'Descartado',
                'right_only': 'Pendiente en Banco'
            })
            
            # Agregar comisiones al resultado
            if not comisiones_banco.empty:
                comisiones_banco['ESTADO'] = 'Conciliado' if comisiones_conciliadas else 'Pendiente en Banco'
                comisiones_banco['NOMBRE'] = 'COMISIÓN BANCARIA'
                
                # Combinar con el resultado principal
                comisiones_resultado = comisiones_banco[['FECHA', 'REFERENCIA', 'MONTO', 'DESCRIPCIÓN', 'ESTADO', 'NOMBRE']]
                conciliacion_final = pd.concat([
                    conciliacion[['FECHA', 'REFERENCIA', 'MONTO', 'DESCRIPCIÓN', 'ESTADO', 'NOMBRE']],
                    comisiones_resultado
                ], ignore_index=True)
            else:
                conciliacion_final = conciliacion[['FECHA', 'REFERENCIA', 'MONTO', 'DESCRIPCIÓN', 'ESTADO', 'NOMBRE']]
            
            # Ordenar
            conciliacion_final = conciliacion_final.sort_values(
                by=['ESTADO', 'FECHA'], 
                ascending=[False, True]
            )
            
            self.df_conciliacion = conciliacion_final
            self.mostrar_resultados()
            
            QMessageBox.information(self, "Conciliación Completada", 
                                  f"Se procesaron {len(conciliacion_final)} registros.\n"
                                  f"Comisiones: {'✅ Conciliadas' if comisiones_conciliadas else '⚠️ Pendientes'}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en la conciliación:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def mostrar_resultados(self):
        """Muestra los resultados en la tabla"""
        if self.df_conciliacion is None:
            return
        
        self.tabla.setRowCount(0)
        
        for idx, row in self.df_conciliacion.iterrows():
            row_position = self.tabla.rowCount()
            self.tabla.insertRow(row_position)
            
            # Fecha
            fecha_item = QTableWidgetItem(str(row.get('FECHA', '-')))
            fecha_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla.setItem(row_position, 0, fecha_item)
            
            # Referencia
            ref_item = QTableWidgetItem(str(row.get('REFERENCIA', '-')))
            ref_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla.setItem(row_position, 1, ref_item)
            
            # Cargo (Monto)
            monto = row.get('MONTO', 0)
            monto_item = QTableWidgetItem(f"Bs. {monto:,.2f}")
            monto_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla.setItem(row_position, 2, monto_item)
            
            # Descripción
            desc = str(row.get('DESCRIPCIÓN', row.get('NOMBRE', '-')))
            desc_item = QTableWidgetItem(desc)
            self.tabla.setItem(row_position, 3, desc_item)
            
            # Estado
            estado = str(row.get('ESTADO', '-'))
            estado_item = QTableWidgetItem(estado)
            estado_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Colorear según estado
            if estado == 'Conciliado':
                estado_item.setBackground(QColor(200, 255, 200))
                estado_item.setForeground(QColor(0, 100, 0))
            elif estado == 'Pendiente en Banco':
                estado_item.setBackground(QColor(255, 235, 200))
                estado_item.setForeground(QColor(200, 100, 0))
            else:  # Descartado
                estado_item.setBackground(QColor(240, 240, 240))
                estado_item.setForeground(QColor(100, 100, 100))
            
            self.tabla.setItem(row_position, 4, estado_item)
        
        self.actualizar_estadisticas()
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas"""
        if self.df_conciliacion is None:
            return
        
        total = len(self.df_conciliacion)
        conciliados = len(self.df_conciliacion[self.df_conciliacion['ESTADO'] == 'Conciliado'])
        pendientes = len(self.df_conciliacion[self.df_conciliacion['ESTADO'] == 'Pendiente en Banco'])
        descartados = len(self.df_conciliacion[self.df_conciliacion['ESTADO'] == 'Descartado'])
        
        total_monto = self.df_conciliacion['MONTO'].sum()
        
        stats_text = (f"📊 Total: {total} registros | "
                     f"✅ Conciliados: {conciliados} | "
                     f"⚠️ Pendientes: {pendientes} | "
                     f"❌ Descartados: {descartados} | "
                     f"💰 Total: Bs. {total_monto:,.2f}")
        
        self.stats_label.setText(stats_text)
    
    def filtrar_tabla(self):
        """Filtra la tabla según búsqueda y filtro de estado"""
        if self.df_conciliacion is None:
            return
        
        texto_busqueda = self.search_input.text().lower()
        filtro_estado = self.filtro_estado.currentText()
        
        for row in range(self.tabla.rowCount()):
            mostrar = True
            
            # Filtro de búsqueda
            if texto_busqueda:
                ref = self.tabla.item(row, 1).text().lower()
                desc = self.tabla.item(row, 3).text().lower()
                monto = self.tabla.item(row, 2).text().lower()
                
                if not (texto_busqueda in ref or texto_busqueda in desc or texto_busqueda in monto):
                    mostrar = False
            
            # Filtro de estado
            if filtro_estado != "Todos los registros":
                estado_item = self.tabla.item(row, 4).text()
                if filtro_estado == "Conciliados" and estado_item != "Conciliado":
                    mostrar = False
                elif filtro_estado == "Pendientes en Banco" and estado_item != "Pendiente en Banco":
                    mostrar = False
                elif filtro_estado == "Descartados" and estado_item != "Descartado":
                    mostrar = False
            
            self.tabla.setRowHidden(row, not mostrar)
    
    def exportar_csv(self):
        """Exporta los resultados a CSV"""
        if self.df_conciliacion is None:
            QMessageBox.warning(self, "Sin datos", "No hay datos para exportar.")
            return
        
        try:
            archivo, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Reporte",
                "Conciliacion_Bancaria.csv",
                "CSV Files (*.csv)"
            )
            
            if archivo:
                self.df_conciliacion.to_csv(archivo, index=False, encoding='utf-8-sig', sep=';')
                QMessageBox.information(self, "Exportado", f"Archivo guardado:\n{archivo}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar:\n{str(e)}")


def main():
    app = QApplication(sys.argv)
    
    # Configurar fuente global
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    ventana = ConciliacionBancaria()
    ventana.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
