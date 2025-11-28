"""
Vista de Resultados de Conciliación
Interfaz con tabla filtrable para mostrar resultados consolidados
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QCheckBox, QLineEdit, QHeaderView, QComboBox,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
import pandas as pd

class ConciliacionView(QWidget):
    """Vista única con filtros para mostrar resultados de conciliación"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ConciliacionView")
        
        self.df_resultados = pd.DataFrame()
        self.df_filtrado = pd.DataFrame()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Establecer fondo sólido para todos los elementos
        self.setStyleSheet("""
            QWidget#ConciliacionView {
                background-color: #1f2630;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QTableWidget {
                background-color: #2a2e39;
                color: #ffffff;
                gridline-color: #3a3e49;
            }
            QHeaderView::section {
                background-color: #343a40;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #3a3e49;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        lbl_titulo = QLabel("📊 Resultados de Conciliación Bancaria")
        lbl_titulo.setObjectName("TituloConciliacion")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)
        
        # Panel de filtros
        filtros_widget = self._crear_panel_filtros()
        layout.addWidget(filtros_widget)
        
        # Estadísticas
        self.lbl_stats = QLabel("Cargue los resultados para ver estadísticas")
        self.lbl_stats.setObjectName("StatsLabel")
        self.lbl_stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_stats)
        
        # Tabla de resultados
        self.tabla = QTableWidget()
        self.tabla.setObjectName("TablaConciliacion")
        self._configurar_tabla()
        layout.addWidget(self.tabla)
        
        # Botones de acción
        botones_widget = self._crear_botones_accion()
        layout.addWidget(botones_widget)
    
    def _crear_panel_filtros(self):
        """Crea el panel de filtros"""
        widget = QWidget()
        widget.setObjectName("PanelFiltros")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Filtro por tipo de pago
        lbl_tipo = QLabel("Tipo:")
        self.chk_otr = QCheckBox("Pago Móvil")
        self.chk_otr.setChecked(True)
        self.chk_otr.stateChanged.connect(self._aplicar_filtros)
        
        self.chk_tra = QCheckBox("Transferencias")
        self.chk_tra.setChecked(True)
        self.chk_tra.stateChanged.connect(self._aplicar_filtros)
        
        self.chk_tdd = QCheckBox("TDD")
        self.chk_tdd.setChecked(True)
        self.chk_tdd.stateChanged.connect(self._aplicar_filtros)
        
        # Filtro por estado
        lbl_estado = QLabel("Estado:")
        self.combo_estado = QComboBox()
        self.combo_estado.addItems([
            "Todos",
            "Conciliado",
            "Pendiente en Banco",
            "Requiere Revisión"
        ])
        self.combo_estado.currentTextChanged.connect(self._aplicar_filtros)
        
        # Búsqueda
        lbl_buscar = QLabel("Buscar:")
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Referencia, Nro Control, Monto...")
        self.txt_buscar.textChanged.connect(self._aplicar_filtros)
        
        # Agregar al layout
        layout.addWidget(lbl_tipo)
        layout.addWidget(self.chk_otr)
        layout.addWidget(self.chk_tra)
        layout.addWidget(self.chk_tdd)
        layout.addSpacing(20)
        layout.addWidget(lbl_estado)
        layout.addWidget(self.combo_estado)
        layout.addSpacing(20)
        layout.addWidget(lbl_buscar)
        layout.addWidget(self.txt_buscar)
        layout.addStretch()
        
        return widget
    
    def _configurar_tabla(self):
        """Configura la tabla de resultados"""
        columnas = [
            "Tipo", "Nro Control", "Fecha", "Referencia", 
            "Descripción", "Monto", "Estado"
        ]
        
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setHorizontalHeaderLabels(columnas)
        
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    
    def _crear_botones_accion(self):
        """Crea los botones de acción"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        btn_exportar = QPushButton("📁 Exportar CSV")
        btn_exportar.setObjectName("BtnExportar")
        btn_exportar.clicked.connect(self._exportar_csv)
        
        btn_limpiar = QPushButton("🔄 Limpiar Filtros")
        btn_limpiar.setObjectName("BtnLimpiar")
        btn_limpiar.clicked.connect(self._limpiar_filtros)
        
        layout.addStretch()
        layout.addWidget(btn_limpiar)
        layout.addWidget(btn_exportar)
        
        return widget
    
    def cargar_resultados(self, df_resultados: pd.DataFrame):
        """Carga los resultados de conciliación en la tabla"""
        self.df_resultados = df_resultados
        self.df_filtrado = df_resultados.copy()
        self._aplicar_filtros()
        self._actualizar_estadisticas()
    
    def _aplicar_filtros(self):
        """Aplica los filtros seleccionados"""
        if self.df_resultados.empty:
            return
        
        df = self.df_resultados.copy()
        
        # Filtro por tipo de pago
        tipos_seleccionados = []
        if self.chk_otr.isChecked():
            tipos_seleccionados.append("Pago Móvil")
        if self.chk_tra.isChecked():
            tipos_seleccionados.append("Transferencias")
        if self.chk_tdd.isChecked():
            tipos_seleccionados.append("Tarjetas de Débito")
        
        if tipos_seleccionados:
            df = df[df['Tipo'].isin(tipos_seleccionados)]
        
        # Filtro por estado
        estado_seleccionado = self.combo_estado.currentText()
        if estado_seleccionado != "Todos":
            df = df[df['Estado'].str.contains(estado_seleccionado, na=False)]
        
        # Filtro por búsqueda
        texto_buscar = self.txt_buscar.text().strip()
        if texto_buscar:
            mask = df.astype(str).apply(lambda row: row.str.contains(texto_buscar, case=False, na=False).any(), axis=1)
            df = df[mask]
        
        self.df_filtrado = df
        self._mostrar_en_tabla(df)
    
    def _mostrar_en_tabla(self, df: pd.DataFrame):
        """Muestra el DataFrame en la tabla"""
        self.tabla.setRowCount(0)
        
        for row_idx, row in df.iterrows():
            self.tabla.insertRow(self.tabla.rowCount())
            
            # Extraer datos
            tipo = str(row.get('Tipo', ''))
            nro_control = str(row.get('Nro_Control', ''))
            fecha = str(row.get('Fecha', ''))
            referencia = str(row.get('Referencia', ''))
            descripcion = str(row.get('Descripcion', ''))
            monto = row.get('Monto', 0)
            estado = str(row.get('Estado', ''))
            
            # Formatear monto
            try:
                monto_fmt = f"{float(monto):,.2f}"
            except:
                monto_fmt = str(monto)
            
            # Crear items (7 columnas)
            items = [
                QTableWidgetItem(tipo),
                QTableWidgetItem(nro_control),
                QTableWidgetItem(fecha),
                QTableWidgetItem(referencia),
                QTableWidgetItem(descripcion),
                QTableWidgetItem(monto_fmt),
                QTableWidgetItem(estado)
            ]
            
            # Aplicar colores según estado
            color_fondo, color_texto = self._obtener_colores_estado(estado, referencia)
            
            for col_idx, item in enumerate(items):
                # Alineación
                if col_idx == 5:  # Monto
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                
                # Aplicar colores
                item.setBackground(color_fondo)
                item.setForeground(color_texto)
                
                # Negrita para estados críticos
                if "Requiere Revisión" in estado or "Pendiente" in estado:
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                
                # Destacar [NO ENCONTRADA] en rojo
                if "[NO ENCONTRADA]" in item.text():
                    item.setForeground(QColor("#FF5252"))
                
                self.tabla.setItem(self.tabla.rowCount() - 1, col_idx, item)
    
    def _obtener_colores_estado(self, estado: str, referencia: str):
        """Retorna los colores según el estado"""
        # Verde - Conciliado
        if "Conciliado" in estado:
            return QColor("#d4edda"), QColor("#155724")
        
        # Amarillo - Pendiente
        elif "Pendiente" in estado:
            return QColor("#fff3cd"), QColor("#856404")
        
        # Naranja - Diferencia Alta
        elif "Diferencia Alta" in estado:
            return QColor("#ffe0b2"), QColor("#e65100")
        
        # Rojo claro - Monto Mayor en Banco
        elif "Monto Mayor en Banco" in estado:
            return QColor("#ffcdd2"), QColor("#c62828")
        
        # Rojo fuerte - Diferencia Excesiva o Requiere Revisión
        elif "Requiere Revisión" in estado or "Diferencia Excesiva" in estado:
            return QColor("#f8d7da"), QColor("#721c24")
        
        # Blanco por defecto
        return QColor("#ffffff"), QColor("#000000")
    
    def _actualizar_estadisticas(self):
        """Actualiza el label de estadísticas"""
        if self.df_resultados.empty:
            self.lbl_stats.setText("No hay resultados para mostrar")
            return
        
        total = len(self.df_resultados)
        conciliados = len(self.df_resultados[self.df_resultados['Estado'].str.contains('Conciliado', na=False)])
        pendientes = len(self.df_resultados[self.df_resultados['Estado'].str.contains('Pendiente', na=False)])
        revision = len(self.df_resultados[self.df_resultados['Estado'].str.contains('Requiere Revisión', na=False)])
        
        tasa = (conciliados / total * 100) if total > 0 else 0
        
        self.lbl_stats.setText(
            f"✅ Conciliados: {conciliados} | ⚠️ Pendientes: {pendientes} | "
            f"🔍 Requiere Revisión: {revision} | 📊 Total: {total} | "
            f"📈 Tasa: {tasa:.1f}%"
        )
    
    def _limpiar_filtros(self):
        """Limpia todos los filtros"""
        self.chk_otr.setChecked(True)
        self.chk_tra.setChecked(True)
        self.chk_tdd.setChecked(True)
        self.combo_estado.setCurrentIndex(0)
        self.txt_buscar.clear()
    
    def _exportar_csv(self):
        """Exporta los resultados filtrados a CSV"""
        if self.df_filtrado.empty:
            QMessageBox.warning(self, "Sin Datos", "No hay datos para exportar")
            return
        
        archivo, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Resultados",
            "conciliacion_resultados.csv",
            "CSV Files (*.csv)"
        )
        
        if archivo:
            self.df_filtrado.to_csv(archivo, sep=';', encoding='utf-8-sig', index=False)
            QMessageBox.information(self, "Éxito", f"Resultados exportados a:\n{archivo}")
