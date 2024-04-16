from gurobipy import GRB
import gurobipy as gb
import pandas as pd
import numpy as np
import math
import random
from gurobipy import Model, GRB, quicksum

# Initialize model
model = Model("CoffeeSupply")

# Constants and Data
price_preorder = 95
price_phil = 120
price_rosso = 105
price_monogram = 110
min_order_rosso = 70
min_order_monogram = 40
probabilities = [
    0.09, 0.12, 0.10, 0.05, 0.16,
    0.14, 0.03, 0.08, 0.05, 0.05,
    0.04, 0.03, 0.02, 0.01, 0.02,
    0.01
]
gallons_used = [
    90, 95, 100, 105, 110,
    115, 120, 125, 130, 135,
    140, 145, 150, 155, 160,
    165
]

# Decision Variables
x = model.addVar(vtype=GRB.CONTINUOUS, name="Preorder")
y_phil = model.addVars(len(probabilities), vtype=GRB.CONTINUOUS, name="Phil")
y_rosso = model.addVars(len(probabilities), vtype=GRB.CONTINUOUS, name="Rosso")
y_monogram = model.addVars(len(probabilities), vtype=GRB.CONTINUOUS, name="Monogram")
b_rosso = model.addVars(len(probabilities), vtype=GRB.BINARY, name="B_Rosso")
b_monogram = model.addVars(len(probabilities), vtype=GRB.BINARY, name="B_Monogram")

# Objective Function
model.setObjective(
    price_preorder * x +
    quicksum(probabilities[n] * (price_phil * y_phil[n] +
                                 price_rosso * y_rosso[n] +
                                 price_monogram * y_monogram[n])
             for n in range(len(probabilities))),
    GRB.MINIMIZE
)

# Constraints
for n in range(len(probabilities)):
    model.addConstr(x + y_phil[n] + y_rosso[n] + y_monogram[n] >= gallons_used[n], name=f"Demand_Fulfillment_{n}")
    model.addConstr(y_rosso[n] >= min_order_rosso * b_rosso[n], name=f"Min_Order_Rosso_{n}")
    model.addConstr(y_monogram[n] >= min_order_monogram * b_monogram[n], name=f"Min_Order_Monogram_{n}")

    # Additional constraints to avoid ordering below minimum if the binary variable is on
    model.addConstr(y_rosso[n] <= (max(gallons_used) - min_order_rosso) * b_rosso[n], name=f"Max_Order_Rosso_{n}")
    model.addConstr(y_monogram[n] <= (max(gallons_used) - min_order_monogram) * b_monogram[n], name=f"Max_Order_Monogram_{n}")

# Solve the model
model.optimize()

# Output the solution
if model.status == GRB.OPTIMAL:
    print(f"Optimal gallons to preorder: {x.X}")
    for n in range(len(probabilities)):
        print(f"Scenario {n+1}:")
        print(f"\tPhil: {y_phil[n].X} gallons")
        print(f"\tRosso: {y_rosso[n].X} gallons")
        print(f"\tMonogram: {y_monogram[n].X} gallons")
else:
    print("No optimal solution found")
