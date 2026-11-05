import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd  # Añadido para exportar la tabla

# --------------------------------------------------
# RUTA PRINCIPAL
# --------------------------------------------------
PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"

# --------------------------------------------------
# LECTURA DE DATOS
# --------------------------------------------------
aristas_red = gpd.read_file(PATH + r"\resultados\aristas_red.geojson")
nodos_red = gpd.read_file(PATH + r"\resultados\nodos_500m.geojson")

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
aristas_natural = aristas_red[aristas_red["tipo"] == "NATURAL"].copy()
G_natural, pos_natural = crear_grafo(aristas_natural, nodos_red)

# --------------------------------------------------
# ARISTAS DE CADA ALTERNATIVA
# --------------------------------------------------
aristas_alt1 = [
    ("N36", "N83"), ("N83", "N84"), ("N84", "N85"), ("N85","N86"), ("N86", "N87")
]

aristas_alt2 = [
    ("N32", "N88"), ("N88", "N89"), ("N89", "N90"), ("N90", "N91"), ("N91", "N92"),
    ("N92", "N93"), ("N93", "N94"), ("N94", "N95"), ("N95","N96"), ("N96", "N97"),
    ("N97", "N98"), ("N98", "N99"),
    # Tramo común desde la confluencia hasta N113
    ("N99", "N100"), ("N100", "N101"), ("N101", "N102"), ("N102", "N103"),
    ("N103", "N104"), ("N104", "N105"), ("N105", "N106"), ("N106", "N107"),
    ("N107", "N108"), ("N108", "N109"), ("N109", "N110"), ("N110", "N111"),
    ("N111", "N112"), ("N112", "N113")
]

aristas_alt3 = [
    ("N40", "N114"), ("N114", "N115"), ("N115", "N116"), ("N116", "N117"),
    ("N117", "N118"), ("N118", "N99"),
    # Tramo común desde la confluencia hasta N113
    ("N99", "N100"), ("N100", "N101"), ("N101", "N102"), ("N102", "N103"),
    ("N103", "N104"), ("N104", "N105"), ("N105", "N106"), ("N106", "N107"),
    ("N107", "N108"), ("N108", "N109"), ("N109", "N110"), ("N110", "N111"),
    ("N111", "N112"), ("N112", "N113")
]

# --------------------------------------------------
# CREACIÓN DE GRAFOS POR ALTERNATIVA
# --------------------------------------------------
G_alt1 = G_natural.copy()
G_alt1.add_edges_from(aristas_alt1)

G_alt2 = G_natural.copy()
G_alt2.add_edges_from(aristas_alt2)
G_alt2.add_edges_from(aristas_alt3)

# --------------------------------------------------
# BETWEENNESS CENTRALITY SUBSET
# --------------------------------------------------
bet_natural = nx.betweenness_centrality_subset(G_natural, sources=sources, targets=targets, normalized=True)
bet_alt1 = nx.betweenness_centrality_subset(G_alt1, sources=sources, targets=targets, normalized=True)
bet_alt2 = nx.betweenness_centrality_subset(G_alt2, sources=sources, targets=targets, normalized=True)

# --------------------------------------------------
# ESCALA DE COLOR COMÚN
# --------------------------------------------------
todos_valores = list(bet_natural.values()) + list(bet_alt1.values()) + list(bet_alt2.values())
vmin = min(todos_valores)
vmax = max(todos_valores)

# ==========================================
# NODOS DE CADA SISTEMA ARTIFICIAL
# ==========================================
nodos_poyo_turia = ["N83", "N84", "N85", "N86", "N87"]
nodos_paleocauces = [
    "N88", "N89", "N90", "N91", "N92", "N93", "N94", "N95", "N96", "N97",
    "N98", "N99", "N100", "N101", "N102", "N103", "N104", "N105", "N106",
    "N107", "N108", "N109", "N110", "N111", "N112", "N113", "N114", "N115",
    "N116", "N117", "N118"
]

# --------------------------------------------------
# REPRESENTACIÓN INDIVIDUAL Y GUARDADO DE IMÁGENES
# --------------------------------------------------
escenarios = [
    (G_natural, bet_natural, "Red natural", "Betweenness_red_natural.png", []),
    (G_alt1, bet_alt1, "Alternativa 1: Poyo-Turia", "Betweenness_alt1.png", nodos_paleocauces),
    (G_alt2, bet_alt2, "Alternativa 2: Paleocauces", "Betweenness_alt2.png", nodos_poyo_turia)
]

for G, bet, titulo, nombre_fichero, nodos_grises in escenarios:
    fig, ax = plt.subplots(figsize=(10, 8))

    nodos_activos = [n for n in G.nodes() if n not in nodos_grises]

    # Nodos fuera de servicio (Gris claro)
    nx.draw_networkx_nodes(
        G, pos_natural,
        nodelist=[n for n in nodos_grises if n in pos_natural],
        node_size=20, node_color="lightgrey", ax=ax
    )

    # Nodos activos con escala Plasma
    nodos_plot = nx.draw_networkx_nodes(
        G, pos_natural,
        nodelist=nodos_activos,
        node_size=20,
        node_color=[bet.get(n, 0) for n in nodos_activos],
        cmap="plasma", vmin=vmin, vmax=vmax, ax=ax
    )

    nx.draw_networkx_edges(G, pos_natural, edge_color="gray", width=0.8, ax=ax)

    # Añadimos la barra de color directamente a cada figura
    cbar = plt.colorbar(nodos_plot, ax=ax, orientation="horizontal", pad=0.05, shrink=0.6)
    cbar.set_label("Betweenness centrality")

    ax.set_title(titulo)
    ax.set_aspect("equal")
    ax.axis("off")

    # Guardado seguro de cada mapa individual
    plt.savefig(
        PATH + r"\resultados\\" + nombre_fichero,
        dpi=300,
        bbox_inches="tight"
    )
    plt.close(fig)  # Cierra la figura para liberar memoria y evitar errores de Tkinter

print("¡Mapas guardados con éxito en la carpeta resultados!")

# --------------------------------------------------
# CREACIÓN Y EXPORTACIÓN DE LA TABLA (CSV) ORDENADA Y REDONDEADA
# --------------------------------------------------

# 1. Obtenemos todos los nodos únicos del grafo
nodos_unicos = list(G_alt2.nodes())

# 2. Función para extraer el número de nodo como entero (ej: "N45" -> 45)
def extraer_numero(nodo_str):
    try:
        return int(nodo_str.replace("N", ""))
    except ValueError:
        return 9999

# 3. Ordenamos los nodos numéricamente (del 1 al 119)
todos_los_nodos_ordenados = sorted(nodos_unicos, key=extraer_numero)

# 4. Construimos el diccionario con los datos
datos_tabla = {
    "Nodo": todos_los_nodos_ordenados,
    "Betweenness_Natural": [bet_natural.get(n, 0.0) for n in todos_los_nodos_ordenados],
    "Betweenness_Alt1": [bet_alt1.get(n, 0.0) for n in todos_los_nodos_ordenados],
    "Betweenness_Alt2": [bet_alt2.get(n, 0.0) for n in todos_los_nodos_ordenados]
}

# 5. Creamos el DataFrame de Pandas
df_betweenness = pd.DataFrame(datos_tabla)

# 6. Redondeamos las columnas numéricas a los decimales deseados (ej: 5 decimales para no perder datos pequeños)
columnas_numericas = ["Betweenness_Natural", "Betweenness_Alt1", "Betweenness_Alt2"]
df_betweenness[columnas_numericas] = df_betweenness[columnas_numericas].round(5)

# NOTA: Si quieres estrictamente 2 decimales fijos (ej: 0.00), cambia el .round(5) por .round(2)

# 7. Guardamos la tabla en un fichero CSV separado por punto y coma
ruta_csv = PATH + r"\resultados\tabla_betweenness_alternativas.csv"
df_betweenness.to_csv(ruta_csv, index=False, sep=";")

print(f"¡Tabla de datos exportada, ordenada y redondeada correctamente en: {ruta_csv}!")
print(df_betweenness.head(15))