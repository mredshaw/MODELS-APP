from gurobipy import GRB
import gurobipy as gb
import pandas as pd
import numpy as np

# Create the model
model = gb.Model("Vaccine_Transportation")

# Create the a single class of decision variables where
# From = {Billy} and To = {29 sites}.
x = model.addVars(29, lb=0, vtype=GRB.CONTINUOUS, name="Billy Shipping")
# From = {Pearson} and To = {29 sites}.
y = model.addVars(29, lb=0, vtype=GRB.CONTINUOUS, name="Pearson Shipping")


# Objective function
Billy_Bishop_Toronto_City_Airport_costs = [0.05, 0.05, 0.05, 0.05, 0.05, 0.06, 0.06, 0.06, 0.06, 0.06, 0.07, 0.07, 0.07, 0.07, 0.07, 0.08, 0.08, 0.08, 0.08, 0.08, 0.09, 0.09, 0.09, 0.09, 0.09, 0.1, 0.1, 0.1, 0.1]
Toronto_Pearson_Airport_costs = [0.08, 0.08, 0.08, 0.08, 0.08, 0.05, 0.05, 0.05, 0.05, 0.05, 0.09, 0.09, 0.09, 0.09, 0.09, 0.1, 0.1, 0.1, 0.1, 0.1, 0.07, 0.07, 0.07, 0.07, 0.07, 0.06, 0.06, 0.06, 0.06]


#Set Objectives
Billy_objective = gb.quicksum(Billy_Bishop_Toronto_City_Airport_costs[j] * x[j] for j in range(29))
Pearson_objective = gb.quicksum(Toronto_Pearson_Airport_costs[j] * y[j] for j in range(29))
model.setObjective(Billy_objective + Pearson_objective, GRB.MINIMIZE)

# Constraints

# Difference constraint for sites 1-5
model.addConstr(gb.quicksum(x[j] for j in range(5)) - gb.quicksum(y[j] for j in range(5)) <= 4800, name="4800 constraint")
model.addConstr(gb.quicksum(y[j] for j in range(5)) - gb.quicksum(x[j] for j in range(5)) <= 4800, name="4800 constraint negative")


# Pearson to sites 21-25 constraint
model.addConstr(gb.quicksum(y[j] for j in range(20,25)) <= 8 * (gb.quicksum(x[j] for j in range(10,15))), name="Second constraint")


# Billy Bishop to sites 26-29 constraint
model.addConstr(gb.quicksum(x[j] for j in range(25,29)) >= 0.8 * (gb.quicksum(y[j] for j in range(15,20))), name="Third constraint")

# Supply constraints
model.addConstr(gb.quicksum(x[j] for j in range(29)) == 100000, "Billy Supply Constraint")
model.addConstr(gb.quicksum(y[j] for j in range(29)) == 250000, "Pearson Supply Constraint")


#Hosipital Constraint
# 50000 = 7x + 22x/4
# x = 4000
# 4000 per day, 7 days = 28000 per week
for j in range(7):
    model.addConstr(x[j] + y[j] <= 28000, f"Hospital Constraint_{j}")

# 50000 = 4*7x + 22x
# x = 1000
# 1000 per day, 7 days = 7000 per week
for j in range(7,29):
    model.addConstr(x[j] + y[j] <= 7000, f"Non-Hospital Constraint_{j}")

# Optimize the model
model.optimize()

# Print the decision variables
print(model.printAttr('X'))
print(model.ObjVal)


#Print Shadow Prices
print(f"-"*50)
for constr in model.getConstrs():
        print(f"Constraint: {constr.ConstrName}, Shadow Price: {constr.Pi}")

