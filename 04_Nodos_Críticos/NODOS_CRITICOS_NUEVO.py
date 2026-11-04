###########################################################################
# SCRIPT PARA LA IDENTIFICACIÓN DE NODOS CRÍTICOS - RED NATURAL COMPLETA
#
# Filtra los nodos mediante intersección espacial con el trazado de barrancos,
# garantizando que se incluyan el Poyo, Gallego y Horteta completos.
###########################################################################

# Importar librerías
import geopandas as gpd
import pandas as pd
import numpy as np

# Parámetros
PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"
nodos_completos = gpd.read_file(PATH + r"\resultados\nodos_betweenness.geojson")
catastro = gpd.read_file(PATH + r"\data_nerea\CATASTRO_FINAL.shp")

# Cargamos la capa del trazado de los barrancos naturales de QGIS para usarla como filtro espacial
trazado_natural = gpd.read_file(PATH + r"\data_nerea\trazado_barrancos.shp")

# ==============================================================================
# 🛠️ FILTRADO ESPACIAL AUTOMÁTICO DE LA RED NATURAL (CORREGIDO)
# ==============================================================================
# Aseguramos que ambos archivos espaciales tengan exactamente el mismo sistema de coordenadas (CRS)
if nodos_completos.crs != trazado_natural.crs:
    nodos_completos = nodos_completos.to_crs(trazado_natural.crs)

# Generamos un buffer de 1.5 metros al trazado para asegurar la captura de los nodos digitalizados
trazado_buffer = trazado_natural.copy()
trazado_buffer["geometry"] = trazado_buffer.geometry.buffer(1.5)

# Para evitar conflictos de nombres duplicados, nos quedamos solo con la geometría del buffer
trazado_solo_geom = trazado_buffer[["geometry"]]

# Intersección espacial limpia
nodos = gpd.sjoin(nodos_completos, trazado_solo_geom, predicate="intersects", how="inner")

# Eliminamos duplicados por si un nodo toca dos tramos fluviales en las confluencias
nodos = nodos.drop_duplicates(subset=["id"]).copy()

# Limpieza de seguridad de columnas espaciales sobrantes
nodos = nodos[[c for c in nodos.columns if not c.startswith('index_')]]

print(f"Filtrado espacial completado: Analizando {len(nodos)} nodos pertenecientes a los cauces naturales completos.")

# Radio del buffer para evaluar el catastro (metros)
radio_influencia = 200

# Aseguramos el CRS métrico para el buffer del catastro
if nodos.crs != catastro.crs:
    catastro = catastro.to_crs(nodos.crs)

# Crear buffer de influencia alrededor de cada nodo natural válido
buffers = nodos.copy()
buffers["geometry"] = buffers.geometry.buffer(radio_influencia)

# Unión espacial de las capas catastro y buffer (edificios dentro del radio de 200m)
# Usamos un sufijo específico para evitar que se pisen los IDs
union_capas = gpd.sjoin(catastro, buffers, predicate="within", how="inner")

# Número de edificios por nodo
edificios_nodo = union_capas.groupby("id").size()

# Asignar el número de edificios afectados a la capa de nodos
nodos["N_EDIFICIOS"] = nodos["id"].map(edificios_nodo).fillna(0).astype(int)

# Umbral de criticidad (10 edificios)
UMBRAL = 10
nodos["CRITICO"] = (nodos["N_EDIFICIOS"] >= UMBRAL).astype(int)

# ==============================================================================
# 📊 CONSTRUCCIÓN Y ORDENACIÓN DE LA TABLA RESUMEN NATURAL
# ==============================================================================
tabla_resultados = nodos[[
    "id",
    "betweenness",
    "N_EDIFICIOS",
    "CRITICO"
]].copy()

# Ordenar de forma correlativa por el número del ID del nodo (N1, N2, N3...)
tabla_resultados["numero"] = (
    tabla_resultados["id"]
    .str.extract(r"(\d+)")
    .astype(int)
)
tabla_resultados = tabla_resultados.sort_values("numero")
tabla_resultados = tabla_resultados.drop(columns="numero")

# Mostrar resultados por consola
print("\n=======================================================")
print("        TABLA RESUMEN - RED NATURAL (POYO + GALLEGO + HORTETA)")
print("=======================================================")
print(tabla_resultados.to_string(index=False))
print("=======================================================")
print(f"\nNúmero total de nodos críticos en la red natural: {nodos['CRITICO'].sum()}")

# ==============================================================================
# 💾 GUARDAR ARCHIVOS DE LA RED NATURAL
# ==============================================================================
tabla_resultados.to_excel(
    PATH + r"\resultados\Tabla_nodos_criticos_NATURAL_12.xlsx",
    index=False
)
nodos.to_file(PATH + r"\resultados\nodos_criticos_NATURAL_12.geojson", driver="GeoJSON")

print("\nTOP 20 NODOS NATURALES CON MÁS EDIFICIOS AFECTADOS:")
print(nodos.sort_values("N_EDIFICIOS", ascending=False)[["id", "N_EDIFICIOS"]].head(20).to_string(index=False))

print("\nProceso terminado correctamente.")