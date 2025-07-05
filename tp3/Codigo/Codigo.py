from funciones import crear_instancia, leer_instancia, weiszfeld_modificado
import time

# crear_instancia(nombre_archivo="instancia5D-500.txt", n_dim=5, n_puntos=500, seed=42)

puntos, pesos = leer_instancia("instancia5D.txt")

tiempo_inicio = time.time()
solucion, iteraciones = weiszfeld_modificado(puntos, pesos)
tiempo_fin = time.time()

tiempo_total = tiempo_fin - tiempo_inicio


print("Centro óptimo:", solucion)
print(f"Iteraciones (Tiempo de Convergencia): {iteraciones}")
print(f"Tiempo de Ejecucion: {tiempo_total:.6f} segundos")


