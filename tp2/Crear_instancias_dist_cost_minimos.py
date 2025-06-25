import random
import math
import heapq
from collections import defaultdict

# --------------------------
# 1. Generar instancia inicial
# --------------------------

def generar_instancia_grande(nombre_archivo, cant_clientes=20, costo_repartidor=5, dist_max=50,
                             cant_refrigerados=7, cant_exclusivos=11, porcentaje_conectividad=0.1, rango_coord=100):
    ids_clientes = list(range(1, cant_clientes + 1))
    refrigerados = sorted(random.sample(ids_clientes, cant_refrigerados))
    restantes = list(set(ids_clientes) - set(refrigerados))
    exclusivos = sorted(random.sample(restantes, cant_exclusivos))
    coords = {i: (random.randint(0, rango_coord), random.randint(0, rango_coord)) for i in [0] + ids_clientes}

    with open(nombre_archivo, 'w') as f:
        f.write(f"{cant_clientes}\n")
        f.write(f"{costo_repartidor}\n")
        f.write(f"{dist_max}\n")
        f.write(f"{cant_refrigerados}\n")
        for r in refrigerados:
            f.write(f"{r}\n")
        f.write(f"{cant_exclusivos}\n")
        for e in exclusivos:
            f.write(f"{e}\n")

        nodos = [0] + ids_clientes
        for i in nodos:
            for j in nodos:
                if i < j and random.random() < porcentaje_conectividad:
                    xi, yi = coords[i]
                    xj, yj = coords[j]
                    dist = round(math.hypot(xi - xj, yi - yj))
                    costo = random.randint(1, 10)  # costo realista aleatorio
                    f.write(f"{i} {j} {dist} {costo}\n")

    print(f"Instancia generada y guardada en {nombre_archivo}")

# --------------------------
# 2. Leer grafo desde archivo
# --------------------------

def leer_grafo_completo(nombre_archivo):
    with open(nombre_archivo, 'r') as f:
        lineas = f.readlines()

    cant_clientes = int(lineas[0])
    cant_nodos = cant_clientes + 1
    cant_refrigerados = int(lineas[3])
    cant_exclusivos = int(lineas[4 + cant_refrigerados])

    header_lines = 5 + cant_refrigerados + 1 + cant_exclusivos
    encabezado = lineas[:header_lines]
    aristas = lineas[header_lines:]

    grafo = defaultdict(list)
    for linea in aristas:
        i, j, dist, costo = map(int, linea.strip().split())
        grafo[i].append((j, dist, costo))
        grafo[j].append((i, dist, costo))  # no dirigido

    return grafo, encabezado

# --------------------------
# 3. Dijkstra por costo
# --------------------------

def dijkstra_por_costo(grafo, origen, n):
    costos = [float('inf')] * n
    distancias = [float('inf')] * n
    costos[origen] = 0
    distancias[origen] = 0
    heap = [(0, 0, origen)]

    while heap:
        c_actual, d_actual, nodo = heapq.heappop(heap)
        if c_actual > costos[nodo]:
            continue
        for vecino, dist, cost in grafo[nodo]:
            nuevo_costo = c_actual + cost
            nueva_dist = d_actual + dist
            if nuevo_costo < costos[vecino]:
                costos[vecino] = nuevo_costo
                distancias[vecino] = nueva_dist
                heapq.heappush(heap, (nuevo_costo, nueva_dist, vecino))
    return costos, distancias

# --------------------------
# 4. Actualizar con distancias y costos mínimos
# --------------------------

def actualizar_con_costos_minimos(nombre_archivo, nuevo_archivo="instancia_actualizada.txt"):
    grafo, encabezado = leer_grafo_completo(nombre_archivo)
    nodos = list(grafo.keys())
    n = max(nodos) + 1

    resultados = {}
    for i in nodos:
        costos, distancias = dijkstra_por_costo(grafo, i, n)
        for j in nodos:
            if i < j and costos[j] < float('inf'):
                resultados[(i, j)] = (distancias[j], costos[j])

    with open(nuevo_archivo, 'w') as f:
        for linea in encabezado:
            f.write(linea)
        for (i, j), (dist, cost) in sorted(resultados.items()):
            f.write(f"{i} {j} {dist} {cost}\n")

    print(f"Grafo actualizado con distancias y costos mínimos guardado en {nuevo_archivo}")

# --------------------------
# 5. Ejecutar todo junto
# --------------------------

# Crear grafo y actualizarlo
generar_instancia_grande("instancia_inicial.txt")
actualizar_con_costos_minimos("instancia_inicial.txt", "instancia_final.txt")
