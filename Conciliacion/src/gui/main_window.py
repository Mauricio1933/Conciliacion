import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox)
from PyQt6.QtGui import QFont, QIcon

from .widgets.file_card import TarjetaArchivo
from ..logic.reconciliation import iniciar_proceso_conciliacion

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def load_styles(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        general_style_path = os.path.join(base_path, '..', '..', 'assets', 'styles', 'general.qss')
        main_window_style_path = os.path.join(base_path, '..', '..', 'assets', 'styles', 'main_window.qss')
        
        styles = ""
        try:
            with open(general_style_path, "r") as f:
                styles += f.read()
            with open(main_window_style_path, "r") as f:
                styles += f.read()
            self.setStyleSheet(styles)
        except FileNotFoundError:
            print("Advertencia: No se encontraron los archivos de estilo.")

    def init_ui(self):
        self.setWindowTitle("Sistema De Conciliaciones Bancarias")
        self.setFixedSize(1000, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(70)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        titulo = QLabel("Sistema De Conciliaciones Bancarias")
        titulo.setObjectName("mainTitle")
        titulo.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        circulos_widget = QWidget()
        circulos_layout = QHBoxLayout()
        circulos_layout.setSpacing(8)
        circulos_layout.setContentsMargins(0, 0, 0, 0)
        
        nombres_circulos = ["circleYellow", "circleBlue", "circleBlack"]
        for nombre in nombres_circulos:
            circulo = QLabel()
            circulo.setObjectName(nombre)
            circulo.setFixedSize(15, 15)
            circulos_layout.addWidget(circulo)
        
        circulos_widget.setLayout(circulos_layout)
        
        header_layout.addWidget(titulo)
        header_layout.addStretch()
        header_layout.addWidget(circulos_widget)
        header.setLayout(header_layout)
        
        menu_bar = QWidget()
        menu_bar.setObjectName("menuBar")
        menu_bar.setFixedHeight(60)
        
        menu_layout = QHBoxLayout()
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)
        
        opciones = ["Reportes", "Usuarios", "Ayuda"]
        for opcion in opciones:
            btn = QPushButton(opcion)
            btn.setObjectName("mainMenuButton")
            btn.setFixedHeight(60)
            btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            menu_layout.addWidget(btn)
        
        menu_layout.addStretch()
        menu_bar.setLayout(menu_layout)
        
        contenido = QWidget()
        contenido.setObjectName("contentArea")
        
        contenido_layout = QVBoxLayout()
        contenido_layout.setContentsMargins(40, 40, 40, 40)
        contenido_layout.setSpacing(30)
        
        tarjetas_layout = QHBoxLayout()
        tarjetas_layout.setSpacing(40)
        
        self.tarjeta1 = TarjetaArchivo("Estado De\nCuenta", self)
        self.tarjeta2 = TarjetaArchivo("Libro de\nVentas", self)
        self.tarjeta3 = TarjetaArchivo("Registro\nSAINT", self)
        
        tarjetas_layout.addWidget(self.tarjeta1)
        tarjetas_layout.addWidget(self.tarjeta2)
        tarjetas_layout.addWidget(self.tarjeta3)
        
        contenido_layout.addLayout(tarjetas_layout)
        
        btn_conciliar_container = QHBoxLayout()
        self.btn_conciliar = QPushButton("Conciliar")
        self.btn_conciliar.setObjectName("conciliateButton")
        self.btn_conciliar.setFixedSize(250, 60)
        self.btn_conciliar.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.btn_conciliar.setEnabled(False)
        self.btn_conciliar.clicked.connect(self.iniciar_conciliacion)
        
        btn_conciliar_container.addStretch()
        btn_conciliar_container.addWidget(self.btn_conciliar)
        btn_conciliar_container.addStretch()
        
        contenido_layout.addLayout(btn_conciliar_container)
        contenido_layout.addStretch()
        
        contenido.setLayout(contenido_layout)
        main_layout.addWidget(header)
        main_layout.addWidget(menu_bar)
        main_layout.addWidget(contenido)
        
        central_widget.setLayout(main_layout)
        self.load_styles()
    
    def verificar_archivos_cargados(self):
        if (self.tarjeta1.archivo_cargado and 
            self.tarjeta2.archivo_cargado and 
            self.tarjeta3.archivo_cargado):
            self.btn_conciliar.setEnabled(True)

    def iniciar_conciliacion(self):
        ruta_estado_cuenta = self.tarjeta1.ruta_archivo
        ruta_libro_ventas = self.tarjeta2.ruta_archivo
        ruta_saint = self.tarjeta3.ruta_archivo

        resultado = iniciar_proceso_conciliacion(
            ruta_estado_cuenta,
            ruta_libro_ventas,
            ruta_saint
        )

        QMessageBox.information(self, "Conciliación Completada", resultado)