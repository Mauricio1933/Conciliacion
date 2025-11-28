"""
Sistema de Estados para Conciliación Bancaria
Arquitectura basada en herencia y polimorfismo para estados reutilizables
"""

from abc import ABC, abstractmethod
from enum import Enum
from PyQt6.QtGui import QColor

class TipoEstado(Enum):
    """Tipos base de estado de conciliación"""
    CONCILIADO = "Conciliado"
    PENDIENTE = "Pendiente en Banco"
    REQUIERE_REVISION = "Requiere Revisión"

#================================================================================
# CLASE BASE ABSTRACTA - ESTADO DE CONCILIACIÓN
#================================================================================

class EstadoConciliacion(ABC):
    """
    Clase base abstracta para todos los estados de conciliación.
    Define el contrato que todos los estados deben cumplir.
    """
    
    def __init__(self):
        self.tipo_base = None
        self.subtipo = None
        self.prioridad = 0  # 1=bajo, 10=crítico
        self.descripcion_detallada = ""
    
    @abstractmethod
    def obtener_descripcion(self) -> str:
        """Retorna la descripción completa del estado"""
        pass
    
    @abstractmethod
    def obtener_color_fondo(self) -> str:
        """Retorna el color de fondo para la UI (hex)"""
        pass
    
    @abstractmethod
    def obtener_color_texto(self) -> str:
        """Retorna el color de texto para la UI (hex)"""
        pass
    
    def es_critico(self) -> bool:
        """Indica si el estado requiere atención inmediata"""
        return self.prioridad >= 7
    
    def requiere_negrita(self) -> bool:
        """Indica si debe mostrarse en negrita"""
        return self.prioridad >= 5

#================================================================================
# ESTADOS BASE - NIVEL 1
#================================================================================

class Conciliado(EstadoConciliacion):
    """Estado base: Transacción conciliada exitosamente"""
    
    def __init__(self):
        super().__init__()
        self.tipo_base = TipoEstado.CONCILIADO
        self.prioridad = 1
    
    def obtener_descripcion(self) -> str:
        return "Conciliado"
    
    def obtener_color_fondo(self) -> str:
        return "#d4edda"  # Verde suave
    
    def obtener_color_texto(self) -> str:
        return "#155724"  # Verde oscuro

class PendienteEnBanco(EstadoConciliacion):
    """Estado base: Transacción pendiente de aparecer en banco"""
    
    def __init__(self):
        super().__init__()
        self.tipo_base = TipoEstado.PENDIENTE
        self.prioridad = 5
    
    def obtener_descripcion(self) -> str:
        return "Pendiente en Banco"
    
    def obtener_color_fondo(self) -> str:
        return "#fff3cd"  # Amarillo suave
    
    def obtener_color_texto(self) -> str:
        return "#856404"  # Amarillo oscuro

class RequiereRevision(EstadoConciliacion):
    """Estado base: Transacción requiere revisión manual"""
    
    def __init__(self):
        super().__init__()
        self.tipo_base = TipoEstado.REQUIERE_REVISION
        self.prioridad = 7
    
    def obtener_descripcion(self) -> str:
        return "Requiere Revisión"
    
    def obtener_color_fondo(self) -> str:
        return "#f8d7da"  # Rojo suave
    
    def obtener_color_texto(self) -> str:
        return "#721c24"  # Rojo oscuro

#================================================================================
# ESTADOS ESPECÍFICOS - PAGO MÓVIL (OTR)
#================================================================================

class ConciliadoPagoMovil(Conciliado):
    """Pago Móvil conciliado con match de referencia y monto"""
    
    def __init__(self, diferencia_dias: int = 0):
        super().__init__()
        self.subtipo = "Pago Móvil"
        self.diferencia_dias = diferencia_dias
    
    def obtener_descripcion(self) -> str:
        if self.diferencia_dias <= 1:
            return "Conciliado"
        return f"Conciliado (±{self.diferencia_dias} días)"

class RevisionPagoMovilFechaDiferente(RequiereRevision):
    """Pago Móvil con fecha fuera de tolerancia"""
    
    def __init__(self, diferencia_dias: int):
        super().__init__()
        self.subtipo = "Fecha Diferente"
        self.diferencia_dias = diferencia_dias
        self.prioridad = 6
    
    def obtener_descripcion(self) -> str:
        return f"Requiere Revisión - Fecha Diferente (±{self.diferencia_dias} días)"
    
    def obtener_color_fondo(self) -> str:
        return "#ffe0b2"  # Naranja suave

class RevisionPagoMovilRefDuplicada(RequiereRevision):
    """Pago Móvil con referencia duplicada"""
    
    def __init__(self, num_coincidencias: int):
        super().__init__()
        self.subtipo = "Ref Duplicada"
        self.num_coincidencias = num_coincidencias
        self.prioridad = 8
    
    def obtener_descripcion(self) -> str:
        return f"Requiere Revisión - Ref Duplicada ({self.num_coincidencias} coincidencias)"

#================================================================================
# ESTADOS ESPECÍFICOS - TRANSFERENCIAS (TRA)
#================================================================================

class ConciliadoTransferencia(Conciliado):
    """Transferencia conciliada con match exacto"""
    
    def __init__(self):
        super().__init__()
        self.subtipo = "Transferencia"
    
    def obtener_descripcion(self) -> str:
        return "Conciliado"

class RevisionTransferenciaRefDuplicada(RequiereRevision):
    """Transferencia con referencia duplicada"""
    
    def __init__(self, num_coincidencias: int):
        super().__init__()
        self.subtipo = "Ref Duplicada"
        self.num_coincidencias = num_coincidencias
        self.prioridad = 8
    
    def obtener_descripcion(self) -> str:
        return f"Requiere Revisión - Ref Duplicada ({self.num_coincidencias} coincidencias)"

#================================================================================
# ESTADOS ESPECÍFICOS - TARJETAS DE DÉBITO (TJD/TDD)
#================================================================================

class ConciliadoTDD(Conciliado):
    """TDD conciliado con comisión estándar (1-3%)"""
    
    def __init__(self, porcentaje_comision: float):
        super().__init__()
        self.subtipo = "TDD"
        self.porcentaje_comision = porcentaje_comision
    
    def obtener_descripcion(self) -> str:
        return f"Conciliado - Comisión {self.porcentaje_comision:.2f}%"

class RevisionTDDDiferenciaAlta(RequiereRevision):
    """TDD con diferencia de comisión alta (3.5%-25%)"""
    
    def __init__(self, porcentaje: float):
        super().__init__()
        self.subtipo = "Diferencia Alta"
        self.porcentaje = porcentaje
        self.prioridad = 6
    
    def obtener_descripcion(self) -> str:
        return f"Requiere Revisión - Diferencia Alta ({self.porcentaje:.2f}%)"
    
    def obtener_color_fondo(self) -> str:
        return "#ffe0b2"  # Naranja suave
    
    def obtener_color_texto(self) -> str:
        return "#e65100"  # Naranja oscuro

class RevisionTDDMontoMayorEnBanco(RequiereRevision):
    """TDD con monto mayor en banco (comisión negativa)"""
    
    def __init__(self, porcentaje: float):
        super().__init__()
        self.subtipo = "Monto Mayor en Banco"
        self.porcentaje = porcentaje
        self.prioridad = 7
    
    def obtener_descripcion(self) -> str:
        return f"Requiere Revisión - Monto Mayor en Banco ({self.porcentaje:.2f}%)"
    
    def obtener_color_fondo(self) -> str:
        return "#ffcdd2"  # Rojo claro
    
    def obtener_color_texto(self) -> str:
        return "#c62828"  # Rojo oscuro

class RevisionTDDDiferenciaExcesiva(RequiereRevision):
    """TDD con diferencia excesiva (>25%)"""
    
    def __init__(self, porcentaje: float):
        super().__init__()
        self.subtipo = "Diferencia Excesiva"
        self.porcentaje = porcentaje
        self.prioridad = 9
    
    def obtener_descripcion(self) -> str:
        return f"Requiere Revisión - Diferencia Excesiva ({self.porcentaje:.2f}%)"
    
    def obtener_color_fondo(self) -> str:
        return "#f8d7da"  # Rojo fuerte
    
    def obtener_color_texto(self) -> str:
        return "#721c24"  # Rojo muy oscuro
