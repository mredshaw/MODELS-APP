from gurobipy import Model, GRB
import numpy as np
import pandas as pd

# Given parameters from the dataset
a1, b1 = 35234.54578551236, 45.89644971  # Basic version
a2, b2 = 37790.24083213697, 8.227794173  # Advanced version

# Create a new model
m = Model("TechEssentials Pricing")

# Add decision variables
p1 = m.addVar(name="p1", lb=0)  # Price for Basic version
p2 = m.addVar(name="p2", lb=0)  # Price for Advanced version

# Set the objective function to maximize revenue
m.setObjective(p1 * (a1 - b1 * p1) + p2 * (a2 - b2 * p2), GRB.MAXIMIZE)

# Add constraints
m.addConstr(a1 + b1 * p1 >= 0, "DemandNonNegativityBasic")
m.addConstr(a2 + b2 * p2 >= 0, "DemandNonNegativityAdvanced")
m.addConstr(p2 >= p1, "PriceOrdering")
m.addConstr(a1 >=0, "BasicDemandNonNegativity")
m.addConstr(a2 >=0, "AdvancedDemandNonNegativity")
m.addConstr(b1 >=0, "BasicSlopeNonNegativity")
m.addConstr(b2 >=0, "AdvancedSlopeNonNegativity")

# Optimize the model
m.optimize()

# Print the optimal prices
if m.status == GRB.OPTIMAL:
    print(f"Optimal Price for Basic Version (p1): ${p1.X:.2f}")
    print(f"Optimal Price for Advanced Version (p2): ${p2.X:.2f}")
    print(f"Total Revenue: ${m.ObjVal:.2f}")  # Print the objective value
else:
    print("No optimal solution found.")