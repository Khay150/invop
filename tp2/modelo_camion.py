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

    def leer_datos(self,filename):
        f = open(filename)

        self.cantidad_clientes = int(f.readline())
        self.costo_repartidor = int(f.readline())
        self.d_max = int(f.readline())

        self.distancias = [[1e6 for _ in range(self.cantidad_clientes + 1)] for _ in range(self.cantidad_clientes + 1)]
        self.costos = [[1e6 for _ in range(self.cantidad_clientes + 1)] for _ in range(self.cantidad_clientes + 1)]

        cantidad_refrigerados = int(f.readline())
        for _ in range(cantidad_refrigerados):
            self.refrigerados.append(int(f.readline()))

        cantidad_exclusivos = int(f.readline())
        for _ in range(cantidad_exclusivos):
            self.exclusivos.append(int(f.readline()))

        for linea in f.readlines():
            row = list(map(int,linea.strip().split()))
            i, j, dij, cij = row
            self.distancias[i][j] = dij
            self.distancias[j][i] = dij
            self.costos[i][j] = cij
            self.costos[j][i] = cij

        f.close()


def cargar_instancia():
    nombre_archivo = "prueba2.txt"
    instancia = InstanciaRecorridoMixto()
    instancia.leer_datos(nombre_archivo)
    return instancia


def agregar_variables(prob, instancia):
    nombres = []
    obj = []
    tipos = []
    lb = []
    ub = []

    n = instancia.cantidad_clientes
    N = list(range(n + 1))  # clientes + depósito (0)

    # Variables x_ij
    for i in N:
        for j in N:
            if i != j:
                nombres.append(f"x_{i}_{j}")
                obj.append(instancia.costos[i][j])
                tipos.append("B")
                lb.append(0)
                ub.append(1)

    # Variables y_i
    for i in N:
        nombres.append(f"y_{i}")
        obj.append(0)
        tipos.append("B")
        lb.append(0)
        ub.append(1)

    # Variables z_ij
    for i in N:
        for j in range(1, n + 1):
            if i != j:
                nombres.append(f"z_{i}_{j}")
                obj.append(instancia.costo_repartidor)
                tipos.append("B")
                lb.append(0)
                ub.append(1)

    # Variables u_i (para MTZ)
    for i in range(1, n + 1):
        nombres.append(f"u_{i}")
        obj.append(0)
        tipos.append("C")
        lb.append(1)
        ub.append(n)

    # u_0 = 0
    nombres.append("u_0")
    obj.append(0)
    tipos.append("C")
    lb.append(0)
    ub.append(0)

    prob.variables.add(obj=obj, lb=lb, ub=ub, types=tipos, names=nombres)


def agregar_restricciones(prob, instancia):
    n = instancia.cantidad_clientes
    N = list(range(n + 1))  # clientes + depósito (0)

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

    # (9) a todo cliente se debe llegar
    for j in range(1, n + 1):
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(
                ind=[var(f"x_{i}_{j}") for i in N if i != j],
                val=[1]*(n)
            )],
            senses=["E"],
            rhs=[1],
            names=[f"llegada_{j}"]
        )

    # (10) de todo cliente se debe salir
    for i in range(1, n + 1):
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(
                ind=[var(f"x_{i}_{j}") for j in N if j != i],
                val=[1]*(n)
            )],
            senses=["E"],
            rhs=[1],
            names=[f"salida_{i}"]
        )

    # (11) Eliminación de subtours (MTZ)
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i != j:
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(
                        ind=[f"u_{i}", f"u_{j}", f"x_{i}_{j}"],
                        val=[1, -1, n]
                    )],
                    senses=["L"],
                    rhs=[n - 1],
                    names=[f"mtz_{i}_{j}"]
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
        if valor > TOLERANCE and nombre.startswith("x_"):
            print(f"{nombre} = {valor}")


def main():
    instancia = cargar_instancia()
    prob = cplex.Cplex()
    armar_lp(prob, instancia)
    resolver_lp(prob)
    mostrar_solucion(prob, instancia)

if __name__ == '__main__':
    main()
