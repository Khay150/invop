import cplex

problem = cplex.Cplex()
problem.set_problem_type(cplex.Cplex.problem_type.LP)
problem.objective.set_sense(problem.objective.sense.maximize)

# Variables
problem.variables.add(names=["x1", "x2", "x3"], lb=[0, 0, 0])

# Función objetivo: 5.900 x1 + 2900 x2 + 1200 x3 
problem.objective.set_linear([("x1", 5900), ("x2", 3100), ("x3", 1200)])


# Restricciones
problem.linear_constraints.add(
    lin_expr=[
        [["x1", "x2", "x3"], [10, 5, 3]],
        [["x1", "x2", "x3"], [20, 10, 6]],
        [["x1"], [1]],
        [["x2"], [1]],
        [["x3"], [1]]
    ],
    senses=["L", "L", "L", "L", "L"],
    rhs=[38000, 80000, 1000, 3000, 7000]
)

# Resolver
problem.solve()

print("x1 =", problem.solution.get_values("x1"))
print("x2 =", problem.solution.get_values("x2"))
print("x3 =", problem.solution.get_values("x3"))
print("Z =", problem.solution.get_objective_value())

