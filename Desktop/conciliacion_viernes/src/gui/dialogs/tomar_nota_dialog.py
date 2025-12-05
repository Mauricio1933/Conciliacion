import os
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QFrame, QScrollArea, QMessageBox, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from src.gui.widgets.barra_custom import CustomTitleBar

class TomarNotaDialog(QDialog):

    windowStateChanged = pyqtSignal(Qt.WindowState)
    
    def __init__(self, datos_fila, parent=None, ruta_notas=None):
        super().__init__(parent)
        self.datos_fila = datos_fila
        
                                                                     
        if ruta_notas and os.path.isdir(ruta_notas):
                                       
             self.ruta_carpeta = os.path.join(ruta_notas, "notas")
             os.makedirs(self.ruta_carpeta, exist_ok=True)
             
             self.ruta_txt = os.path.join(self.ruta_carpeta, "notas_conciliacion.txt")
             self.ruta_pdf = os.path.join(self.ruta_carpeta, "Notas_Conciliacion.pdf")
        else:
                                                               
            self.ruta_txt = self._get_default_notas_path()
            self.ruta_carpeta = os.path.dirname(self.ruta_txt)
            self.ruta_pdf = os.path.join(self.ruta_carpeta, "Notas_Conciliacion.pdf")
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(700, 600)
        
        self.init_ui()
        
    def _get_default_notas_path(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.abspath(os.path.join(base_path, "../../../../data_files/conciliaciones/general/notas"))
        os.makedirs(data_path, exist_ok=True)
        return os.path.join(data_path, "notas_conciliacion.txt")
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        title_bar = CustomTitleBar(self)
        title_bar.setFixedHeight(40)
        main_layout.addWidget(title_bar)
        
        content_widget = QFrame()
        content_widget.setObjectName("NotaDialogContent")
        content_widget.setStyleSheet("""
            #NotaDialogContent {
                background-color: #1E1E1E;
                border: 1px solid #333;
                border-top: none;
                border-radius: 0px 0px 10px 10px;
            }
            QLabel { color: #E0E0E0; font-family: 'Inter'; }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
                
        lbl_titulo = QLabel("📝 Tomar Nota")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFD700;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(lbl_titulo)
        
                   
        info_group = QFrame()
        info_group.setStyleSheet("background-color: #252525; border-radius: 6px; padding: 10px;")
        info_layout = QVBoxLayout(info_group)
        
        lbl_sub = QLabel("Detalles del Registro Seleccionado:")
        lbl_sub.setStyleSheet("font-weight: bold; color: #BBB; margin-bottom: 5px;")
        info_layout.addWidget(lbl_sub)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(5)
        
        for k, v in self.datos_fila.items():
            row_layout = QHBoxLayout()
            lbl_k = QLabel(f"{k}:")
            lbl_k.setStyleSheet("font-weight: bold; color: #888; min-width: 100px;")
            lbl_v = QLabel(str(v))
            lbl_v.setStyleSheet("color: white;")
            lbl_v.setWordWrap(True)
            row_layout.addWidget(lbl_k)
            row_layout.addWidget(lbl_v, 1)
            scroll_layout.addLayout(row_layout)
            
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        scroll.setMaximumHeight(200)
        info_layout.addWidget(scroll)
        
        content_layout.addWidget(info_group)
        
                    
        lbl_input = QLabel("Nota / Observación:")
        lbl_input.setStyleSheet("font-weight: bold; color: #FFD700; margin-top: 5px;")
        content_layout.addWidget(lbl_input)
        
        self.txt_nota = QTextEdit()
        self.txt_nota.setPlaceholderText("Escriba su nota aquí...")
        self.txt_nota.setStyleSheet("""
            QTextEdit {
                background-color: #2D2D2D;
                color: white;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 1px solid #FFD700;
            }
        """)
        content_layout.addWidget(self.txt_nota)
        
                 
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #505050; }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Guardar Nota")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: black;
                font-weight: bold;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #FFE57F; }
        """)
        btn_save.clicked.connect(self.guardar_nota)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        content_layout.addLayout(btn_layout)
        
        main_layout.addWidget(content_widget)

    def guardar_nota(self):
        nota = self.txt_nota.toPlainText().strip()
        if not nota:
            QMessageBox.warning(self, "Atención", "La nota no puede estar vacía.")
            return
            
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            entry = f"\n{'='*50}\n"
            entry += f"FECHA: {timestamp}\n"
            entry += f"{'-'*50}\n"
            entry += "DATOS DEL REGISTRO:\n"
            for k, v in self.datos_fila.items():
                entry += f"  {k}: {v}\n"
            entry += f"{'-'*50}\n"
            entry += "NOTA:\n"
            entry += f"{nota}\n"
            entry += f"{'='*50}\n"
            
                                                         
            with open(self.ruta_txt, "a", encoding="utf-8") as f:
                f.write(entry)
            
                                     
            self.generar_pdf_notas()
                
            QMessageBox.information(self, "Éxito", f"Nota guardada y PDF actualizado.\n\nUbicación: {self.ruta_pdf}")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la nota:\n{e}")

    def generar_pdf_notas(self):
        """Lee el archivo TXT acumulado y genera un PDF bien formateado."""
        if not os.path.exists(self.ruta_txt):
            return

        try:
            doc = SimpleDocTemplate(self.ruta_pdf, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

                    
            title_style = styles['Title']
            story.append(Paragraph("Notas de Conciliación", title_style))
            story.append(Spacer(1, 12))

                                          
            with open(self.ruta_txt, "r", encoding="utf-8") as f:
                content = f.read()

                      
            body_style = styles['BodyText']
            code_style = ParagraphStyle('Code', parent=styles['BodyText'], fontName='Courier', fontSize=8)

                               
            notas = content.split('='*50)
            
            for nota_raw in notas:
                if not nota_raw.strip(): continue
                
                lines = nota_raw.strip().split('\n')
                fecha = ""
                datos = []
                texto_nota = []
                
                mode = "header"                      
                
                for line in lines:
                    if "FECHA:" in line:
                        fecha = line.replace("FECHA:", "").strip()
                    elif "DATOS DEL REGISTRO:" in line:
                        mode = "datos"
                    elif "NOTA:" in line:
                        mode = "nota"
                    elif "-"*50 in line:
                        continue
                    else:
                        if mode == "datos":
                            if line.strip(): datos.append(line.strip())
                        elif mode == "nota":
                            if line.strip(): texto_nota.append(line.strip())

                                
                if fecha:
                    story.append(Paragraph(f"<b>Fecha de Nota:</b> {fecha}", body_style))
                    story.append(Spacer(1, 6))
                
                if datos:
                    story.append(Paragraph("<b>Detalles del Movimiento:</b>", body_style))
                    for d in datos:
                        story.append(Paragraph(d, code_style))
                    story.append(Spacer(1, 6))
                
                if texto_nota:
                    story.append(Paragraph("<b>Observación:</b>", body_style))
                    full_nota = "<br/>".join(texto_nota)
                    story.append(Paragraph(full_nota, body_style))
                
                story.append(Spacer(1, 12))
                story.append(Paragraph("_" * 60, body_style))
                story.append(Spacer(1, 12))

            doc.build(story)
            
        except Exception as e:
            print(f"Error generando PDF de notas: {e}")
                                                                                         

    def changeEvent(self, event):
        """ Maneja cambios de estado de la ventana (maximizar/restaurar). """
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self.windowStateChanged.emit(self.windowState())
