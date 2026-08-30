###########################################################################
# SCRIPT PARA COLOCAR LOS NODOS DE LA RED CADA 500 METROS #

# Este script construye la red del sistema, primero identifica los nodoos que pertenecen
# a cada cauce, y los ordena según la posicion a lo largo de la red. 
# De esta forma se genera una arista para cada par de nodos consecutivos. 
# Se obtiene al igual que se realizó con los nodos, una capa de aristas, 
# estas capas serviran como base para poder crear el grafo final.

###########################################################################

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

# Parametros
PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"

# Lectura de datos, en concreto las capas de barrancos que se han obtenido en el script
# de preparacion de datos y luego la de nodos_500m creada en el script creacion_nodos

streams = gpd.read_file(PATH + r"\resultados\trazado_barrancos_recorte.geojson")
artificial = gpd.read_file(PATH + r"\resultados\trazado_cauces_artificiales_recorte.geojson")
nodos = gpd.read_file(PATH + r"\resultados\nodos_500m.geojson")
print("Nodos leídos:", len(nodos)) # he tenido problemas y he preguntado como sacar los nodos 
# entonces me ha devuelto esta funcion que me indica cuantos nodos carga inicialmente.

# se vuelve a unir la red de cauces naturales y artificiales al igual que con creacion_nodos

streams["TIPO"] = "NATURAL"
artificial["TIPO"] = "ARTIFICIAL"

union_cauces = pd.concat([streams, artificial], ignore_index=True)
union_cauces = gpd.GeoDataFrame(union_cauces, crs=streams.crs)

# Se inicializa al igual que en creacion_nodos la estructura donde se van a almacenar 
# las aristas de la red

aristas_red = []
id_arista = 1

for i, linea in union_cauces.iterrows():

    print(f"\nProcesando línea {i}")
    nodos_cauce = []

    # Buscar nodos pertenecientes a la línea

    for j, nodo in nodos.iterrows(): 
        if linea.geometry.distance(nodo.geometry) < 1:
            posicion = linea.geometry.project(nodo.geometry)
            nodos_cauce.append((posicion, nodo["id"], nodo.geometry))

        # La funcion project() devuelve la distancia medida desde el inicio de la linea
        # hasta alcanzar el nodo

    # Ordenarlos desde aguas arriba hasta aguas abajo

    nodos_cauce.sort(key=lambda x: x[0])
    print("Primer nodo:", nodos_cauce[0][1])
    print("Último nodo:", nodos_cauce[-1][1])
    # Invierto el barranco Gallego porque me he dado cuenta de que lo cogia al reves
    if nodos_cauce[0][1] == "N11" and nodos_cauce[-1][1] == "N71":
        nodos_cauce.reverse()
    print(f"Línea {i}: {len(nodos_cauce)} nodos -> {len(nodos_cauce)-1} aristas")

    # Funcion simplemente para ver que un tramo tiene almenos 2 nodos, que es lo lógico
    if len(nodos_cauce) < 2:
        print("No hay suficientes nodos.")
        continue

    # Crear aristas
    for k in range(len(nodos_cauce)-1):

        nodo_origen = nodos_cauce[k]
        nodo_destino = nodos_cauce[k+1]

        # Ahora se quiere generar una línea que une el nodo origen con el nodo destino
        linea_arista = LineString([nodo_origen[2],nodo_destino[2]])

        aristas_red.append({
            "ID_ARISTA": f"E_{id_arista}",
            "origen": nodo_origen[1],
            "destino": nodo_destino[1],
            "tipo": linea["TIPO"],
            "longitud": linea_arista.length,
            "geometry": linea_arista
        })
        id_arista += 1

# Creación de una capa donde se encuentren todas las aristas almacenadas
gdf_aristas = gpd.GeoDataFrame(aristas_red, crs=union_cauces.crs)

# En la carpeta resultados creamos una capa aristas_red donde se almacenan estas
gdf_aristas.to_file(PATH + r"\resultados\aristas_red.geojson", driver="GeoJSON")

# Indicamos que saque el numero de aristas que hemos obtenido
print("Número de aristas:", len(gdf_aristas))

total_esperadas = 0

for i, linea in union_cauces.iterrows():
    nodos2_cauce = []
    for j, nodo in nodos.iterrows():
        if linea.geometry.distance(nodo.geometry) < 1:
            posicion = linea.geometry.project(nodo.geometry)
            nodos2_cauce.append((posicion, j))
            
    total_esperadas += max(0, len(nodos2_cauce)-1)

print("\nAristas esperadas:", total_esperadas)
print("Aristas creadas:", len(gdf_aristas))
