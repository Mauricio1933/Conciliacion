"""
Clase Base Abstracta para Conciliadores
Define el contrato que todos los conciliadores deben cumplir
"""

from abc import ABC, abstractmethod
import pandas as pd

#================================================================================
# CLASE BASE ABSTRACTA - CONCILIADOR
#================================================================================

class BaseConciliador(ABC):
    """
    Clase base abstracta que define el contrato para todos los conciliadores.
    Cada tipo de pago (OTR, TRA, TDD) debe implementar esta interfaz.
    """
    
    def __init__(self, estado_cuenta_df: pd.DataFrame, libro_ventas_df: pd.DataFrame):
        """
        Constructor base.
        
        Args:
            estado_cuenta_df: DataFrame con movimientos del banco
            libro_ventas_df: DataFrame con ventas del libro
        """
        self.estado_cuenta = estado_cuenta_df
        self.libro_ventas = libro_ventas_df
        self.resultados = None
        self.tipo_pago = None  # Será definido por cada hijo (OTR, TRA, TDD)
        self.codigo_pago = None  # Código en el libro (OTR, TRA, TJD)
    
    #============================================================================
    # MÉTODOS ABSTRACTOS (OBLIGATORIOS)
    #============================================================================
    
    @abstractmethod
    def filtrar_transacciones(self):
        """
        Filtra las transacciones del tipo específico del estado de cuenta y libro.
        Cada conciliador implementa su propia lógica de filtrado.
        """
        pass
    
    @abstractmethod
    def conciliar(self):
        """
        Ejecuta la lógica de conciliación específica.
        Cada conciliador tiene su propio algoritmo de matching.
        """
        pass
    
    #============================================================================
    # MÉTODOS COMUNES (COMPARTIDOS)
    #============================================================================
    
    def obtener_resultados(self) -> pd.DataFrame:
        """
        Retorna el DataFrame de resultados.
        
        Returns:
            pd.DataFrame: Resultados de la conciliación
        """
        return self.resultados if self.resultados is not None else pd.DataFrame()
    
    def exportar_resultados(self, ruta: str):
        """
        Exporta resultados a CSV.
        
        Args:
            ruta: Ruta del archivo de salida
        """
        if self.resultados is not None and not self.resultados.empty:
            self.resultados.to_csv(ruta, sep=';', encoding='utf-8-sig', index=False)
            print(f"✅ Resultados de {self.tipo_pago} exportados a: {ruta}")
        else:
            print(f"⚠️  No hay resultados de {self.tipo_pago} para exportar")
    
    def obtener_estadisticas(self) -> dict:
        """
        Calcula estadísticas de la conciliación.
        
        Returns:
            dict: Diccionario con estadísticas
        """
        if self.resultados is None or self.resultados.empty:
            return {
                'tipo_pago': self.tipo_pago,
                'total': 0,
                'conciliados': 0,
                'pendientes': 0,
                'requiere_revision': 0,
                'tasa_conciliacion': 0.0
            }
        
        total = len(self.resultados)
        conciliados = len(self.resultados[self.resultados['Estado'].str.contains('Conciliado', na=False)])
        pendientes = len(self.resultados[self.resultados['Estado'].str.contains('Pendiente', na=False)])
        requiere_revision = len(self.resultados[self.resultados['Estado'].str.contains('Requiere Revisión', na=False)])
        
        tasa = (conciliados / total * 100) if total > 0 else 0.0
        
        return {
            'tipo_pago': self.tipo_pago,
            'total': total,
            'conciliados': conciliados,
            'pendientes': pendientes,
            'requiere_revision': requiere_revision,
            'tasa_conciliacion': tasa
        }
    
    def ejecutar(self):
        """
        Método plantilla que ejecuta el flujo completo de conciliación.
        Este método es igual para todos, pero usa métodos específicos de cada hijo.
        """
        print(f"\n🔄 Iniciando conciliación de {self.tipo_pago}...")
        
        # Paso 1: Filtrar transacciones
        self.filtrar_transacciones()
        
        # Paso 2: Ejecutar conciliación
        self.conciliar()
        
        # Paso 3: Mostrar estadísticas
        stats = self.obtener_estadisticas()
        print(f"   ✅ Conciliados: {stats['conciliados']}/{stats['total']} ({stats['tasa_conciliacion']:.1f}%)")
        print(f"   ⚠️  Pendientes: {stats['pendientes']}")
        print(f"   🔍 Requiere Revisión: {stats['requiere_revision']}")
        
        return self.resultados
