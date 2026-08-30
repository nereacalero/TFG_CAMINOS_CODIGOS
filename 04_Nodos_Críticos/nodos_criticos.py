###########################################################################
# SCRIPT PARA LA IDENTIFICACIÓN DE NODOS CRÍTICOS
#
# Este script identifica automáticamente los nodos críticos de la red.
# Para ello se genera un buffer de influencia alrededor de cada nodo,
# posteriormente se contabiliza el número de edificios del catastro que
# quedan contenidos en dicho buffer.
#
# Finalmente, un nodo se considera crítico cuando el número de edificios
# afectados es igual o superior a un umbral establecido (10 edificios).
###########################################################################

# Importar librerías
import geopandas as gpd

# Parámetros
PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"
nodos = gpd.read_file(PATH + r"\resultados\nodos_betweenness.geojson")
catastro = gpd.read_file(PATH + r"\data_nerea\CATASTRO_FINAL.shp")

# Radio del buffer (metros)
radio_influencia = 200

# Crear buffer alrededor de cada nodo
buffers = nodos.copy()
buffers["geometry"] = buffers.geometry.buffer(radio_influencia)

# Hacemos la intersección con el catastro ya que es lo que realmente nos interesa

# Unión de las capas catastro y buffer creado
union_capas = gpd.sjoin(catastro,buffers,predicate="within",how="inner")

# Número de edificios por nodo
edificios_nodo = union_capas.groupby("id").size()

# Número de edificios afectados
nodos["N_EDIFICIOS"] = nodos["id"].map(edificios_nodo).fillna(0).astype(int)

# Umbral de criticidad, 10 edficios entonces se considera critico
UMBRAL = 10

# Clasificación
nodos["CRITICO"] = (nodos["N_EDIFICIOS"] >= UMBRAL).astype(int)

# Mostrar tabla de resultados
print("\nRESUMEN")
print(nodos[["id","betweenness","N_EDIFICIOS","CRITICO"]])
print("\nNúmero de nodos críticos:",
      nodos["CRITICO"].sum())

# Crear tabla resumen
tabla_resultados = nodos[[
    "id",
    "betweenness",
    "N_EDIFICIOS",
    "CRITICO"
]].copy()

# Ordenar por número de nodo (N1, N2, ..., N135)
tabla_resultados["numero"] = (
    tabla_resultados["id"]
    .str.extract(r"(\d+)")
    .astype(int)
)

tabla_resultados = tabla_resultados.sort_values("numero")
tabla_resultados = tabla_resultados.drop(columns="numero")

# Mostrar por pantalla
print(tabla_resultados)

# Guardar en Excel
tabla_resultados.to_excel(
    PATH + r"\resultados\Tabla_nodos_criticos.xlsx",
    index=False
)

# Guardar resultados
nodos.to_file(PATH + r"\resultados\nodos_criticos2.geojson",driver="GeoJSON")
print(nodos.sort_values("N_EDIFICIOS", ascending=False)[["id","N_EDIFICIOS"]].head(20))
print("\nProceso terminado.")

