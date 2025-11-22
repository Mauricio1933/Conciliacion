"""
Script de prueba para verificar la suma de comisiones
"""

import pandas as pd
from pathlib import Path

# Cargar archivos
directorio = Path(__file__).parent
estado_cuenta = pd.read_csv(directorio / "Estado_Cuenta-3_limpio.csv")
registro_saint = pd.read_csv(directorio / "egresos_saint_bancaribe_junio_mejorado.csv")

print("=" * 70)
print("VERIFICACIÓN DE COMISIONES BANCARIAS")
print("=" * 70)

# Normalizar encabezados
estado_cuenta.columns = estado_cuenta.columns.str.upper().str.strip()
registro_saint.columns = registro_saint.columns.str.upper().str.strip()

# Filtrar solo ND
df_banco = estado_cuenta[estado_cuenta['TIPO'] == 'ND'].copy()

# Normalizar montos del banco
df_banco['MONTO'] = df_banco['CARGO'].astype(str)
df_banco['MONTO'] = df_banco['MONTO'].str.replace('.', '', regex=False)
df_banco['MONTO'] = df_banco['MONTO'].str.replace(',', '.', regex=False)
df_banco['MONTO'] = pd.to_numeric(df_banco['MONTO'], errors='coerce')

# Normalizar montos de Saint
registro_saint['MONTO'] = pd.to_numeric(registro_saint['MONTO'], errors='coerce')

# Buscar comisiones en el banco
comisiones_banco = df_banco[df_banco['DESCRIPCIÓN'].str.contains('COMISION', case=False, na=False)].copy()

print(f"\n📊 COMISIONES EN ESTADO DE CUENTA:")
print(f"   Total de comisiones encontradas: {len(comisiones_banco)}")
print(f"\n   Primeras 10 comisiones:")
for idx, row in comisiones_banco.head(10).iterrows():
    print(f"   - {row['FECHA']}: {row['DESCRIPCIÓN'][:40]:40} = Bs. {row['MONTO']:>10,.2f}")

if len(comisiones_banco) > 10:
    print(f"   ... y {len(comisiones_banco) - 10} más")

suma_comisiones = comisiones_banco['MONTO'].sum()
print(f"\n   💰 SUMA TOTAL DE COMISIONES: Bs. {suma_comisiones:,.2f}")

# Buscar en Saint
print(f"\n📊 COMISIONES EN REGISTRO SAINT:")
comision_saint = registro_saint[
    registro_saint['TIPO_NOTA'].str.contains('COMISION', case=False, na=False)
]

if not comision_saint.empty:
    for idx, row in comision_saint.iterrows():
        print(f"   - {row['TIPO_NOTA']}: {row['NOMBRE']} = Bs. {row['MONTO']:,.2f}")
    
    monto_saint = comision_saint['MONTO'].iloc[0]
    print(f"\n   💰 MONTO EN SAINT: Bs. {monto_saint:,.2f}")
    
    # Comparar
    diferencia = abs(suma_comisiones - monto_saint)
    print(f"\n🔍 COMPARACIÓN:")
    print(f"   Suma Banco:  Bs. {suma_comisiones:,.2f}")
    print(f"   Monto Saint: Bs. {monto_saint:,.2f}")
    print(f"   Diferencia:  Bs. {diferencia:,.2f}")
    
    if diferencia < 0.10:
        print(f"\n   ✅ LAS COMISIONES COINCIDEN (diferencia < 0.10)")
    else:
        print(f"\n   ⚠️ LAS COMISIONES NO COINCIDEN (diferencia = {diferencia:.2f})")
        print(f"\n   Posibles razones:")
        print(f"   - Hay comisiones en el banco que no están incluidas")
        print(f"   - Hay comisiones en Saint que no están en el banco")
        print(f"   - Error en el cálculo o formato de montos")
else:
    print("   ❌ No se encontró registro de comisiones en Saint")

print("\n" + "=" * 70)

# Guardar detalle de comisiones
comisiones_banco_export = comisiones_banco[['FECHA', 'REFERENCIA', 'DESCRIPCIÓN', 'MONTO']].copy()
comisiones_banco_export.to_csv(
    directorio / "comisiones_detalle.csv",
    index=False,
    encoding='utf-8-sig',
    sep=';'
)
print(f"\n✅ Detalle de comisiones guardado en: comisiones_detalle.csv")
