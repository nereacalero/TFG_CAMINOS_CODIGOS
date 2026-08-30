# SCRIPT E : N40 --> ... --> N99

import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt

PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"
archivo_aristas = (PATH+ r"\resultados\aristas_red.geojson")
archivo_N40 = (PATH+ r"\resultados_hidrograma_completo_temporal_2\hidrograma_N40.xlsx")

# LECTURA DEL HIDROGRAMA EN EL NODO N40
datos_N40 = pd.read_excel(archivo_N40)

# Eliminar posibles filas con NaN
datos_N40 = datos_N40.dropna(subset=["Q_N40(m3/s)"])
tiempo_N40 = datos_N40["t(horas)"].to_numpy(dtype=float)
Q_N40 = datos_N40["Q_N40(m3/s)"].to_numpy(dtype=float)

# APLICACION DE LA BIFURCACION 
Q_N40_E = 0.274451451 * Q_N40

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
    # --------------------------------------------------------
    # Comprobar que existe camino
    # --------------------------------------------------------

    if not nx.has_path(
        G,
        nodo_inicial,
        nodo_final
    ):

        raise ValueError(
            f"No existe un camino entre "
            f"{nodo_inicial} y {nodo_final}"
        )

    # --------------------------------------------------------
    # Obtener recorrido
    # -------------------------------------------------------

    recorrido = nx.shortest_path(
        G,
        source=nodo_inicial,
        target=nodo_final
    )

    print("\n======================================")
    print(f"RECORRIDO {nodo_inicial} -> {nodo_final}")
    print("======================================")
    print(" -> ".join(recorrido))

    # --------------------------------------------------------
    # Diccionarios
    # -------------------------------------------------------

    hidrogramas = {}
    tiempos = {}

    # Hidrograma inicial
    hidrogramas[nodo_inicial] = (caudal_inicial.copy())
    tiempos[nodo_inicial] = (tiempo_inicial.copy())
    tiempo_actual = (tiempo_inicial.copy())
    caudal_actual = (caudal_inicial.copy())

    # --------------------------------------------------------
    # Recorrer cada arista
    # --------------------------------------------------------

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

        # ----------------------------------------------------
        # Tiempo de viaje
        # ----------------------------------------------------

        tiempo_viaje_segundos = (longitud / velocidad)
        tiempo_viaje_horas = (tiempo_viaje_segundos / 3600)

        # ----------------------------------------------------
        # Desplazar hidrograma
        # ----------------------------------------------------

        tiempo_actual = (tiempo_actual + tiempo_viaje_horas)

        # Con velocidad constante y sin pérdidas:
        # el caudal no cambia, únicamente se desplaza
        # temporalmente.

        caudal_actual = (caudal_actual.copy())

        # Guardar resultado
        hidrogramas[destino] = (caudal_actual.copy())
        tiempos[destino] = (tiempo_actual.copy())

        # ----------------------------------------------------
        # Mostrar información
        # ----------------------------------------------------

        print("\n--------------------------------------")
        print(f"{origen} -> {destino}")
        print("ID arista:",id_arista)
        print("Longitud:",longitud,"m")
        print(
            "Tiempo de viaje:",
            round(
                tiempo_viaje_horas,
                4
            ),
            "h"
        )

        print(
            "Caudal máximo:",
            np.max(caudal_actual),
            "m³/s"
        )
    return (recorrido,tiempos,hidrogramas)

print("Qmax N40:", np.max(Q_N40))
print("Qmax N40_E:", np.max(Q_N40_E))
print("NaN en Q_N40:", np.isnan(Q_N40).sum())
print("NaN en Q_N40_E:", np.isnan(Q_N40_E).sum())

# REALIZAR LA PROPAGACIÓN
(
    recorrido_E,
    tiempos_E,
    hidrogramas_E
) = propagar_hidrograma(
    "N40",
    "N99",
    tiempo_N40,
    Q_N40_E
)

# Obtención de N99
tiempo_N99 = tiempos_E["N99"]
Q_N99 = hidrogramas_E["N99"]

# Representación grafica
fig, ax = plt.subplots(figsize=(12, 7))
ax.plot(
    tiempo_N40,
    Q_N40_E,
    label="N40 - Entrada Script E",
    linewidth=2
)

ax.plot(
    tiempo_N99,
    Q_N99,
    label="N99 - Llegada",
    linewidth=2
)

ax.set_xlabel("Tiempo (h)")
ax.set_ylabel("Caudal (m³/s)")
ax.set_title("Propagación del hidrograma desde N40 hasta N99")
ax.grid(True,alpha=0.3)
ax.legend()
plt.tight_layout()

archivo_grafica_N99 = (
    PATH
    + r"\resultados_hidrograma_completo_temporal_2\hidrograma_N40_N99.png"
)
plt.savefig(archivo_grafica_N99,dpi=300,bbox_inches="tight")
plt.show()
print("\nGráfica guardada en:")
print(archivo_grafica_N99)

# GUARDAR LOS RESULTADOS DE N99
resultado_N99 = pd.DataFrame({
    "t(horas)" : tiempo_N99,
    "Q_N99(m3/s)" : Q_N99})

resultado_N99.to_excel(PATH
    + r"\resultados_hidrograma_completo_temporal_2\hidrograma_N99_E.xlsx",index=False)

print("\n======================================")
print("RESULTADO N99")
print("======================================")

print(
    "Caudal máximo en N40:",
    np.max(Q_N40_E),
    "m³/s"
)

print(
    "Caudal máximo en N99:",
    np.max(Q_N99),
    "m³/s"
)

print(
    "Tiempo pico N40:",
    tiempo_N40[np.argmax(Q_N40_E)],
    "h"
)

print(
    "Tiempo pico N99:",
    tiempo_N99[np.argmax(Q_N99)],
    "h"
)