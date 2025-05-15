import cplex

problem = cplex.Cplex()
problem.set_problem_type(cplex.Cplex.problem_type.LP)
problem.objective.set_sense(problem.objective.sense.minimize)

# Variables
problem.variables.add(names=["y1", "y2", "y3", "y4", "y5"], lb=[0, 0, 0, 0, 0])

# Función objetivo: 5.900 x1 + 2900 x2 + 1200 x3 
problem.objective.set_linear([("y1", 38000), ("y2", 80000), ("y3", 1000), ("y4", 3000), ("y5", 7000)])


# Restricciones
problem.linear_constraints.add(
    lin_expr=[
        [["y1", "y2", "y3"], [10, 20, 1]],
        [["y1", "y2", "y4"], [5, 10, 1]],
        [["y1", "y2", "y5"], [3, 6, 1]],
    ],
    senses=["G", "G", "G"],
    rhs=[5900, 2900, 1200]
)

# Resolver
problem.solve()

print("y1 =", problem.solution.get_values("y1"))
print("y2 =", problem.solution.get_values("y2"))
print("y3 =", problem.solution.get_values("y3"))
print("y4 =", problem.solution.get_values("y4"))
print("y5 =", problem.solution.get_values("y5"))
print("Z =", problem.solution.get_objective_value())

