import pandas as pd
import re
from pathlib import Path


class LibroVentasCsv:
    def __init__(self, excel_path: str, banco_filtro: str = 'BANCARIBE'):

        self.excel_path = Path(excel_path)
        self.banco_filtro = banco_filtro
        self.sheet_name = 'Ventas AVEC x Todos los Meses'
        self.use_cols = 'A, G, AN'
        
    
        base_name = self.excel_path.stem
        if banco_filtro:
            self.csv_path = self.excel_path.parent / f"{base_name}_{banco_filtro}_procesado.csv"
        else:
            self.csv_path = self.excel_path.parent / f"{base_name}_procesado.csv"
    
    def _cargar_excel(self) -> pd.DataFrame:
        print(f"[1/4] Leyendo archivo Excel...")
        
        df = pd.read_excel(
            self.excel_path,
            sheet_name=self.sheet_name,
            header=5,
            usecols=self.use_cols
        )
        
        print(f"Columnas cargadas: {df.columns.tolist()}")
        return df
    
    def _limpiar_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        print(f"\n[2/4] Limpiando datos...")
        

        col_id = df.columns[0]

        df[col_id] = pd.to_numeric(df[col_id], errors='coerce')
        df_limpio = df.dropna(subset=[col_id])
        
        df_limpio = df_limpio.copy()
        df_limpio[col_id] = df_limpio[col_id].astype(int)
        
        df_limpio.columns = ['Nro_Control', 'Monto_Total', 'Info_Pago_Mezclada']
        
        print(f"Filas encontradas: {len(df_limpio)}")
        return df_limpio
    
    def _separar_info_pagos(self, df: pd.DataFrame) -> pd.DataFrame:
        #Utilice regex para extraer la informacion de la celda combinada
        print(f"\n[3/4] Extrayendo información de pagos...")
        
        patron = r'FP:\s*(?P<Forma_Pago>[^,]+),\s*Fec:\s*(?P<Fecha_Pago>[^,]+),\s*Ref:\s*(?P<Referencia>[^,]+),\s*Bco:\s*(?P<Banco>[^)]+)'
 
        matches = df['Info_Pago_Mezclada'].str.extractall(patron)

        matches_wide = matches.unstack()
        
        new_columns = []
        for col_name, match_idx in matches_wide.columns:
            new_columns.append(f"{col_name}_{match_idx + 1}")
        matches_wide.columns = new_columns
        
        # Unir con el DataFrame original (LEFT JOIN)
        df_final = df.join(matches_wide, how='left')
        
        # Limpiar espacios en blanco
        for col in df_final.columns:
            if df_final[col].dtype == 'object':
                df_final[col] = df_final[col].str.strip()
        
        print(f"Información de pagos extraída correctamente")
        return df_final
    
    def _aplicar_filtro_banco(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.banco_filtro is None:
            return df
        
        print(f"\n Aplicando filtro: Solo transacciones de {self.banco_filtro}")
        
        filas_antes = len(df)
        
        
        mascara_banco_1 = df['Banco_1'].str.contains(self.banco_filtro, case=False, na=False) if 'Banco_1' in df.columns else False
        mascara_banco_2 = df['Banco_2'].str.contains(self.banco_filtro, case=False, na=False) if 'Banco_2' in df.columns else False
        
        df_filtrado = df[mascara_banco_1 | mascara_banco_2].copy()
        
        filas_despues = len(df_filtrado)
        print(f" Filas antes del filtro: {filas_antes}")
        print(f" Filas después del filtro: {filas_despues}")
        print(f" Filas eliminadas: {filas_antes - filas_despues}")
        
        return df_filtrado
    
    def _ordenar_columnas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ordena las columnas en el formato final."""
        print(f"\n[4/4] Aplicando formato final...")
        
        # Definir orden de columnas
        cols_base = ['Nro_Control', 'Monto_Total']
        cols_pago_1 = ['Forma_Pago_1', 'Fecha_Pago_1', 'Referencia_1', 'Banco_1']
        cols_pago_2 = ['Forma_Pago_2', 'Fecha_Pago_2', 'Referencia_2', 'Banco_2']
        
        # Construir lista de columnas finales
        columnas_finales = cols_base.copy()
        
        # Agregar columnas de Pago 1
        if 'Forma_Pago_1' in df.columns:
            columnas_finales.extend(cols_pago_1)
        else:
            for c in cols_pago_1:
                df[c] = ""
            columnas_finales.extend(cols_pago_1)
        
        # Agregar columnas de Pago 2 si existen
        if 'Forma_Pago_2' in df.columns:
            columnas_finales.extend(cols_pago_2)
        
        # Aplicar orden
        df_ordenado = df[columnas_finales]
        
        # Reemplazar NaN con strings vacíos
        df_ordenado.fillna('', inplace=True)
        
        print(f"✓ Formato aplicado correctamente")
        return df_ordenado
    
    def ejecutar(self) -> Path:

        print("=" * 60)
        print("PROCESAMIENTO COMPLETO DEL LIBRO DE VENTAS")
        print("=" * 60)
        
        # Flujo de procesamiento
        df = self._cargar_excel()
        df = self._limpiar_datos(df)
        df = self._separar_info_pagos(df)
        df = self._aplicar_filtro_banco(df)
        df = self._ordenar_columnas(df)
        

        df.to_csv(self.csv_path, sep=';', index=False, encoding='utf-8-sig')
        
        # Resumen
        print("\n" + "=" * 60)
        print("PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"📊 Total de facturas procesadas: {len(df)}")
        print(f"📁 Archivo generado: {self.csv_path}")
        
        # Estadísticas de pagos
        if 'Forma_Pago_1' in df.columns:
            pagos_1 = (df['Forma_Pago_1'] != '').sum()
            print(f"💳 Facturas con al menos 1 pago: {pagos_1}")
        
        if 'Forma_Pago_2' in df.columns:
            pagos_2 = (df['Forma_Pago_2'] != '').sum()
            print(f"💳 Facturas con 2 pagos: {pagos_2}")
        
        return self.csv_path


class LimpiarGuionesReferencias:
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.csv_limpio_path = self.csv_path.parent / f"{self.csv_path.stem}_limpio.csv"
    
    def _limpiar_referencia(self, ref):
        if pd.isna(ref) or ref == '':
            return ref
        
        ref_str = str(ref)
        ref_limpio = re.sub(r'[-\.]+$', '', ref_str)
        
        return ref_limpio
    
    def ejecutar(self) -> Path:
        print("=" * 60)
        print("LIMPIEZA DE GUIONES EN REFERENCIAS")
        print("=" * 60)
        
        print("\n[1/3] Cargando archivo CSV...")
        df = pd.read_csv(self.csv_path, sep=';', encoding='utf-8-sig')
        print(f"✓ Archivo cargado: {len(df)} filas")
        
        print("\n[2/3] Limpiando guiones de referencias...")
        
        guiones_ref1_antes = df['Referencia_1'].astype(str).str.contains('-', na=False).sum()
        guiones_ref2_antes = df['Referencia_2'].astype(str).str.contains('-', na=False).sum() if 'Referencia_2' in df.columns else 0
        
        df['Referencia_1'] = df['Referencia_1'].apply(self._limpiar_referencia)
        if 'Referencia_2' in df.columns:
            df['Referencia_2'] = df['Referencia_2'].apply(self._limpiar_referencia)
        
        guiones_ref1_despues = df['Referencia_1'].astype(str).str.contains('-', na=False).sum()
        guiones_ref2_despues = df['Referencia_2'].astype(str).str.contains('-', na=False).sum() if 'Referencia_2' in df.columns else 0
        
        print(f"✓ Referencias limpiadas:")
        print(f"   - Referencia_1: {guiones_ref1_antes} con guiones → {guiones_ref1_despues} restantes")
        if 'Referencia_2' in df.columns:
            print(f"   - Referencia_2: {guiones_ref2_antes} con guiones → {guiones_ref2_despues} restantes")
        
        print("\n[3/3] Guardando archivo limpio...")
        df.to_csv(self.csv_limpio_path, sep=';', index=False, encoding='utf-8-sig')
        
        print("\n" + "=" * 60)
        print("PROCESO COMPLETADO")
        print("=" * 60)
        print(f"📊 Total de filas procesadas: {len(df)}")
        print(f"📁 Archivo de entrada: {self.csv_path}")
        print(f"📁 Archivo de salida: {self.csv_limpio_path}")
        print(f"🧹 Guiones eliminados: {(guiones_ref1_antes + guiones_ref2_antes) - (guiones_ref1_despues + guiones_ref2_despues)}")
        
        return self.csv_limpio_path
