###########################################################################
# SCRIPT DE CÁLCULO INDEPENDIENTE CON NODOS DE FONDO (GRIS)
###########################################################################

import os
import geopandas as gpd
import pandas as pd

# 1. PARÁMETROS GLOBALES
PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"
RADIO_INFLUENCIA = 200
UMBRAL = 10

# Cargar las capas base
print("Cargando capas...")
todos_los_nodos = gpd.read_file(os.path.join(PATH, "resultados", "nodos_betweenness.geojson"))
catastro = gpd.read_file(os.path.join(PATH, "data_nerea", "CATASTRO_FINAL.shp"))

# 2. SEPARACIÓN DE NODOS (Identificadores basados en tus imágenes)
nodos_morados_alt1 = ["N36", "N83", "N84", "N85", "N86", "N87"]

nodos_naranjas_alt2 = [
    "N88", "N89", "N90", "N91", "N92", "N93", "N94", "N95", "N96", "N97", 
    "N98", "N99", "N100", "N101", "N102", "N103", "N104", "N105", "N106", 
    "N107", "N108", "N109", "N110", "N111", "N112", "N113", "N114", "N115", "N116", "N117", "N118"
]

# Definimos la Red Natural pura (quitando todos los nodos de las alternativas)
nodos_naturales = todos_los_nodos[
    ~todos_los_nodos["id"].isin(nodos_morados_alt1 + nodos_naranjas_alt2)
].copy()


# 3. FUNCIÓN DE CÁLCULO EXCLUSIVO DE ALTERNATIVA 1
def calcular_escenario_alt1_aislado():
    print("\n--- Calculando de forma aislada: Alternativa 1 ---")
    
    # Unimos UNICAMENTE la red natural con los nodos de la Alternativa 1 para el cálculo
    nodos_calculo = pd.concat([nodos_naturales, todos_los_nodos[todos_los_nodos["id"].isin(nodos_morados_alt1)]]).copy()
    
    # Crear buffers solo para la red activa
    buffers = nodos_calculo.copy()
    buffers["geometry"] = buffers.geometry.buffer(RADIO_INFLUENCIA)

    # Intersección espacial con el catastro
    union_capas = gpd.sjoin(catastro, buffers, predicate="within", how="inner")
    edificios_nodo = union_capas.groupby("id").size()

    # Asignar los edificios y evaluar criticidad reales
    nodos_calculo["N_EDIFICIOS"] = nodos_calculo["id"].map(edificios_nodo).fillna(0).astype(int)
    nodos_calculo["CRITICO"] = (nodos_calculo["N_EDIFICIOS"] >= UMBRAL).astype(int)

    print(f"Nodos críticos reales calculados en Alt 1: {nodos_calculo['CRITICO'].sum()}")

    # --- AQUÍ AÑADIMOS LA ALTERNATIVA 2 COMO FONDO SIN QUE AFECTE AL CÁLCULO ---
    nodos_fondo = todos_los_nodos[todos_los_nodos["id"].isin(nodos_naranjas_alt2)].copy()
    nodos_fondo["N_EDIFICIOS"] = 0
    nodos_fondo["CRITICO"] = -1  # Le asignamos un -1 para identificar que son nodos "Inactivos/Gris"

    # Unimos todo en la capa final que exportaremos a QGIS
    capa_final_qgis = pd.concat([nodos_calculo, nodos_fondo]).copy()

    # Ordenar y limpiar tabla resumen
    capa_final_qgis["numero"] = capa_final_qgis["id"].str.extract(r"(\d+)").astype(int)
    capa_final_qgis = capa_final_qgis.sort_values("numero").drop(columns="numero")

    # Exportar resultados de la Alternativa 1
    ruta_excel = os.path.join(PATH, "resultados", "Tabla_nodos_criticos_Alternativa_1_Aislada.xlsx")
    ruta_geojson = os.path.join(PATH, "resultados", "nodos_criticos_Alternativa_1_Aislada.geojson")

    capa_final_qgis[["id", "betweenness", "N_EDIFICIOS", "CRITICO"]].to_excel(ruta_excel, index=False)
    capa_final_qgis.to_file(ruta_geojson, driver="GeoJSON")

    print(f"📊 Resultados guardados en: {ruta_excel}")
    print(f"🗺️ Capa para QGIS guardada en: {ruta_geojson}")

# Ejecutar el proceso
calcular_escenario_alt1_aislado()