import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx

# Cargar las capas y archivos necesarios

PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"
archivo_aristas = PATH + r"\resultados\aristas_red.geojson"
archivo_hidrograma = PATH + r"\HIDROGRAMAS\POYO.xlsx"

# Se establece la velocidad constante en toda la red
velocidad = 5.0       # m/s

# Lectura de las aristas

aristas = gpd.read_file(archivo_aristas)
print("\nCOLUMNAS ARISTAS:")
print(aristas.columns.tolist())

# Creación del grafo
G = nx.DiGraph()

for _, fila in aristas.iterrows():

    G.add_edge(
        fila["origen"],
        fila["destino"],
        ID_ARISTA=fila["ID_ARISTA"],
        longitud=float(fila["longitud"])
    )

# Recorrido inicial del Poyo N1 - N11

nodo_inicial = "N1"
nodo_final = "N11"

if not nx.has_path(
    G,
    nodo_inicial,
    nodo_final
):

    raise ValueError(
        "No existe un recorrido entre N1 y N11."
    )

recorrido = nx.shortest_path(
    G,
    source=nodo_inicial,
    target=nodo_final
)


print("\n======================================")
print("RECORRIDO DEL POYO")
print("======================================")

print(
    " -> ".join(recorrido)
)

# Lectura del hidrograma de entrada del poyo

hidrograma = pd.read_excel(
    archivo_hidrograma,
    header=2
)

print("\nCOLUMNAS HIDROGRAMA:")
print(hidrograma.columns.tolist())

tiempo = hidrograma["t(horas)"].to_numpy(dtype=float)
caudal = hidrograma["Q(m3/s)"].to_numpy(dtype=float)

# Paso temporal
dt = np.diff(tiempo)
print("\nPaso temporal del hidrograma:")

print("mínimo:",dt.min(),"h")
print("máximo:",dt.max(),"h")

# Guardar los hidrogramas
hidrogramas = {}
tiempos = {}

# Hidrograma inicial
hidrogramas["N1"] = caudal.copy()
tiempos["N1"] = tiempo.copy()

# Propagación de los hidrogramas
tiempo_actual = tiempo.copy()
caudal_actual = caudal.copy()

for i in range(len(recorrido) - 1):
    origen = recorrido[i]
    destino = recorrido[i + 1]
    # --------------------------------------------------------
    # Buscar información del tramo
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
    # Tiempo de viaje
    # --------------------------------------------------------

    tiempo_viaje_segundos = (longitud / velocidad)
    tiempo_viaje_horas = (tiempo_viaje_segundos / 3600)

    # Propagación del hidrograma

    tiempo_actual = (tiempo_actual + tiempo_viaje_horas)

    # El caudal se conserva
    caudal_actual = (caudal_actual.copy())

    # Guardar resultado en el nodo
    hidrogramas[destino] = (caudal_actual.copy())
    tiempos[destino] = (tiempo_actual.copy())

    # --------------------------------------------------------
    # Mostrar información
    # --------------------------------------------------------

    print("\n--------------------------------------")
    print(f"{origen} -> {destino}")
    print("ID arista:",id_arista)
    print("Longitud:",longitud,"m")
    print("Tiempo de viaje:",tiempo_viaje_segundos,"s")
    print("Tiempo de viaje:",tiempo_viaje_horas,"h")
    print("Pico:",np.max(caudal_actual),"m3/s")


# Resultado nodo final N11

print("\n======================================")
print("RESULTADO N11")
print("======================================")

print("Nodos recorridos:")
print(" -> ".join(recorrido))
print("\nCaudal máximo en N1:",np.max(hidrogramas["N1"]),"m3/s")
print("Caudal máximo en N11:",np.max(hidrogramas["N11"]),"m3/s")

print("\nTiempo del pico en N1:",tiempos["N1"][np.argmax(hidrogramas["N1"])],"h")
print("Tiempo del pico en N11:",tiempos["N11"][np.argmax(hidrogramas["N11"])],"h")

# Representación gráfica

fig, ax = plt.subplots(figsize=(12, 7))

for nodo in recorrido:
    ax.plot(tiempos[nodo],hidrogramas[nodo],label=nodo)

ax.set_xlabel("Tiempo (h)")
ax.set_ylabel("Caudal (m³/s)")
ax.set_title("Propagación del hidrograma ""desde N1 hasta N11")
ax.grid(True,alpha=0.3)
ax.legend(ncol=2)
plt.tight_layout()

plt.savefig(
    PATH
    + r"\resultados_hidrograma_natural_temporal\hidrogramas_Poyo_N1_N11.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()


# Comparación N1 - N11

fig, ax = plt.subplots(figsize=(12, 7))

ax.plot(
    tiempos["N1"],
    hidrogramas["N1"],
    label="N1 - Entrada",
    linewidth=2
)


ax.plot(
    tiempos["N11"],
    hidrogramas["N11"],
    label="N11 - Llegada",
    linewidth=2
)


ax.set_xlabel("Tiempo (h)")
ax.set_ylabel("Caudal (m³/s)")
ax.set_title("Hidrograma de entrada y llegada a N11")
ax.grid(True,alpha=0.3)
ax.legend()

plt.tight_layout()
plt.savefig(
    PATH
    + r"\resultados_hidrograma_natural_temporal\hidrograma_Poyo_N1_N11_comparacion.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()
plt.figure(figsize=(10,5))

plt.plot(
    tiempos["N1"],
    hidrogramas["N1"],
    linewidth=2,
    label="N1"
)

plt.xlabel("Tiempo (h)")
plt.ylabel("Caudal (m³/s)")
plt.title("Hidrograma de entrada N1")
plt.grid(True)
plt.legend()

plt.show()