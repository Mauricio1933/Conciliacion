import pdfplumber
import csv
import re
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional

class EstadoDeCuentaPdfToCsv:
                                                                   
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.base = self.pdf_path.stem
        self.txt_path = self.pdf_path.with_suffix('.txt')
        self.csv_path = self.pdf_path.parent / f"{self.base}_limpio.csv"
        self.resumen_path = self.pdf_path.parent / f"{self.base}_resumen.json"
        self.patron_fecha = re.compile(r'^\d{2}-[A-Z]{3}-\d{4}$')
        self.patron_numero_largo = re.compile(r'\d{10,}')                          

    def convertir_pdf_a_txt(self) -> Path:
                                                                           
        try:
            texto_completo = []
            
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, pagina in enumerate(pdf.pages, 1):
                    contenido = pagina.extract_text()
                    if contenido:
                        texto_completo.append(contenido)
                    else:
                        print(f"⚠️ Advertencia: Página {i} vacía o sin texto extraíble")

            with open(self.txt_path, "w", encoding="utf-8") as txt_file:
                txt_file.write("\n".join(texto_completo))

            print(f"✓ PDF convertido a TXT: {self.txt_path}")
            return self.txt_path
            
        except Exception as e:
            raise Exception(f"Error al convertir PDF a TXT: {e}")

    def _es_linea_movimiento(self, linea: str) -> bool:
        """Determina si una línea representa un movimiento bancario."""
        partes = linea.split()
        return len(partes) > 0 and self.patron_fecha.match(partes[0])

    def _extraer_numero_largo(self, texto: str) -> str:
        """Extrae número largo (10+ dígitos) de un texto."""
        match = self.patron_numero_largo.search(texto)
        return match.group(0) if match else ""

    def _parsear_movimiento(self, linea: str, lineas_siguientes: List[str]) -> Tuple[Tuple, int]:
        """
        Extrae los campos de un movimiento bancario.
        Retorna: (tupla_movimiento, cantidad_de_lineas_consumidas)
        """
        partes = linea.split()
        
        fecha = partes[0]
        
                                                                  
        cargo = partes[-3]
        abono = partes[-2]
        saldo = partes[-1]
        
                                                                                                            
        idx_referencia = None
        for i in range(1, len(partes) - 3):                                          
            if partes[i].isdigit() and len(partes[i]) >= 10:
                idx_referencia = i
                break
        
        if idx_referencia is None:
                                                                  
            oficina = partes[1]
            referencia = partes[2]
            tipo = partes[3]
            descripcion_partes = partes[4:-3]
        else:
                                                               
            oficina = " ".join(partes[1:idx_referencia])
            referencia = partes[idx_referencia]
            tipo = partes[idx_referencia + 1]
            descripcion_partes = partes[idx_referencia + 2:-3]
        
        descripcion = " ".join(descripcion_partes)
        
        lineas_consumidas = 0
        
                                                                
        if lineas_siguientes:
            siguiente = lineas_siguientes[0]
            
                                                       
            if not self._es_linea_movimiento(siguiente):
                                                                                                          
                numero_encontrado = self._extraer_numero_largo(siguiente)
                
                if numero_encontrado:
                                                
                    referencia += numero_encontrado
                                                                   
                    descripcion_adicional = siguiente.replace(numero_encontrado, "").strip()
                    if descripcion_adicional:
                        descripcion += " " + descripcion_adicional
                else:
                                                   
                    descripcion += " " + siguiente.strip()
                
                lineas_consumidas = 1

        return (
            (fecha, oficina, referencia, tipo, descripcion.strip(), cargo, abono, saldo),
            lineas_consumidas
        )

    def procesar_txt_a_csv(self) -> Path:
                                                                             
        if not self.txt_path.exists():
            raise FileNotFoundError(f"Archivo TXT no encontrado: {self.txt_path}")

        movimientos = []

        with open(self.txt_path, "r", encoding="utf-8") as f:
            lineas = [l.strip() for l in f if l.strip()]

        i = 0
        while i < len(lineas):
            linea = lineas[i]

            if self._es_linea_movimiento(linea):
                lineas_siguientes = lineas[i + 1:] if i + 1 < len(lineas) else []
                movimiento, lineas_consumidas = self._parsear_movimiento(linea, lineas_siguientes)
                movimientos.append(movimiento)
                i += lineas_consumidas

            i += 1

                        
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Fecha", "Oficina", "Referencia", "Tipo", "Descripción", "Cargo", "Abono", "Saldo"])
            writer.writerows(movimientos)

        print(f"✓ CSV generado: {self.csv_path} ({len(movimientos)} movimientos)")
        return self.csv_path

    def extraer_resumen_bancario(self) -> Optional[Dict]:
        """Extrae el resumen bancario del TXT (Saldo Mes Anterior, NC, ND, Saldo Final)."""
        if not self.txt_path.exists():
            return None
        
        try:
            with open(self.txt_path, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            resumen = {}
            campos_faltantes = []
            
                                                                                                     
            match_saldo_anterior = re.search(r'Saldo\s+Mes\s+Anterior\s*[-–—]*\s*([\d.,]+)', contenido, re.IGNORECASE)
            if match_saldo_anterior:
                resumen['saldo_mes_anterior'] = match_saldo_anterior.group(1)
            else:
                campos_faltantes.append('Saldo Mes Anterior')
            
                                                                                    
            match_nc = re.search(r'Notas?\s+de\s+Cr[ée]dito\s+(\d+)\s+([\d.,]+)', contenido, re.IGNORECASE)
            if match_nc:
                resumen['notas_credito_cantidad'] = int(match_nc.group(1))
                resumen['notas_credito_monto'] = match_nc.group(2)
            else:
                campos_faltantes.append('Notas de Crédito')
            
                                                   
            match_nd = re.search(r'Notas?\s+de\s+D[ée]bito\s+(\d+)\s+([\d.,]+)', contenido, re.IGNORECASE)
            if match_nd:
                resumen['notas_debito_cantidad'] = int(match_nd.group(1))
                resumen['notas_debito_monto'] = match_nd.group(2)
            else:
                campos_faltantes.append('Notas de Débito')
            
                                                             
            match_saldo_final = re.search(r'Saldo\s+Final\s+(?:del\s+)?Mes\s*[-–—]*\s*([\d.,]+)', contenido, re.IGNORECASE)
            if match_saldo_final:
                resumen['saldo_final_mes'] = match_saldo_final.group(1)
            else:
                campos_faltantes.append('Saldo Final del Mes')
            
                                                 
            if campos_faltantes:
                print(f"⚠️ No se encontraron los siguientes campos en el PDF:")
                for campo in campos_faltantes:
                    print(f"   - {campo}")
                print(f"   Esto puede deberse a un formato diferente del estado de cuenta.")
            
                                                          
            if resumen:
                with open(self.resumen_path, 'w', encoding='utf-8') as f:
                    json.dump(resumen, f, indent=2, ensure_ascii=False)
                
                                                                       
                if len(campos_faltantes) == 0:
                    print(f"✓ Resumen bancario extraído completo: {self.resumen_path}")
                else:
                    print(f"⚠️ Resumen bancario extraído parcialmente: {self.resumen_path}")
                    print(f"   ({len(resumen)} de 4 campos encontrados)")
            else:
                print(f"❌ No se pudo extraer ningún dato del resumen bancario")
                print(f"   El formato del PDF podría ser incompatible")
            
            return resumen if resumen else None
            
        except Exception as e:
            print(f"⚠️ Error al extraer resumen bancario: {e}")
            return None

    def ejecutar(self) -> Tuple[Path, Optional[Dict]]:
        """Ejecuta el flujo completo: PDF → TXT → CSV + Resumen (elimina TXT automáticamente)."""
        print(f"Procesando: {self.pdf_path.name}")
        try:
            self.convertir_pdf_a_txt()
            resumen = self.extraer_resumen_bancario()
            csv_resultado = self.procesar_txt_a_csv()
            return csv_resultado, resumen
        finally:
                                                                  
            self.limpiar_archivos_intermedios()
    
    def limpiar_archivos_intermedios(self):
        """Elimina el archivo TXT intermedio si ya no se necesita."""
        if self.txt_path.exists():
            self.txt_path.unlink()
            print(f"✓ Archivo intermedio eliminado: {self.txt_path}")