from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
from src.logic.Registro_saint_to_csv import RegistroSaintCsv

class WorkerSignals(QObject):

    finished = pyqtSignal(str)
    error = pyqtSignal(str)

class SaintWorker(QRunnable):

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.signals = WorkerSignals()

    def run(self):

        try:
            procesador = RegistroSaintCsv(excel_path=self.file_path)
            csv_final_path = procesador.ejecutar()
            self.signals.finished.emit(str(csv_final_path))
        except Exception as e:
            error_msg = f"Ocurrió un error al procesar el Registro SAINT:\n{e}"
            self.signals.error.emit(error_msg)