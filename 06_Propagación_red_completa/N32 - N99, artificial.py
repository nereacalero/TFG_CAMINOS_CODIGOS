# SCRIPT B : N32 --> ... --> N99
import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt

PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"
archivo_aristas = (PATH+ r"\resultados\aristas_red.geojson")
archivo_N32 = (PATH+ r"\resultados_hidrograma_completo_temporal_2\hidrograma_N32.xlsx")

# LECTURA DEL HIDROGRAMA EN EL NODO N32
datos_N32 = pd.read_excel(archivo_N32)

# Eliminar posibles filas con NaN
datos_N32 = datos_N32.dropna(subset=["Q_N32(m3/s)"])
tiempo_N32 = datos_N32["t(horas)"].to_numpy(dtype=float)
Q_N32 = datos_N32["Q_N32(m3/s)"].to_numpy(dtype=float)

# APLICACION DE LA BIFURCACION 
Q_N32_B = 0.10469859 * Q_N32

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

    print("\n======================================")
    print(f"RECORRIDO {nodo_inicial} -> {nodo_final}")
    print("======================================")
    print(" -> ".join(recorrido))

    # Listas para guardar los resultados
    hidrogramas = {}
    tiempos = {}

    # Hidrograma inicial
    hidrogramas[nodo_inicial] = (caudal_inicial.copy())
    tiempos[nodo_inicial] = (tiempo_inicial.copy())
    tiempo_actual = (tiempo_inicial.copy())
    caudal_actual = (caudal_inicial.copy())

    # Recorrer las aristas

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

        # Tiempo de desplazamiento
        tiempo_viaje_segundos = (longitud / velocidad)
        tiempo_viaje_horas = (tiempo_viaje_segundos / 3600)

        # Propagacion de los hidrogramas
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

print("Qmax N32:", np.max(Q_N32))
print("Qmax N32_A:", np.max(Q_N32_B))
print("NaN en Q_N32:", np.isnan(Q_N32).sum())
print("NaN en Q_N32_A:", np.isnan(Q_N32_B).sum())

# REALIZAR LA PROPAGACIÓN
(
    recorrido_B,
    tiempos_B,
    hidrogramas_B
) = propagar_hidrograma(
    "N32",
    "N99",
    tiempo_N32,
    Q_N32_B
)

# Obtención de N99
tiempo_N99 = tiempos_B["N99"]
Q_N99 = hidrogramas_B["N99"]

# Representación grafica
fig, ax = plt.subplots(figsize=(12, 7))
ax.plot(
    tiempo_N32,
    Q_N32_B,
    label="N32 - Entrada Script B",
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
ax.set_title("Propagación del hidrograma desde N32 hasta N99")
ax.grid(True,alpha=0.3)
ax.legend()
plt.tight_layout()

archivo_grafica_N99 = (PATH+ r"\resultados_hidrograma_completo_temporal_2\hidrograma_N32_N99.png")
plt.savefig(archivo_grafica_N99,dpi=300,bbox_inches="tight")
plt.show()
print("\nGráfica guardada en:")
print(archivo_grafica_N99)

# GUARDAR LOS RESULTADOS DE N99
resultado_N99 = pd.DataFrame({
    "t(horas)" : tiempo_N99,
    "Q_N99(m3/s)" : Q_N99})

resultado_N99.to_excel(PATH+ r"\resultados_hidrograma_completo_temporal_2\hidrograma_N99_B.xlsx",index=False)

print("RESULTADO N99")

print("Caudal máximo en N32:",np.max(Q_N32_B), "m³/s")
print("Caudal máximo en N99:",np.max(Q_N99),"m³/s")
print("Tiempo pico N32:",tiempo_N32[np.argmax(Q_N32_B)],"h")
print("Tiempo pico N99:",tiempo_N99[np.argmax(Q_N99)],"h")