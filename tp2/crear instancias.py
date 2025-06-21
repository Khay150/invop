import random
import math

def generar_instancia_grande(nombre_archivo, cant_clientes=500, costo_repartidor=5, dist_max=15,
                            cant_refrigerados=20, cant_exclusivos=30, porcentaje_conectividad=0.01, rango_coord=1000):

    ids_clientes = list(range(1, cant_clientes + 1))

    # Seleccionar refrigerados y exclusivos sin solapamiento
    refrigerados = sorted(random.sample(ids_clientes, cant_refrigerados))
    restantes = list(set(ids_clientes) - set(refrigerados))
    exclusivos = sorted(random.sample(restantes, cant_exclusivos))

    # Coordenadas para depósito (0) y clientes
    coords = {i: (random.randint(0, rango_coord), random.randint(0, rango_coord)) for i in [0] + ids_clientes}

    with open(nombre_archivo, 'w') as f:
        # Primeras líneas
        f.write(f"{cant_clientes}\n")
        f.write(f"{costo_repartidor}\n")
        f.write(f"{dist_max}\n")
        f.write(f"{cant_refrigerados}\n")
        for r in refrigerados:
            f.write(f"{r}\n")
        f.write(f"{cant_exclusivos}\n")
        for e in exclusivos:
            f.write(f"{e}\n")

        # Distancias y costos: para no generar demasiados, pongo un porcentaje de conectividad
        nodos = [0] + ids_clientes
        for i in nodos:
            for j in nodos:
                if i < j and random.random() < porcentaje_conectividad:
                    xi, yi = coords[i]
                    xj, yj = coords[j]
                    dist = round(math.hypot(xi - xj, yi - yj))
                    costo = dist  # puede ajustarse si querés otro costo
                    f.write(f"{i} {j} {dist} {costo}\n")

    print(f"Instancia guardada en {nombre_archivo}")

# Ejemplo de uso:
generar_instancia_grande("Prueba_500C.txt")
