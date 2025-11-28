"""
Conciliador de Pago Móvil (OTR) - Versión Simple
Mantiene la lógica original pero adapta el formato de salida
"""

import pandas as pd
from .base_conciliador import BaseConciliador
from ..utils.normalizadores import normalizar_monto, normalizar_referencia, parsear_fecha
from ..utils.validadores import calcular_diferencia_dias, validar_monto_cercano

class PagoMovilConciliador(BaseConciliador):
    
    def __init__(self, estado_cuenta_df, libro_ventas_df, 
                 tolerancia_monto=0.10, tolerancia_dias=5):
        super().__init__(estado_cuenta_df, libro_ventas_df)
        self.tipo_pago = "Pago Móvil"
        self.codigo_pago = "OTR"
        self.tolerancia_monto = tolerancia_monto
        self.tolerancia_dias = tolerancia_dias
        
        self.pm_banco = None
        self.pm_ventas = None
    
    def filtrar_transacciones(self):
        # Filtrar del banco
        self.pm_banco = self.estado_cuenta[
            self.estado_cuenta['Descripción'].str.contains('PAGO MOVIL', na=False, case=False)
        ].copy()
        
        # Normalizar datos del banco
        self.pm_banco['Monto_Normalizado'] = self.pm_banco['Abono'].apply(normalizar_monto)
        self.pm_banco['Ref_Normalizada'] = self.pm_banco['Referencia'].apply(normalizar_referencia)
        self.pm_banco['Fecha_Parsed'] = self.pm_banco['Fecha'].apply(parsear_fecha)
        
        # Filtrar del libro de ventas
        self.pm_ventas = self.libro_ventas[
            self.libro_ventas['Forma_Pago_1'].str.contains('OTR', na=False) |
            self.libro_ventas['Forma_Pago_2'].str.contains('OTR', na=False)
        ].copy()
        
        # Normalizar datos del libro
        self.pm_ventas['Fecha_Pago_1_Parsed'] = self.pm_ventas['Fecha_Pago_1'].apply(parsear_fecha)
        self.pm_ventas['Fecha_Pago_2_Parsed'] = self.pm_ventas['Fecha_Pago_2'].apply(parsear_fecha)
        
        print(f"   📊 Banco: {len(self.pm_banco)} | Libro: {len(self.pm_ventas)}")
    
    def conciliar(self):
        resultados = []
        
        # Procesar cada entrada del libro de ventas
        for idx, row in self.pm_ventas.iterrows():
            es_otr_1 = 'OTR' in str(row.get('Forma_Pago_1', ''))
            es_otr_2 = 'OTR' in str(row.get('Forma_Pago_2', ''))
            
            if es_otr_1:
                ref_ventas = normalizar_referencia(row.get('Referencia_1', ''))
                fecha_pago = row.get('Fecha_Pago_1', '')
                fecha_parsed = row['Fecha_Pago_1_Parsed']
            elif es_otr_2:
                ref_ventas = normalizar_referencia(row.get('Referencia_2', ''))
                fecha_pago = row.get('Fecha_Pago_2', '')
                fecha_parsed = row['Fecha_Pago_2_Parsed']
            else:
                continue
            
            nro_control = row.get('Nro_Control', '')
            monto_ventas = float(row.get('Monto_Total', 0))
            
            # Buscar coincidencias en el banco
            encontrado = False
            
            for idx_banco, row_banco in self.pm_banco.iterrows():
                ref_banco = row_banco['Ref_Normalizada']
                monto_banco = row_banco['Monto_Normalizado']
                fecha_banco = row_banco['Fecha']
                
                if ref_ventas and ref_banco and ref_ventas in ref_banco:
                    if validar_monto_cercano(monto_ventas, monto_banco, self.tolerancia_monto):
                        encontrado = True
                        estado = "Conciliado"
                        break
            
            if not encontrado:
                estado = "Pendiente en Banco"
            
            resultados.append({
                'Tipo': self.tipo_pago,
                'Nro_Control': nro_control,
                'Fecha': fecha_pago,
                'Referencia': ref_ventas if ref_ventas else '[NO ENCONTRADA]',
                'Descripcion': 'PAGO MOVIL',
                'Monto': monto_ventas,
                'Estado': estado
            })
        
        self.resultados = pd.DataFrame(resultados)
        
        if not self.resultados.empty:
            self.resultados['Monto'] = self.resultados['Monto'].round(2)
