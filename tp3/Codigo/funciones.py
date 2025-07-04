import numpy as np

def leer_instancia(nombre_archivo):
    """
    Lee una instancia guardada en un archivo .txt con formato:
    x1 x2 ... xn w

    Parámetros:
        nombre_archivo (str): ruta al archivo.

    Devuelve:
        puntos (np.ndarray): array de tamaño (m, n) con las coordenadas.
        pesos (np.ndarray): array de tamaño (m,) con los pesos.
    """
    datos = []

    with open(nombre_archivo, "r") as f:
        for linea in f:
            if linea.strip().startswith("#") or not linea.strip():
                continue  # Ignorar comentarios y líneas vacías
            valores = list(map(float, linea.strip().split()))
            datos.append(valores)

    datos = np.array(datos)
    puntos = datos[:, :-1]  # todas las columnas menos la última
    pesos = datos[:, -1]    # última columna

    return puntos, pesos
