import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

#prueba 1

class TarjetaArchivo(QWidget):
    def __init__(self, titulo, ventana_principal):
        super().__init__()
        self.archivo_cargado = False
        self.titulo = titulo
        self.ventana_principal = ventana_principal
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Tarjeta principal
        self.tarjeta = QWidget()
        self.tarjeta.setFixedSize(280, 280)
        self.tarjeta.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #FFE4A3, stop:1 #FFD666);
                border: 8px solid #FFA500;
                border-radius: 25px;
            }
        """)
        
        tarjeta_layout = QVBoxLayout()
        tarjeta_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Título
        self.label_titulo = QLabel(self.titulo)
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.label_titulo.setStyleSheet("background: transparent; color: #000000;")
        self.label_titulo.setWordWrap(True)
        
        # Label para mostrar estado de carga
        self.label_estado = QLabel("")
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_estado.setFont(QFont("Arial", 11))
        self.label_estado.setStyleSheet("background: transparent; color: #006400;")
        self.label_estado.setWordWrap(True)
        
        tarjeta_layout.addWidget(self.label_titulo)
        tarjeta_layout.addWidget(self.label_estado)
        self.tarjeta.setLayout(tarjeta_layout)
        
        # Botón Importar
        self.btn_importar = QPushButton("Importar")
        self.btn_importar.setFixedSize(180, 45)
        self.btn_importar.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.btn_importar.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #000000;
                border: 2px solid #CCCCCC;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """)
        self.btn_importar.clicked.connect(self.importar_archivo)
        
        layout.addWidget(self.tarjeta, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.btn_importar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
    
    def importar_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo Excel",
            "",
            "Archivos Excel (*.xlsx)"
        )
        
        if archivo:
            self.archivo_cargado = True
            self.label_estado.setText("✓ Archivo cargado correctamente")
            # Notificar a la ventana principal
            self.ventana_principal.verificar_archivos_cargados()

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Sistema De Conciliaciones Bancarias")
        self.setFixedSize(1000, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header blanco
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("background-color: #FFFFFF;")
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        # Título
        titulo = QLabel("Sistema De Conciliaciones Bancarias")
        titulo.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        titulo.setStyleSheet("color: #000000;")
        
        # Círculos decorativos
        circulos_widget = QWidget()
        circulos_layout = QHBoxLayout()
        circulos_layout.setSpacing(8)
        circulos_layout.setContentsMargins(0, 0, 0, 0)
        
        colores = ["#FFD700", "#4A90E2", "#000000"]
        for color in colores:
            circulo = QLabel()
            circulo.setFixedSize(15, 15)
            circulo.setStyleSheet(f"""
                background-color: {color};
                border-radius: 7px;
            """)
            circulos_layout.addWidget(circulo)
        
        circulos_widget.setLayout(circulos_layout)
        
        header_layout.addWidget(titulo)
        header_layout.addStretch()
        header_layout.addWidget(circulos_widget)
        header.setLayout(header_layout)
        
        # Barra de menú negra
        menu_bar = QWidget()
        menu_bar.setFixedHeight(60)
        menu_bar.setStyleSheet("background-color: #000000;")
        
        menu_layout = QHBoxLayout()
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)
        
        opciones = ["Reportes", "Usuarios", "Ayuda"]
        for opcion in opciones:
            btn = QPushButton(opcion)
            btn.setFixedHeight(60)
            btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #000000;
                    color: #FFA500;
                    border: none;
                    border-right: 2px solid #333333;
                    padding: 0 40px;
                }
                QPushButton:hover {
                    background-color: #1a1a1a;
                }
            """)
            menu_layout.addWidget(btn)
        
        menu_layout.addStretch()
        menu_bar.setLayout(menu_layout)
        
        # Área de contenido negra
        contenido = QWidget()
        contenido.setStyleSheet("background-color: #000000;")
        
        contenido_layout = QVBoxLayout()
        contenido_layout.setContentsMargins(40, 40, 40, 40)
        contenido_layout.setSpacing(30)
        
        # Tarjetas
        tarjetas_layout = QHBoxLayout()
        tarjetas_layout.setSpacing(40)
        
        self.tarjeta1 = TarjetaArchivo("Estado De\nCuenta", self)
        self.tarjeta2 = TarjetaArchivo("Libro de\nVentas", self)
        self.tarjeta3 = TarjetaArchivo("Registro\nSAINT", self)
        
        tarjetas_layout.addWidget(self.tarjeta1)
        tarjetas_layout.addWidget(self.tarjeta2)
        tarjetas_layout.addWidget(self.tarjeta3)
        
        contenido_layout.addLayout(tarjetas_layout)
        
        # Botón Conciliar
        btn_conciliar_container = QHBoxLayout()
        self.btn_conciliar = QPushButton("Conciliar")
        self.btn_conciliar.setFixedSize(250, 60)
        self.btn_conciliar.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.btn_conciliar.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: #333333;
                border: none;
                border-radius: 10px;
            }
        """)
        self.btn_conciliar.setEnabled(False)
        
        btn_conciliar_container.addStretch()
        btn_conciliar_container.addWidget(self.btn_conciliar)
        btn_conciliar_container.addStretch()
        
        contenido_layout.addLayout(btn_conciliar_container)
        contenido_layout.addStretch()
        
        contenido.setLayout(contenido_layout)
        
        # Agregar todo al layout principal
        main_layout.addWidget(header)
        main_layout.addWidget(menu_bar)
        main_layout.addWidget(contenido)
        
        central_widget.setLayout(main_layout)
    
    def verificar_archivos_cargados(self):
        if (self.tarjeta1.archivo_cargado and 
            self.tarjeta2.archivo_cargado and 
            self.tarjeta3.archivo_cargado):
            self.btn_conciliar.setStyleSheet("""
                QPushButton {
                    background-color: #FFA500;
                    color: #000000;
                    border: none;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #FF8C00;
                }
                QPushButton:pressed {
                    background-color: #FF7700;
                }
            """)
            self.btn_conciliar.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())