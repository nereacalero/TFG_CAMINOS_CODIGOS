# Importar las librerias necesarias para el proceso
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt


# Leer el grafo que se ha creado pero para evitar problemas, leemos tambien las capas de aristas y nodos
PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"

# Lectura de datos, en concreto las capas de barrancos que se han obtenido en el script
# de preparacion de datos y luego la de nodos_500m creada en el script creacion_nodos

aristas_red = gpd.read_file(PATH + r"\resultados\aristas_red.geojson")
nodos_red = gpd.read_file(PATH + r"\resultados\nodos_500m.geojson")
print(nodos_red.columns)

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

posicion_nodo = {}

for n in G.nodes():
    posicion_nodo[n] = (G.nodes[n]["x"],G.nodes[n]["y"])

# Como tengo problemas para que tome los nodos que toca se los meto yo a mano
sources = ["N1", "N71", "N72"]     # Cabeceras
targets = ["N61", "N87", "N113"]    # Desembocaduras

def crear_grafo(aristas, nodos):

    G = nx.DiGraph()

    for _, nodo in nodos.iterrows():
        G.add_node(
            nodo["id"],
            x=nodo.geometry.x,
            y=nodo.geometry.y
        )

    for _, arista in aristas.iterrows():
        G.add_edge(
            arista["origen"],
            arista["destino"]
        )

    posiciones = {
        n: (G.nodes[n]["x"], G.nodes[n]["y"])
        for n in G.nodes()
    }

    return G, posiciones


# Grafo completo
G_total, pos_total = crear_grafo(aristas_red, nodos_red)

# Grafo natural
aristas_natural = aristas_red[
    aristas_red["tipo"] == "NATURAL"
]

G_natural, pos_natural = crear_grafo(
    aristas_natural,
    nodos_red
)


bet_total = nx.betweenness_centrality_subset(
    G_total,
    sources=sources,
    targets=targets,
    normalized=True
)

bet_natural = nx.betweenness_centrality_subset(
    G_natural,
    sources=sources,
    targets=targets,
    normalized=True
)


# REPRESENTACIÓN CONJUNTA

# Mismo rango de colores para ambas figuras
vmin = min(min(bet_total.values()), min(bet_natural.values()))
vmax = max(max(bet_total.values()), max(bet_natural.values()))

fig, (ax1, ax2) = plt.subplots(
    1, 2,
    figsize=(16, 9)
)
# RED COMPLETA

colores1 = [bet_total[n] for n in G.nodes()]

nodos1 = nx.draw_networkx_nodes(
    G,
    posicion_nodo,
    node_size=20,
    node_color=colores1,
    cmap="plasma",
    vmin=vmin,
    vmax=vmax,
    ax=ax1
)

nx.draw_networkx_edges(
    G,
    posicion_nodo,
    edge_color="gray",
    width=0.8,
    ax=ax1
)

ax1.set_title("a) Red completa")
ax1.set_aspect("equal")
ax1.axis("off")

# RED NATURAL

colores2 = [bet_natural[n] for n in G.nodes()]

nodos2 = nx.draw_networkx_nodes(
    G,
    posicion_nodo,
    node_size=20,
    node_color=colores2,
    cmap="plasma",
    vmin=vmin,
    vmax=vmax,
    ax=ax2
)

nx.draw_networkx_edges(
    G,
    posicion_nodo,
    edge_color="gray",
    width=0.8,
    ax=ax2
)

ax2.set_title("b) Red natural")
ax2.set_aspect("equal")
ax2.axis("off")

# HACER UN ESPACIO PARA LA LEYENDA DEL GRÁFICO

fig.subplots_adjust(
    left=0.05,
    right=0.95,
    top=0.92,
    bottom=0.22,
    wspace=0.10
)

# Eje independiente para la barra
cax = fig.add_axes([0.25, 0.08, 0.50, 0.03])

cbar = fig.colorbar(
    nodos1,
    cax=cax,
    orientation="horizontal"
)

cbar.set_label("Betweenness centrality")

plt.savefig(
    PATH + r"\resultados\Comparacion_betweenness2.png",
    dpi=300
)

plt.show()