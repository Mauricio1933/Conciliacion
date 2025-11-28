"""
Funciones de Normalización para Conciliación Bancaria
Funciones reutilizables para limpiar y estandarizar datos
"""

import pandas as pd
from datetime import datetime

#================================================================================
# NORMALIZACIÓN DE MONTOS
#================================================================================

def normalizar_monto(monto):
    """
    Convierte montos en diferentes formatos a float.
    
    Formatos soportados:
    - Float/Int: 1234.56
    - String con comas: "1.234,56"
    - String con puntos: "1,234.56"
    - String con comillas: '"1234.56"'
    
    Args:
        monto: Monto en cualquier formato
        
    Returns:
        float: Monto normalizado
    """
    if isinstance(monto, (int, float)):
        return float(monto)
    
    if pd.isna(monto) or monto == '':
        return 0.0
    
    # Limpiar y convertir
    monto_str = str(monto).replace('"', '').replace('.', '').replace(',', '.')
    try:
        return float(monto_str)
    except:
        return 0.0

#================================================================================
# NORMALIZACIÓN DE REFERENCIAS
#================================================================================

def normalizar_referencia(ref):
    """
    Normaliza referencias bancarias para comparación.
    
    - Elimina espacios
    - Elimina '.0' al final
    - Convierte a string
    - Toma últimos 6 dígitos para mejor match
    
    Args:
        ref: Referencia en cualquier formato
        
    Returns:
        str: Referencia normalizada
    """
    if pd.isna(ref) or ref == '':
        return ''
    
    ref_str = str(ref).strip()
    
    # Eliminar .0 al final (común en Excel)
    if ref_str.endswith('.0'):
        ref_str = ref_str[:-2]
    
    # Tomar últimos 6 dígitos para mejor comparación
    if len(ref_str) > 6:
        return ref_str[-6:]
    
    return ref_str

#================================================================================
# NORMALIZACIÓN DE FECHAS
#================================================================================

def parsear_fecha(fecha_str):
    """
    Convierte fecha en diferentes formatos a datetime.
    
    Formatos soportados:
    - DD/MM/YYYY (Libro de Ventas)
    - DD-MMM-YYYY (Estado de Cuenta: 03-JUN-2025)
    - YYYY-MM-DD (ISO)
    
    Args:
        fecha_str: Fecha en string
        
    Returns:
        datetime: Objeto datetime o None si falla
    """
    try:
        if pd.isna(fecha_str) or fecha_str == '':
            return None
        
        fecha_str = str(fecha_str).strip()
        
        # Intentar formato DD/MM/YYYY
        if '/' in fecha_str:
            return datetime.strptime(fecha_str, '%d/%m/%Y')
        
        # Intentar formato DD-MMM-YYYY
        elif '-' in fecha_str and len(fecha_str.split('-')) == 3:
            try:
                return datetime.strptime(fecha_str, '%d-%b-%Y')
            except:
                # Intentar DD-MM-YYYY
                return datetime.strptime(fecha_str, '%d-%m-%Y')
        
        # Intentar formato ISO YYYY-MM-DD
        else:
            return datetime.strptime(fecha_str, '%Y-%m-%d')
    
    except:
        return None

def estandarizar_fecha(fecha_str):
    """
    Convierte cualquier fecha a formato estándar DD/MM/YYYY.
    
    Args:
        fecha_str: Fecha en cualquier formato
        
    Returns:
        str: Fecha en formato DD/MM/YYYY o string original si falla
    """
    fecha_dt = parsear_fecha(fecha_str)
    if fecha_dt:
        return fecha_dt.strftime('%d/%m/%Y')
    return str(fecha_str) if fecha_str else ''
