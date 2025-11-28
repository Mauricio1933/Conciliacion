"""
Funciones de Validación para Conciliación Bancaria
Cálculos y validaciones reutilizables
"""

from datetime import timedelta

#================================================================================
# VALIDACIÓN DE DÍAS HÁBILES
#================================================================================

def es_dia_habil(fecha):
    """
    Verifica si una fecha es día hábil (lunes a viernes).
    
    Args:
        fecha (datetime): Fecha a verificar
        
    Returns:
        bool: True si es día hábil, False si es fin de semana
    """
    return fecha.weekday() < 5  # 0=Lunes, 4=Viernes

def calcular_dias_habiles(fecha_inicio, fecha_fin):
    """
    Calcula la cantidad de días hábiles entre dos fechas.
    
    Args:
        fecha_inicio (datetime): Fecha inicial
        fecha_fin (datetime): Fecha final
        
    Returns:
        int: Cantidad de días hábiles (excluye fines de semana)
    """
    if fecha_inicio > fecha_fin:
        return -1
    
    dias_habiles = 0
    fecha_actual = fecha_inicio + timedelta(days=1)  # Empezar desde el día siguiente
    
    while fecha_actual <= fecha_fin:
        if es_dia_habil(fecha_actual):
            dias_habiles += 1
        fecha_actual += timedelta(days=1)
    
    return dias_habiles

def calcular_diferencia_dias(fecha1, fecha2):
    """
    Calcula la diferencia absoluta en días entre dos fechas.
    
    Args:
        fecha1 (datetime): Primera fecha
        fecha2 (datetime): Segunda fecha
        
    Returns:
        int: Diferencia en días (valor absoluto)
    """
    try:
        return abs((fecha1 - fecha2).days)
    except:
        return 999  # Valor alto para indicar error

#================================================================================
# VALIDACIÓN DE MONTOS
#================================================================================

def calcular_diferencia_porcentual(monto_libro, monto_banco):
    """
    Calcula la diferencia porcentual entre dos montos.
    
    Fórmula: (Monto_Libro - Monto_Banco) / Monto_Libro * 100
    
    Args:
        monto_libro (float): Monto del libro de ventas
        monto_banco (float): Monto del banco
        
    Returns:
        float: Diferencia porcentual
    """
    if monto_libro == 0:
        return 0.0
    
    return ((monto_libro - monto_banco) / monto_libro) * 100

def validar_monto_cercano(monto1, monto2, tolerancia=0.10):
    """
    Verifica si dos montos están dentro de la tolerancia especificada.
    
    Args:
        monto1 (float): Primer monto
        monto2 (float): Segundo monto
        tolerancia (float): Tolerancia en Bs (default: 0.10)
        
    Returns:
        bool: True si la diferencia está dentro de la tolerancia
    """
    return abs(monto1 - monto2) <= tolerancia

def calcular_comision(monto_bruto, monto_neto):
    """
    Calcula la comisión bancaria.
    
    Args:
        monto_bruto (float): Monto antes de comisión
        monto_neto (float): Monto después de comisión
        
    Returns:
        float: Comisión cobrada
    """
    return monto_bruto - monto_neto
