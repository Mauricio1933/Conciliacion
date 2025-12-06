import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from src.logic.CONCILIACIONMAESTRA import ConciliacionMaestra
import traceback

class WorkerConciliacion(QThread):
    progreso = pyqtSignal(str)
    finalizado = pyqtSignal(object)                                                  

    def __init__(self, df_banco, df_ventas, df_saint):
        super().__init__()
        self.df_banco = df_banco
        self.df_ventas = df_ventas
        self.df_saint = df_saint

    def run(self):
        try:
            self.progreso.emit("Iniciando la conciliación...")
            conciliador = ConciliacionMaestra(self.df_banco, self.df_ventas, self.df_saint)
            
                                                                                               
                                               
            self.progreso.emit("Procesando datos... Esto puede tardar unos momentos.")
            
            resultado_df = conciliador.ejecutar()
            
            self.progreso.emit("¡Conciliación completada con éxito!")
            self.finalizado.emit(resultado_df)
        except Exception as e:
            error_info = traceback.format_exc()
            self.progreso.emit(f"ERROR: {e}\n{error_info}")
            self.finalizado.emit(e)

class VentanaConciliacion(QDialog):
    def __init__(self, df_banco, df_ventas, df_saint, parent=None):
        super().__init__(parent)
        self.df_banco = df_banco
        self.df_ventas = df_ventas
        self.df_saint = df_saint
        self.df_resultado = None

        self.init_ui()
        self.iniciar_proceso()

    def init_ui(self):
        self.setWindowTitle("Proceso de Conciliación")
        self.setMinimumSize(600, 400)
        self.setStyleSheet("background-color: #1E1E1E; color: white; font-size: 14px;")

        layout = QVBoxLayout(self)

        title = QLabel("Conciliacion")
        title.setObjectName("RecordsTitle")
        title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.lbl_estado = QLabel("Preparando para iniciar la conciliación...")
        self.lbl_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_estado.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(self.lbl_estado)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background-color: #111; border: 1px solid #444; border-radius: 5px;")
        layout.addWidget(self.log_box)

        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.setEnabled(False)
        self.btn_cerrar.setStyleSheet("background-color: #333; color: #888; padding: 10px; border-radius: 5px;")
        self.btn_cerrar.clicked.connect(self.accept)                                              
        layout.addWidget(self.btn_cerrar)

    def iniciar_proceso(self):
        self.worker = WorkerConciliacion(self.df_banco, self.df_ventas, self.df_saint)
        self.worker.progreso.connect(self.actualizar_log)
        self.worker.finalizado.connect(self.proceso_finalizado)
        self.worker.start()

    def actualizar_log(self, mensaje):
        self.log_box.append(mensaje)

    def proceso_finalizado(self, resultado):
        if isinstance(resultado, Exception):
            self.lbl_estado.setText("❌ Error en la Conciliación")
            self.lbl_estado.setStyleSheet("color: #FF5252; font-weight: bold; font-size: 16px;")
            QMessageBox.critical(self, "Error Crítico", f"Ocurrió un error irrecuperable:\n\n{resultado}")
        else:
            self.df_resultado = resultado
            self.lbl_estado.setText("✅ Proceso Terminado")
            self.lbl_estado.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 16px;")
        
        self.btn_cerrar.setEnabled(True)
        self.btn_cerrar.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; border-radius: 5px;")