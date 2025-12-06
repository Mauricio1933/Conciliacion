from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
import traceback
from src.logic.CONCILIACIONMAESTRA import ConciliacionMaestra

class WorkerSignals(QObject):

    finished = pyqtSignal(object)                                
    error = pyqtSignal(str)                               

class ConciliacionWorker(QRunnable):

    def __init__(self, df_banco, df_ventas, df_saint):
        super().__init__()
        self.df_banco = df_banco
        self.df_ventas = df_ventas
        self.df_saint = df_saint
        self.signals = WorkerSignals()

    def run(self):
        try:
            conciliador = ConciliacionMaestra(self.df_banco, self.df_ventas, self.df_saint)
            resultado_df = conciliador.ejecutar()
            self.signals.finished.emit(resultado_df)
        except Exception as e:
            error_msg = f"Error en la conciliación:\n{traceback.format_exc()}"
            self.signals.error.emit(error_msg)
