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
            row = list(map(int, linea.strip().split()))
            i, j, dij, cij = row
            self.distancias[i][j] = dij
            self.distancias[j][i] = dij
            self.costos[i][j] = cij
            self.costos[j][i] = cij

        f.close()

def cargar_instancia():
    nombre_archivo = "prueba3.txt"
    instancia = InstanciaRecorridoMixto()
    instancia.leer_datos(nombre_archivo)
    return instancia

def agregar_variables(prob, instancia):
    nombres, obj, tipos, lb, ub = [], [], [], [], []

    n = instancia.cantidad_clientes
    N = list(range(n + 1))  # clientes + depósito (0)

    # x_ij
    for i in N:
        for j in N:
            if i != j:
                nombres.append(f"x_{i}_{j}")
                obj.append(instancia.costos[i][j])
                tipos.append("B")
                lb.append(0)
                ub.append(1)

    # z_ij
    for i in N:
        for j in N:
            if i != j:
                nombres.append(f"z_{i}_{j}")
                obj.append(instancia.costo_repartidor)
                tipos.append("B")
                lb.append(0)
                ub.append(1)

    # a_ij
    for i in N:
        for j in N:
            if i != j:
                nombres.append(f"a_{i}_{j}")
                obj.append(0)
                tipos.append("B")
                lb.append(0)
                ub.append(1)

    # w_i
    for i in N:
        nombres.append(f"w_{i}")
        obj.append(0)
        tipos.append("B")
        lb.append(0)
        ub.append(1)

    # u_i (MTZ)
    for i in range(1, n + 1):
        nombres.append(f"u_{i}")
        obj.append(0)
        tipos.append("I")
        lb.append(1)
        ub.append(n)

    # u_0 = 0
    nombres.append("u_0")
    obj.append(0)
    tipos.append("I")
    lb.append(0)
    ub.append(0)

    prob.variables.add(obj=obj, lb=lb, ub=ub, types=tipos, names=nombres)

def agregar_restricciones(prob, instancia):
    n = instancia.cantidad_clientes
    N = list(range(n + 1))
    var = lambda name: prob.variables.get_indices(name)
    M1, M2, M = 1e6, 1e6, n

    # (1)
    for i in N:
        z_ij = [var(f"z_{i}_{j}") for j in N if j != i]
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=z_ij + [var(f"w_{i}")], val=[1]*len(z_ij)+[-4])],
            senses=["G"], rhs=[0], names=[f"min_z_vs_w_{i}"]
        )
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=z_ij + [var(f"w_{i}")], val=[1]*len(z_ij)+[-(n - 1)])],
            senses=["L"], rhs=[0], names=[f"max_z_vs_w_{i}"]
        )

    # (2)
    for j in instancia.exclusivos:
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[var(f"x_{i}_{j}") for i in N if i != j], val=[1] * n)],
            senses=["E"], rhs=[1], names=[f"solo_camion_exclusivo_{j}"]
        )

    # (3)
    for i in N:
        for j in N:
            if i != j:
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(ind=[var(f"z_{i}_{j}"), var(f"a_{i}_{j}")], val=[1, -1])],
                    senses=["L"], rhs=[0], names=[f"z_leq_a_{i}_{j}"]
                )

    # (4)
    for i in N:
        z_ij = [var(f"z_{i}_{j}") for j in instancia.refrigerados if i != j]
        if z_ij:
            prob.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=z_ij, val=[1]*len(z_ij))],
                senses=["L"], rhs=[1], names=[f"refrigerado_uno_{i}"]
            )

    # (5) y (6)
    for i in N:
        for j in N:
            if i != j:
                # Dmax >= d_ij - M(1 - a_ij)
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(
                        ind=[var(f"a_{i}_{j}")],
                        val=[M1]
                    )],
                    senses=["L"],
                    rhs=[instancia.d_max - instancia.distancias[i][j] + M1],
                    names=[f"distmax1_{i}_{j}"]
                )

                # d_ij >= Dmax + 1 - M a_ij
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(
                        ind=[var(f"a_{i}_{j}")],
                        val=[M2]
                    )],
                    senses=["G"],
                    rhs=[-instancia.distancias[i][j] + instancia.d_max + 1],
                    names=[f"distmax2_{i}_{j}"]
                )

    # (7)
    for j in range(1, n + 1):
        x_ij = [var(f"x_{i}_{j}") for i in N if i != j]
        z_ij = [var(f"z_{i}_{j}") for i in N if i != j]
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=x_ij + z_ij, val=[1]*(len(x_ij)+len(z_ij)))],
            senses=["E"], rhs=[1], names=[f"atencion_{j}"]
        )

    # (8)
    for i in range(1, n + 1):
        entrada = [var(f"x_{j}_{i}") for j in N if j != i]
        salida = [var(f"x_{i}_{j}") for j in N if j != i]
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=entrada + salida, val=[1]*len(entrada) + [-1]*len(salida))],
            senses=["E"], rhs=[0], names=[f"flujo_camion_{i}"]
        )

    # (9)
    prob.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=[var(f"x_0_{j}") for j in range(1, n + 1)], val=[1]*n)],
        senses=["E"], rhs=[1], names=["salida_deposito"]
    )

    # (10)
    prob.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=[var(f"x_{i}_0") for i in range(1, n + 1)], val=[1]*n)],
        senses=["E"], rhs=[1], names=["llegada_deposito"]
    )

    # (11)
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i != j:
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(
                        ind=[var(f"u_{i}"), var(f"u_{j}"), var(f"x_{i}_{j}")],
                        val=[1, -1, n]
                    )],
                    senses=["L"], rhs=[n - 1], names=[f"mtz_{i}_{j}"]
                )

    # (12)
    prob.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=[var("u_0")], val=[1])],
        senses=["E"], rhs=[0], names=["u0_igual_cero"]
    )

    # (13)
    for i in range(1, n + 1):
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[var(f"u_{i}")], val=[1])],
            senses=["G"], rhs=[1], names=[f"u_{i}_min"]
        )
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[var(f"u_{i}")], val=[1])],
            senses=["L"], rhs=[n], names=[f"u_{i}_max"]
        )

    # (14)
    prob.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=[var("w_0")], val=[1])],
        senses=["E"], rhs=[0], names=["w0_cero"]
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

    print("\nVariables activas:")
    for nombre, valor in zip(nombres, valores):
        if valor > TOLERANCE:
            print(f"{nombre} = {valor}")

def main():
    instancia = cargar_instancia()
    prob = cplex.Cplex()
    armar_lp(prob, instancia)
    resolver_lp(prob)
    mostrar_solucion(prob, instancia)

if __name__ == '__main__':
    main()
