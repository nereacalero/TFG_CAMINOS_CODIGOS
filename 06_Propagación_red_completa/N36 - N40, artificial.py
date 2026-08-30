# SCRIPT D : N36 --> ... --> N40

import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt

PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"
archivo_aristas = (PATH+ r"\resultados\aristas_red.geojson")
archivo_N36 = (PATH+ r"\resultados_hidrograma_completo_temporal_2\hidrograma_N36.xlsx")

# LECTURA DEL HIDROGRAMA EN EL NODO N36
datos_N36 = pd.read_excel(archivo_N36)

# Eliminar posibles filas con NaN
datos_N36 = datos_N36.dropna(subset=["Q_N36(m3/s)"])
tiempo_N36 = datos_N36["t(horas)"].to_numpy(dtype=float)
Q_N36 = datos_N36["Q_N36(m3/s)"].to_numpy(dtype=float)

# APLICACION DE LA BIFURCACION 
Q_N36_D = 0.7053815043 * Q_N36
#Q_N36_D = 0.5459 * Q_N36

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

    # Listas para guardar resultados
    hidrogramas = {}
    tiempos = {}

    # Hidrograma inicial
    hidrogramas[nodo_inicial] = (caudal_inicial.copy())
    tiempos[nodo_inicial] = (tiempo_inicial.copy())
    tiempo_actual = (tiempo_inicial.copy())
    caudal_actual = (caudal_inicial.copy())

    # Recorrer cada arista
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

        # Tiempo de desplazamiento de hidrogramas
        tiempo_viaje_segundos = (longitud / velocidad)
        tiempo_viaje_horas = (tiempo_viaje_segundos / 3600)

        # Desplzamiento de hidrogramas
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

print("Qmax N36:", np.max(Q_N36))
print("Qmax N36_D:", np.max(Q_N36_D))
print("NaN en Q_N36:", np.isnan(Q_N36).sum())
print("NaN en Q_N36_D:", np.isnan(Q_N36_D).sum())

# REALIZAR LA PROPAGACIÓN
(
    recorrido_D,
    tiempos_D,
    hidrogramas_D
) = propagar_hidrograma(
    "N36",
    "N40",
    tiempo_N36,
    Q_N36_D
)

# ============================================================
# GUARDAR HIDROGRAMAS DE LOS NODOS CRÍTICOS
# ============================================================

nodos_criticos = [
    "N37",
    "N38",
    "N39"
]

for nodo in nodos_criticos:

    if nodo in hidrogramas_D:

        resultado = pd.DataFrame({
        
                    "t(horas)": tiempos_D[nodo],
        
                    f"Q_{nodo}(m3/s)": hidrogramas_D[nodo]
        
                })

        archivo_salida = (
            PATH
            + rf"\resultados_hidrograma_completo_temporal_2\hidrograma_{nodo}.xlsx"
        )

        resultado.to_excel(
            archivo_salida,
            index=False
        )

        print(
            f"Guardado: hidrograma_{nodo}.xlsx"
        )

# Obtención de N99
tiempo_N40 = tiempos_D["N40"]
Q_N40 = hidrogramas_D["N40"]

# Representación grafica
fig, ax = plt.subplots(figsize=(12, 7))
ax.plot(
    tiempo_N36,
    Q_N36_D,
    label="N36 - Entrada Script D",
    linewidth=2
)

ax.plot(
    tiempo_N40,
    Q_N40,
    label="N40 - Llegada",
    linewidth=2
)

ax.set_xlabel("Tiempo (h)")
ax.set_ylabel("Caudal (m³/s)")
ax.set_title("Propagación del hidrograma desde N36 hasta N40")
ax.grid(True,alpha=0.3)
ax.legend()
plt.tight_layout()

archivo_grafica_N40 = (PATH+ r"\resultados_hidrograma_completo_temporal_2\hidrograma_N36_N40.png")
plt.savefig(archivo_grafica_N40,dpi=300,bbox_inches="tight")
plt.show()
print("\nGráfica guardada en:")
print(archivo_grafica_N40)

# GUARDAR LOS RESULTADOS DE N40
resultado_N40 = pd.DataFrame({
    "t(horas)" : tiempo_N40,
    "Q_N40(m3/s)" : Q_N40})

resultado_N40.to_excel(PATH+ r"\resultados_hidrograma_completo_temporal_2\hidrograma_N40.xlsx",index=False)

print("RESULTADO N40")
print("Caudal máximo en N36:",np.max(Q_N36_D),"m³/s")
print("Caudal máximo en N40:",np.max(Q_N40),"m³/s")
print("Tiempo pico N36:",tiempo_N36[np.argmax(Q_N36_D)],"h")
print("Tiempo pico N40:",tiempo_N40[np.argmax(Q_N40)],"h")