import pandas as pd
from pathlib import Path


class RegistroSaintCsv:
   
    def __init__(self, excel_path: str, sheet_name: str = None, max_rows: int = None):
        self.excel_path = Path(excel_path)
        self.sheet_name = sheet_name
        self.max_rows = max_rows
        
        # Generar nombre del archivo de salida
        base_name = self.excel_path.stem
        self.csv_path = self.excel_path.parent / f"{base_name}_procesado.csv"
    
    def _separar_descripcion(self, descripcion):

        if pd.isna(descripcion):
            return pd.Series(['', '', ''])
        
        descripcion_str = str(descripcion).strip()
        
        # Caso especial 1: PAGO NO IDENTIFICADO
        # Marcado especial para facilitar conciliación
        if descripcion_str == 'PAGO NO IDENTIFICADO':
            return pd.Series(['PAGO NO IDENTIFICADO', 'SIN_REF', 'REVISAR'])
        
        # Caso especial 2: COMISIONES BANCARIAS
        # Marcado especial para facilitar conciliación
        if descripcion_str == 'COMISIONES BANCARIAS':
            return pd.Series(['COMISIONES BANCARIAS', 'AUTO', 'BANCO'])
        
        # Caso normal: dividir en 3 partes (TIPO_NOTA, REFERENCIA, NOMBRE)
        partes = descripcion_str.split(maxsplit=2)
        
        # Asegurar que siempre haya 3 elementos
        while len(partes) < 3:
            partes.append('')
        
        return pd.Series(partes[:3])
    
    def _cargar_excel(self) -> pd.DataFrame:    
        print(f"[1/3] Leyendo archivo Excel...")
        
        # Parámetros de lectura
        params = {
            'header': 0,
            'usecols': 'C:D',  # Columnas DESCRIPCION y MONTO
            'skiprows': 5,     # Saltar las primeras 5 filas
        }
        
        # Agregar sheet_name si está especificado
        if self.sheet_name:
            params['sheet_name'] = self.sheet_name
        
        # Agregar nrows si está especificado
        if self.max_rows:
            params['nrows'] = self.max_rows
        
        # Especificar motor para archivos .xlsx
        params['engine'] = 'openpyxl'
        
        df = pd.read_excel(self.excel_path, **params)
        
        print(f"✓ Datos cargados: {len(df)} filas")
        print(f"✓ Columnas encontradas: {df.columns.tolist()}")
        
        return df
    
    def _procesar_descripcion(self, df: pd.DataFrame) -> pd.DataFrame:
        print(f"\n[2/3] Separando columna DESCRIPCION...")
        
        # Verificar que exista la columna DESCRIPCION
        if 'DESCRIPCION' not in df.columns:
            raise ValueError("No se encontró la columna 'DESCRIPCION' en el Excel")
        
        # Aplicar la función de separación a cada fila
        df[['TIPO_NOTA', 'REFERENCIA', 'NOMBRE']] = df['DESCRIPCION'].apply(self._separar_descripcion)
        
        # Reordenar columnas: TIPO_NOTA, REFERENCIA, NOMBRE, MONTO
        df_procesado = df[['TIPO_NOTA', 'REFERENCIA', 'NOMBRE', 'MONTO']]
        
        print(f"✓ Columna DESCRIPCION separada en: TIPO_NOTA, REFERENCIA, NOMBRE")
        
        return df_procesado
    
    def _limpiar_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia datos nulos o inválidos."""
        print(f"\n[3/3] Limpiando datos...")
        
        filas_antes = len(df)
        
        # Eliminar filas donde todas las columnas sean NaN
        df_limpio = df.dropna(how='all')
        
        filas_despues = len(df_limpio)
        
        if filas_antes != filas_despues:
            print(f"✓ Filas eliminadas (vacías): {filas_antes - filas_despues}")
        
        print(f"✓ Filas válidas: {filas_despues}")
        
        return df_limpio
    
    def ejecutar(self) -> Path:
        """
        Ejecuta el flujo completo de procesamiento.
        
        Returns:
            Path: Ruta al archivo CSV generado
        """
        print("=" * 60)
        print("PROCESAMIENTO DEL REGISTRO SAINT")
        print("=" * 60)
        
        try:
            # Flujo de procesamiento
            df = self._cargar_excel()
            df = self._procesar_descripcion(df)
            df = self._limpiar_datos(df)
            
            # Guardar CSV
            df.to_csv(self.csv_path, index=False, encoding='utf-8-sig')
            
            # Resumen
            print("\n" + "=" * 60)
            print("PROCESO COMPLETADO EXITOSAMENTE")
            print("=" * 60)
            print(f"📊 Total de registros procesados: {len(df)}")
            print(f"📁 Archivo generado: {self.csv_path}")
            
            # Contar casos especiales
            casos_especiales = df[df['REFERENCIA'].isin(['SIN_REF', 'AUTO'])].shape[0]
            if casos_especiales > 0:
                print(f"⚠️  Casos especiales detectados: {casos_especiales}")
                print(f"   - PAGO NO IDENTIFICADO: {(df['REFERENCIA'] == 'SIN_REF').sum()}")
                print(f"   - COMISIONES BANCARIAS: {(df['REFERENCIA'] == 'AUTO').sum()}")
            
            # Mostrar muestra
            print("\n--- MUESTRA DE DATOS (primeras 5 filas) ---")
            print(df.head())
            
            return self.csv_path
            
        except Exception as e:
            print(f"\n✗ ERROR al procesar el archivo: {e}")
            raise
