import numpy as np

# -------------------------------
# Funcion Para Crear Instancias
# -------------------------------

def crear_instancia(nombre_archivo="instancia.txt", n_dim=2, n_puntos=10,
                    rango_coords=(-100, 100), rango_pesos=(1, 10), seed=None):

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

# -------------------------------
# Funcion Para Leer Instancias
# -------------------------------

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

# -------------------------------
# Implementacion del Algoritmo de Weiszfeld
# -------------------------------

# -------------------------------
# Operador de Weiszfeld original (T(x))
# -------------------------------
def operador_weiszfeld(x, puntos, pesos):
    """
    Calcula el operador de Weiszfeld en el punto x.

    Parámetros:
        x (np.ndarray): punto actual.
        puntos (np.ndarray): coordenadas de los puntos de demanda.
        pesos (np.ndarray): pesos asociados a cada punto.

    Retorna:
        np.ndarray: nuevo punto calculado por el operador.
    """
    numerador = np.zeros_like(x)
    denominador = 0.0
    for i in range(len(puntos)):
        distancia = np.linalg.norm(x - puntos[i])
        if distancia == 0:
            continue  # evitar división por cero
        numerador += (pesos[i] * puntos[i]) / distancia
        denominador += pesos[i] / distancia
    return numerador / denominador

# --------------------------------------
# Calcular R(p_j)
# --------------------------------------
def calcular_R(punto_j, puntos, pesos, indice_j):
    """
    Calcula el vector R_j en el punto p_j

    Parámetros:
        punto_j (np.ndarray): el punto p_j.
        puntos (np.ndarray): conjunto de puntos p_i.
        pesos (np.ndarray): pesos w_i.
        indice_j (int): índice del punto p_j.

    Retorna:
        np.ndarray: vector R_j.
    """
    return sum(pesos[i] * (punto_j - puntos[i]) / np.linalg.norm(punto_j - puntos[i]) 
               for i in range(len(puntos)) if i != indice_j)

# --------------------------------------------------
# Operador S(p_j)
# --------------------------------------------------
def operador_S(punto_j, pesos, puntos, indice_j):
    """
    Aplica el operador S sobre p_j para escapar de un punto no diferenciable.

    Parámetros:
        punto_j (np.ndarray): el punto p_j.
        pesos (np.ndarray): pesos w_i.
        puntos (np.ndarray): conjunto de puntos.
        indice_j (int): índice de p_j.

    Retorna:
        np.ndarray: nuevo punto x^0 alejado de p_j.
    """
    Rj = calcular_R(punto_j, puntos, pesos, indice_j)
    norma_Rj = np.linalg.norm(Rj)
    direccion = -Rj / norma_Rj
    denominador_tj = sum(pesos[i] / np.linalg.norm(puntos[i] - punto_j) 
                         for i in range(len(puntos)) if i != indice_j)
    paso = (norma_Rj - pesos[indice_j]) / denominador_tj
    return punto_j + direccion * paso

# -------------------------------------------------------
# Modificación 2
# -------------------------------------------------------
def punto_inicial(puntos, pesos):
    """
    Encuentra un buen punto inicial para el algoritmo de Weiszfeld.

    Parámetros:
        puntos (np.ndarray): puntos p_i.
        pesos (np.ndarray): pesos w_i.

    Retorna:
        np.ndarray: punto inicial x^0.
    """
    costos = [sum(pesos[i] * np.linalg.norm(puntos[s] - puntos[i]) for i in range(len(puntos))) 
              for s in range(len(puntos))]
    j = np.argmin(costos)
    Rj = calcular_R(puntos[j], puntos, pesos, j)
    if np.linalg.norm(Rj) <= pesos[j]:
        return puntos[j]
    return operador_S(puntos[j], pesos, puntos, j)

# ----------------------------------------------------------------
# Algoritmo completo de Weiszfeld con ambas modificaciones
# ----------------------------------------------------------------
def weiszfeld_modificado(puntos, pesos, tolerancia=1e-6, max_iter=1000):
    """
    Resuelve el problema de Fermat-Weber con el algoritmo de Weiszfeld modificado.

    Parámetros:
        puntos (np.ndarray): coordenadas de los puntos de demanda.
        pesos (np.ndarray): importancia o prioridad de cada punto.
        tolerancia (float): criterio de convergencia.
        max_iter (int): cantidad máxima de iteraciones.

    Retorna:
        np.ndarray: solución aproximada (centro óptimo).
    """
    x = punto_inicial(puntos, pesos)  # ← Modificación 2
    for iteracion in range(1, max_iter + 1):
        # Modificación 1: si x coincide con algún punto de demanda
        if any(np.allclose(x, p) for p in puntos):
            j = np.argwhere([np.allclose(x, p) for p in puntos]).flatten()[0]
            Rj = calcular_R(x, puntos, pesos, j)
            if np.linalg.norm(Rj) <= pesos[j]:
                return x, iteracion  # x es óptimo
            x = operador_S(x, pesos, puntos, j)  # aplicar S(p_j)
        else:
            x_nuevo = operador_weiszfeld(x, puntos, pesos)
            if np.linalg.norm(x_nuevo - x) < tolerancia:
                return x_nuevo, iteracion  # convergencia
            x = x_nuevo
    return x, max_iter  # retorno por máximo número de iteraciones