# Importar las librerias necesarias para el proceso
import geopandas as gpd
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.ops import split

# Parametros
PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"

# Lectura de datos, en concreto las capas de barrancos que se han obtenido en el script
# de preparacion de datos y luego la de nodos_500m creada en el script creacion_nodos

aristas_red = gpd.read_file(PATH + r"\resultados\aristas_red.geojson")
nodos_red = gpd.read_file(PATH + r"\resultados\nodos_500m.geojson")
print("Nodos leídos:", len(nodos_red)) # he tenido problemas y he preguntado como sacar los nodos 
# entonces me ha devuelto esta funcion que me indica cuantos nodos carga inicialmente.

# Se crea un grafo vacío donde se depositará el grafo_final
G = nx.DiGraph()

# Al grafo que hemos creado vacio la intencion ahora es meter uno a uno los nodos que 
# estamos leyendo de la capa de nodos_red con las coordenadas de estos

for i, nodo in nodos_red.iterrows():
    G.add_node(nodo["id"], x = nodo.geometry.x, y = nodo.geometry.y)

# la funcion anterior coge el nodo indice i, y se guarda con las propiedades de las coord
# x e y.

# Hacemos lo mismo pero ahora con las aristas, las vamos metiendo una a una,
# de forma que las coja como origen /destino y nos las pinte con los nodos.

for i, arista in aristas_red.iterrows():
    G.add_edge(arista['origen'], arista['destino'])

# le pedimos que dibuje la linea que une dos nodos consecutivos por eso indica
# que este comando una los nodos origen con los destinos de forma lógica

posicion_nodo = {}

for n in G.nodes():
    if "x" in G.nodes[n] and "y" in G.nodes[n]:
        posicion_nodo[n] = (G.nodes[n]["x"], G.nodes[n]["y"])

# Le pedimos que nos dibuje por un lado los nodos y por otro las aristas
nx.draw_networkx_nodes(G, posicion_nodo, node_size = 8, node_color = "red")
nx.draw_networkx_edges(G, posicion_nodo, edge_color="blue", width=1.5)

# Dibujar el grafo que se ha creado con las capas que hemos leido
plt.show()