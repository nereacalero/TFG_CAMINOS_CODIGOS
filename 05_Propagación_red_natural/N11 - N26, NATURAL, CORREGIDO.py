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

# ============================================================
# CORRECCIONES TEMPORALES
# ============================================================

corr_N11_N17 = 0.581719 / 6

corr_N17_N25 = (0.86714 - 0.581719) / 8

correcciones = {

    ("N11","N12"): corr_N11_N17,
    ("N12","N13"): corr_N11_N17,
    ("N13","N14"): corr_N11_N17,
    ("N14","N15"): corr_N11_N17,
    ("N15","N16"): corr_N11_N17,
    ("N16","N17"): corr_N11_N17,

    ("N17","N18"): corr_N17_N25,
    ("N18","N19"): corr_N17_N25,
    ("N19","N20"): corr_N17_N25,
    ("N20","N21"): corr_N17_N25,
    ("N21","N22"): corr_N17_N25,
    ("N22","N23"): corr_N17_N25,
    ("N23","N24"): corr_N17_N25,
    ("N24","N25"): corr_N17_N25

}

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

        correccion = correcciones.get(
            (origen, destino),
            0
        )

        tiempo_viaje_horas += correccion
        
        
        #tiempo_viaje_segundos = (
         #   longitud / velocidad
        #)


        #tiempo_viaje_horas = (
         #   tiempo_viaje_segundos / 3600
        #)


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

poyo = poyo[
    ["t(horas)", "Q(m3/s)"]
].dropna()

tiempo_poyo = poyo[
    "t(horas)"
].to_numpy(dtype=float)


caudal_poyo = poyo[
    "Q(m3/s)"
].to_numpy(dtype=float)

print("NaN Poyo =", np.isnan(caudal_poyo).sum())
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

gallego = gallego[
    ["t(horas)", "Q(m3/s)"]
].dropna()

tiempo_gallego = gallego[
    "t(horas)"
].to_numpy(dtype=float)


caudal_gallego = gallego[
    "Q(m3/s)"
].to_numpy(dtype=float
)

print("NaN Gallego =", np.isnan(caudal_gallego).sum())
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

print("\n--- N17 ---")

indice17 = np.argmax(
    hidrogramas_N11_N26["N17"]
)

Tp17 = tiempos_N11_N26["N17"][indice17]

print("Tp17 =", Tp17)

print("\n--- N25 ---")

indice25 = np.argmax(
    hidrogramas_N11_N26["N25"]
)

Tp25 = tiempos_N11_N26["N25"][indice25]

print("Tp25 =", Tp25)


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

df_N17 = pd.DataFrame({
    "Tiempo_h": tiempos_N11_N26["N17"],
    "Caudal_m3s": hidrogramas_N11_N26["N17"]
})

df_N17.to_excel(
    PATH
    + r"\resultados_hidrograma_natural_temporal\hidrograma_N17.xlsx",
    index=False
)

print("Excel de N17 guardado")

plt.figure(figsize=(10,5))

plt.plot(
    tiempos_N11_N26["N17"],
    hidrogramas_N11_N26["N17"],
    linewidth=2,
    label="N17"
)

plt.xlabel("Tiempo (h)")
plt.ylabel("Caudal (m³/s)")
plt.title("Hidrograma de entrada N17")
plt.grid(True)
plt.legend()

plt.savefig(
PATH
+ r"\resultados_hidrograma_natural_temporal\hidrograma_Poyo_N17.png",
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
    + r"\resultados_hidrograma_natural_temporal\hidrograma_N17.xlsx"
)

prof = pd.read_excel(
    PATH
    + r"\HIDROGRAMAS\Hidrogramas nodos.xlsx",
    sheet_name="N17_Poyo AgAb Pla de Quart"
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

df_N25 = pd.DataFrame({
    "Tiempo_h": tiempos_N11_N26["N25"],
    "Caudal_m3s": hidrogramas_N11_N26["N25"]
})

df_N25.to_excel(
    PATH
    + r"\resultados_hidrograma_natural_temporal\hidrograma_N25.xlsx",
    index=False
)

print("Excel de N25 guardado")

plt.figure(figsize=(10,5))

plt.plot(
    tiempos_N11_N26["N25"],
    hidrogramas_N11_N26["N25"],
    linewidth=2,
    label="N25"
)

plt.xlabel("Tiempo (h)")
plt.ylabel("Caudal (m³/s)")
plt.title("Hidrograma de entrada N25")
plt.grid(True)
plt.legend()

plt.savefig(
PATH
+ r"\resultados_hidrograma_natural_temporal\hidrograma_Poyo_N25.png",
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
    + r"\resultados_hidrograma_natural_temporal\hidrograma_N25.xlsx"
)

prof = pd.read_excel(
    PATH
    + r"\HIDROGRAMAS\Hidrogramas nodos.xlsx",
    sheet_name="N25_AgAb Conflu Poyo-Horteta"
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

print(nx.shortest_path(G,"N11","N17"))
print(nx.shortest_path(G,"N11","N25"))


# ============================================================
# CÁLCULO AUTOMÁTICO DEL NUEVO DESFASE (Añadir tras pintar la gráfica de N17)
# ============================================================
indice_mio = np.argmax(mio["Caudal_m3s"])
Tp_mio = mio["Tiempo_h"].iloc[indice_mio]

indice_prof = np.argmax(prof["flow"])
Tp_prof = prof["horas"].iloc[indice_prof]

print("\n--- ANALIZADOR DE DESFASE EN TIEMPO REAL ---")
print("Tu tiempo de pico actual:", Tp_mio, "h")
print("Tiempo de pico del profesor:", Tp_prof, "h")

# Esto te dirá exactamente cuánto le sobra o le falta a tu modelo HOY
error_desfase = Tp_prof - Tp_mio
print("CORRECCIÓN REQUERIDA (añadir al desfase actual):", error_desfase, "horas")