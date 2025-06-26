import random
import math
import heapq
from collections import defaultdict

VALOR_GRANDE = 10**6

# --------------------------
# 1. Generar instancia inicial
# --------------------------

def generar_instancia(nombre_archivo, cant_clientes=20, costo_repartidor=5, dist_max=50,
                      cant_refrigerados=7, cant_exclusivos=11, porcentaje_conectividad=0.1, rango_coord=100):
    ids_clientes = list(range(1, cant_clientes + 1))
    refrigerados = sorted(random.sample(ids_clientes, cant_refrigerados))
    restantes = list(set(ids_clientes) - set(refrigerados))
    exclusivos = sorted(random.sample(restantes, min(cant_exclusivos, len(restantes))))
    coords = {i: (random.randint(0, rango_coord), random.randint(0, rango_coord)) for i in [0] + ids_clientes}

    with open(nombre_archivo, 'w') as f:
        f.write(f"{cant_clientes}\n")
        f.write(f"{costo_repartidor}\n")
        f.write(f"{dist_max}\n")
        f.write(f"{cant_refrigerados}\n")
        for r in refrigerados:
            f.write(f"{r}\n")
        f.write(f"{len(exclusivos)}\n")
        for e in exclusivos:
            f.write(f"{e}\n")

        aristas = {}
        nodos = [0] + ids_clientes
        for i in nodos:
            for j in nodos:
                if i < j and random.random() < porcentaje_conectividad:
                    xi, yi = coords[i]
                    xj, yj = coords[j]
                    dist = round(math.hypot(xi - xj, yi - yj))
                    costo = random.randint(1, 10)
                    aristas[(i, j)] = (dist, costo)

        for i in nodos:
            for j in nodos:
                if i < j and (i, j) not in aristas:
                    aristas[(i, j)] = (VALOR_GRANDE, VALOR_GRANDE)

        for (i, j), (d, c) in aristas.items():
            f.write(f"{i} {j} {d} {c}\n")

    print(f"Instancia generada y guardada en {nombre_archivo}")

# --------------------------
# 2. Leer instancia y grafo
# --------------------------

def leer_instancia(nombre_archivo):
    with open(nombre_archivo, 'r') as f:
        lineas = f.readlines()

    cant_clientes = int(lineas[0])
    cant_refrigerados = int(lineas[3])
    cant_exclusivos = int(lineas[4 + cant_refrigerados])
    header = lineas[:5 + cant_refrigerados + cant_exclusivos]
    aristas = lineas[len(header):]

    grafo = defaultdict(list)
    for linea in aristas:
        i, j, d, c = map(int, linea.strip().split())
        grafo[i].append((j, d, c))
        grafo[j].append((i, d, c))
    return grafo, header

# --------------------------
# 3. Dijkstra genérico
# --------------------------

def dijkstra(grafo, origen, n, modo='dist'):
    peso = 1 if modo == 'dist' else 2
    distancias = [float('inf')] * n
    distancias[origen] = 0
    heap = [(0, origen)]

    while heap:
        d_actual, nodo = heapq.heappop(heap)
        if d_actual > distancias[nodo]:
            continue
        for vecino, d, c in grafo[nodo]:
            peso_actual = d if peso == 1 else c
            nueva_d = d_actual + peso_actual
            if nueva_d < distancias[vecino]:
                distancias[vecino] = nueva_d
                heapq.heappush(heap, (nueva_d, vecino))
    return distancias

# --------------------------
# 4. Actualizar distancias mínimas
# --------------------------

def actualizar_distancias_minimas(nombre_archivo, salida="Instancia_Dist_Mod.txt"):
    grafo, header = leer_instancia(nombre_archivo)
    nodos = list(grafo.keys())
    n = max(nodos) + 1
    resultado = {}

    for i in nodos:
        dist = dijkstra(grafo, i, n, modo='dist')
        for j in nodos:
            if i != j:
                par = tuple(sorted((i, j)))
                if par not in resultado or dist[j] < resultado[par][0]:
                    resultado[par] = [dist[j], VALOR_GRANDE]

    for i in nodos:
        for j, _, c in grafo[i]:
            par = tuple(sorted((i, j)))
            if par in resultado:
                resultado[par][1] = c

    with open(salida, 'w') as f:
        f.writelines(header)
        for (i, j), (d, c) in sorted(resultado.items()):
            f.write(f"{i} {j} {d} {c}\n")
    print(f"Distancias mínimas actualizadas en: {salida}")

# --------------------------
# 5. Actualizar costos mínimos
# --------------------------

def actualizar_costos_minimos(nombre_archivo, salida="Instancia_F.txt"):
    grafo, header = leer_instancia(nombre_archivo)
    nodos = list(grafo.keys())
    n = max(nodos) + 1
    resultado = {}

    for i in nodos:
        costos = dijkstra(grafo, i, n, modo='costo')
        for j in nodos:
            if i != j:
                par = tuple(sorted((i, j)))
                if par not in resultado or costos[j] < resultado[par][1]:
                    resultado[par] = [VALOR_GRANDE, costos[j]]

    for i in nodos:
        for j, d, _ in grafo[i]:
            par = tuple(sorted((i, j)))
            if par in resultado:
                resultado[par][0] = d

    with open(salida, 'w') as f:
        f.writelines(header)
        for (i, j), (d, c) in sorted(resultado.items()):
            f.write(f"{i} {j} {d} {c}\n")
    print(f"Costos mínimos actualizados en: {salida}")

# --------------------------
# 6. Ejemplo de uso
# --------------------------

if __name__ == "__main__":
    generar_instancia("Instancia_Original.txt", cant_clientes=10, costo_repartidor=5, dist_max=50,
                      cant_refrigerados=7, cant_exclusivos=3, porcentaje_conectividad=0.5, rango_coord=100)
    
    actualizar_distancias_minimas("Instancia_Original.txt", "Instancia_Dist_Mod.txt")
    actualizar_costos_minimos("Instancia_Dist_Mod.txt", "Instancia_F.txt")
