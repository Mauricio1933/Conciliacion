                       
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

class ConciliacionMaestra:
    def __init__(self, df_banco, df_ventas, df_saint):
        self.df_banco = df_banco.copy()
        self.df_ventas = df_ventas.copy()
        self.df_saint = df_saint.copy()
        
        self.resultados = []
        self.indices_banco_conciliados = set()

                                              
        if not self.df_banco.empty:
            mask_basura = self.df_banco['Referencia'].astype(str).str.upper().isin(['FIN', 'DIA', 'SALDO', 'TOTAL', 'PAGINA'])
            self.df_banco = self.df_banco[~mask_basura].copy()
            
            mask_monto_basura = (
                self.df_banco['Cargo'].astype(str).str.contains('FIN', case=False, na=False) | 
                self.df_banco['Abono'].astype(str).str.contains('FIN', case=False, na=False)
            )
            self.df_banco = self.df_banco[~mask_monto_basura].copy()
            self.df_banco = self.df_banco.reset_index(drop=True)

                                               
        self.fecha_corte = None 
        self.mes_banco_tuple = None 

        if not self.df_banco.empty:
            fechas_banco = self.df_banco['Fecha'].apply(self.estandarizar_fecha).dropna()
            if not fechas_banco.empty:
                self.fecha_corte = fechas_banco.max()
                meses = fechas_banco.apply(lambda x: (x.year, x.month))
                self.mes_banco_tuple = meses.mode()[0] 
                                                                              
    def normalizar_monto(self, monto):

        try:
                                                      
            if isinstance(monto, (int, float)): 
                return float(monto)
            
                                 
            if pd.isna(monto) or str(monto).strip() == '': 
                return 0.0
            
                              
            monto_str = str(monto).replace('"', '').replace("'", "").strip()
            
                                              
            if ',' in monto_str and '.' in monto_str:
                                                                             
                return float(monto_str.replace('.', '').replace(',', '.'))
            elif ',' in monto_str:
                                                          
                return float(monto_str.replace(',', '.'))
            else:
                                                                              
                return float(monto_str)
                
        except ValueError:
            return 0.0

    def normalizar_ref(self, ref):
        if pd.isna(ref): return ''
        return str(ref).strip().replace('.0', '').replace('310', '')[-6:]

    def estandarizar_fecha(self, f):
        try:
            if pd.isna(f) or str(f).strip() == '': return None
            if len(str(f)) < 5: return None
            
            f_str = str(f).strip()
            
                                           
            if '/' in f_str: 
                return datetime.strptime(f_str, '%d/%m/%Y')
            
                                                          
            if '-' in f_str:
                                                  
                meses_es = {
                    'ENE': '01', 'FEB': '02', 'MAR': '03', 'ABR': '04',
                    'MAY': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
                    'SEP': '09', 'OCT': '10', 'NOV': '11', 'DIC': '12'
                }
                partes = f_str.split('-')
                if len(partes) == 3 and partes[1].upper() in meses_es:
                    dia = partes[0]
                    mes = meses_es[partes[1].upper()]
                    año = partes[2]
                    return datetime.strptime(f"{dia}/{mes}/{año}", '%d/%m/%Y')
                
                                                       
                return datetime.strptime(f_str, '%d-%b-%Y')
            
            return None
        except: 
            return None

    def fecha_str(self, f_obj):
        return f_obj.strftime('%d/%m/%Y') if f_obj else ""

    def calcular_dias(self, f1, f2):
        if not f1 or not f2: return 999
        return abs((f1 - f2).days)

    def calcular_dias_habiles(self, f_inicio, f_fin):
        if not f_inicio or not f_fin or f_inicio > f_fin: return -1
        dias = 0
        curr = f_inicio + timedelta(days=1)
        while curr <= f_fin:
            if curr.weekday() < 5: dias += 1
            curr += timedelta(days=1)
        return dias
    
    def limpiar_texto(self, texto):
        if not isinstance(texto, str): return str(texto)
        texto = ' '.join(texto.split())
        return texto.replace("MOVIL MOVIL", "MOVIL")

    def calcular_diferencia_porcentual(self, monto_libro, monto_banco):
        if monto_libro == 0: return 0
        return ((monto_libro - monto_banco) / monto_libro) * 100

                                                                               
                                
                                                                               
    def conciliar_pago_movil(self):
        print("   -> Ejecutando Pago Móvil...")
                                                        
        ventas = self.df_ventas[
            self.df_ventas['Forma_Pago_1'].str.contains('OTR', na=False) |
            self.df_ventas['Forma_Pago_2'].str.contains('OTR', na=False)
        ]
        banco = self.df_banco[
            (self.df_banco['Tipo'] == 'NC') & 
            (self.df_banco['Descripción'].str.contains('PAGO MOVIL', na=False))
        ]
        mes_banco = None
        if self.fecha_corte: mes_banco = (self.fecha_corte.year, self.fecha_corte.month)

        for idx, row in ventas.iterrows():
            es_1 = 'OTR' in str(row.get('Forma_Pago_1', ''))
            ref = self.normalizar_ref(row['Referencia_1'] if es_1 else row['Referencia_2'])
            fecha = self.estandarizar_fecha(row['Fecha_Pago_1'] if es_1 else row['Fecha_Pago_2'])
            monto = self.normalizar_monto(row['Monto_Total'])
            ctrl = row['Nro_Control']

            if mes_banco and fecha:
                if (fecha.year, fecha.month) < mes_banco:
                    self._agregar_resultado(ctrl, self.fecha_str(fecha), ref, f"Pago Móvil (Ref: {ref})", monto, "Pendiente - Mes Anterior", "OTR")
                    continue

            match = False
            for idx_b, row_b in banco.iterrows():
                if idx_b in self.indices_banco_conciliados: continue
                ref_b = self.normalizar_ref(row_b['Referencia'])
                monto_b = self.normalizar_monto(row_b['Abono'])
                fecha_b = self.estandarizar_fecha(row_b['Fecha'])

                if ref in ref_b and abs(monto_b - monto) < 0.10:
                                                                               
                                                                                                  
                    if not fecha or not fecha_b:
                        continue                                          
                    
                    dias_diff = (fecha_b - fecha).days                      
                    
                                                                            
                    if dias_diff < -1:
                        continue                                                
                    
                                                                     
                    if dias_diff > 5:
                        continue                                            
                    
                    desc_limpia = self.limpiar_texto(row_b['Descripción'])
                    
                                                           
                    if dias_diff == 0:
                        estado = "Conciliado"
                    elif 1 <= dias_diff <= 5:
                        estado = "Conciliado"
                        desc_limpia += f" (Realizado el {self.fecha_str(fecha)})"
                    elif dias_diff == -1:
                        estado = "Conciliado"
                        desc_limpia += f" [⚠️ BANCO 1 DÍA ADELANTADO - Verificar fecha SAE]"
                    else:
                        estado = "Requiere Revisión - Fecha Lejana"
                        desc_limpia += f" (Dif: {abs(dias_diff)} días)"

                    self.indices_banco_conciliados.add(idx_b)
                    self._agregar_resultado(ctrl, self.fecha_str(fecha_b), row_b['Referencia'], desc_limpia, monto_b, estado, "OTR", orden_interno=1)
                                                                            
                    if idx_b + 1 in self.df_banco.index:
                        fila_sig = self.df_banco.loc[idx_b + 1]                            
                        if 'COMISION' in str(fila_sig['Descripción']).upper():
                            self._agregar_resultado(ctrl, fila_sig['Fecha'], fila_sig['Referencia'], self.limpiar_texto(fila_sig['Descripción']), 
                                                  self.normalizar_monto(fila_sig['Cargo']), "Conciliado", "COMISION", orden_interno=2)
                            self.indices_banco_conciliados.add(idx_b + 1)
                    match = True
                    break
            
            if not match:
                self._agregar_resultado(ctrl, self.fecha_str(fecha), "[NO ENCONTRADA]", f"Pago Móvil (Ref: {ref})", monto, "Pendiente en Banco", "OTR")

                                                                               
                                    
                                                                               
    def conciliar_transferencias(self):
        print("   -> Ejecutando Transferencias...")
                                                        
        ventas = self.df_ventas[
            self.df_ventas['Forma_Pago_1'].str.contains('TRA', na=False) |
            self.df_ventas['Forma_Pago_2'].str.contains('TRA', na=False)
        ]
        banco = self.df_banco[
            (self.df_banco['Tipo'] == 'NC') & 
            (self.df_banco['Descripción'].str.contains('TRANSFERENCIA', na=False)) &
            (~self.df_banco['Descripción'].str.contains('PAGO MOVIL', na=False))
        ]
        mes_banco = None
        if self.fecha_corte: mes_banco = (self.fecha_corte.year, self.fecha_corte.month)

        for idx, row in ventas.iterrows():
            es_1 = 'TRA' in str(row.get('Forma_Pago_1', ''))
            ref = self.normalizar_ref(row['Referencia_1'] if es_1 else row['Referencia_2'])
            fecha = self.estandarizar_fecha(row['Fecha_Pago_1'] if es_1 else row['Fecha_Pago_2'])
            monto = self.normalizar_monto(row['Monto_Total'])
            ctrl = row['Nro_Control']

            if mes_banco and fecha:
                if (fecha.year, fecha.month) < mes_banco:
                    self._agregar_resultado(ctrl, self.fecha_str(fecha), "[NO ENCONTRADA]", 
                                          f"Transferencia (Ref: {ref})", monto, "Pendiente - Mes Anterior", "TRA")
                    continue

            match = False
            for idx_b, row_b in banco.iterrows():
                if idx_b in self.indices_banco_conciliados: continue
                ref_b = self.normalizar_ref(row_b['Referencia'])
                monto_b = self.normalizar_monto(row_b['Abono'])
                fecha_b = self.estandarizar_fecha(row_b['Fecha'])

                if len(ref_b) >= 5 and ref.endswith(ref_b[-5:]) and abs(monto_b - monto) < 0.10:
                                                                               
                    if not fecha or not fecha_b:
                        continue
                    
                    dias_diff = (fecha_b - fecha).days
                    
                                                                                          
                    if dias_diff < -1 or dias_diff > 5:
                        continue
                    
                    desc_limpia = self.limpiar_texto(row_b['Descripción'])
                    
                    if dias_diff == 0:
                        estado = "Conciliado"
                    elif 1 <= dias_diff <= 5:
                        estado = "Conciliado"
                        desc_limpia += f" (Realizado el {self.fecha_str(fecha)})"
                    elif dias_diff == -1:
                        estado = "Conciliado"
                        desc_limpia += f" [⚠️ BANCO 1 DÍA ADELANTADO - Verificar fecha SAE]"
                    else:
                        estado = "Requiere Revisión - Fecha Lejana"
                        desc_limpia += f" (Dif: {abs(dias_diff)} días)"

                    self.indices_banco_conciliados.add(idx_b)
                    self._agregar_resultado(ctrl, self.fecha_str(fecha_b), row_b['Referencia'], desc_limpia, monto_b, estado, "TRA")
                    match = True
                    break
            
            if not match:
                self._agregar_resultado(ctrl, self.fecha_str(fecha), "[NO ENCONTRADA]", 
                                      f"Transferencia (Ref: {ref})", monto, "Pendiente en Banco", "TRA")

                                                                               
                                                                      
                                                                               
    def conciliar_tdd(self):
        print("   -> Ejecutando TDD (Lógica Matriz de Candidatos)...")
        
                           
        ventas_tdd = self.df_ventas[
            self.df_ventas['Forma_Pago_1'].str.contains('TJD|TAR|DEB|PUN', na=False) |
            self.df_ventas['Forma_Pago_2'].str.contains('TJD|TAR|DEB|PUN', na=False)
        ].copy()
        
        ventas_tdd['Fecha_Obj'] = ventas_tdd.apply(
            lambda x: self.estandarizar_fecha(x['Fecha_Pago_1'] if 'T' in str(x['Forma_Pago_1']) else x['Fecha_Pago_2']), axis=1
        )
        
                             
        if self.mes_banco_tuple:
            ventas_viejas = ventas_tdd[ventas_tdd['Fecha_Obj'].apply(lambda x: (x.year, x.month) < self.mes_banco_tuple if x else False)]
            ventas_tdd = ventas_tdd[~ventas_tdd.index.isin(ventas_viejas.index)]
            for _, r in ventas_viejas.iterrows():
                self._agregar_resultado(r['Nro_Control'], self.fecha_str(r['Fecha_Obj']), "[NO ENCONTRADA]", 
                                      f"TDD (Ref Libro: {r['Nro_Control']})", self.normalizar_monto(r['Monto_Total']), "Pendiente - Mes Anterior", "TDD")

                       
        libro_grp = ventas_tdd.groupby('Fecha_Obj').agg({
            'Monto_Total': 'sum',
            'Nro_Control': lambda x: list(x)
        }).reset_index()

                           
        banco_tdd = self.df_banco[
            (self.df_banco['Tipo'] == 'NC') & 
            (self.df_banco['Descripción'].str.contains('TDD|PUNTO|POS|CARACAS|LIQUIDACION', na=False))
        ].copy()
        
        banco_tdd['Fecha_Obj'] = banco_tdd['Fecha'].apply(self.estandarizar_fecha)
        
                         
        mapa_indices = {}
        for idx, row in banco_tdd.iterrows():
            f = row['Fecha_Obj']
            if f not in mapa_indices: mapa_indices[f] = []
            mapa_indices[f].append(idx)

                       
        banco_grp = banco_tdd.groupby('Fecha_Obj').agg({'Abono': lambda x: sum(self.normalizar_monto(v) for v in x)}).reset_index()

                                                                       
        todas_coincidencias = []

        for idx_l, row_l in libro_grp.iterrows():
            fecha_l = row_l['Fecha_Obj']
            monto_l = self.normalizar_monto(row_l['Monto_Total'])
            ctls = row_l['Nro_Control']

            for idx_b_grp, row_b_grp in banco_grp.iterrows():
                fecha_b = row_b_grp['Fecha_Obj']
                
                                 
                if fecha_b >= fecha_l:
                    dias = self.calcular_dias_habiles(fecha_l, fecha_b)
                    if 1 <= dias <= 6:
                        monto_b = row_b_grp['Abono']
                        pct = self.calcular_diferencia_porcentual(monto_l, monto_b)
                        
                        todas_coincidencias.append({
                            'fecha_l': fecha_l,
                            'idx_l': idx_l,                         
                            'fecha_b': fecha_b,
                            'idx_b_grp': idx_b_grp,                         
                            'ctls': ctls,
                            'monto_l': monto_l,
                            'monto_b': monto_b,
                            'pct': pct,
                            'dias': dias,
                            'es_valido': -1 <= pct <= 3.5                 
                        })

                                                           
        candidatos_validos = [c for c in todas_coincidencias if c['es_valido']]
                                                               
        candidatos_validos.sort(key=lambda x: (x['dias'], abs(x['pct'])))

        emparejamientos = {}                      
        fechas_banco_usadas = set()                                 

        for c in candidatos_validos:
            if c['idx_l'] in emparejamientos: continue
            if c['fecha_b'] in fechas_banco_usadas: continue                                          
            
                                                                                     
            indices_reales = mapa_indices.get(c['fecha_b'], [])
            if any(idx in self.indices_banco_conciliados for idx in indices_reales): continue

            emparejamientos[c['idx_l']] = c
            fechas_banco_usadas.add(c['fecha_b'])

                                                                 
        candidatos_restantes = [c for c in todas_coincidencias if not c['es_valido']]
        candidatos_restantes.sort(key=lambda x: (x['dias'], abs(x['pct'])))

        for c in candidatos_restantes:
            if c['idx_l'] in emparejamientos: continue
            if c['fecha_b'] in fechas_banco_usadas: continue
            
            indices_reales = mapa_indices.get(c['fecha_b'], [])
            if any(idx in self.indices_banco_conciliados for idx in indices_reales): continue

                                                                                                     
                                                                                         
            emparejamientos[c['idx_l']] = c
            fechas_banco_usadas.add(c['fecha_b'])

                                    
                                     
        for idx_l, match in emparejamientos.items():
            pct = match['pct']
            ctls = match['ctls']
            
            if -1 <= pct <= 3.5:
                estado = "Conciliado"
                nota = f"Lote TDD (Com: {pct:.2f}%)"
            elif 3.5 < pct <= 25:
                estado = "Requiere Revisión - Diferencia Alta"
                nota = f"Lote TDD [Falta {pct:.2f}%]"
            elif pct < -1:
                estado = "Requiere Revisión - Monto Mayor en Banco"
                nota = f"Diferencia: {pct:.2f}%"
            else:
                estado = "Requiere Revisión - Diferencia Excesiva"
                nota = f"Diferencia: {pct:.2f}% (>25%)"

                                
            indices_reales = mapa_indices.get(match['fecha_b'], [])
            for i, idx_real in enumerate(indices_reales):
                self.indices_banco_conciliados.add(idx_real)
                fila = self.df_banco.loc[idx_real]
                
                monto_debe = match['monto_l'] if i == 0 else 0
                desc_visual = f"{self.limpiar_texto(fila['Descripción'])} (Ventas del {self.fecha_str(match['fecha_l'])} - {nota})"
                
                self._agregar_resultado(f"Lote {self.fecha_str(match['fecha_l'])}", fila['Fecha'], 
                                      fila['Referencia'], desc_visual, 
                                      self.normalizar_monto(fila['Abono']), estado, "TDD", monto_debe=monto_debe, orden_interno=1)
                
                               
                                                                        
                if idx_real + 1 in self.df_banco.index:
                    fila_sig = self.df_banco.loc[idx_real + 1]                            
                    if 'COMISION' in str(fila_sig['Descripción']).upper():
                        self._agregar_resultado(f"Lote {self.fecha_str(match['fecha_l'])}", fila_sig['Fecha'], 
                                              fila_sig['Referencia'], self.limpiar_texto(fila_sig['Descripción']), 
                                              self.normalizar_monto(fila_sig['Cargo']), "Conciliado", "COMISION", orden_interno=2)
                        self.indices_banco_conciliados.add(idx_real + 1)

                                                     
        for idx_l, row_l in libro_grp.iterrows():
            if idx_l not in emparejamientos:
                fecha_l = row_l['Fecha_Obj']
                monto_l = self.normalizar_monto(row_l['Monto_Total'])
                ctls = row_l['Nro_Control']
                rango = f"{min(ctls)} al {max(ctls)}" if ctls else ""
                
                estado_pendiente = "Pendiente en Banco"
                nota_pendiente = "No aparece en banco"
                
                if self.fecha_corte and fecha_l:
                    dias_para_cierre = (self.fecha_corte - fecha_l).days
                    if 0 <= dias_para_cierre <= 3:
                        estado_pendiente = "Pendiente - Pago en Transcurso"
                        nota_pendiente = "Cierre de Lote en tránsito (Fin de Mes)"

                self._agregar_resultado(f"Ctls: {rango}", self.fecha_str(fecha_l), "[NO ENCONTRADA]", 
                                      f"CIERRE TDD - {nota_pendiente}", monto_l, estado_pendiente, "TDD")

                                                                               
                               
                                                                               
    def conciliar_saint(self):
        print("   -> Ejecutando SAINT (Egresos)...")
                                                        
        df_banco_work = self.df_banco[self.df_banco['Tipo'] == 'ND'].copy()
        df_banco_work['MONTO_NORM'] = df_banco_work['Cargo'].apply(self.normalizar_monto)
        df_banco_work['REF_CLEAN'] = df_banco_work['Referencia'].apply(self.normalizar_ref)
        self.df_saint['MONTO_NORM'] = self.df_saint['MONTO'].apply(self.normalizar_monto)
        self.df_saint['REF_CLEAN'] = self.df_saint['REFERENCIA'].apply(self.normalizar_ref)

                                                         
        patron_comision = (
            'COMISION|ISLR|IGTF|IMPUESTO|MANTENIMIENTO|GASTOS|ADMINISTRACION|'
            'SERV AL CARACAS|EMISION.*ESTADO DE CUENTA'
        )
        comisiones_banco_todas = df_banco_work[
            df_banco_work['Descripción'].str.contains(patron_comision, case=False, na=False)
        ]
        suma_com_banco = comisiones_banco_todas['MONTO_NORM'].sum()
        
                                          
        patron_saint = 'COMISIONES BANCARIAS|GASTOS BANCARIOS'
        comision_saint_rows = self.df_saint[
            self.df_saint['TIPO_NOTA'].astype(str).str.contains(patron_saint, case=False, na=False) |
            self.df_saint['NOMBRE'].astype(str).str.contains(patron_saint, case=False, na=False)
        ]
        suma_com_saint = comision_saint_rows['MONTO_NORM'].sum()
        
        comisiones_cuadran = abs(suma_com_banco - suma_com_saint) < 1.00
        estado_com = 'Conciliado' if comisiones_cuadran else 'Requiere Revisión - Diferencia Comisiones'
        nota_com = "Cuadre Global" if comisiones_cuadran else f"Dif: {(suma_com_banco - suma_com_saint):.2f}"

        banco_candidatos = df_banco_work[~df_banco_work.index.isin(comisiones_banco_todas.index)]
        saint_candidatos = self.df_saint[~self.df_saint.index.isin(comision_saint_rows.index)]

        for idx_s, row_s in saint_candidatos.iterrows():
            ref_s = row_s['REF_CLEAN']
            monto_s = row_s['MONTO_NORM']
            nombre_s = row_s.get('NOMBRE', 'Egreso')
            if monto_s == 0: continue

            match = False
            match_exacto = None
            match_por_monto = None
            
                                         
            for idx_b, row_b in banco_candidatos.iterrows():
                if idx_b in self.indices_banco_conciliados: continue
                ref_b = row_b['REF_CLEAN']
                monto_b = row_b['MONTO_NORM']
                
                                                 
                if abs(monto_b - monto_s) < 0.10:
                                                          
                    termina_con = str(ref_b).endswith(str(ref_s)) if len(str(ref_s)) > 2 else False
                    if row_s['REFERENCIA'] in ['SIN_REF', 'PAGO NO IDENTIFICADO']:
                        termina_con = True                                                         
                    
                    if termina_con:
                                                            
                        match_exacto = (idx_b, row_b)
                        break                                          
                    else:
                                                                         
                        if match_por_monto is None:                                    
                            match_por_monto = (idx_b, row_b)
            
                                                
            if match_exacto:
                                                   
                idx_b, row_b = match_exacto
                self.indices_banco_conciliados.add(idx_b)
                desc_final = f"{self.limpiar_texto(row_b['Descripción'])}, {nombre_s}"
                self._agregar_resultado("SAINT", row_b['Fecha'], row_b['Referencia'], desc_final, 
                                      row_b['MONTO_NORM'], "Conciliado", "SAINT")
                match = True
                
            elif match_por_monto:
                                                                              
                idx_b, row_b = match_por_monto
                self.indices_banco_conciliados.add(idx_b)
                
                desc_discrepancia = (
                    f"{self.limpiar_texto(row_b['Descripción'])}, {nombre_s} "
                    f"[⚠️ Ref_Banco: {row_b['Referencia']} / Ref_SAINT: {row_s['REFERENCIA']}]"
                )
                
                self._agregar_resultado(
                    "SAINT", 
                    row_b['Fecha'], 
                    "[NO ENCONTRADA]",                                         
                    desc_discrepancia, 
                    row_b['MONTO_NORM'],                       
                    "Requiere Revisión - Verificar Referencia", 
                    "SAINT",
                    monto_debe=None,
                    orden_interno=0
                )
                match = True
            
            if not match:
                                             
                self._agregar_resultado("SAINT", "Ver SAINT", row_s['REFERENCIA'], f"Egreso: {nombre_s}", 
                                      monto_s, "Pendiente en Banco", "SAINT")

        if not comisiones_banco_todas.empty:
            for idx, row_c in comisiones_banco_todas.iterrows():
                if idx in self.indices_banco_conciliados: continue
                self.indices_banco_conciliados.add(idx)
                self._agregar_resultado("COMISIONES", row_c['Fecha'], row_c['Referencia'], 
                                      f"{self.limpiar_texto(row_c['Descripción'])} ({nota_com})", 
                                      row_c['MONTO_NORM'], estado_com, "COMISION")


                                                                               
              
                                                                               
    def _agregar_resultado(self, control, fecha, ref, desc, monto, estado, tipo, monto_debe=None, orden_interno=0):
        if any(x in estado for x in ["Pendiente en Banco", "Mes Anterior", "Transcurso"]):
            cargo = 0
            abono = 0
        else:
            es_salida = (tipo in ["SAINT", "COMISION"]) or (tipo == "SOBRANTE" and "SAINT" in estado)
            cargo = monto if es_salida else 0
            abono = monto if not es_salida else 0

        if "Pendiente en Libro" in estado or "Pendiente en SAINT" in estado:
            sae_debe = 0
            saint_haber = 0
        else:
            if monto_debe is not None:
                sae_debe = monto_debe
            else:
                sae_debe = monto if tipo in ["OTR", "TRA", "TDD"] else 0
            saint_haber = monto if tipo == "SAINT" else 0

        self.resultados.append({
            'Fecha': fecha, 'Referencia': ref, 'Descripción': desc,
            'Cargo': cargo, 'Abono': abono,
            'SAE (Debe)': sae_debe, 'SAINT (Haber)': saint_haber,
            'Estado': estado, 'Nro_Control': control, 'Orden_Interno': orden_interno
        })


    def diagnostico_banco(self):
        """
        Diagnóstico DETALLADO del estado de cuenta bancario original vs procesado.
        Rastrea cada tipo de movimiento y de dónde proviene.
        """
        print("\n" + "="*80)
        print("🔍 DIAGNÓSTICO DETALLADO DEL ESTADO DE CUENTA BANCARIO")
        print("="*80)
        
                                                    
        nc_original = self.df_banco[self.df_banco['Tipo'] == 'NC'].copy()
        nd_original = self.df_banco[self.df_banco['Tipo'] == 'ND'].copy()
        
        total_nc_original = len(nc_original)
        monto_nc_original = nc_original['Abono'].apply(self.normalizar_monto).sum()
        
        total_nd_original = len(nd_original)
        monto_nd_original = nd_original['Cargo'].apply(self.normalizar_monto).sum()
        
        print(f"\n📄 ESTADO DE CUENTA BANCARIO (Archivo Original):")
        print(f"   NC (Ingresos):  {total_nc_original:>3} movimientos | Bs. {monto_nc_original:>15,.2f}")
        print(f"   ND (Egresos):   {total_nd_original:>3} movimientos | Bs. {monto_nd_original:>15,.2f}")
        print(f"   {'─'*75}")
        print(f"   TOTAL BANCO:    {len(self.df_banco):>3} movimientos")
        
                                                     
        nc_procesadas = [idx for idx in self.indices_banco_conciliados if idx in nc_original.index]
        nd_procesadas = [idx for idx in self.indices_banco_conciliados if idx in nd_original.index]
        
        print(f"\n✅ MOVIMIENTOS DEL BANCO PROCESADOS:")
        print(f"   NC procesadas:  {len(nc_procesadas):>3} / {total_nc_original:>3} ({len(nc_procesadas)/total_nc_original*100:>5.1f}%)")
        print(f"   ND procesadas:  {len(nd_procesadas):>3} / {total_nd_original:>3} ({len(nd_procesadas)/total_nd_original*100:>5.1f}%)")
        print(f"   {'─'*75}")
        print(f"   TOTAL:          {len(self.indices_banco_conciliados):>3} / {len(self.df_banco):>3}")
        
                                                                
        nc_no_procesadas = nc_original[~nc_original.index.isin(self.indices_banco_conciliados)]
        nd_no_procesadas = nd_original[~nd_original.index.isin(self.indices_banco_conciliados)]
        
        if not nc_no_procesadas.empty:
            monto_nc_no_proc = nc_no_procesadas['Abono'].apply(self.normalizar_monto).sum()
            print(f"\n⚠️  NC NO PROCESADAS ({len(nc_no_procesadas)} movimientos = Bs. {monto_nc_no_proc:,.2f}):")
            print(f"   Estas aparecerán como 'Pendiente en Libro' (no están en SAE)")
            for idx, row in nc_no_procesadas.head(5).iterrows():
                print(f"   - {row['Fecha']} | {row['Referencia'][:20]:20} | {self.normalizar_monto(row['Abono']):>10,.2f} | {row['Descripción'][:40]}")
            if len(nc_no_procesadas) > 5:
                print(f"   ... y {len(nc_no_procesadas) - 5} más")
        
        if not nd_no_procesadas.empty:
            monto_nd_no_proc = nd_no_procesadas['Cargo'].apply(self.normalizar_monto).sum()
            print(f"\n⚠️  ND NO PROCESADAS ({len(nd_no_procesadas)} movimientos = Bs. {monto_nd_no_proc:,.2f}):")
            print(f"   Estas aparecerán como 'Pendiente en SAINT' (no están en SAINT)")
            for idx, row in nd_no_procesadas.head(5).iterrows():
                print(f"   - {row['Fecha']} | {row['Referencia'][:20]:20} | {self.normalizar_monto(row['Cargo']):>10,.2f} | {row['Descripción'][:40]}")
            if len(nd_no_procesadas) > 5:
                print(f"   ... y {len(nd_no_procesadas) - 5} más")
        
                                                      
        df_resultado = pd.DataFrame(self.resultados)
        
        print(f"\n📊 ANÁLISIS DETALLADO DEL RESULTADO FINAL:")
        print(f"   {'─'*75}")
        
                                       
        tipos = df_resultado.groupby('Nro_Control').size()
        
                             
        filas_otr = df_resultado[df_resultado['Nro_Control'].str.contains('OTR|Pago Móvil', na=False, case=False)]
        filas_tra = df_resultado[df_resultado['Nro_Control'].str.contains('TRA|Transferencia', na=False, case=False)]
        filas_tdd = df_resultado[df_resultado['Nro_Control'].str.contains('TDD|Lote|Ctls', na=False, case=False)]
        filas_saint = df_resultado[df_resultado['Nro_Control'].str.contains('SAINT|COMISION', na=False, case=False)]
        filas_sobrante = df_resultado[df_resultado['Nro_Control'] == '-']
        
        print(f"\n   Por Módulo:")
        print(f"   • Pago Móvil (OTR):        {len(filas_otr):>3} filas")
        print(f"   • Transferencias (TRA):    {len(filas_tra):>3} filas")
        print(f"   • TDD (Lotes):             {len(filas_tdd):>3} filas")
        print(f"   • SAINT/Comisiones:        {len(filas_saint):>3} filas")
        print(f"   • Sobrantes (sin match):   {len(filas_sobrante):>3} filas")
        print(f"   {'─'*75}")
        print(f"   TOTAL FILAS RESULTADO:     {len(df_resultado):>3}")
        
                                                
        filas_del_banco_original = len(self.df_banco)
        filas_agregadas_correctas = len(df_resultado) - filas_del_banco_original
        
        print(f"\n🔢 RESUMEN DE FILAS:")
        print(f"   Banco original:                    {filas_del_banco_original:>3} filas")
        print(f"   Procesadas del banco:              {len(self.indices_banco_conciliados):>3} filas")
        print(f"   NO procesadas (sobrantes banco):   {filas_del_banco_original - len(self.indices_banco_conciliados):>3} filas")
        print(f"   {'─'*75}")
        print(f"   Agregadas (SAE/SAINT pendientes):  {filas_agregadas_correctas:>3} filas")
        print(f"   {'─'*75}")
        print(f"   TOTAL EN RESULTADO:                {len(df_resultado):>3} filas")
        
                                            
        print(f"\n📋 DESGLOSE DE LAS {filas_agregadas_correctas} FILAS AGREGADAS:")
        
                                 
        filas_sae_pendientes = df_resultado[
            (df_resultado['Estado'].str.contains('Pendiente en Banco', na=False)) &
            (df_resultado['SAE (Debe)'] > 0)
        ]
        
                                   
        filas_saint_pendientes = df_resultado[
            (df_resultado['Estado'].str.contains('Pendiente en Banco', na=False)) &
            (df_resultado['SAINT (Haber)'] > 0)
        ]
        
                                            
        filas_ventas_no_banco = df_resultado[
            df_resultado['Estado'].str.contains('Pendiente en Banco|Transcurso', na=False) &
            (df_resultado['SAE (Debe)'] > 0)
        ]
        
        print(f"   • Ventas SAE no en banco:          {len(filas_ventas_no_banco):>3} filas")
        print(f"   • Egresos SAINT no en banco:       {len(filas_saint_pendientes):>3} filas")
        print(f"   • Otros (comisiones auto, etc):    {filas_agregadas_correctas - len(filas_ventas_no_banco) - len(filas_saint_pendientes):>3} filas")
        
                                                      
        filas_otros = filas_agregadas_correctas - len(filas_ventas_no_banco) - len(filas_saint_pendientes)
        if filas_otros > 0:
            print(f"\n🔍 LISTADO DETALLADO DE LAS {filas_otros} FILAS 'OTROS' (Potenciales duplicados):")
            
                                                                             
            filas_otros_df = df_resultado[
                ~df_resultado.index.isin(filas_ventas_no_banco.index) &
                ~df_resultado.index.isin(filas_saint_pendientes.index)
            ]
            
                                                                               
            filas_otros_nd = filas_otros_df[filas_otros_df['Cargo'] > 0]
            
            if len(filas_otros_nd) > 0:
                print(f"\n   ND en 'Otros' ({len(filas_otros_nd)} filas - CANDIDATAS A DUPLICACIÓN):")
                for idx, row in filas_otros_nd.iterrows():
                    print(f"   - {row['Fecha']} | {str(row['Referencia'])[:20]:20} | Cargo: {row['Cargo']:>10,.2f} | {str(row['Descripción'])[:50]}")
            
                                                                                       
            filas_otros_nc = filas_otros_df[(filas_otros_df['Abono'] > 0) | (filas_otros_df['SAE (Debe)'] > 0)]
            
            if len(filas_otros_nc) > 0:
                print(f"\n   NC/SAE en 'Otros' ({len(filas_otros_nc)} filas):")
                for idx, row in filas_otros_nc.head(10).iterrows():
                    print(f"   - {row['Fecha']} | {str(row['Referencia'])[:20]:20} | Abono: {row['Abono']:>10,.2f} / SAE: {row['SAE (Debe)']:>10,.2f} | {str(row['Descripción'])[:50]}")
        
                                           
        print(f"\n🔍 ANÁLISIS DE LAS 3 NC FALTANTES:")
        print(f"   Banco original tiene: {total_nc_original} NC")
        print(f"   Reporte muestra: {len(df_resultado[df_resultado['Abono'] > 0])} NC con Abono > 0")
        print(f"   Diferencia: {total_nc_original - len(df_resultado[df_resultado['Abono'] > 0])} NC faltantes")
        
                                                                   
        nc_con_abono_cero = df_resultado[
            (df_resultado['Abono'] == 0) & 
            (df_resultado['SAE (Debe)'] > 0)
        ]
        
        if len(nc_con_abono_cero) > 0:
            print(f"\n   CANDIDATAS A SER LAS 3 NC FALTANTES (Abono=0, SAE>0):")
            for idx, row in nc_con_abono_cero.head(5).iterrows():
                print(f"   - {row['Fecha']} | {str(row['Referencia'])[:20]:20} | SAE: {row['SAE (Debe)']:>10,.2f} | Estado: {row['Estado'][:40]}")
        
                                                                                
        print(f"\n🔍 BÚSQUEDA ESPECÍFICA DE LAS 3 NC FALTANTES:")
        print(f"   Buscando NC del banco de JUNIO que tienen Abono=0 en el resultado...")
        
                                                                
        nc_banco_junio = nc_original[nc_original['Fecha'].apply(lambda x: isinstance(x, str) and '/06/' in x or (hasattr(x, 'month') and x.month == 6))]
        
        print(f"   NC del banco en JUNIO: {len(nc_banco_junio)}")
        
                                                                 
        nc_banco_junio_indices = set(nc_banco_junio.index)
        
        nc_banco_con_abono_cero = df_resultado[
            df_resultado.index.isin(nc_banco_junio_indices) & 
            (df_resultado['Abono'] == 0)
        ]
        
        if len(nc_banco_con_abono_cero) > 0:
            print(f"\n   ✅ ENCONTRADAS: {len(nc_banco_con_abono_cero)} NC del banco de JUNIO con Abono=0:")
            for idx, row in nc_banco_con_abono_cero.iterrows():
                print(f"   - Idx: {idx} | {row['Fecha']} | Ref: {str(row['Referencia'])[:25]:25} | Abono: {row['Abono']:>10,.2f} | Estado: {row['Estado'][:50]}")
                                                
                if idx in nc_original.index:
                    banco_row = nc_original.loc[idx]
                    print(f"     └─ Banco original: Abono={self.normalizar_monto(banco_row['Abono']):>10,.2f} | Desc: {str(banco_row['Descripción'])[:50]}")
        else:
            print(f"\n   ⚠️ NO SE ENCONTRARON NC del banco de JUNIO con Abono=0")
            print(f"   Esto sugiere que las 3 NC faltantes NO son del banco, sino del SAE")
        
        print("="*80 + "\n")
        
        return {
            'nc_original': total_nc_original,
            'nd_original': total_nd_original,
            'nc_procesadas': len(nc_procesadas),
            'nd_procesadas': len(nd_procesadas),
            'nc_no_procesadas': len(nc_no_procesadas),
            'nd_no_procesadas': len(nd_no_procesadas),
            'filas_agregadas': filas_agregadas_correctas,
            'total_resultado': len(df_resultado)
        }

    def resumen_auditoria(self):
        """
        Valida que no hayamos perdido ni inventado filas por error técnico.
        """
        df_resultado = pd.DataFrame(self.resultados)
        
        print("\n" + "="*40)
        print("🔍 AUDITORÍA TÉCNICA")
        print("="*40)
        
                                                                 
        total_filas_banco = len(self.df_banco)
        
                                   
        total_reporte = len(df_resultado)
        
                                                 
        agregadas_sae = len(df_resultado[
            (df_resultado['Estado'].str.contains('Pendiente en Banco|Mes Anterior|Transcurso', na=False)) & 
            (df_resultado['Abono'] == 0) & (df_resultado['Cargo'] == 0)
        ])
        
        print(f"• Filas Originales Banco: {total_filas_banco}")
        print(f"• Filas Agregadas (Pendientes): {agregadas_sae}")
        print(f"• Total Esperado: {total_filas_banco + agregadas_sae}")
        print(f"• Total Real en Reporte: {total_reporte}")
        
        if total_reporte == (total_filas_banco + agregadas_sae):
            print("\n✅ INTEGRIDAD DE DATOS: CORRECTA")
        else:
            diff = total_reporte - (total_filas_banco + agregadas_sae)
            print(f"\n⚠️ ALERTA: Hay {diff} filas de diferencia inexplicada.")
            
                                   
            print(f"\n🔍 DIAGNÓSTICO DETALLADO:")
            
                                     
            pendientes_saint = df_resultado[
                (df_resultado['Estado'].str.contains('Pendiente en Banco', na=False)) & 
                (df_resultado['Cargo'] > 0) & (df_resultado['Abono'] == 0)
            ]
            print(f"   • Pendientes SAINT (Cargo>0): {len(pendientes_saint)}")
            
                                    
            filas_banco_proc = len([idx for idx in self.indices_banco_conciliados])
            print(f"   • Del Banco (procesadas): {filas_banco_proc}")
            
                                  
            otras = total_reporte - (filas_banco_proc + agregadas_sae + len(pendientes_saint))
            print(f"   • Otras filas (diferencia): {otras}")
            
            if otras > 0:
                print(f"\n   Las 'otras' pueden ser:")
                print(f"   - Sobrantes del banco no procesados")
                print(f"   - Filas con estados especiales")
                
                                                     
                no_pendientes = df_resultado[
                    ~df_resultado['Estado'].str.contains('Pendiente', na=False)
                ]
                print(f"\n   Total filas NO pendientes: {len(no_pendientes)}")
                print(f"   Debería coincidir con banco proc: {filas_banco_proc}")
                print(f"   Diferencia: {len(no_pendientes) - filas_banco_proc}")
                
                                                         
                sobrantes_esperados = total_filas_banco - filas_banco_proc
                print(f"\n   📋 DESGLOSE DE LAS {otras} 'OTRAS' FILAS:")
                print(f"   - Sobrantes banco esperados:     {sobrantes_esperados}")
                print(f"   - Sobrantes banco reales (otras): {otras}")
                print(f"   - Diferencia (fila extra):        {otras - sobrantes_esperados}")
                
                if otras - sobrantes_esperados > 0:
                    print(f"\n   🔍 LISTADO DE FILAS SOSPECHOSAS:")
                    print(f"   Primeras 10 filas conciliadas/revisión:\n")
                    
                    sospechosas = df_resultado[
                        (df_resultado['Estado'].str.contains('Conciliado|Revisión', na=False)) &
                        ((df_resultado['Abono'] > 0) | (df_resultado['Cargo'] > 0))
                    ]
                    
                    for idx, row in sospechosas.head(10).iterrows():
                        desc_corta = str(row['Descripción'])[:45]
                        print(f"   [{idx}] {row['Fecha']:10} | {desc_corta:45} | C:{row['Cargo']:>8.2f} A:{row['Abono']:>8.2f}")
                    
                                                                        
                    print(f"\n   📊 DESGLOSE DE LAS {otras} 'OTRAS' FILAS POR ESTADO:")
                    print(f"   (Estas son las filas que NO son pendientes SAE/SAINT)\n")
                    
                                                                                         
                    filas_procesadas_y_pendientes = filas_banco_proc + agregadas_sae + len(pendientes_saint)
                    
                                                        
                    estados = df_resultado['Estado'].value_counts()
                    print(f"   Resumen por estado (TODAS LAS FILAS):")
                    for estado, count in estados.items():
                        print(f"   - {estado:50} : {count:3} filas")
                    
                    print(f"\n   🔍 Identificando la fila extra:")
                    print(f"   - Banco procesado: {filas_banco_proc}")
                    print(f"   - Pendientes SAE: {agregadas_sae}")
                    print(f"   - Pendientes SAINT: {len(pendientes_saint)}")
                    print(f"   - Total contabilizado: {filas_procesadas_y_pendientes}")
                    print(f"   - Total reporte: {total_reporte}")
                    print(f"   - Diferencia (otras): {otras}")
                    print(f"   - Banco NO procesado esperado: {total_filas_banco - filas_banco_proc}")
                    print(f"   - Fila extra: {otras - (total_filas_banco - filas_banco_proc)}")
        print("="*40 + "\n")        

    def ejecutar(self):
        print("INICIANDO CONCILIACIÓN MAESTRA...")
        self.conciliar_pago_movil()
        self.conciliar_transferencias()
        self.conciliar_tdd()
        if self.df_saint is not None:
            self.conciliar_saint()
        
        for idx, row in self.df_banco.iterrows():
            if idx not in self.indices_banco_conciliados:
                cargo = self.normalizar_monto(row['Cargo'])
                abono = self.normalizar_monto(row['Abono'])
                if cargo == 0 and abono == 0: continue
                
                estado_sobrante = "Pendiente en SAINT" if cargo > 0 else "Pendiente en Libro"
                self._agregar_resultado("-", row['Fecha'], row['Referencia'], self.limpiar_texto(row['Descripción']), 
                                      cargo if cargo > 0 else abono, estado_sobrante, "SOBRANTE")

        df_final = pd.DataFrame(self.resultados)
        if not df_final.empty:
            df_final['Nro_Control'] = df_final['Nro_Control'].astype(str)
            df_final = df_final.sort_values(by=['Fecha', 'Nro_Control', 'Orden_Interno'], ascending=[True, True, True])
            df_final = df_final.drop(columns=['Orden_Interno'])
        
                                   
        self.resumen_auditoria()                                        
        
                                                                      
                                  
        
        return df_final