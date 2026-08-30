# COMPARACION DE HIDROGRAMAS
import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt

PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"
archivo_aristas = (PATH+ r"\resultados\aristas_red.geojson")
archivo_poyo = PATH + r"\HIDROGRAMAS\POYO.xlsx"
archivo_N61 = PATH + r"\resultados_hidrograma_completo_temporal_2\hidrograma_N61.xlsx"
archivo_N87 = PATH + r"\resultados_hidrograma_completo_temporal_2\hidrograma_N87.xlsx"
archivo_N113 = PATH + r"\resultados_hidrograma_completo_temporal_2\hidrograma_N113.xlsx"

poyo = pd.read_excel(archivo_poyo,header=2)
tiempo_N1 = poyo["t(horas)"].to_numpy(dtype=float)
Q_N1 = poyo["Q(m3/s)"].to_numpy(dtype=float)

datos_N61 = pd.read_excel(archivo_N61)
tiempo_N61 = datos_N61["t(horas)"].to_numpy(dtype=float)
Q_N61 = datos_N61["Q_N61(m3/s)"].to_numpy(dtype=float)

datos_N87 = pd.read_excel(archivo_N87)
tiempo_N87 = datos_N87["t(horas)"].to_numpy(dtype=float)
Q_N87 = datos_N87["Q_N87(m3/s)"].to_numpy(dtype=float)

datos_N113 = pd.read_excel(archivo_N113)
tiempo_N113 = datos_N113["t(horas)"].to_numpy(dtype=float)
Q_N113 = datos_N113["Q_N113(m3/s)"].to_numpy(dtype=float)

fig, ax = plt.subplots(figsize=(12,7))

ax.plot(
    tiempo_N1,
    Q_N1,
    label="N1 - Entrada",
    linewidth=2
)

ax.plot(
    tiempo_N61,
    Q_N61,
    label="N61 - Salida natural",
    linewidth=2
)

ax.set_xlabel("Tiempo (h)")
ax.set_ylabel("Caudal (m³/s)")
ax.set_title("Comparación N1 y N61")
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
plt.savefig(
    PATH +
    r"\resultados_hidrograma_completo_temporal_2\Comparación_N1_N61.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()


fig, ax = plt.subplots(figsize=(12,7))
ax.plot(
    tiempo_N1,
    Q_N1,
    label="N1 - Entrada",
    linewidth=2
)

ax.plot(
    tiempo_N87,
    Q_N87,
    label="N87 - Salida artificial",
    linewidth=2
)

ax.set_xlabel("Tiempo (h)")
ax.set_ylabel("Caudal (m³/s)")
ax.set_title("Comparación N1 y N87")
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig(
    PATH +
    r"\resultados_hidrograma_completo_temporal_2\Comparación_N1_N87.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

fig, ax = plt.subplots(figsize=(12,7))
ax.plot(
    tiempo_N1,
    Q_N1,
    label="N1 - Entrada",
    linewidth=2
)

ax.plot(
    tiempo_N113,
    Q_N113,
    label="N113 - Salida artificial",
    linewidth=2
)

ax.set_xlabel("Tiempo (h)")
ax.set_ylabel("Caudal (m³/s)")
ax.set_title("Comparación N1 y N113")
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
plt.savefig(
    PATH +
    r"\resultados_hidrograma_completo_temporal_2\Comparación_N1_N113.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

fig, ax = plt.subplots(figsize=(12,7))

ax.plot(
    tiempo_N61,
    Q_N61,
    label="N61 - Natural",
    linewidth=2
)

ax.plot(
    tiempo_N87,
    Q_N87,
    label="N87 - Artificial",
    linewidth=2
)

ax.plot(
    tiempo_N113,
    Q_N113,
    label="N113 - Artificial",
    linewidth=2
)

ax.set_xlabel("Tiempo (h)")
ax.set_ylabel("Caudal (m³/s)")
ax.set_title(
    "Comparación de hidrogramas red completa"
)

ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
plt.savefig(
    PATH +
    r"\resultados_hidrograma_completo_temporal_2\Comparación de hidrogramas red completa.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

print("\nRESUMEN DE PICOS")
print("N61:",np.max(Q_N61),"m3/s")
print("N87:",np.max(Q_N87),"m3/s")
print("N113:",np.max(Q_N113),"m3/s")