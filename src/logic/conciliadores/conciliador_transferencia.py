"""
Conciliador de Transferencias (TRA) - Versión Simple
"""

import pandas as pd
from .base_conciliador import BaseConciliador
from ..utils.normalizadores import normalizar_monto, normalizar_referencia, parsear_fecha

class TransferenciaConciliador(BaseConciliador):
    
    def __init__(self, estado_cuenta_df, libro_ventas_df):
        super().__init__(estado_cuenta_df, libro_ventas_df)
        self.tipo_pago = "Transferencias"
        self.codigo_pago = "TRA"
        
        self.tra_banco = None
        self.tra_ventas = None
    
    def filtrar_transacciones(self):
        # Filtrar del banco
        self.tra_banco = self.estado_cuenta[
            self.estado_cuenta['Descripción'].str.contains('TRANSFERENCIA', na=False, case=False)
        ].copy()
        
        # Normalizar datos del banco
        self.tra_banco['Monto_Normalizado'] = self.tra_banco['Abono'].apply(normalizar_monto)
        self.tra_banco['Ref_Normalizada'] = self.tra_banco['Referencia'].apply(normalizar_referencia)
        
        # Filtrar del libro de ventas
        self.tra_ventas = self.libro_ventas[
            self.libro_ventas['Forma_Pago_1'].str.contains('TRA', na=False) |
            self.libro_ventas['Forma_Pago_2'].str.contains('TRA', na=False)
        ].copy()
        
        print(f"   📊 Banco: {len(self.tra_banco)} | Libro: {len(self.tra_ventas)}")
    
    def conciliar(self):
        resultados = []
        
        for idx, row in self.tra_ventas.iterrows():
            es_tra_1 = 'TRA' in str(row.get('Forma_Pago_1', ''))
            es_tra_2 = 'TRA' in str(row.get('Forma_Pago_2', ''))
            
            if es_tra_1:
                ref_ventas = normalizar_referencia(row.get('Referencia_1', ''))
                fecha_pago = row.get('Fecha_Pago_1', '')
            elif es_tra_2:
                ref_ventas = normalizar_referencia(row.get('Referencia_2', ''))
                fecha_pago = row.get('Fecha_Pago_2', '')
            else:
                continue
            
            nro_control = row.get('Nro_Control', '')
            monto_ventas = float(row.get('Monto_Total', 0))
            
            # Buscar en el banco
            encontrado = False
            for idx_banco, row_banco in self.tra_banco.iterrows():
                ref_banco = row_banco['Ref_Normalizada']
                
                if ref_ventas and ref_banco and ref_ventas == ref_banco:
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
                'Descripcion': 'TRANSFERENCIA',
                'Monto': monto_ventas,
                'Estado': estado
            })
        
        self.resultados = pd.DataFrame(resultados)
        
        if not self.resultados.empty:
            self.resultados['Monto'] = self.resultados['Monto'].round(2)
