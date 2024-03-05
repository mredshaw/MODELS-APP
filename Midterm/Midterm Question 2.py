import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Load the data
df = pd.read_csv('/Users/mikeredshaw/Downloads/non_profits.csv')

# Create lists for alpha and beta values
alpha = df['alpha_i'].tolist()
beta = df['beta_i'].tolist()

budget = 50000000

# Create a new model
model = gp.Model('NonprofitFunding')

# Number of nonprofits
N = len(df)

# Decision variables
a = model.addVars(N, lb=0, vtype=GRB.CONTINUOUS, name="a")
x = model.addVars(N, lb=0, vtype=GRB.CONTINUOUS, name="x")  # Variable for fractional exponent

# Objective function
model.setObjective(gp.quicksum(2 * x[i] for i in range(N)), GRB.MAXIMIZE)

# Constraints
# Budget Constraint
model.addConstr(gp.quicksum(a[i] for i in range(N)) <= budget, "Budget")


# Power constraint using addGenConstrPow()
for i in range(N):
    model.addGenConstrPow(a[i], x[i], 2.0/3.0, f"PowConstraint_{i}")


# Optimize the model
model.optimize()

# Check the optimization status
if model.Status == GRB.OPTIMAL:
    print("Optimal solution found.")
    # Print the decision variables
    for v in model.getVars():
        print(f"{v.varName} = {v.x}")
    print(f"Objective Value: {model.ObjVal}")
elif model.Status == GRB.INFEASIBLE:
    print("Model is infeasible.")
    # Compute and print the IIS (Irreducible Inconsistent Subsystem)
    model.computeIIS()
    model.write("model.ilp")
    print("IIS written to file 'model.ilp'")
elif model.Status == GRB.UNBOUNDED:
    print("Model is unbounded.")
else:
    print(f"Optimization was stopped with status {model.Status}")


print(f"Number of constraints: {model.NumConstrs}") 
print(f"Number of decision variables: {model.NumVars}")
# Sum of decision variables
decision_variable_sum = sum(v.x for v in model.getVars())
print(f"Sum of decision variables: {decision_variable_sum}")
nonzero_decision_variables = sum(1 for v in model.getVars() if v.x != 0)
print(f"Number of nonzero decision variables: {nonzero_decision_variables}")

print(f"Number of non-zero decision variables for 'a': {sum(1 for v in model.getVars() if v.varName.startswith('a') and v.x != 0)}")




