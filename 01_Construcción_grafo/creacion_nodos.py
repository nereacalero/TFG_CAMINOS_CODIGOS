###########################################################################
# SCRIPT PARA COLOCAR LOS NODOS DE LA RED CADA 500 METROS #

# Se parte de la red y nodos que se han obtenido en la preparación de los datos, lo que
# hace es que para cada uno de los cauces, identifica los nodos que pertenecen a este
# los ordena segun la posicion de estos a lo larrgo del cauce y interpola diferentes nodos
# cada 500 metros entre dos nodos consecutivos. 
# Los nodos generados y originales se almacenan en una nueva capa que llamaré nodos_500m
# para asi poder diferenciarla de la creada a partir del script de preparación de datos
# esta capa será la base para la creación de la capa de aristas que se hace a continuación.

###########################################################################

# Importar las librerias necesarias para el proceso
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely.ops import split

# Primero cargo parametros
PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"

# Se leen las capas que se han creado en el primer script de preparación de datos
streams = gpd.read_file(PATH + r"\resultados\trazado_barrancos_recorte.geojson")
artificial = gpd.read_file(PATH + r"\resultados\trazado_cauces_artificiales_recorte.geojson")
nodos = gpd.read_file(PATH + r"\resultados\nodos.geojson")

print(nodos["TIPO"].value_counts()) # para ver los diferentes tipos de nodo que tenemos 

# Creación de una variable que contenga toda la red, es decir, la unión del Gallego,
# Horteta y Poyo, junto con los cauces artificiales

union_cauces = pd.concat([streams, artificial], ignore_index=True)
union_cauces = gpd.GeoDataFrame(union_cauces, crs=streams.crs)

# Comprobación de cuales son los nodos que pertenecen a cada línea y su posición dentro del cauce
for i, linea in union_cauces.iterrows():
    print(f"\nLÍNEA {i}")

    for j, nodo in nodos.iterrows():

        distancia = linea.geometry.distance(nodo.geometry)
        # En caso de que la distancia sea 0, el nodo está justo encima,
        # como comprobación de que los nodos están bien conectados

        if distancia < 1:
            posicion_nodo = linea.geometry.project(nodo.geometry)
            # nos da la posicion del nodo que luego se podrá ordenar

            print(f"Nodo {j} -> {posicion_nodo:.2f} m")

################################################################
# Una vez hecho todo lo anterior queremos recorrer toda la línea del barranco
# y colocar nodos cada 500 metros entre los nodos existentes
################################################################
distancia_nodos = 500   # distancia entre nodos nuevos

# Lista donde se guardarán todos los puntos generados
puntos = []


import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10,10))

union_cauces.plot(ax=ax, color="yellow")

for i, linea in union_cauces.iterrows():
    x, y = linea.geometry.interpolate(0.5, normalized=True).coords[0]
    ax.text(x, y, str(i), fontsize=14, color="red")

plt.show()

# Recorremos cada cauce de la red
for i, linea in union_cauces.iterrows():

    print("\nProcesando línea:", i)
    print("Longitud:", linea.geometry.length)

    # Guardar los nodos que pertenecen a este cauce

    nodos_cauce = []

    for j, nodo in nodos.iterrows():
        # Si el nodo está suficientemente cerca del cauce,
        # se considera perteneciente a esa línea

        if linea.geometry.distance(nodo.geometry) < 0.5:
            # Calculamos la distancia desde el inicio del cauce hasta el nodo
            posicion_nodo = linea.geometry.project(nodo.geometry)
            # Guardamos posición y geometría del nodo
            nodos_cauce.append((posicion_nodo, nodo.geometry))

    print(f"Línea {i} -> {len(nodos_cauce)} nodos") # compruebo que tienen 2 nodos, inicio y fin
    # porque tuve problemas con un cauce artificial, porque no lo conecté del todo bien.
    print("Posiciones encontradas:")

    for posicion_nodo, _ in nodos_cauce:
        print(f"   {posicion_nodo:.2f}")

    # Ordenamos los nodos desde el inicio de la línea hasta el final
    nodos_cauce.sort(key=lambda x: x[0]) # seguir orden logico de aguas arriba a aguas abajo

    # Importante comprobar que almenos cada tramo tiene 2 nodos ya que 
    # dos puntos determinan un tramo sino no sería posible.

    if len(nodos_cauce) < 2:
        print("Esta línea no tiene suficientes nodos")
        continue

    # Generar puntos cada 500 metros entre cada pareja de nodos consecutivos
    for k in range(len(nodos_cauce)-1):

        inicio = nodos_cauce[k][0]
        fin = nodos_cauce[k+1][0]

        # Añadir nodo inicial
        puntos.append(nodos_cauce[k][1])

        # Primer punto nuevo cada 500 metros, colocar cada 500m
        d = inicio + distancia_nodos 

        while d < fin:
            punto = linea.geometry.interpolate(d)
            puntos.append(punto)
            d += distancia_nodos

        # Añadir nodo final
        puntos.append(nodos_cauce[k+1][1])

# Crear capa GIS con los puntos generados
gdf_puntos = gpd.GeoDataFrame(geometry=puntos, crs=union_cauces.crs)

# He tenido que buscar una función que me elimine los nodos que se duplicaban, porque creaba 180 nodos y solo eran 167 realmente
gdf_puntos = gdf_puntos.drop_duplicates(subset="geometry").reset_index(drop=True)

# Le pedimos que nos saque una tabla con todos los nodos, su correspondiente identificador y las coordenadas de cada nodo
gdf_puntos["id"] = [f"N{i}" for i in range(1, len(gdf_puntos)+1)]

print("\nTABLA NODOS")
gdf_puntos["X"] = gdf_puntos.geometry.x
gdf_puntos["Y"] = gdf_puntos.geometry.y

print(gdf_puntos[["id","X","Y"]])

# Guardar resultado
gdf_puntos.to_file(PATH + r"\resultados\nodos_500m.geojson", driver="GeoJSON")

print(union_cauces.columns)