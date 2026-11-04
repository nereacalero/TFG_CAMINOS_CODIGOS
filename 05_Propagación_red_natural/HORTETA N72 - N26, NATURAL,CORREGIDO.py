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

# HIDROGRAMA DE ENTRADA DEL HORTETA EN N72
archivo_hidrograma = PATH + r"\HIDROGRAMAS\HORTETA.xlsx"


# ============================================================
# 2. VELOCIDAD DE PROPAGACIÓN
# ============================================================

velocidad = 5.0       # m/s

# ============================================================
# CORRECCIONES TEMPORALES
# ============================================================

corr_N72_N77 = 0.87421 / 5

# ============================================================
# 3. LEER RED DE ARISTAS
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

correcciones = {

    ("N72","N73"): corr_N72_N77,
    ("N73","N74"): corr_N72_N77,
    ("N74","N75"): corr_N72_N77,
    ("N75","N76"): corr_N72_N77,
    ("N76","N77"): corr_N72_N77

}

# ============================================================
# 5. LEER HIDROGRAMA DE ENTRADA EN N72
# ============================================================

hidrograma = pd.read_excel(
    archivo_hidrograma,
    header=2
)

print("\nCOLUMNAS HIDROGRAMA:")
print(hidrograma.columns.tolist())

print("\nPRIMERAS FILAS:")
print(hidrograma.head())


# ============================================================
# 6. PREPARAR HIDROGRAMA
# ============================================================

tiempo = hidrograma[
    "t(horas)"
].to_numpy(dtype=float)

caudal_entrada = hidrograma[
    "Q(m3/s)"
].to_numpy(dtype=float)


# ============================================================
# 7. DEFINIR NODOS INICIAL Y FINAL
# ============================================================

nodo_inicial = "N72"

nodo_final = "N26"


# ============================================================
# 8. BUSCAR RECORRIDO N72 -> N26
# ============================================================

if not nx.has_path(
    G,
    nodo_inicial,
    nodo_final
):

    raise ValueError(
        f"No existe un camino entre "
        f"{nodo_inicial} y {nodo_final}"
    )


recorrido = nx.shortest_path(
    G,
    source=nodo_inicial,
    target=nodo_final
)


print("\n======================================")
print("RECORRIDO DEL HORTETA")
print("======================================")

print(
    " → ".join(recorrido)
)


# ============================================================
# 9. DICCIONARIOS PARA GUARDAR RESULTADOS
# ============================================================

hidrogramas_nodos = {}

tiempos_nodos = {}


# Hidrograma inicial

hidrogramas_nodos[
    nodo_inicial
] = caudal_entrada.copy()


tiempos_nodos[
    nodo_inicial
] = tiempo.copy()


# Variables que iremos actualizando

caudal_actual = caudal_entrada.copy()

tiempo_actual = tiempo.copy()


# ============================================================
# 10. PROPAGACIÓN
# ============================================================

for i in range(
    len(recorrido) - 1
):

    origen = recorrido[i]

    destino = recorrido[i + 1]


    print("\n--------------------------------------")

    print(
        f"{origen} → {destino}"
    )


    # --------------------------------------------------------
    # Buscar la arista
    # --------------------------------------------------------

    tramo = aristas[
        (aristas["origen"] == origen) &
        (aristas["destino"] == destino)
    ]


    if tramo.empty:

        raise ValueError(
            f"No se encuentra la arista "
            f"{origen} → {destino}"
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

    #tiempo_viaje_segundos = (
     #   longitud / velocidad
    #)


    #tiempo_viaje_horas = (
     #   tiempo_viaje_segundos / 3600
    #)

    tiempo_viaje_segundos = (
        longitud / velocidad
    )

    tiempo_viaje_horas = (
        tiempo_viaje_segundos / 3600
    )

    correccion = correcciones.get(
        (origen, destino),
        0
    )

    tiempo_viaje_horas += correccion


    # --------------------------------------------------------
    # Propagar el hidrograma
    # --------------------------------------------------------

    # El caudal se mantiene.
    # Únicamente se desplaza en el tiempo.

    tiempo_actual = (
        tiempo_actual
        + tiempo_viaje_horas
    )


    caudal_salida = (
        caudal_actual.copy()
    )


    # --------------------------------------------------------
    # Guardar resultado en el nodo destino
    # --------------------------------------------------------

    hidrogramas_nodos[
        destino
    ] = caudal_salida.copy()


    tiempos_nodos[
        destino
    ] = tiempo_actual.copy()


    # Actualizar para el siguiente tramo

    caudal_actual = (
        caudal_salida.copy()
    )


    # --------------------------------------------------------
    # Mostrar información
    # --------------------------------------------------------

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
        "Velocidad:",
        velocidad,
        "m/s"
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
        np.max(caudal_salida),
        "m³/s"
    )


# ============================================================
# 11. RESULTADO FINAL
# ============================================================

print("\n======================================")
print("RESULTADO FINAL")
print("======================================")


print(
    "\nRecorrido:"
)

print(
    " → ".join(recorrido)
)


print(
    "\nCaudal máximo en N72:",
    np.max(
        hidrogramas_nodos["N72"]
    ),
    "m³/s"
)


print(
    "Caudal máximo en N26:",
    np.max(
        hidrogramas_nodos["N26"]
    ),
    "m³/s"
)


# ============================================================
# 12. TIEMPO DEL PICO
# ============================================================

indice_pico_N72 = np.argmax(
    hidrogramas_nodos["N72"]
)

indice_pico_N26 = np.argmax(
    hidrogramas_nodos["N26"]
)


print(
    "\nTiempo del pico en N72:",
    tiempos_nodos["N72"][
        indice_pico_N72
    ],
    "h"
)


print(
    "Tiempo del pico en N26:",
    tiempos_nodos["N26"][
        indice_pico_N26
    ],
    "h"
)


# ============================================================
# 13. REPRESENTAR TODOS LOS HIDROGRAMAS
# ============================================================

fig, ax = plt.subplots(
    figsize=(12, 7)
)


for nodo in recorrido:

    ax.plot(
        tiempos_nodos[nodo],
        hidrogramas_nodos[nodo],
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
    "desde N72 hasta N26 - Barranco del Horteta"
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
    + r"\resultados_hidrograma_natural_temporal\hidrogramas_N72_N26_Horteta.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 14. COMPARACIÓN N72 - N26
# ============================================================

fig, ax = plt.subplots(
    figsize=(12, 7)
)


ax.plot(
    tiempos_nodos["N72"],
    hidrogramas_nodos["N72"],
    label="N72 - Entrada",
    linewidth=2
)


ax.plot(
    tiempos_nodos["N26"],
    hidrogramas_nodos["N26"],
    label="N26 - Llegada",
    linewidth=2
)


ax.set_xlabel(
    "Tiempo (h)"
)

ax.set_ylabel(
    "Caudal (m³/s)"
)

ax.set_title(
    "Hidrograma de entrada y llegada al N26 - Horteta"
)

ax.grid(
    True,
    alpha=0.3
)

ax.legend()


plt.tight_layout()


plt.savefig(
    PATH
    + r"\resultados_hidrograma_natural_temporal\hidrograma_N72_N26_Horteta.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

plt.figure(figsize=(10,5))

plt.plot(
    tiempos_nodos["N72"],
    hidrogramas_nodos["N72"],
    linewidth=2,
    label="N72"
)

plt.xlabel("Tiempo (h)")
plt.ylabel("Caudal (m³/s)")
plt.title("Hidrograma de entrada N72")
plt.grid(True)
plt.legend()

plt.show()

############################################3333

df_N77 = pd.DataFrame({
    "Tiempo_h": tiempos_nodos["N77"],
    "Caudal_m3s": hidrogramas_nodos["N77"]
})

df_N77.to_excel(
    PATH
    + r"\resultados_hidrograma_natural_temporal\hidrograma_N77.xlsx",
    index=False
)

print("Excel de N77 guardado")

plt.figure(figsize=(10,5))

plt.plot(
    tiempos_nodos["N77"],
    hidrogramas_nodos["N77"],
    linewidth=2,
    label="N46"
)

plt.xlabel("Tiempo (h)")
plt.ylabel("Caudal (m³/s)")
plt.title("Hidrograma de entrada N77")
plt.grid(True)
plt.legend()

plt.savefig(
PATH
+ r"\resultados_hidrograma_natural_temporal\hidrograma_Poyo_N77.png",
dpi=300,
bbox_inches="tight"
)
plt.show()

plt.show()

import pandas as pd
import matplotlib.pyplot as plt

# TU HIDROGRAMA
mio = pd.read_excel(
    PATH
    + r"\resultados_hidrograma_natural_temporal\hidrograma_N77.xlsx"
)

prof = pd.read_excel(
    PATH
    + r"\HIDROGRAMAS\Hidrogramas nodos.xlsx",
    sheet_name="N77_Horteta AgArr Conflu Poyo"
)
prof["time"] = pd.to_datetime(prof["time"])

t0 = prof["time"].iloc[0]

prof["horas"] = (
    prof["time"] - t0
).dt.total_seconds()/3600

plt.figure(figsize=(12,6))

plt.plot(
    mio["Tiempo_h"],
    mio["Caudal_m3s"],
    label="Mi modelo"
)

plt.plot(
    prof["horas"],
    prof["flow"],
    label="Profesor"
)

plt.xlabel("Tiempo (h)")
plt.ylabel("Caudal (m³/s)")
plt.legend()
plt.grid()

plt.show()

indice_mio = np.argmax(mio["Caudal_m3s"])
Tp_mio = mio["Tiempo_h"].iloc[indice_mio]

indice_prof = np.argmax(prof["flow"])
Tp_prof = prof["horas"].iloc[indice_prof]

print("Tp modelo =", Tp_mio)
print("Tp profesor =", Tp_prof)
print("Desfase =", Tp_mio - Tp_prof)

print(nx.shortest_path(G,"N72","N77"))

print(
    "Correccion por arista =",
    corr_N72_N77
)