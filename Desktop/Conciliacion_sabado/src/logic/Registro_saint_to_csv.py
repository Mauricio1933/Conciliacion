import pandas as pd
from pathlib import Path

class RegistroSaintCsv:
   
    def __init__(self, excel_path: str, sheet_name: str = None, max_rows: int = None):
        self.excel_path = Path(excel_path)
        self.sheet_name = sheet_name
        self.max_rows = max_rows
        self.formato_detectado = None                       
        
                                              
        base_name = self.excel_path.stem
        self.csv_path = self.excel_path.parent / f"{base_name}_procesado.csv"
    
    def _detectar_formato(self) -> str:
        try:
                                                        
            df_muestra = pd.read_excel(
                self.excel_path,
                sheet_name=0,                
                nrows=10,
                engine='openpyxl'
            )
            
            columnas = df_muestra.columns.tolist()
            
                                                                                        
                                                                            
            if len(columnas) >= 5:
                                                                    
                if 'ND' in str(df_muestra.iloc[0:5, 1].values):
                    print("📋 Formato detectado: NUEVO (columnas separadas con hoja COMISIONES)")
                    return 'nuevo'
            
                                                                 
            if 'DESCRIPCION' in columnas or 'C' in columnas:
                print("📋 Formato detectado: ANTIGUO (descripción mezclada)")
                return 'antiguo'
            
                                               
            print("⚠️ No se pudo detectar formato específico, usando formato ANTIGUO por defecto")
            return 'antiguo'
            
        except Exception as e:
            print(f"⚠️ Error al detectar formato: {e}, usando formato ANTIGUO por defecto")
            return 'antiguo'
    
    def _separar_descripcion(self, descripcion):
        """Para formato antiguo: separa descripción mezclada."""
        if pd.isna(descripcion):
            return pd.Series(['', '', ''])
        
        descripcion_str = str(descripcion).strip()
        
                                               
        if descripcion_str == 'PAGO NO IDENTIFICADO':
            return pd.Series(['PAGO NO IDENTIFICADO', 'SIN_REF', 'REVISAR'])
        
                                               
        if descripcion_str == 'COMISIONES BANCARIAS':
            return pd.Series(['COMISIONES BANCARIAS', 'AUTO', 'BANCO'])
        
                                                                          
        partes = descripcion_str.split(maxsplit=2)
        
                                               
        while len(partes) < 3:
            partes.append('')
        
        return pd.Series(partes[:3])
    
    def _cargar_excel_antiguo(self) -> pd.DataFrame:
        """Carga el formato antiguo (descripción mezclada)."""
        print(f"[1/3] Leyendo archivo Excel (formato antiguo)...")
        
        params = {
            'header': 0,
            'usecols': 'C:D',                                
            'skiprows': 5,
            'engine': 'openpyxl'
        }
        
        if self.sheet_name:
            params['sheet_name'] = self.sheet_name
        
        if self.max_rows:
            params['nrows'] = self.max_rows
        
        df = pd.read_excel(self.excel_path, **params)
        
        print(f"✓ Datos cargados: {len(df)} filas")
        print(f"✓ Columnas encontradas: {df.columns.tolist()}")
        
        return df
    
    def _cargar_excel_nuevo(self) -> pd.DataFrame:
        """Carga el formato nuevo (columnas separadas + hoja COMISIONES)."""
        print(f"[1/3] Leyendo archivo Excel (formato nuevo)...")
        
                                                 
                                                                             
        df = pd.read_excel(
            self.excel_path,
            sheet_name=0,
            header=3,                                     
            usecols='B:E',
            engine='openpyxl'
        )
        
                            
        df.columns = ['TIPO_NOTA', 'REFERENCIA', 'NOMBRE', 'MONTO']
        
                              
        df = df.dropna(subset=['REFERENCIA', 'MONTO'], how='all')
        
        print(f"✓ Egresos normales cargados: {len(df)} filas")
        
                                 
        try:
            df_comisiones = pd.read_excel(
                self.excel_path,
                sheet_name='COMISIONES',
                header=None,
                engine='openpyxl'
            )
            
                                                                                   
            ultima_col = df_comisiones.iloc[:, -1]
            for idx in reversed(range(len(ultima_col))):
                valor = ultima_col.iloc[idx]
                if pd.notna(valor) and isinstance(valor, (int, float)) and valor > 0:
                    total_comisiones = round(float(valor), 2)                           
                    print(f"✓ Total de comisiones encontrado: {total_comisiones}")
                    
                                                         
                    fila_comision = pd.DataFrame({
                        'TIPO_NOTA': ['ND'],
                        'REFERENCIA': ['AUTO'],
                        'NOMBRE': ['COMISIONES BANCARIAS'],
                        'MONTO': [total_comisiones]
                    })
                    
                    df = pd.concat([df, fila_comision], ignore_index=True)
                    break
        except Exception as e:
            print(f"⚠️ No se pudo leer la hoja COMISIONES: {e}")
        
        return df
    
    def _procesar_descripcion(self, df: pd.DataFrame) -> pd.DataFrame:
        print(f"\n[2/3] Separando columna DESCRIPCION...")
        
        if 'DESCRIPCION' not in df.columns:
            raise ValueError("No se encontró la columna 'DESCRIPCION' en el Excel")
        
        df[['TIPO_NOTA', 'REFERENCIA', 'NOMBRE']] = df['DESCRIPCION'].apply(self._separar_descripcion)
        
        df_procesado = df[['TIPO_NOTA', 'REFERENCIA', 'NOMBRE', 'MONTO']]
        
        print(f"✓ Columna DESCRIPCION separada en: TIPO_NOTA, REFERENCIA, NOMBRE")
        
        return df_procesado
    
    def _limpiar_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        print(f"\n[3/3] Limpiando datos...")
        
        filas_antes = len(df)
        
                                                          
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
                                              
            self.formato_detectado = self._detectar_formato()
            
                                     
            if self.formato_detectado == 'nuevo':
                df = self._cargar_excel_nuevo()
                                                     
            else:
                df = self._cargar_excel_antiguo()
                df = self._procesar_descripcion(df)
            
                                                       
            df = self._limpiar_datos(df)
            
                         
            df.to_csv(self.csv_path, index=False, encoding='utf-8-sig')
            
                     
            print("\n" + "=" * 60)
            print("PROCESO COMPLETADO EXITOSAMENTE")
            print("=" * 60)
            print(f"📊 Total de registros procesados: {len(df)}")
            print(f"📁 Archivo generado: {self.csv_path}")
            
                                     
            casos_especiales = df[df['REFERENCIA'].isin(['SIN_REF', 'AUTO'])].shape[0]
            if casos_especiales > 0:
                print(f"⚠️  Casos especiales detectados: {casos_especiales}")
                print(f"   - PAGO NO IDENTIFICADO: {(df['REFERENCIA'] == 'SIN_REF').sum()}")
                print(f"   - COMISIONES BANCARIAS: {(df['REFERENCIA'] == 'AUTO').sum()}")
            
                             
            print("\n--- MUESTRA DE DATOS (primeras 5 filas) ---")
            print(df.head())
            
            return self.csv_path
            
        except Exception as e:
            print(f"\n✗ ERROR al procesar el archivo: {e}")
            raise
