"""
Conciliador de Tarjetas de Débito (TDD/TJD) - Versión Simple
"""

import pandas as pd
from .base_conciliador import BaseConciliador
from ..utils.normalizadores import normalizar_monto, parsear_fecha
from ..utils.validadores import calcular_dias_habiles, calcular_diferencia_porcentual

class TDDConciliador(BaseConciliador):
    
    def __init__(self, estado_cuenta_df, libro_ventas_df):
        super().__init__(estado_cuenta_df, libro_ventas_df)
        self.tipo_pago = "Tarjetas de Débito"
        self.codigo_pago = "TJD"
        
        self.tdd_banco = None
        self.tdd_ventas = None
    
    def filtrar_transacciones(self):
        # Filtrar del banco
        self.tdd_banco = self.estado_cuenta[
            (self.estado_cuenta['Tipo'] == 'NC') &
            (self.estado_cuenta['Descripción'].str.contains('TDD - CARACAS', na=False, case=False))
        ].copy()
        
        # Normalizar datos del banco
        self.tdd_banco['Monto_Normalizado'] = self.tdd_banco['Abono'].apply(normalizar_monto)
        self.tdd_banco['Fecha_Parsed'] = self.tdd_banco['Fecha'].apply(parsear_fecha)
        
        # Filtrar del libro de ventas
        self.tdd_ventas = self.libro_ventas[
            self.libro_ventas['Forma_Pago_1'].str.contains('TJD', na=False) |
            self.libro_ventas['Forma_Pago_2'].str.contains('TJD', na=False)
        ].copy()
        
        print(f"   📊 Banco: {len(self.tdd_banco)} | Libro: {len(self.tdd_ventas)}")
    
    def conciliar(self):
        resultados = []
        
        # Agrupar banco por fecha
        tdd_banco_valido = self.tdd_banco[self.tdd_banco['Fecha_Parsed'].notna()].copy()
        agrupacion_banco = tdd_banco_valido.groupby('Fecha_Parsed').agg({
            'Monto_Normalizado': 'sum',
            'Fecha': 'first'
        }).reset_index()
        
        # Agrupar libro por fecha
        filas_libro = []
        for idx, row in self.tdd_ventas.iterrows():
            es_tjd_1 = 'TJD' in str(row.get('Forma_Pago_1', ''))
            es_tjd_2 = 'TJD' in str(row.get('Forma_Pago_2', ''))
            
            fecha_parsed = parsear_fecha(row.get('Fecha_Pago_1', '')) if es_tjd_1 else parsear_fecha(row.get('Fecha_Pago_2', ''))
            if fecha_parsed:
                monto = float(row.get('Monto_Total', 0))
                filas_libro.append({'Fecha_Parsed': fecha_parsed, 'Monto': monto, 'Nro_Control': row.get('Nro_Control', '')})
        
        df_libro = pd.DataFrame(filas_libro)
        
        if len(df_libro) > 0:
            agrupacion_libro = df_libro.groupby('Fecha_Parsed').agg({
                'Monto': 'sum',
                'Nro_Control': 'first'
            }).reset_index()
            
            for idx, row_libro in agrupacion_libro.iterrows():
                fecha_libro = row_libro['Fecha_Parsed']
                monto_libro = row_libro['Monto']
                nro_control = row_libro['Nro_Control']
                
                estado = "Pendiente en Banco"
                
                # Buscar match en banco
                for idx_banco, row_banco in agrupacion_banco.iterrows():
                    fecha_banco = row_banco['Fecha_Parsed']
                    monto_banco = row_banco['Monto_Normalizado']
                    
                    if fecha_banco > fecha_libro:
                        dias = calcular_dias_habiles(fecha_libro, fecha_banco)
                        if 1 <= dias <= 6:
                            diff = calcular_diferencia_porcentual(monto_libro, monto_banco)
                            if -1 <= diff <= 3.5:
                                estado = f"Conciliado - Comisión {diff:.2f}%"
                                break
                
                resultados.append({
                    'Tipo': self.tipo_pago,
                    'Nro_Control': nro_control,
                    'Fecha': fecha_libro.strftime('%d/%m/%Y'),
                    'Referencia': '',
                    'Descripcion': 'TDD - CARACAS',
                    'Monto': monto_libro,
                    'Estado': estado
                })
        
        self.resultados = pd.DataFrame(resultados)
        
        if not self.resultados.empty:
            self.resultados['Monto'] = self.resultados['Monto'].round(2)
