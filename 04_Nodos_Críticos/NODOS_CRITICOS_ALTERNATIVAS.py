###########################################################################
# SCRIPT FINAL PARA IDENTIFICAR NODOS CRÍTICOS POR ESCENARIO COMBINADO
###########################################################################

import os
import geopandas as gpd
import pandas as pd

# 1. PARÁMETROS GLOBALES
PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"
RADIO_INFLUENCIA = 200
UMBRAL = 10

# Cargar las capas base una sola vez
print("Cargando capa única de todos los nodos...")
todos_los_nodos = gpd.read_file(os.path.join(PATH, "resultados", "nodos_betweenness.geojson"))

print("Cargando capa de catastro...")
catastro = gpd.read_file(os.path.join(PATH, "data_nerea", "CATASTRO_FINAL.shp"))


# 2. DEFINICIÓN DE LOS NODOS EXCLUSIVOS DE CADA ALTERNATIVA
# ⚠️ REVISA ESTAS LISTAS: Añade o quita los identificadores según corresponda exactamente con tus datos.
nodos_morados_alt1 = ["N83", "N84", "N85", "N86", "N87"]

nodos_naranjas_alt2 = [
    "N88", "N89", "N90", "N91", "N92", "N93", "N94", "N95", "N96", "N97", 
    "N98", "N99", "N100", "N101", "N102", "N103", "N104", "N105", "N106", 
    "N107", "N108", "N109", "N110", "N111", "N112", "N113", "N114", "N115", "N116", "N117", "N118"
]


# 3. FUNCIÓN DE PROCESAMIENTO E INTERSECCIÓN
def procesar_escenario_combinado(nombre_escenario, lista_nodos_alternativa, es_actual=False):
    """Filtra la red para componer el escenario y calcula los nodos críticos."""
    print(f"\n--- Procesando Escenario: {nombre_escenario} ---")
    
    if es_actual:
        # Para la red natural pura, excluimos todos los nodos que son de las alternativas
        nodos_escenario = todos_los_nodos[
            ~todos_los_nodos["id"].isin(nodos_morados_alt1 + nodos_naranjas_alt2)
        ].copy()
    else:
        # Para las alternativas, cogemos la red natural pura Y LE SUMAMOS sus nodos específicos
        nodos_naturales = todos_los_nodos[
            ~todos_los_nodos["id"].isin(nodos_morados_alt1 + nodos_naranjas_alt2)
        ]
        nodos_especificos_alt = todos_los_nodos[
            todos_los_nodos["id"].isin(lista_nodos_alternativa)
        ]
        
        # Unimos ambos subconjuntos en una sola capa para simular el escenario completo
        nodos_escenario = pd.concat([nodos_naturales, nodos_especificos_alt]).copy()
        
    print(f"Número total de nodos evaluados en este escenario: {len(nodos_escenario)}")

    # Crear buffer alrededor de los nodos del escenario
    buffers = nodos_escenario.copy()
    buffers["geometry"] = buffers.geometry.buffer(RADIO_INFLUENCIA)

    # Spatial Join: Unión de catastro y buffers
    union_capas = gpd.sjoin(catastro, buffers, predicate="within", how="inner")

    # Contar edificios por ID de nodo
    edificios_nodo = union_capas.groupby("id").size()

    # Mapear resultados
    nodos_escenario["N_EDIFICIOS"] = nodos_escenario["id"].map(edificios_nodo).fillna(0).astype(int)
    nodos_escenario["CRITICO"] = (nodos_escenario["N_EDIFICIOS"] >= UMBRAL).astype(int)

    # Clasificar y ordenar la tabla de resultados
    tabla_resumen = nodos_escenario[["id", "betweenness", "N_EDIFICIOS", "CRITICO"]].copy()
    tabla_resumen["numero"] = tabla_resumen["id"].str.extract(r"(\d+)").astype(int)
    tabla_resumen = tabla_resumen.sort_values("numero").drop(columns="numero")

    print(f"Total nodos críticos en {nombre_escenario}: {nodos_escenario['CRITICO'].sum()}")

    # 4. EXPORTAR LOS TRES RESULTADOS POR SEPARADO
    ruta_excel = os.path.join(PATH, "resultados", f"Tabla_nodos_criticos_{nombre_escenario}.xlsx")
    ruta_geojson = os.path.join(PATH, "resultados", f"nodos_criticos_{nombre_escenario}.geojson")

    tabla_resumen.to_excel(ruta_excel, index=False)
    nodos_escenario.to_file(ruta_geojson, driver="GeoJSON")

    print(f" 📊 Excel guardado en: {ruta_excel}")
    print(f" 🗺️ GeoJSON guardado en: {ruta_geojson}")


# 5. EJECUCIÓN DE LOS 3 ESCENARIOS INDEPENDIENTES
# Escenario 0: Solo Red Natural
procesar_escenario_combinado("Red_Natural", [], es_actual=True)

# Escenario 1: Red Natural + Nodos Morados
procesar_escenario_combinado("Alternativa_1", nodos_morados_alt1)

# Escenario 2: Red Natural + Nodos Naranjas
procesar_escenario_combinado("Alternativa_2", nodos_naranjas_alt2)

print("\n🚀 ¡Todos los archivos independientes generados con éxito!")