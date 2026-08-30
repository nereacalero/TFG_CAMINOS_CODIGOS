# Cargamos las librerias necesarias
import os
import glob
import geopandas as gpd
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt

# Leer las capas que se necesitan para obtener los datos para aplicar Manning.
PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS\secciones_def3"
nodos_red = pd.read_excel(r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS\QGIS\EXCELS\NODOS_500M.xlsx")
aristas_red = pd.read_excel(r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS\QGIS\EXCELS\ARISTAS_RED.xlsx")

# He tenido un problema y no sabía si estarían duplicadas las aristas entonces tuve que hacer esto
secciones_transversales = glob.glob(os.path.join(PATH, "**", "*.gpkg"), recursive=True)

# Ordenar E_1, E_2, ..., E_105, me daba problemas por no tenerlos ordenados entonces hice esta funcion
secciones_transversales.sort(key=lambda x: int(re.search(r"E_(\d+)", os.path.basename(x)).group(1)))

# Carpeta donde guardaremos las figuras de las secciones llenas
PATH_FIGURAS = os.path.join(PATH, "FIGURAS")
os.makedirs(PATH_FIGURAS, exist_ok=True)

# Número de Manning
N_MANNING = 0.035

# La idea ahora es crear un bucle de forma que lea todas las secciones transversales (es decir, sus datos de cada una de ellas)
# y seguidamente que nos saque los resultados.
def leer_perfil(secciones_transversales):

    seccion = gpd.read_file(secciones_transversales)
    nombre = os.path.basename(secciones_transversales).replace(".gpkg","")

    x = seccion["distance"].to_numpy()
    z = seccion["elevation"].to_numpy()

    return nombre, x, z

# Ahora necesitamos calcular los datos necesarios para la ecuacion de manning
def calcular_nivel_agua(x,z):
    i_min = np.argmin(z)
    borde_izq = np.argmax(z[:i_min+1])
    borde_der = i_min +np.argmax(z[i_min:])
    nivel_agua = min(z[borde_izq],z[borde_der])

    return nivel_agua, borde_izq, borde_der

def calcular_area(x, z, nivel):

    x_agua = []
    z_agua = []

    for i in range(len(x)-1):

        x1, z1 = x[i], z[i]
        x2, z2 = x[i+1], z[i+1]
        dentro1 = z1 <= nivel
        dentro2 = z2 <= nivel

        # Los dos puntos están bajo el agua
        if dentro1 and dentro2:
            if len(x_agua) == 0:
                x_agua.append(x1)
                z_agua.append(z1)
            x_agua.append(x2)
            z_agua.append(z2)

        # Sale del agua
        elif dentro1 and not dentro2:
            t = (nivel-z1)/(z2-z1)
            xc = x1+t*(x2-x1)
            if len(x_agua) == 0:
                x_agua.append(x1)
                z_agua.append(z1)
            x_agua.append(xc)
            z_agua.append(nivel)

        # Entra en el agua
        elif (not dentro1) and dentro2:
            t = (nivel-z1)/(z2-z1)
            xc = x1+t*(x2-x1)
            x_agua.append(xc)
            z_agua.append(nivel)
            x_agua.append(x2)
            z_agua.append(z2)

    x_agua = np.array(x_agua)
    z_agua = np.array(z_agua)

    profundidad = nivel-z_agua
    area = np.trapezoid(profundidad, x_agua)

    return area, profundidad, x_agua, z_agua

def calcular_perimetro(x_agua, z_agua):

    perimetro = 0

    for i in range(len(x_agua)-1):

        dx = x_agua[i+1]-x_agua[i]
        dz = z_agua[i+1]-z_agua[i]

        perimetro += np.sqrt(dx**2 + dz**2)

    return perimetro

def calcular_radio(area_mojada, perimetro_mojado):
    radio_hidraulico = area_mojada / perimetro_mojado
    return radio_hidraulico


def calcular_pendiente(nombre, aristas_red, nodos_red):
    arista = aristas_red[aristas_red["ID_ARISTA"] == nombre]
    origen = arista.iloc[0]["origen"]
    destino = arista.iloc[0]["destino"]
    longitud = arista.iloc[0]["longitud"]

    # Buscamos las cotas de los nodos
    cota_origen = nodos_red.loc[nodos_red["id"] == origen,"COTA"].iloc[0]
    cota_destino = nodos_red.loc[nodos_red["id"] == destino,"COTA"].iloc[0]

    pendiente = float((cota_origen - cota_destino) / longitud)
    return pendiente


def calcular_manning(area_mojada, radio_hidraulico, pendiente):
    pendiente = abs(pendiente) # para que no me salgan numeros complejos

    Q = (1/N_MANNING) * area_mojada * (radio_hidraulico**(2/3)) * (pendiente**0.5)
    return Q


def representar_seccion(nombre, x, z, nivel, x_agua, z_agua, borde_izq, borde_der):

    plt.figure(figsize=(10,5))

    plt.plot(x,z,color="black",linewidth=2,label="Terreno")

    # Polígono del agua
    plt.fill_between(x_agua,z_agua,nivel,color="deepskyblue",alpha=0.6,label="Agua")

    plt.plot(x,z,color="black",linewidth=3,zorder=5)
    plt.axhline(nivel,color="blue",linestyle="--",label=f"Nivel = {nivel:.2f} m")

    plt.xlabel("Distancia (m)")
    plt.ylabel("Cota (m)")
    plt.title(f"Sección transversal {nombre}")

    plt.grid(True)

    plt.scatter(x[borde_izq], z[borde_izq],color="red",s=70,zorder = 5,label = "borde izquierdo")

    plt.scatter(x[borde_der],z[borde_der],color="green",s=70,zorder = 5,label = "borde derecho")
    
    plt.legend()

    direccion_figuras = os.path.join(PATH_FIGURAS, f"{nombre}.png")
    plt.savefig(direccion_figuras,dpi=300,bbox_inches="tight")
    plt.close()

# He tenido muchos problemas para que python por si solo tomase las secciones y calculase la seccion llena, entonces
# lo que habia pensado era en hacerlo manualmente. Hablando con unos compañeros me dijeron que podía hacerlo manualmente
# pero de una forma rapida en python y me dijeron que buscara esta funcion.

def seleccionar_bordes(nombre, x, z):

    fig, ax = plt.subplots(figsize=(10,5))

    ax.plot(x, z, color="black", linewidth=2)
    ax.set_title(f"{nombre}")
    ax.set_xlabel("Distancia (m)")
    ax.set_ylabel("Cota (m)")
    ax.grid(True)

    print(f"\nSeleccionar los dos bordes del cauce para {nombre}")

    # Dos clics primero a la izquierda y luego a la derecha
    puntos = plt.ginput(2, timeout=-1)
    plt.close()

    # Coordenadas X de los clics
    x1 = puntos[0][0]
    x2 = puntos[1][0]

    # Buscar el punto del perfil más cercano
    borde_izq = np.argmin(np.abs(x - x1))
    borde_der = np.argmin(np.abs(x - x2))

    if borde_izq > borde_der:
        borde_izq, borde_der = borde_der, borde_izq

    return borde_izq, borde_der

resultados = []

for seccion in secciones_transversales:

    print(seccion)

    nombre, x, z = leer_perfil(seccion)

    print(f"Procesando {nombre}")
    print(nombre)
    print("Número de puntos:", len(x))

    nivel, borde_izq, borde_der = calcular_nivel_agua(x,z)
    borde_izq, borde_der = seleccionar_bordes(nombre, x, z)

    nivel = min(z[borde_izq],z[borde_der])

    x_cauce = x[borde_izq:borde_der+1]
    z_cauce = z[borde_izq:borde_der+1]

    area, profundidad, x_agua, z_agua = calcular_area(
        x_cauce,z_cauce,nivel)

    perimetro = calcular_perimetro(x_agua, z_agua)
    radio = calcular_radio(area, perimetro)
    pendiente = calcular_pendiente(nombre, aristas_red, nodos_red)
    caudal = calcular_manning(area, radio, pendiente)
    representar_seccion(
        nombre,
        x,
        z,
        nivel,
        x_agua,
        z_agua,
        borde_izq,
        borde_der
    )

    resultados.append({
        "ID_ARISTA": nombre,
        "AREA": area,
        "PERIMETRO": perimetro,
        "RADIO": radio,
        "PENDIENTE": pendiente,
        "CAUDAL": caudal
    })

plt.xlim(x.min()-2, x.max()+2)
plt.ylim(min(z)-0.5,max(z)+0.5)

df = pd.DataFrame(resultados)
df.to_excel(os.path.join(PATH, "Resultados.xlsx"),index=False)
