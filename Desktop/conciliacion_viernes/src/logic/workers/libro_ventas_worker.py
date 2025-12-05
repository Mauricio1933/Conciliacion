from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
from src.logic.Libro_ventas_to_csv import LibroVentasCsv

class WorkerSignals(QObject):

    finished = pyqtSignal(str)
    error = pyqtSignal(str)

class LibroVentasWorker(QRunnable):

    def __init__(self, excel_path: str, banco_filtro: str = 'BANCARIBE'):
        super().__init__()
        self.excel_path = excel_path
        self.banco_filtro = banco_filtro
        self.signals = WorkerSignals()

    def run(self):
        """Ejecuta la tarea de conversión y limpieza."""
        try:
            procesador = LibroVentasCsv(excel_path=self.excel_path, banco_filtro=self.banco_filtro)
            csv_final_path = procesador.ejecutar()
            
            self.signals.finished.emit(str(csv_final_path))
        except Exception as e:
            error_msg = f"Ocurrió un error al procesar el Libro de Ventas:\n{e}"
            self.signals.error.emit(error_msg)