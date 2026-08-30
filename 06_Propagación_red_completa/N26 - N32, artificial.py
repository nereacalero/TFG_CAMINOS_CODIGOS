import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx

# Cargar las capas
PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"
archivo_aristas = PATH + r"\resultados\aristas_red.geojson"
archivo_poyo = PATH + r"\HIDROGRAMAS\POYO.xlsx"
archivo_gallego = PATH + r"\HIDROGRAMAS\GALLEGO.xlsx"
archivo_horteta = PATH + r"\HIDROGRAMAS\HORTETA.xlsx"

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

    # Listas para guardar los resultados
    hidrogramas = {}
    tiempos = {}

    # Hidrograma inicial
    hidrogramas[nodo_inicial] = (caudal_inicial.copy())
    tiempos[nodo_inicial] = (tiempo_inicial.copy())
    tiempo_actual = (tiempo_inicial.copy())
    caudal_actual = (caudal_inicial.copy())

    # Se recorre cada arista 

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

        # Tiempo de desplazamiento del hidrograma
        tiempo_viaje_segundos = (longitud / velocidad)
        tiempo_viaje_horas = (tiempo_viaje_segundos / 3600)

        # Desplazar el hidrograma hasta el nodo final
        tiempo_actual = (tiempo_actual + tiempo_viaje_horas)

        # Con velocidad constante y sin pérdidas:
        # el caudal no cambia, únicamente se desplaza
        # temporalmente.

        caudal_actual = (caudal_actual.copy())

        # Guardar resultado
        hidrogramas[destino] = (caudal_actual.copy())
        tiempos[destino] = (tiempo_actual.copy())

        # Mostrar los resultados

        print("\n--------------------------------------")
        print(f"{origen} -> {destino}")
        print("ID arista:",id_arista)
        print("Longitud:",longitud,"m")
        print("Tiempo de viaje:",round(tiempo_viaje_horas,4),"h")
        print("Caudal máximo:",np.max(caudal_actual),"m³/s")
    return (recorrido,tiempos,hidrogramas)

# POYO
print("\n\n")
print("####################################################")
print("#                 POYO: N1 -> N11                  #")
print("####################################################")

poyo = pd.read_excel(archivo_poyo,header=2)
tiempo_poyo = poyo["t(horas)"].to_numpy(dtype=float)
caudal_poyo = poyo["Q(m3/s)"].to_numpy(dtype=float)

(
    recorrido_poyo,
    tiempos_poyo,
    hidrogramas_poyo
) = propagar_hidrograma(
    "N1",
    "N11",
    tiempo_poyo,
    caudal_poyo
)
tiempo_poyo_N11 = tiempos_poyo["N11"]
caudal_poyo_N11 = hidrogramas_poyo["N11"]

# GALLEGO
print("\n\n")
print("####################################################")
print("#              GALLEGO: N71 -> N11                 #")
print("####################################################")

gallego = pd.read_excel(archivo_gallego,header=2)
tiempo_gallego = gallego["t(horas)"].to_numpy(dtype=float)
caudal_gallego = gallego["Q(m3/s)"].to_numpy(dtype=float)
(
    recorrido_gallego,
    tiempos_gallego,
    hidrogramas_gallego
) = propagar_hidrograma(
    "N71",
    "N11",
    tiempo_gallego,
    caudal_gallego
)

tiempo_gallego_N11 = tiempos_gallego["N11"]
caudal_gallego_N11 = hidrogramas_gallego["N11"]

# SUMA N11
print("\n\n")
print("####################################################")
print("#             CONFLUENCIA EN N11                   #")
print("####################################################")

# Unificar tiempos
tiempo_N11 = np.unique(
    np.concatenate(
        [
            tiempo_poyo_N11,
            tiempo_gallego_N11
        ]
    )
)

# Interpolar ambos hidrogramas
Q_poyo_N11 = np.interp(
    tiempo_N11,
    tiempo_poyo_N11,
    caudal_poyo_N11,
    left=0,
    right=0
)

Q_gallego_N11 = np.interp(
    tiempo_N11,
    tiempo_gallego_N11,
    caudal_gallego_N11,
    left=0,
    right=0
)

# SUMA
Q_N11 = (Q_poyo_N11 + Q_gallego_N11)
print("\nCaudal máximo Poyo en N11:",np.max(Q_poyo_N11),"m³/s")
print("Caudal máximo Gallego en N11:",np.max(Q_gallego_N11),"m³/s")
print("Caudal máximo resultante en N11:",np.max(Q_N11),"m³/s")

# N11 - N26
print("\n\n")
print("####################################################")
print("#                N11 -> N26                        #")
print("####################################################")

(
    recorrido_N11_N26,
    tiempos_N11_N26,
    hidrogramas_N11_N26
) = propagar_hidrograma(
    "N11",
    "N26",
    tiempo_N11,
    Q_N11
)
tiempo_N11_N26 = tiempos_N11_N26["N26"]
Q_N11_N26 = hidrogramas_N11_N26["N26"]

# HORTETA
print("\n\n")
print("####################################################")
print("#              HORTETA: N72 -> N26                 #")
print("####################################################")

horteta = pd.read_excel(archivo_horteta,header=2)
tiempo_horteta = horteta["t(horas)"].to_numpy(dtype=float)
caudal_horteta = horteta["Q(m3/s)"].to_numpy(dtype=float)

(
    recorrido_horteta,
    tiempos_horteta,
    hidrogramas_horteta
) = propagar_hidrograma(
    "N72",
    "N26",
    tiempo_horteta,
    caudal_horteta
)

tiempo_horteta_N26 = tiempos_horteta["N26"]
Q_horteta_N26 = hidrogramas_horteta["N26"]

# Suma de N26
print("\n\n")
print("####################################################")
print("#             CONFLUENCIA EN N26                   #")
print("####################################################")

tiempo_N26 = np.unique(
    np.concatenate(
        [
            tiempo_N11_N26,
            tiempo_horteta_N26
        ]
    )
)

Q_N11_N26_comun = np.interp(
    tiempo_N26,
    tiempo_N11_N26,
    Q_N11_N26,
    left=0,
    right=0
)

Q_horteta_N26_comun = np.interp(
    tiempo_N26,
    tiempo_horteta_N26,
    Q_horteta_N26,
    left=0,
    right=0
)

# Suma de hidrogramas
Q_N26 = (Q_N11_N26_comun+Q_horteta_N26_comun)
print("\nCaudal máximo procedente de N11:",np.max(Q_N11_N26_comun),"m³/s")
print("Caudal máximo procedente del Horteta:",np.max(Q_horteta_N26_comun),"m³/s")
print("Caudal máximo RESULTANTE EN N26:",np.max(Q_N26),"m³/s")

# Guardar datos nodo confluencia
resultado_N26 = pd.DataFrame({
    "t(horas)": tiempo_N26,
    "Q_N11_N26(m3/s)": Q_N11_N26_comun,
    "Q_Horteta_N26(m3/s)": Q_horteta_N26_comun,
    "Q_N26(m3/s)": Q_N26
})

archivo_resultado_N26 = (PATH + r"\resultados_hidrograma_natural_temporal\hidrograma_N26_confluencia.xlsx")
resultado_N26.to_excel(archivo_resultado_N26,index=False)

print("\nDatos de N26 guardados en:")
print(archivo_resultado_N26)

# CONFLUENCIA N26
fig, ax = plt.subplots(figsize=(12, 7))
# Aportación desde N11
ax.plot(
    tiempo_N26,
    Q_N11_N26_comun,
    label="N11 → N26",
    linewidth=2
)

# Aportación del Horteta
ax.plot(
    tiempo_N26,
    Q_horteta_N26_comun,
    label="Horteta → N26",
    linewidth=2
)

# SUMA
ax.plot(
    tiempo_N26,
    Q_N26,
    label="N26 - Hidrograma resultante",
    linewidth=3
)

ax.set_xlabel("Tiempo (h)")
ax.set_ylabel("Caudal (m³/s)")
ax.set_title("Confluencia en N26: suma de hidrogramas")
ax.grid(True,alpha=0.3)
ax.legend()
plt.tight_layout()

archivo_grafica_N26 = (PATH+ r"\resultados_hidrograma_natural_temporal\confluencia_N26.png")

plt.savefig(
    archivo_grafica_N26,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 14. PROPAGAR N26 -> N32
# ============================================================

print("\n\n")
print("####################################################")
print("#                N26 -> N32                        #")
print("####################################################")

(
    recorrido_N26_N32,
    tiempos_N26_N32,
    hidrogramas_N26_N32
) = propagar_hidrograma(
    "N26",
    "N32",
    tiempo_N26,
    Q_N26
)

tiempo_N32 = tiempos_N26_N32["N32"]
Q_N32 = hidrogramas_N26_N32["N32"]

# Guardar datos N32

resultado_N32 = pd.DataFrame({
    "t(horas)": tiempo_N32,
    "Q_N32(m3/s)": Q_N32
})

archivo_resultado_N32 = (PATH+ r"\resultados_hidrograma_completo_temporal_2\hidrograma_N32.xlsx")
resultado_N32.to_excel(archivo_resultado_N32,index=False)

print("\nHidrograma N32 guardado en:")
print(archivo_resultado_N32)

# Resultado N32
print("\n\n")
print("####################################################")
print("#                 RESULTADO FINAL                  #")
print("####################################################")

print("\nRecorrido N26 -> N32:")
print(" -> ".join(recorrido_N26_N32))
print("\nCaudal máximo en N26:",np.max(Q_N26),"m³/s")
print("Caudal máximo en N32:",np.max(Q_N32),"m³/s")

indice_pico_N26 = np.argmax(Q_N26)
indice_pico_N32 = np.argmax(Q_N32)

print(
    "\nTiempo del pico en N26:",
    tiempo_N26[indice_pico_N26],"h"
    )
print(
    "Tiempo del pico en N32:",
    tiempo_N32[indice_pico_N32],"h")

# Representacion N32
fig, ax = plt.subplots(figsize=(12, 7))

ax.plot(
    tiempo_N26,
    Q_N26,
    label="N26 - Confluencia",
    linewidth=2
)

ax.plot(
    tiempo_N32,
    Q_N32,
    label="N32 - Bifurcacion",
    linewidth=2
)

ax.set_xlabel("Tiempo (h)")
ax.set_ylabel("Caudal (m³/s)")
ax.set_title("Propagación del hidrograma desde N26 hasta N32")
ax.grid(True,alpha=0.3)
ax.legend()

plt.tight_layout()
archivo_grafica_N32 = (PATH+ r"\resultados_hidrograma_completo_temporal_2\hidrograma_N26_N32.png")
plt.savefig(
    archivo_grafica_N32,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\n======================================")
print("PROCESO TERMINADO")
print("======================================")
print("\nSe han generado:")
print("1. hidrograma_N26_confluencia.xlsx")
print("2. confluencia_N26.png")
print("3. hidrograma_N26_N32.png")