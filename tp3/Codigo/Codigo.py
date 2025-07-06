from funciones import crear_instancia, leer_instancia, funcion_objetivo, weiszfeld_modificado, descenso_coordenado
import time

# crear_instancia(nombre_archivo="instancia5D-500.txt", n_dim=5, n_puntos=500, seed=42)

puntos, pesos = leer_instancia("instancia5D-500.txt")

# -----------------------------------------------
# Evaluar Algoritmo de Weiszfeld
# -----------------------------------------------

tiempo_inicio_weiszfeld = time.time()
solucion_weiszfeld, iteraciones_weiszfeld = weiszfeld_modificado(puntos, pesos)
tiempo_fin_weiszfeld = time.time()
tiempo_total_weiszfeld = tiempo_fin_weiszfeld - tiempo_inicio_weiszfeld
valor_en_funcion_objetivo_weiszfeld = funcion_objetivo(solucion_weiszfeld, puntos, pesos)


# -----------------------------------------------
# Evaluar Método Descenso Coordenado
# -----------------------------------------------

tiempo_inicio_des_coord = time.time()
solucion_des_coord, iteraciones_des_coord = descenso_coordenado(puntos, pesos)
tiempo_fin_des_coord = time.time()
tiempo_total_des_coord = tiempo_fin_des_coord - tiempo_inicio_des_coord
valor_en_funcion_objetivo_des_coord = funcion_objetivo(solucion_des_coord, puntos, pesos)


print("Valores Obtenidos Por el Algoritmo de Weiszfeld: \n")

print("Centro óptimo Weiszfeld:", solucion_weiszfeld)
print(f"Iteraciones Weiszfeld (Tiempo de Convergencia): {iteraciones_weiszfeld}")
print("Valor función objetivo Weiszfeld:", valor_en_funcion_objetivo_weiszfeld)
print(f"Tiempo de Ejecucion: {tiempo_total_weiszfeld}")

print("\n")

print("Valores Obtenidos Por el Método de Descenso Coordenado: \n")

print("Centro óptimo Descenso Coordenado:", solucion_des_coord)
print(f"Iteraciones Descenso Coordenado (Tiempo de Convergencia): {iteraciones_des_coord}")
print("Valor función objetivo Descenso Coordenado:", valor_en_funcion_objetivo_des_coord)
print(f"Tiempo de Ejecucion: {tiempo_total_des_coord}")