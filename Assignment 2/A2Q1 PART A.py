from gurobipy import Model, GRB
import numpy as np
import pandas as pd

# Given parameters from the dataset
df = pd.read_csv('https://raw.githubusercontent.com/mredshaw/MODELS-APP/main/Assignment%202/price_response.csv')  # Change to your file's path

intercepts = df['Intercept'].to_numpy()
sensitivities = abs(df['Sensitivity'].to_numpy())
capacities = df['Capacity'].to_numpy()

#Set the intercepts and sensitivities for the two products
a1, a2, b1, b2 = intercepts[0], intercepts[1], sensitivities[0], sensitivities[1]

# Create a new model
m = Model("TechEssentials Pricing")

# Add decision variables
p1 = m.addVar(name="p1", lb=0)  # Price for Basic version
p2 = m.addVar(name="p2", lb=0)  # Price for Advanced version

# Set the objective function to maximize revenue
m.setObjective(p1 * (a1 - b1 * p1) + p2 * (a2 - b2 * p2), GRB.MAXIMIZE)

# Add constraints
m.addConstr(a1 - b1 * p1 >= 0, "DemandNonNegativityBasic")
m.addConstr(a2 - b2 * p2 >= 0, "DemandNonNegativityAdvanced")
m.addConstr(p2 - p1 >= 0.01, "PriceOrdering")

# Optimize the model
m.optimize()

# Print the optimal prices
if m.status == GRB.OPTIMAL:
    print(f"Optimal Price for Basic Version (p1): ${p1.X:.2f}")
    print(f"Optimal Price for Advanced Version (p2): ${p2.X:.2f}")
    print(f"Total Revenue: ${m.ObjVal:.2f}")  # Print the objective value
else:
    print("No optimal solution found.")