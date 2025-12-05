import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import pandas as pd


class ReportePDFGenerator: 
    def __init__(self, df_resultado, output_path, timestamp=None):
        self.df_resultado = df_resultado
        self.output_path = output_path
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1E1E1E'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#4A4A4A'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
    
    def generar(self):
        try:
            doc = SimpleDocTemplate(
                self.output_path,
                pagesize=A4,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )
            
            story = []
            story.extend(self._create_header())
            story.extend(self._create_summary())
            story.extend(self._create_results_table())
            
            doc.build(story)
            return True
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
    
    def _create_header(self):
        elements = []
        
        title = Paragraph(
            "Unidad Educativa Colegio Salesiano Pio XII",
            self.styles['CustomTitle']
        )
        elements.append(title)
        
        subtitle = Paragraph(
            "Reporte de Conciliación Bancaria",
            self.styles['CustomSubtitle']
        )
        elements.append(subtitle)
        
        fecha = Paragraph(
            f"<b>Fecha de Generación:</b> {self.timestamp}",
            self.styles['Normal']
        )
        elements.append(fecha)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_summary(self):
        """Crea el resumen de estadísticas de la conciliación."""
        elements = []
        
        if self.df_resultado is None or self.df_resultado.empty:
            return elements
        
        total_registros = len(self.df_resultado)
        conciliados = len(self.df_resultado[self.df_resultado['Estado'] == 'Conciliado'])
        pendientes_banco = len(self.df_resultado[self.df_resultado['Estado'] == 'Pendiente en Banco'])
        pendientes_libro = len(self.df_resultado[self.df_resultado['Estado'].str.contains('Pendiente en Libro', na=False)])
        pendientes_saint = len(self.df_resultado[self.df_resultado['Estado'].str.contains('Pendiente en SAINT', na=False)])
        revision = len(self.df_resultado[self.df_resultado['Estado'].str.contains('Revisión|Error', na=False)])
        
        section_title = Paragraph("Resumen de Conciliación", self.styles['SectionTitle'])
        elements.append(section_title)
        
        summary_data = [
            ['Total de Registros:', str(total_registros)],
            ['Conciliados:', f"{conciliados} ({conciliados/total_registros*100:.1f}%)" if total_registros > 0 else "0"],
            ['Pendientes en Banco:', str(pendientes_banco)],
            ['Pendientes en Libro de Ventas:', str(pendientes_libro)],
            ['Pendientes en SAINT:', str(pendientes_saint)],
            ['Requieren Revisión:', str(revision)]
        ]
        
        summary_table = Table(summary_data, colWidths=[3.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8E8E8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_results_table(self):
        elements = []
        
        if self.df_resultado is None or self.df_resultado.empty:
            elements.append(Paragraph("No hay datos para mostrar.", self.styles['Normal']))
            return elements
        
        section_title = Paragraph("Detalle de Movimientos", self.styles['SectionTitle'])
        elements.append(section_title)
        
                                                                                                        
        max_rows = 100
        df_display = self.df_resultado.head(max_rows)
        
        headers = ['Fecha', 'Referencia', 'Descripción', 'Cargo', 'Abono', 'SAE', 'SAINT', 'Estado']
        
        table_data = [headers]
        
        for _, row in df_display.iterrows():
            table_data.append([
                str(row.get('Fecha', '')),
                str(row.get('Referencia', ''))[:20],                    
                str(row.get('Descripción', ''))[:30],                    
                self._format_currency(row.get('Cargo', 0)),
                self._format_currency(row.get('Abono', 0)),
                self._format_currency(row.get('SAE (Debe)', 0)),
                self._format_currency(row.get('SAINT (Haber)', 0)),
                str(row.get('Estado', ''))[:20]
            ])
        
                     
        col_widths = [0.8*inch, 1*inch, 1.8*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 1.2*inch]
        results_table = Table(table_data, colWidths=col_widths)
        
                                    
        table_style = [
                        
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
                       
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (3, 1), (6, -1), 'RIGHT'),                         
            ('ALIGN', (0, 1), (2, -1), 'LEFT'),
            ('ALIGN', (7, 1), (7, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            
                    
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
                                   
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F5F5F5')))
        
        results_table.setStyle(TableStyle(table_style))
        elements.append(results_table)
        
                                   
        if len(self.df_resultado) > max_rows:
            nota = Paragraph(
                f"<i>Nota: Se muestran los primeros {max_rows} registros de {len(self.df_resultado)} totales.</i>",
                self.styles['Normal']
            )
            elements.append(Spacer(1, 10))
            elements.append(nota)
        
        return elements
    
    def _format_currency(self, valor):
        """Formatea un valor como moneda."""
        try:
            v = float(str(valor).replace(',', '.'))
            if v == 0:
                return "-"
            return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return str(valor)
