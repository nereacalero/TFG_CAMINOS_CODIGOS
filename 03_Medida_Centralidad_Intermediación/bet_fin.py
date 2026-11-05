import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt


# --------------------------------------------------
# RUTA PRINCIPAL
# --------------------------------------------------

PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"


# --------------------------------------------------
# LECTURA DE DATOS
# --------------------------------------------------

aristas_red = gpd.read_file(
    PATH + r"\resultados\aristas_red.geojson"
)

nodos_red = gpd.read_file(
    PATH + r"\resultados\nodos_500m.geojson"
)


# Cabeceras y desembocaduras
sources = ["N1", "N71", "N72"]
targets = ["N61", "N87", "N113"]


# --------------------------------------------------
# FUNCIÓN PARA CREAR EL GRAFO
# --------------------------------------------------

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


# --------------------------------------------------
# ESCENARIO INICIAL: RED NATURAL
# --------------------------------------------------

aristas_natural = aristas_red[
    aristas_red["tipo"] == "NATURAL"
].copy()

G_natural, pos_natural = crear_grafo(
    aristas_natural,
    nodos_red
)

# --------------------------------------------------
# ARISTAS DE CADA ALTERNATIVA
# --------------------------------------------------

aristas_alt1 = [
    ("N36", "N83"),
    ("N83", "N84"),
    ("N84", "N85"),
    ("N85","N86"),
    ("N86", "N87")
]

aristas_alt2 = [
    ("N32", "N88"),
    ("N88", "N89"),
    ("N89", "N90"),
    ("N90", "N91"),
    ("N91", "N92"),
    ("N92", "N93"),
    ("N93", "N94"),
    ("N94", "N95"),
    ("N95","N96"),
    ("N96", "N97"),
    ("N97", "N98"),
    ("N98", "N99"),

    # Tramo común desde la confluencia hasta N113
    ("N99", "N100"),
    ("N100", "N101"),
    ("N101", "N102"),
    ("N102", "N103"),
    ("N103", "N104"),
    ("N104", "N105"),
    ("N105", "N106"),
    ("N106", "N107"),
    ("N107", "N108"),
    ("N108", "N109"),
    ("N109", "N110"),
    ("N110", "N111"),
    ("N111", "N112"),
    ("N112", "N113")
]

aristas_alt3 = [
    ("N40", "N114"),
    ("N114", "N115"),
    ("N115", "N116"),
    ("N116", "N117"),
    ("N117", "N118"),
    ("N118", "N99"),

    # Tramo común desde la confluencia hasta N113
    ("N99", "N100"),
    ("N100", "N101"),
    ("N101", "N102"),
    ("N102", "N103"),
    ("N103", "N104"),
    ("N104", "N105"),
    ("N105", "N106"),
    ("N106", "N107"),
    ("N107", "N108"),
    ("N108", "N109"),
    ("N109", "N110"),
    ("N110", "N111"),
    ("N111", "N112"),
    ("N112", "N113")
]
# --------------------------------------------------
# ALTERNATIVA 1
# Conexión Barranco del Poyo - nuevo cauce del Turia
# --------------------------------------------------

G_alt1 = G_natural.copy()
G_alt1.add_edges_from(aristas_alt1)


# --------------------------------------------------
# ALTERNATIVA 2
# Sistema completo de paleocauces
# --------------------------------------------------

G_alt2 = G_natural.copy()

G_alt2.add_edges_from(aristas_alt2)
G_alt2.add_edges_from(aristas_alt3)


# --------------------------------------------------
# ALTERNATIVA 3
# Segundo paleocauce: N40 -> N99
# --------------------------------------------------

#G_alt3 = G_natural.copy()
#G_alt3.add_edges_from(aristas_alt3)


# --------------------------------------------------
# BETWENNESS CENTRALITY
# --------------------------------------------------
print("¿N99 está en G_natural?", "N99" in G_natural)
print("¿N113 está en G_natural?", "N113" in G_natural)

print("¿N99 está en G_alt2?", "N99" in G_alt2)
print("¿N113 está en G_alt2?", "N113" in G_alt2)

print("\nAristas que llegan a N99:")
print(list(G_natural.in_edges("N99")))

print("\nAristas que salen de N99:")
print(list(G_natural.out_edges("N99")))

print("\nGrado de N99:", G_alt2.degree("N99"))
print("Grado de N113:", G_alt2.degree("N113"))

print("\nAristas que llegan a N113:")
print(list(G_alt2.in_edges("N113")))

print("\nAristas que salen de N113:")
print(list(G_alt2.out_edges("N113")))

bet_natural = nx.betweenness_centrality_subset(
    G_natural,
    sources=sources,
    targets=targets,
    normalized=True
)

bet_alt1 = nx.betweenness_centrality_subset(
    G_alt1,
    sources=sources,
    targets=targets,
    normalized=True
)

bet_alt2 = nx.betweenness_centrality_subset(
    G_alt2,
    sources=sources,
    targets=targets,
    normalized=True
)

#bet_alt3 = nx.betweenness_centrality_subset(
 #   G_alt3,
  #  sources=sources,
   # targets=targets,
    #normalized=True
#)


# --------------------------------------------------
# ESCALA DE COLOR COMÚN
# --------------------------------------------------

todos_valores = (
    list(bet_natural.values())
    + list(bet_alt1.values())
    + list(bet_alt2.values())
)

vmin = min(todos_valores)
vmax = max(todos_valores)

# ==========================================
# NODOS DE CADA SISTEMA ARTIFICIAL
# ==========================================

nodos_poyo_turia = [
    "N83", "N84", "N85", "N86", "N87"
]

nodos_paleocauces = [
    "N88", "N89", "N90", "N91", "N92",
    "N93", "N94", "N95", "N96", "N97",
    "N98", "N99", "N100", "N101", "N102",
    "N103", "N104", "N105", "N106",
    "N107", "N108", "N109", "N110",
    "N111", "N112", "N113",
    "N114", "N115", "N116", "N117",
    "N118"
]


# --------------------------------------------------
# REPRESENTACIÓN INDIVIDUAL
# --------------------------------------------------

escenarios = [

    (
        G_natural,
        bet_natural,
        "Red natural",
        "Betweenness_red_natural.png",
        []
    ),

    (
        G_alt1,
        bet_alt1,
        "Alternativa 1: Poyo-Turia",
        "Betweenness_alt1.png",
        nodos_paleocauces
    ),

    (
        G_alt2,
        bet_alt2,
        "Alternativa 2: Paleocauces",
        "Betweenness_alt2.png",
        nodos_poyo_turia
    )
]


for G, bet, titulo, nombre_fichero, nodos_grises in escenarios:

    fig, ax = plt.subplots(
        figsize=(10, 8)
    )

    # Nodos activos
    nodos_activos = [
        n for n in G.nodes()
        if n not in nodos_grises
    ]

    # Nodos fuera de servicio
    nx.draw_networkx_nodes(
        G,
        pos_natural,
        nodelist=[
            n for n in nodos_grises
            if n in pos_natural
        ],
        node_size=20,
        node_color="lightgrey",
        ax=ax
    )

    # Nodos activos coloreados
    nodos_plot = nx.draw_networkx_nodes(
        G,
        pos_natural,
        nodelist=nodos_activos,
        node_size=20,
        node_color=[
            bet.get(n, 0)
            for n in nodos_activos
        ],
        cmap="plasma",
        vmin=vmin,
        vmax=vmax,
        ax=ax
    )

    nx.draw_networkx_edges(
        G,
        pos_natural,
        edge_color="gray",
        width=0.8,
        ax=ax
    )

    cbar = plt.colorbar(
        nodos_plot,
        ax=ax
    )

    cbar.set_label(
        "Betweenness centrality"
    )

    ax.set_title(titulo)

    ax.set_aspect("equal")

    ax.axis("off")

    plt.savefig(
        PATH + r"\resultados\\" + nombre_fichero,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()


# --------------------------------------------------
# LEYENDA
# --------------------------------------------------

fig.subplots_adjust(
    left=0.05,
    right=0.95,
    top=0.95,
    bottom=0.12,
    hspace=0.10,
    wspace=0.05
)

cax = fig.add_axes([
    0.25,
    0.05,
    0.50,
    0.025
])

cbar = fig.colorbar(
    nodos_plot,
    cax=cax,
    orientation="horizontal"
)

cbar.set_label("Betweenness centrality")


# --------------------------------------------------
# GUARDAR FIGURA
# --------------------------------------------------

plt.savefig(
    PATH + r"\resultados\Comparacion_alternativas_betweenness.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# --------------------------------------------------
# EXPORTACIÓ DE RESULTATS A UNA TAULA (CSV)
# --------------------------------------------------
import pandas as pd

# Obtenim la llista completa de tots els nodes únics de la xarxa
todos_los_nodos = sorted(list(G_natural.nodes()))

# Construïm un diccionari ordenat per nodes
datos_tabla = {
    "Nodo": todos_los_nodos,
    "Betweenness_Natural": [bet_natural.get(n, 0.0) for n in todos_los_nodos],
    "Betweenness_Alt1": [bet_alt1.get(n, 0.0) for n in todos_los_nodos],
    "Betweenness_Alt2": [bet_alt2.get(n, 0.0) for n in todos_los_nodos]
    # Si actives l'Alternativa 3 en el futur, només has de descomentar la línia següent:
    # "Betweenness_Alt3": [bet_alt3.get(n, 0.0) for n in todos_los_nodos]
}

# Creem el DataFrame de Pandas
df_betweenness = pd.DataFrame(datos_tabla)

# Exportem la taula a un fitxer CSV a la teva carpeta de resultats
ruta_salida_csv = PATH + r"\resultados\tabla_betweenness_nodos_alternativas.csv"
df_betweenness.to_csv(ruta_salida_csv, index=False, sep=";")

print(f"\n¡Taula exportada correctament a: {ruta_salida_csv}!")
# Mostrem els primers nodes a la consola per a verificar que tot estigui bé
print(df_betweenness.head(15))