import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class TarjetaArchivo(QWidget):
    def __init__(self, titulo, ventana_principal):
        super().__init__()
        self.archivo_cargado = False
        self.ruta_archivo = None
        self.titulo = titulo
        self.ventana_principal = ventana_principal
        self.init_ui()
    
    def load_styles(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        style_path = os.path.join(base_path, '..', '..', '..', 'assets', 'styles', 'file_card.qss')
        try:
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Advertencia: No se encontró el archivo de estilo en {style_path}")

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        self.tarjeta = QWidget()
        self.tarjeta.setObjectName("fileCard")
        self.tarjeta.setFixedSize(280, 280)
        
        tarjeta_layout = QVBoxLayout()
        tarjeta_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.label_titulo = QLabel(self.titulo)
        self.label_titulo.setObjectName("fileCardTitle")
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.label_titulo.setWordWrap(True)
        
        self.label_estado = QLabel("")
        self.label_estado.setObjectName("fileCardStatus")
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_estado.setFont(QFont("Arial", 11))
        self.label_estado.setWordWrap(True)
        
        tarjeta_layout.addWidget(self.label_titulo)
        tarjeta_layout.addWidget(self.label_estado)
        self.tarjeta.setLayout(tarjeta_layout)
        
        self.btn_importar = QPushButton("Importar")
        self.btn_importar.setObjectName("importButton")
        self.btn_importar.setFixedSize(180, 45)
        self.btn_importar.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.btn_importar.clicked.connect(self.importar_archivo)
        
        layout.addWidget(self.tarjeta, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.btn_importar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
        self.load_styles()
    
    def importar_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo Excel",
            "",
            "Archivos Excel (*.xlsx)"
        )
        
        if archivo:
            self.archivo_cargado = True
            self.ruta_archivo = archivo
            self.label_estado.setText("✓ Archivo cargado correctamente")
            self.ventana_principal.verificar_archivos_cargados()