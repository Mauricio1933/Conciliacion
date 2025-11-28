"""
Conciliación Maestra - Orquestador de los 3 Conciliadores
Coordina la ejecución de Pago Móvil, Transferencias y TDD
"""

import pandas as pd
from pathlib import Path
from .conciliadores import PagoMovilConciliador, TransferenciaConciliador, TDDConciliador

#================================================================================
# CLASE MAESTRA ORQUESTADORA
#================================================================================

class ConciliacionMaestra:
    """
    Orquesta los 3 conciliadores para ejecutar la conciliación completa.
    
    Coordina:
    - Pago Móvil (OTR)
    - Transferencias (TRA)
    - Tarjetas de Débito (TDD/TJD)
    """
    
    def __init__(self, estado_cuenta_df: pd.DataFrame, libro_ventas_df: pd.DataFrame):
        """
        Inicializa la conciliación maestra.
        
        Args:
            estado_cuenta_df: DataFrame con movimientos del banco
            libro_ventas_df: DataFrame con ventas del libro
        """
        print("🔧 Inicializando sistema de conciliación...")
        
        self.estado_cuenta_df = estado_cuenta_df
        self.libro_ventas_df = libro_ventas_df
        
        # Crear instancias de los 3 conciliadores
        self.pago_movil = PagoMovilConciliador(
            estado_cuenta_df,
            libro_ventas_df
        )
        
        self.transferencia = TransferenciaConciliador(
            estado_cuenta_df,
            libro_ventas_df
        )
        
        self.tdd = TDDConciliador(
            estado_cuenta_df,
            libro_ventas_df
        )
        
        self.resultados_consolidados = None
    
    def ejecutar_conciliacion_completa(self):
        """
        Ejecuta los 3 conciliadores en secuencia y consolida resultados.
        
        Returns:
            pd.DataFrame: Resultados consolidados de los 3 tipos de pago
        """
        print("\n" + "=" * 80)
        print("CONCILIACIÓN BANCARIA COMPLETA")
        print("=" * 80)
        
        # Ejecutar cada conciliador
        print("\n1️⃣ Pago Móvil (OTR)")
        self.pago_movil.ejecutar()
        
        print("\n2️⃣ Transferencias (TRA)")
        self.transferencia.ejecutar()
        
        print("\n3️⃣ Tarjetas de Débito (TDD)")
        self.tdd.ejecutar()
        
        # Consolidar resultados
        self._consolidar_resultados()
        
        # Mostrar resumen
        self._mostrar_resumen()
        
        return self.resultados_consolidados
    
    def _consolidar_resultados(self):
        """Consolida los resultados de los 3 conciliadores en un solo DataFrame"""
        resultados = []
        
        # Agregar resultados de Pago Móvil
        df_pm = self.pago_movil.obtener_resultados()
        if not df_pm.empty:
            resultados.append(df_pm)
        
        # Agregar resultados de Transferencias
        df_tra = self.transferencia.obtener_resultados()
        if not df_tra.empty:
            resultados.append(df_tra)
        
        # Agregar resultados de TDD
        df_tdd = self.tdd.obtener_resultados()
        if not df_tdd.empty:
            resultados.append(df_tdd)
        
        # Concatenar todos los resultados
        if resultados:
            self.resultados_consolidados = pd.concat(resultados, ignore_index=True)
        else:
            self.resultados_consolidados = pd.DataFrame()
    
    def _mostrar_resumen(self):
        """Muestra resumen consolidado de la conciliación"""
        print("\n" + "=" * 80)
        print("📊 RESUMEN CONSOLIDADO")
        print("=" * 80)
        
        stats_pm = self.pago_movil.obtener_estadisticas()
        stats_tra = self.transferencia.obtener_estadisticas()
        stats_tdd = self.tdd.obtener_estadisticas()
        
        print(f"\n{'Tipo de Pago':<25} {'Total':<10} {'Conciliados':<15} {'Pendientes':<15} {'Revisión':<15} {'Tasa':<10}")
        print("-" * 90)
        
        print(f"{stats_pm['tipo_pago']:<25} {stats_pm['total']:<10} {stats_pm['conciliados']:<15} "
              f"{stats_pm['pendientes']:<15} {stats_pm['requiere_revision']:<15} {stats_pm['tasa_conciliacion']:.1f}%")
        
        print(f"{stats_tra['tipo_pago']:<25} {stats_tra['total']:<10} {stats_tra['conciliados']:<15} "
              f"{stats_tra['pendientes']:<15} {stats_tra['requiere_revision']:<15} {stats_tra['tasa_conciliacion']:.1f}%")
        
        print(f"{stats_tdd['tipo_pago']:<25} {stats_tdd['total']:<10} {stats_tdd['conciliados']:<15} "
              f"{stats_tdd['pendientes']:<15} {stats_tdd['requiere_revision']:<15} {stats_tdd['tasa_conciliacion']:.1f}%")
        
        print("-" * 90)
        
        total_transacciones = stats_pm['total'] + stats_tra['total'] + stats_tdd['total']
        total_conciliados = stats_pm['conciliados'] + stats_tra['conciliados'] + stats_tdd['conciliados']
        total_pendientes = stats_pm['pendientes'] + stats_tra['pendientes'] + stats_tdd['pendientes']
        total_revision = stats_pm['requiere_revision'] + stats_tra['requiere_revision'] + stats_tdd['requiere_revision']
        
        tasa_global = (total_conciliados / total_transacciones * 100) if total_transacciones > 0 else 0.0
        
        print(f"{'TOTAL':<25} {total_transacciones:<10} {total_conciliados:<15} "
              f"{total_pendientes:<15} {total_revision:<15} {tasa_global:.1f}%")
        
        print("\n" + "=" * 80)
    
    def exportar_resultados(self, directorio_salida: str = None):
        """
        Exporta resultados consolidados y por tipo de pago.
        
        Args:
            directorio_salida: Directorio donde guardar los archivos
        """
        if directorio_salida is None:
            directorio_salida = Path.cwd() / "resultados_conciliacion"
        else:
            directorio_salida = Path(directorio_salida)
        
        directorio_salida.mkdir(exist_ok=True)
        
        # Exportar consolidado
        if self.resultados_consolidados is not None and not self.resultados_consolidados.empty:
            ruta_consolidado = directorio_salida / "conciliacion_consolidada.csv"
            self.resultados_consolidados.to_csv(ruta_consolidado, sep=';', encoding='utf-8-sig', index=False)
            print(f"\n📁 Consolidado: {ruta_consolidado}")
        
        # Exportar por tipo
        self.pago_movil.exportar_resultados(directorio_salida / "conciliacion_pago_movil.csv")
        self.transferencia.exportar_resultados(directorio_salida / "conciliacion_transferencias.csv")
        self.tdd.exportar_resultados(directorio_salida / "conciliacion_tdd.csv")
    
    def obtener_resultados_consolidados(self) -> pd.DataFrame:
        """
        Retorna el DataFrame consolidado de todos los resultados.
        
        Returns:
            pd.DataFrame: Resultados consolidados
        """
        return self.resultados_consolidados if self.resultados_consolidados is not None else pd.DataFrame()
