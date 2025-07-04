import numpy as np

def crear_instancia(nombre_archivo="instancia.txt", n_dim=2, n_puntos=10,
                    rango_coords=(-100, 100), rango_pesos=(1, 10), seed=None):
    """
    Crea y guarda una instancia del problema de Fermat-Weber en un archivo .txt.

    Parámetros:
        nombre_archivo (str): nombre del archivo de salida.
        n_dim (int): dimensión del espacio (n).
        n_puntos (int): cantidad de puntos (m).
        rango_coords (tuple): rango para las coordenadas (min, max).
        rango_pesos (tuple): rango para los pesos positivos (min, max).
        seed (int): semilla para reproducibilidad.

    Devuelve:
        puntos (np.ndarray): array de tamaño (m, n) con las coordenadas.
        pesos (np.ndarray): array de tamaño (m,) con los pesos.
    """
    if seed is not None:
        np.random.seed(seed)

    puntos = np.random.uniform(rango_coords[0], rango_coords[1], size=(n_puntos, n_dim))
    pesos = np.random.uniform(rango_pesos[0], rango_pesos[1], size=n_puntos)
    
    pesos = pesos.reshape(-1, 1)
    datos = np.hstack((puntos, pesos))

    with open(nombre_archivo, "w") as f:
        f.write("# Formato: x1 x2 ... xn w\n")
        for fila in datos:
            f.write(" ".join(f"{valor:.6f}" for valor in fila) + "\n")

    print(f"✅ Instancia guardada en '{nombre_archivo}'")
    return datos


crear_instancia(nombre_archivo="instancia5D.txt", n_dim=5, n_puntos=10, seed=42)