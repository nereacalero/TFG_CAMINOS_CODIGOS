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

# Hidrograma inicial del Poyo en N1
archivo_poyo = PATH + r"\HIDROGRAMAS\POYO.xlsx"

# Hidrograma inicial del Gallego en N71
archivo_gallego = PATH + r"\HIDROGRAMAS\GALLEGO.xlsx"


# ============================================================
# 2. VELOCIDAD DE PROPAGACIÓN
# ============================================================

velocidad = 5.0       # m/s


# ============================================================
# 3. LEER RED
# ============================================================

aristas = gpd.read_file(
    archivo_aristas
)

print("\nCOLUMNAS ARISTAS:")
print(aristas.columns.tolist())


# ============================================================
# 4. CREAR GRAFO
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
# 5. FUNCIÓN PARA PROPAGAR UN HIDROGRAMA
# ============================================================

def propagar_hidrograma(
    nodo_inicial,
    nodo_final,
    tiempo_inicial,
    caudal_inicial
):

    # --------------------------------------------------------
    # Buscar recorrido
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


    recorrido = nx.shortest_path(
        G,
        source=nodo_inicial,
        target=nodo_final
    )


    print("\n======================================")
    print(
        f"RECORRIDO {nodo_inicial} -> {nodo_final}"
    )
    print("======================================")

    print(
        " -> ".join(recorrido)
    )


    # --------------------------------------------------------
    # Diccionarios
    # --------------------------------------------------------

    hidrogramas = {}

    tiempos = {}


    hidrogramas[nodo_inicial] = (
        caudal_inicial.copy()
    )

    tiempos[nodo_inicial] = (
        tiempo_inicial.copy()
    )


    tiempo_actual = tiempo_inicial.copy()

    caudal_actual = caudal_inicial.copy()


    # --------------------------------------------------------
    # Recorrer las aristas
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


        id_arista = tramo[
            "ID_ARISTA"
        ]


        longitud = float(
            tramo["longitud"]
        )


        # ----------------------------------------------------
        # Tiempo de viaje
        # ----------------------------------------------------

        tiempo_viaje_segundos = (
            longitud / velocidad
        )


        tiempo_viaje_horas = (
            tiempo_viaje_segundos / 3600
        )


        # ----------------------------------------------------
        # Desplazar hidrograma
        # ----------------------------------------------------

        tiempo_actual = (
            tiempo_actual
            + tiempo_viaje_horas
        )


        # El caudal se conserva

        caudal_actual = (
            caudal_actual.copy()
        )


        # Guardar

        hidrogramas[destino] = (
            caudal_actual.copy()
        )

        tiempos[destino] = (
            tiempo_actual.copy()
        )


        # ----------------------------------------------------
        # Mostrar información
        # ----------------------------------------------------

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


    return (
        recorrido,
        tiempos,
        hidrogramas
    )


# ============================================================
# 6. HIDROGRAMA DEL POYO
# ============================================================

poyo = pd.read_excel(
    archivo_poyo,
    header=2
)


tiempo_poyo = poyo[
    "t(horas)"
].to_numpy(dtype=float)


caudal_poyo = poyo[
    "Q(m3/s)"
].to_numpy(dtype=float)


# ============================================================
# 7. PROPAGAR POYO N1 -> N11
# ============================================================

recorrido_poyo, tiempos_poyo, hidrogramas_poyo = (
    propagar_hidrograma(
        "N1",
        "N11",
        tiempo_poyo,
        caudal_poyo
    )
)


tiempo_poyo_N11 = tiempos_poyo[
    "N11"
]

caudal_poyo_N11 = hidrogramas_poyo[
    "N11"
]


# ============================================================
# 8. HIDROGRAMA DEL GALLEGO
# ============================================================

gallego = pd.read_excel(
    archivo_gallego,
    header=2
)


tiempo_gallego = gallego[
    "t(horas)"
].to_numpy(dtype=float)


caudal_gallego = gallego[
    "Q(m3/s)"
].to_numpy(dtype=float
)


# ============================================================
# 9. PROPAGAR GALLEGO N71 -> N11
# ============================================================

recorrido_gallego, tiempos_gallego, hidrogramas_gallego = (
    propagar_hidrograma(
        "N71",
        "N11",
        tiempo_gallego,
        caudal_gallego
    )
)


tiempo_gallego_N11 = tiempos_gallego[
    "N11"
]

caudal_gallego_N11 = hidrogramas_gallego[
    "N11"
]


# ============================================================
# 10. SUMAR HIDROGRAMAS EN N11
# ============================================================

print("\n======================================")
print("CONFLUENCIA EN N11")
print("======================================")


# Crear eje temporal común

tiempo_comun = np.unique(
    np.concatenate(
        [
            tiempo_poyo_N11,
            tiempo_gallego_N11
        ]
    )
)


# Interpolar ambos hidrogramas
# Fuera de su intervalo se considera Q = 0

caudal_poyo_comun = np.interp(
    tiempo_comun,
    tiempo_poyo_N11,
    caudal_poyo_N11,
    left=0,
    right=0
)


caudal_gallego_comun = np.interp(
    tiempo_comun,
    tiempo_gallego_N11,
    caudal_gallego_N11,
    left=0,
    right=0
)


# SUMA EN LA CONFLUENCIA

caudal_N11 = (
    caudal_poyo_comun
    +
    caudal_gallego_comun
)


print(
    "Caudal máximo Poyo en N11:",
    np.max(caudal_poyo_N11),
    "m3/s"
)


print(
    "Caudal máximo Gallego en N11:",
    np.max(caudal_gallego_N11),
    "m3/s"
)


print(
    "Caudal máximo resultante en N11:",
    np.max(caudal_N11),
    "m3/s"
)


# ============================================================
# 11. GUARDAR HIDROGRAMA RESULTANTE EN N11
# ============================================================

hidrograma_N11 = pd.DataFrame({

    "t(horas)": tiempo_comun,

    "Q_Poyo(m3/s)": caudal_poyo_comun,

    "Q_Gallego(m3/s)": caudal_gallego_comun,

    "Q_N11(m3/s)": caudal_N11

})


hidrograma_N11.to_excel(
    PATH
    + r"\resultados_hidrograma_natural_temporal\hidrograma_N11_confluencia.xlsx",
    index=False
)


# ============================================================
# 12. REPRESENTAR LA CONFLUENCIA
# ============================================================

fig, ax = plt.subplots(
    figsize=(12, 7)
)


ax.plot(
    tiempo_comun,
    caudal_poyo_comun,
    label="Poyo → N11",
    linewidth=2
)


ax.plot(
    tiempo_comun,
    caudal_gallego_comun,
    label="Gallego → N11",
    linewidth=2
)


ax.plot(
    tiempo_comun,
    caudal_N11,
    label="N11 - Hidrograma resultante",
    linewidth=3
)


ax.set_xlabel(
    "Tiempo (h)"
)

ax.set_ylabel(
    "Caudal (m³/s)"
)

ax.set_title(
    "Confluencia del Poyo y Gallego en N11"
)

ax.grid(
    True,
    alpha=0.3
)

ax.legend()


plt.tight_layout()


plt.savefig(
    PATH
    + r"\resultados_hidrograma_natural_temporal\confluencia_Poyo_Gallego_N11.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 13. PROPAGAR N11 -> N26
# ============================================================

print("\n======================================")
print("PROPAGACIÓN N11 -> N26")
print("======================================")


recorrido_N11_N26, tiempos_N11_N26, hidrogramas_N11_N26 = (
    propagar_hidrograma(
        "N11",
        "N26",
        tiempo_comun,
        caudal_N11
    )
)


# ============================================================
# 14. HIDROGRAMA FINAL EN N26
# ============================================================

tiempo_N26 = tiempos_N11_N26[
    "N26"
]

caudal_N26 = hidrogramas_N11_N26[
    "N26"
]


print("\n======================================")
print("RESULTADO FINAL")
print("======================================")


print(
    "\nRecorrido desde N11:"
)

print(
    " -> ".join(
        recorrido_N11_N26
    )
)


print(
    "\nCaudal máximo en N11:",
    np.max(caudal_N11),
    "m3/s"
)


print(
    "Caudal máximo en N26:",
    np.max(caudal_N26),
    "m3/s"
)


indice_pico_N11 = np.argmax(
    caudal_N11
)


indice_pico_N26 = np.argmax(
    caudal_N26
)


print(
    "\nTiempo del pico en N11:",
    tiempo_comun[
        indice_pico_N11
    ],
    "h"
)


print(
    "Tiempo del pico en N26:",
    tiempo_N26[
        indice_pico_N26
    ],
    "h"
)


# ============================================================
# 15. TODOS LOS HIDROGRAMAS N11 -> N26
# ============================================================

fig, ax = plt.subplots(
    figsize=(12, 7)
)


for nodo in recorrido_N11_N26:

    ax.plot(
        tiempos_N11_N26[nodo],
        hidrogramas_N11_N26[nodo],
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
    "desde N11 hasta N26"
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
    + r"\resultados_hidrograma_natural_temporal\hidrogramas_N11_N26.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 16. COMPARACIÓN N11 - N26
# ============================================================

fig, ax = plt.subplots(
    figsize=(12, 7)
)


ax.plot(
    tiempo_comun,
    caudal_N11,
    label="N11 - Confluencia",
    linewidth=2
)


ax.plot(
    tiempo_N26,
    caudal_N26,
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
    "Hidrograma resultante en N11 y N26"
)

ax.grid(
    True,
    alpha=0.3
)

ax.legend()


plt.tight_layout()


plt.savefig(
    PATH
    + r"\resultados_hidrograma_natural_temporal\hidrograma_N11_N26_comparacion.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()