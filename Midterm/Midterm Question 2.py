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
e = model.addVars(N, lb=0, vtype=GRB.CONTINUOUS, name="e")
z = model.addVars(N, lb=0, vtype=GRB.CONTINUOUS, name="z")  # New variable for square root term

# Objective function
model.setObjective(gp.quicksum(2 * z[i] for i in range(N)), GRB.MAXIMIZE)

# Constraints
# Budget Constraint
model.addConstr(gp.quicksum(a[i] for i in range(N)) <= budget, "Budget")

# Square root term constraint
for i in range(N):
    model.addConstr(z[i] * z[i] <= e[i] * beta[i] * a[i], f"SqrtConstraint_{i}")

for i in range(N):
    model.addConstr(e[i] * beta[i] * a[i] == z[i] * z[i], f"EffortLevel_{i}")



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

