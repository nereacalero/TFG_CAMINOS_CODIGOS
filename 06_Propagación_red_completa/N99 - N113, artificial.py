# SCRIPT G : N99 --> ... --> N113

import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt

PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"
archivo_aristas = (PATH+ r"\resultados\aristas_red.geojson")
archivo_N99_B = (
    PATH +
    r"\resultados_hidrograma_completo_temporal_2\hidrograma_N99_B.xlsx"
)

archivo_N99_E = (
    PATH +
    r"\resultados_hidrograma_completo_temporal_2\hidrograma_N99_E.xlsx"
)

datos_B = pd.read_excel(archivo_N99_B)
datos_E = pd.read_excel(archivo_N99_E)

tiempo_N99_B = datos_B["t(horas)"].to_numpy(dtype=float)
Q_N99_B = datos_B["Q_N99(m3/s)"].to_numpy(dtype=float)

tiempo_N99_E = datos_E["t(horas)"].to_numpy(dtype=float)
Q_N99_E = datos_E["Q_N99(m3/s)"].to_numpy(dtype=float)

# VELOCIDAD CONSTANTE
velocidad = 5.0       # m/s

# LEER ARISTAS
aristas = gpd.read_file(archivo_aristas)
print("\nCOLUMNAS ARISTAS:")
print(aristas.columns.tolist())

# CREACION DEL GRAFO
G = nx.DiGraph()

for _, fila in aristas.iterrows():
    G.add_edge(
        fila["origen"],
        fila["destino"],
        ID_ARISTA=fila["ID_ARISTA"],
        longitud=float(fila["longitud"])
    )

# PROPAGACIÓN DE HIDROGRAMAS

def propagar_hidrograma(
    nodo_inicial,
    nodo_final,
    tiempo_inicial,
    caudal_inicial
):
    # Existe camino?
    if not nx.has_path(
        G,
        nodo_inicial,
        nodo_final
    ):

        raise ValueError(
            f"No existe un camino entre "
            f"{nodo_inicial} y {nodo_final}"
        )

    # Recorrido
    recorrido = nx.shortest_path(
        G,
        source=nodo_inicial,
        target=nodo_final
    )

    print(f"RECORRIDO {nodo_inicial} -> {nodo_final}")
    print(" -> ".join(recorrido))

    # Creamos listas donde guardar los resultados

    hidrogramas = {}
    tiempos = {}

    # Hidrograma inicial
    hidrogramas[nodo_inicial] = (caudal_inicial.copy())
    tiempos[nodo_inicial] = (tiempo_inicial.copy())
    tiempo_actual = (tiempo_inicial.copy())
    caudal_actual = (caudal_inicial.copy())

    # Recorremos cada arista para que siga la red completa

    for i in range(
        len(recorrido) - 1
    ):
        origen = recorrido[i]
        destino = recorrido[i + 1]

        # Buscar arista
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
        id_arista = tramo["ID_ARISTA"]
        longitud = float(tramo["longitud"])

        # Tiempo de desplazamiento durante la propagación

        tiempo_viaje_segundos = (longitud / velocidad)
        tiempo_viaje_horas = (tiempo_viaje_segundos / 3600)

        # Desplazamiento del hidrograma hasta el nodo desembocadura
        tiempo_actual = (tiempo_actual + tiempo_viaje_horas)

        # Con velocidad constante y sin pérdidas:
        # el caudal no cambia, únicamente se desplaza
        # temporalmente.

        caudal_actual = (caudal_actual.copy())

        # Guardar resultado
        hidrogramas[destino] = (caudal_actual.copy())
        tiempos[destino] = (tiempo_actual.copy())

        # Resultados
        print("\n--------------------------------------")
        print(f"{origen} -> {destino}")
        print("ID arista:",id_arista)
        print("Longitud:",longitud,"m")
        print("Tiempo de viaje:",round(tiempo_viaje_horas,4),"h")
        print("Caudal máximo:",np.max(caudal_actual),"m³/s")

    return (recorrido,tiempos,hidrogramas)

# Confluencia en el nodo N99, se suman los hidrogramas resultantes de las anteriores

tiempo_N99 = np.unique(
    np.concatenate(
        [
            tiempo_N99_B,
            tiempo_N99_E
        ]
    )
)

Q_N99_B_comun = np.interp(
    tiempo_N99,
    tiempo_N99_B,
    Q_N99_B,
    left=0,
    right=0
)

Q_N99_E_comun = np.interp(
    tiempo_N99,
    tiempo_N99_E,
    Q_N99_E,
    left=0,
    right=0
)

Q_N99 = (Q_N99_B_comun + Q_N99_E_comun)

# Representación de la suma de hidrogramas en el nodo N99

fig, ax = plt.subplots(figsize=(12, 7))

ax.plot(
    tiempo_N99,
    Q_N99_B_comun,
    label="Rama B -> N99",
    linewidth=2
)

ax.plot(
    tiempo_N99,
    Q_N99_E_comun,
    label="Rama E -> N99",
    linewidth=2
)

ax.plot(
    tiempo_N99,
    Q_N99,
    label="N99 - Hidrograma resultante",
    linewidth=3
)

ax.set_xlabel("Tiempo (h)")
ax.set_ylabel("Caudal (m³/s)")
ax.set_title("Confluencia de hidrogramas en N99")
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()

archivo_confluencia_N99 = (PATH + r"\resultados_hidrograma_completo_temporal_2\confluencia_N99.png")
plt.savefig(archivo_confluencia_N99,dpi=300,bbox_inches="tight")
plt.show()

print("\nGráfica guardada en:")
print(archivo_confluencia_N99)

print("CONFLUENCIA N99")

print("Caudal máximo rama B:",np.max(Q_N99_B_comun),"m³/s")
print("Caudal máximo rama E:",np.max(Q_N99_E_comun),"m³/s")
print("Caudal máximo N99:",np.max(Q_N99),"m³/s")

# REALIZAR LA PROPAGACIÓN
(
    recorrido_G,
    tiempos_G,
    hidrogramas_G
) = propagar_hidrograma(
    "N99",
    "N113",
    tiempo_N99,
    Q_N99
)

# Obtención de N99
tiempo_N113 = tiempos_G["N113"]
Q_N113 = hidrogramas_G["N113"]
# Representación grafica
fig, ax = plt.subplots(figsize=(12, 7))
ax.plot(
    tiempo_N99,
    Q_N99,
    label="N99 - Confluencia",
)

ax.plot(
    tiempo_N113,
    Q_N113,
    label="N113 - Llegada",
)

ax.set_xlabel("Tiempo (h)")
ax.set_ylabel("Caudal (m³/s)")
ax.set_title("Propagación del hidrograma desde N99 hasta N113")
ax.grid(True,alpha=0.3)
ax.legend()
plt.tight_layout()

archivo_grafica_N113 = (PATH + r"\resultados_hidrograma_completo_temporal_2\hidrograma_N99_N113.png")
plt.savefig(archivo_grafica_N113,dpi=300,bbox_inches="tight")
plt.show()
print("\nGráfica guardada en:")
print(archivo_grafica_N113)

# GUARDAR LOS RESULTADOS DE N113
resultado_N113 = pd.DataFrame({
    "t(horas)" : tiempo_N113,
    "Q_N113(m3/s)" : Q_N113
})

resultado_N113.to_excel(PATH + r"\resultados_hidrograma_completo_temporal_2\hidrograma_N113.xlsx",index=False)

print("RESULTADO N113")
print("Caudal máximo en N99:",np.max(Q_N99),"m³/s")
print("Caudal máximo en N113:",np.max(Q_N113),"m³/s")
print("Tiempo pico N99:",tiempo_N99[np.argmax(Q_N99)],"h")
print("Tiempo pico N113:",tiempo_N113[np.argmax(Q_N113)],"h")

print("Qmax rama B =", np.max(Q_N99_B_comun))
print("Qmax rama E =", np.max(Q_N99_E_comun))
print("Qmax N99 =", np.max(Q_N99))