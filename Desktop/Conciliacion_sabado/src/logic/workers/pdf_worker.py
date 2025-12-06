from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
import traceback
import sys

from src.logic.convert_pdf_csv import EstadoDeCuentaPdfToCsv

class WorkerSignals(QObject):

    finished = pyqtSignal(str, dict)                                                         
    error = pyqtSignal(str)                                


class PdfConverterWorker(QRunnable):

    def __init__(self, pdf_path: str):
        super().__init__()
        self.pdf_path = pdf_path
        self.signals = WorkerSignals()

    def run(self):

        try:
                                                  
            converter = EstadoDeCuentaPdfToCsv(pdf_path=self.pdf_path)
                                                 
            csv_path, resumen = converter.ejecutar()
            
                                                                 
            self.signals.finished.emit(str(csv_path), resumen if resumen else {})
            
        except Exception as e:
                                          
            error_msg = f"Ocurrió un error al procesar el PDF:\n{e}"
                                      
            self.signals.error.emit(error_msg)