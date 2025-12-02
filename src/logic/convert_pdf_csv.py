import pdfplumber
import csv
import re
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional

class EstadoDeCuentaPdfToCsv:
    #Procesa estados de cuenta en PDF y los convierte a CSV limpio.
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.base = self.pdf_path.stem
        self.txt_path = self.pdf_path.with_suffix('.txt')
        self.csv_path = self.pdf_path.parent / f"{self.base}_limpio.csv"
        self.resumen_path = self.pdf_path.parent / f"{self.base}_resumen.json"
        self.patron_fecha = re.compile(r'^\d{2}-[A-Z]{3}-\d{4}$')
        self.patron_numero_largo = re.compile(r'\d{10,}')  # Números de 10+ dígitos

    def convertir_pdf_a_txt(self) -> Path:
        #Esta funcion extrae la informacion del Pdf y lo tnasforma a un Txt
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
        
        # Los últimos 3 elementos SIEMPRE son: cargo, abono, saldo
        cargo = partes[-3]
        abono = partes[-2]
        saldo = partes[-1]
        
        # Esto se encarga de encontrar dónde empieza la referencia (primer número largo después de la fecha)
        idx_referencia = None
        for i in range(1, len(partes) - 3):  # Excluir fecha y los 3 últimos (montos)
            if partes[i].isdigit() and len(partes[i]) >= 10:
                idx_referencia = i
                break
        
        if idx_referencia is None:
            # Si no hay referencia larga, asumir estructura simple
            oficina = partes[1]
            referencia = partes[2]
            tipo = partes[3]
            descripcion_partes = partes[4:-3]
        else:
            # La oficina es todo entre la fecha y la referencia
            oficina = " ".join(partes[1:idx_referencia])
            referencia = partes[idx_referencia]
            tipo = partes[idx_referencia + 1]
            descripcion_partes = partes[idx_referencia + 2:-3]
        
        descripcion = " ".join(descripcion_partes)
        
        lineas_consumidas = 0
        
        # Verificar si hay continuación en las siguientes líneas
        if lineas_siguientes:
            siguiente = lineas_siguientes[0]
            
            # Si la siguiente línea NO es un movimiento
            if not self._es_linea_movimiento(siguiente):
                # Buscar si hay un número largo en la siguiente línea (posible continuación de referencia)
                numero_encontrado = self._extraer_numero_largo(siguiente)
                
                if numero_encontrado:
                    # Concatenar a la referencia
                    referencia += numero_encontrado
                    # Quitar ese número de la descripción adicional
                    descripcion_adicional = siguiente.replace(numero_encontrado, "").strip()
                    if descripcion_adicional:
                        descripcion += " " + descripcion_adicional
                else:
                    # Solo es descripción adicional
                    descripcion += " " + siguiente.strip()
                
                lineas_consumidas = 1

        return (
            (fecha, oficina, referencia, tipo, descripcion.strip(), cargo, abono, saldo),
            lineas_consumidas
        )

    def procesar_txt_a_csv(self) -> Path:
        #Esta funcion procesa el txt ya creado y lo convierte a un csv limpio
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

        # Guardar en CSV
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
            
            # Buscar Saldo Mes Anterior
            match_saldo_anterior = re.search(r'Saldo Mes Anterior\s+--\s+([\d.,]+)', contenido)
            if match_saldo_anterior:
                resumen['saldo_mes_anterior'] = match_saldo_anterior.group(1)
            
            # Buscar Notas de Crédito (cantidad y monto)
            match_nc = re.search(r'Notas de Crédito\s+(\d+)\s+([\d.,]+)', contenido)
            if match_nc:
                resumen['notas_credito_cantidad'] = int(match_nc.group(1))
                resumen['notas_credito_monto'] = match_nc.group(2)
            
            # Buscar Notas de Débito (cantidad y monto)
            match_nd = re.search(r'Notas de Débito\s+(\d+)\s+([\d.,]+)', contenido)
            if match_nd:
                resumen['notas_debito_cantidad'] = int(match_nd.group(1))
                resumen['notas_debito_monto'] = match_nd.group(2)
            
            # Buscar Saldo Final del Mes
            match_saldo_final = re.search(r'Saldo Final del Mes\s+--\s+([\d.,]+)', contenido)
            if match_saldo_final:
                resumen['saldo_final_mes'] = match_saldo_final.group(1)
            
            # Guardar en JSON
            if resumen:
                with open(self.resumen_path, 'w', encoding='utf-8') as f:
                    json.dump(resumen, f, indent=2, ensure_ascii=False)
                print(f"✓ Resumen bancario extraído: {self.resumen_path}")
            
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
            # Eliminar archivo TXT temporal incluso si hay errores
            self.limpiar_archivos_intermedios()
    
    def limpiar_archivos_intermedios(self):
        """Elimina el archivo TXT intermedio si ya no se necesita."""
        if self.txt_path.exists():
            self.txt_path.unlink()
            print(f"✓ Archivo intermedio eliminado: {self.txt_path}")