import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx


# ============================================================
# 1. RUTAS
# ============================================================

PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"

archivo_aristas = PATH + r"\resultados\aristas_red.geojson"

# Hidrograma de entrada en N71
archivo_hidrograma = PATH + r"\HIDROGRAMAS\GALLEGO.xlsx"


# ============================================================
# 2. VELOCIDAD DE PROPAGACIÓN
# ============================================================

velocidad = 5.0       # m/s


# ============================================================
# 3. LEER ARISTAS DE LA RED
# ============================================================

aristas = gpd.read_file(
    archivo_aristas
)

print("\nCOLUMNAS ARISTAS:")
print(aristas.columns.tolist())


# ============================================================
# 4. CREAR GRAFO DE LA RED
# ============================================================

G = nx.DiGraph()

for _, fila in aristas.iterrows():

    G.add_edge(
        fila["origen"],
        fila["destino"],
        ID_ARISTA=fila["ID_ARISTA"],
        longitud=float(fila["longitud"])
    )


# ============================================================
# 5. DEFINIR INICIO Y FINAL
# ============================================================

nodo_inicial = "N71"
nodo_final = "N11"


# Comprobar que existe un camino

if not nx.has_path(
    G,
    nodo_inicial,
    nodo_final
):

    raise ValueError(
        f"No existe un recorrido entre "
        f"{nodo_inicial} y {nodo_final}."
    )


# Obtener recorrido

recorrido = nx.shortest_path(
    G,
    source=nodo_inicial,
    target=nodo_final
)


print("\n======================================")
print("RECORRIDO DEL GALLEGO")
print("======================================")

print(
    " -> ".join(recorrido)
)


# ============================================================
# 6. LEER HIDROGRAMA DE ENTRADA
# ============================================================

hidrograma = pd.read_excel(
    archivo_hidrograma,
    header=2
)


print("\nCOLUMNAS HIDROGRAMA:")
print(
    hidrograma.columns.tolist()
)


print("\nPRIMERAS FILAS:")
print(
    hidrograma.head()
)


# ============================================================
# 7. EXTRAER TIEMPO Y CAUDAL
# ============================================================

tiempo = hidrograma[
    "t(horas)"
].to_numpy(dtype=float)


caudal = hidrograma[
    "Q(m3/s)"
].to_numpy(dtype=float)


# ============================================================
# 8. COMPROBAR PASO TEMPORAL
# ============================================================

dt = np.diff(tiempo)

print("\n======================================")
print("PASO TEMPORAL")
print("======================================")

print(
    "Paso temporal mínimo:",
    dt.min(),
    "h"
)

print(
    "Paso temporal máximo:",
    dt.max(),
    "h"
)


# ============================================================
# 9. GUARDAR HIDROGRAMAS DE LOS NODOS
# ============================================================

hidrogramas = {}

tiempos = {}


# Hidrograma inicial en N71

hidrogramas["N71"] = caudal.copy()

tiempos["N71"] = tiempo.copy()


# ============================================================
# 10. PROPAGACIÓN N71 -> N11
# ============================================================

tiempo_actual = tiempo.copy()

caudal_actual = caudal.copy()


for i in range(
    len(recorrido) - 1
):

    origen = recorrido[i]

    destino = recorrido[i + 1]


    # --------------------------------------------------------
    # Buscar la arista correspondiente
    # --------------------------------------------------------

    tramo = aristas[
        (aristas["origen"] == origen) &
        (aristas["destino"] == destino)
    ]


    if tramo.empty:

        raise ValueError(
            f"No se encuentra la arista "
            f"{origen} -> {destino}"
        )


    tramo = tramo.iloc[0]


    id_arista = tramo[
        "ID_ARISTA"
    ]


    longitud = float(
        tramo["longitud"]
    )


    # --------------------------------------------------------
    # Calcular tiempo de viaje
    # --------------------------------------------------------

    tiempo_viaje_segundos = (
        longitud / velocidad
    )


    tiempo_viaje_horas = (
        tiempo_viaje_segundos / 3600
    )


    # --------------------------------------------------------
    # Desplazar el hidrograma
    # --------------------------------------------------------

    tiempo_actual = (
        tiempo_actual
        + tiempo_viaje_horas
    )


    # El caudal se conserva
    caudal_actual = (
        caudal_actual.copy()
    )


    # Guardar hidrograma en el nodo destino

    hidrogramas[destino] = (
        caudal_actual.copy()
    )


    tiempos[destino] = (
        tiempo_actual.copy()
    )


    # --------------------------------------------------------
    # Mostrar información del tramo
    # --------------------------------------------------------

    print("\n--------------------------------------")

    print(
        f"{origen} -> {destino}"
    )

    print(
        "ID arista:",
        id_arista
    )

    print(
        "Longitud:",
        longitud,
        "m"
    )

    print(
        "Tiempo de viaje:",
        tiempo_viaje_segundos,
        "s"
    )

    print(
        "Tiempo de viaje:",
        tiempo_viaje_horas,
        "h"
    )

    print(
        "Caudal máximo:",
        np.max(caudal_actual),
        "m3/s"
    )


# ============================================================
# 11. RESULTADO FINAL EN N11
# ============================================================

print("\n======================================")
print("RESULTADO FINAL DEL GALLEGO")
print("======================================")


print(
    "\nRecorrido:"
)

print(
    " -> ".join(recorrido)
)


print(
    "\nCaudal máximo en N71:",
    np.max(
        hidrogramas["N71"]
    ),
    "m3/s"
)


print(
    "Caudal máximo en N11:",
    np.max(
        hidrogramas["N11"]
    ),
    "m3/s"
)


# Tiempo del pico

indice_pico_N71 = np.argmax(
    hidrogramas["N71"]
)

indice_pico_N11 = np.argmax(
    hidrogramas["N11"]
)


print(
    "\nTiempo del pico en N71:",
    tiempos["N71"][indice_pico_N71],
    "h"
)


print(
    "Tiempo del pico en N11:",
    tiempos["N11"][indice_pico_N11],
    "h"
)


# ============================================================
# 12. GRÁFICA DE TODOS LOS HIDROGRAMAS
# ============================================================

fig, ax = plt.subplots(
    figsize=(12, 7)
)


for nodo in recorrido:

    ax.plot(
        tiempos[nodo],
        hidrogramas[nodo],
        label=nodo
    )


ax.set_xlabel(
    "Tiempo (h)"
)

ax.set_ylabel(
    "Caudal (m³/s)"
)

ax.set_title(
    "Propagación del hidrograma "
    "por el Barranco del Gallego"
)

ax.grid(
    True,
    alpha=0.3
)

ax.legend(
    ncol=2
)

plt.tight_layout()


plt.savefig(
    PATH
    + r"\resultados_hidrograma_natural_temporal\hidrogramas_Gallego_N71_N11.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 13. COMPARACIÓN N71 - N11
# ============================================================

fig, ax = plt.subplots(
    figsize=(12, 7)
)


ax.plot(
    tiempos["N71"],
    hidrogramas["N71"],
    label="N71 - Entrada",
    linewidth=2
)


ax.plot(
    tiempos["N11"],
    hidrogramas["N11"],
    label="N11 - Llegada",
    linewidth=2
)


ax.set_xlabel(
    "Tiempo (h)"
)

ax.set_ylabel(
    "Caudal (m³/s)"
)

ax.set_title(
    "Hidrograma de entrada y llegada a N11 - Gallego"
)

ax.grid(
    True,
    alpha=0.3
)

ax.legend()


plt.tight_layout()


plt.savefig(
    PATH
    + r"\resultados_hidrograma_natural_temporal\hidrograma_Gallego_N71_N11_comparacion.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

plt.figure(figsize=(10,5))

plt.plot(
    tiempos["N71"],
    hidrogramas["N71"],
    linewidth=2,
    label="N71"
)

plt.xlabel("Tiempo (h)")
plt.ylabel("Caudal (m³/s)")
plt.title("Hidrograma de entrada N71")
plt.grid(True)
plt.legend()

plt.show()