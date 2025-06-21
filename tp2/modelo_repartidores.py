import sys
import cplex

TOLERANCE = 1e-6

class InstanciaRecorridoMixto:
    def __init__(self):
        self.cantidad_clientes = 0
        self.costo_repartidor = 0
        self.d_max = 0
        self.refrigerados = []
        self.exclusivos = []
        self.distancias = []        
        self.costos = []        

    def leer_datos(self, filename):
        with open(filename) as f:
            self.cantidad_clientes = int(f.readline())
            self.costo_repartidor = int(f.readline())
            self.d_max = int(f.readline())

            self.distancias = [[1e6 for _ in range(self.cantidad_clientes + 1)] for _ in range(self.cantidad_clientes + 1)]
            self.costos = [[1e6 for _ in range(self.cantidad_clientes + 1)] for _ in range(self.cantidad_clientes + 1)]

            cantidad_refrigerados = int(f.readline())
            self.refrigerados = [int(f.readline()) for _ in range(cantidad_refrigerados)]

            cantidad_exclusivos = int(f.readline())
            self.exclusivos = [int(f.readline()) for _ in range(cantidad_exclusivos)]

            for linea in f.readlines():
                i, j, dij, cij = map(int, linea.strip().split())
                self.distancias[i][j] = self.distancias[j][i] = dij
                self.costos[i][j] = self.costos[j][i] = cij


def cargar_instancia():
    nombre_archivo = "prueba.txt"
    instancia = InstanciaRecorridoMixto()
    instancia.leer_datos(nombre_archivo)
    return instancia


def agregar_variables(prob, instancia):
    nombres, obj, tipos, lb, ub = [], [], [], [], []
    
    n = instancia.cantidad_clientes
    N = list(range(n + 1)) # clientes + depósito (0)

    # Variables x_ij: indica si el camión va de i a j
    for i in N:
        for j in N:
            if i != j:
                nombres.append(f"x_{i}_{j}")
                obj.append(instancia.costos[i][j])
                tipos.append("B")
                lb.append(0)
                ub.append(1)

    # Variables z_ij: indica si el repartidor va de i a j
    # Variables a_ij: indica si la distancia entre i y j <= d_max
    for i in N:
        for j in range(1, n + 1):
            if i != j:
                nombres.append(f"z_{i}_{j}")
                obj.append(instancia.costo_repartidor)
                tipos.append("B")
                lb.append(0)
                ub.append(1)

                nombres.append(f"a_{i}_{j}")
                obj.append(0)
                tipos.append("B")
                lb.append(0)
                ub.append(1)

    # Variables u_i: posición del cliente i en el circuito del camión (para eliminación de subtours)
    for i in range(1, n + 1):
        nombres.append(f"u_{i}")
        obj.append(0)
        tipos.append("I")
        lb.append(1)
        ub.append(n)

    # u_0 = 0 (depósito)
    nombres.append("u_0")
    obj.append(0)
    tipos.append("I")
    lb.append(0)
    ub.append(0)

    # Variables w_i: indica si el nodo i es una parada del camión desde la que parte un repartidor
    for i in N:
        nombres.append(f"w_{i}")
        obj.append(0)
        tipos.append("B")
        lb.append(0)
        ub.append(1)

    prob.variables.add(obj=obj, lb=lb, ub=ub, types=tipos, names=nombres)

def agregar_restricciones(prob, instancia):
    n = instancia.cantidad_clientes
    N = list(range(n + 1))
    M1 = M2 = 1e6

    def var(name):
        return prob.variables.get_indices(name)

    # (7) del depósito se va a algún cliente
    prob.linear_constraints.add(
        lin_expr=[cplex.SparsePair(
            ind=[var(f"x_0_{j}") for j in range(1, n + 1)],
            val=[1]*n
        )],
        senses=["E"],
        rhs=[1],
        names=["salida_deposito"]
    )

    # (8) de algún cliente se llega al depósito
    prob.linear_constraints.add(
        lin_expr=[cplex.SparsePair(
            ind=[var(f"x_{i}_0") for i in range(1, n + 1)],
            val=[1]*n
        )],
        senses=["E"],
        rhs=[1],
        names=["llegada_deposito"]
    )



    

    # (9) A cada cliente se debe llegar exactamente una vez
    for j in range(1, n + 1):
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair([f"x_{i}_{j}" for i in N if i != j], [1]*n)],
            senses=["E"], rhs=[1], names=[f"llegada_{j}"]
        )

    # (10) De cada cliente se debe salir exactamente una vez
    for i in range(1, n + 1):
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair([f"x_{i}_{j}" for j in N if j != i], [1]*n)],
            senses=["E"], rhs=[1], names=[f"salida_{i}"]
        )

    # (11) Eliminación de subtours (restricción MTZ)
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i != j:
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair([f"u_{i}", f"u_{j}", f"x_{i}_{j}"], [1, -1, n])],
                    senses=["L"], rhs=[n - 1], names=[f"mtz_{i}_{j}"]
                )

    # Clientes exclusivos deben ser visitados solo por el camión
    for j in instancia.exclusivos:
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair([f"x_{i}_{j}" for i in N if i != j], [1]*n)],
            senses=["E"], rhs=[1], names=[f"exclusivo_{j}"]
        )

    # Restricción de distancia: se reemplaza la desigualdad con las dos nuevas
    for i in N:
        for j in range(1, n + 1):
            if i != j:
                dij = instancia.distancias[i][j]
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair([f"a_{i}_{j}"], [M1])],
                    senses=["G"], rhs=[dij - instancia.d_max], names=[f"dentro_rango_{i}_{j}"]
                )
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair([f"a_{i}_{j}"], [-M2])],
                    senses=["G"], rhs=[instancia.d_max + 1 - dij], names=[f"fuera_rango_{i}_{j}"]
                )

    # Solo una entrega refrigerada por repartidor
    for i in N:
        refrigerados_i = [j for j in instancia.refrigerados if j != i]
        if refrigerados_i:
            prob.linear_constraints.add(
                lin_expr=[cplex.SparsePair([f"z_{i}_{j}" for j in refrigerados_i] + [f"w_{i}"], [1]*len(refrigerados_i) + [-1])],
                senses=["L"], rhs=[0], names=[f"refrigerados_uno_{i}"]
            )

    # z_ij solo puede usarse si hay repartidor en i y no se usa x_ij a la vez
    for i in N:
        for j in range(1, n + 1):
            if i != j:
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair([f"z_{i}_{j}", f"w_{i}"], [1, -1])],
                    senses=["L"], rhs=[0], names=[f"z_implica_w_{i}_{j}"]
                )
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair([f"z_{i}_{j}", f"x_{i}_{j}"], [1, 1])],
                    senses=["L"], rhs=[1], names=[f"z_excluye_x_{i}_{j}"]
                )

    # Cada cliente debe ser atendido por el camión o repartidor
    for j in range(1, n + 1):
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(
                [f"z_{i}_{j}" for i in N if i != j] + [f"x_{i}_{j}" for i in N if i != j],
                [1]*n + [1]*n
            )],
            senses=["E"], rhs=[1], names=[f"atencion_{j}"]
        )

    # Restricción deseable: repartidor debe hacer al menos 4 y como máximo (n-1) entregas
    for i in N:
        z_vars = [f"z_{i}_{j}" for j in range(1, n + 1) if i != j]
        if z_vars:
            prob.linear_constraints.add(
                lin_expr=[cplex.SparsePair(z_vars + [f"w_{i}"], [1]*len(z_vars) + [-4])],
                senses=["G"], rhs=[0], names=[f"min_entregas_{i}"]
            )
            prob.linear_constraints.add(
                lin_expr=[cplex.SparsePair(z_vars + [f"w_{i}"], [1]*len(z_vars) + [-(n-1)])],
                senses=["L"], rhs=[0], names=[f"max_entregas_{i}"]
            )

def armar_lp(prob, instancia):
    agregar_variables(prob, instancia)
    agregar_restricciones(prob, instancia)
    prob.objective.set_sense(prob.objective.sense.minimize)
    prob.write("recorridoMixto.lp")

def resolver_lp(prob):
    prob.parameters.timelimit.set(60)
    prob.solve()

def mostrar_solucion(prob, instancia):
    status = prob.solution.get_status_string()
    valor_obj = prob.solution.get_objective_value()
    print(f"Función objetivo: {valor_obj} ({status})")

    valores = prob.solution.get_values()
    nombres = prob.variables.get_names()
    print("\nRutas seleccionadas:")
    for nombre, valor in zip(nombres, valores):
        if valor > TOLERANCE and (nombre.startswith("x_") or nombre.startswith("z_")):
            print(f"{nombre} = {valor}")

def main():
    instancia = cargar_instancia()
    prob = cplex.Cplex()
    armar_lp(prob, instancia)
    resolver_lp(prob)
    mostrar_solucion(prob, instancia)

if __name__ == '__main__':
    main()
