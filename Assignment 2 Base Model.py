import pandas as pd
from gurobipy import Model, GRB

# Load the dataset
df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Assignment 2/price_response.csv')

# Create a Gurobi model
model = Model('Maximize Revenue')

# Add price variables for each product
prices = model.addVars(df.index, name='price', lb=0)

# Define the objective function (total revenue)
revenue = sum((df.loc[i, 'Intercept'] + df.loc[i, 'Sensitivity'] * prices[i]) * prices[i] for i in df.index)
model.setObjective(revenue, GRB.MAXIMIZE)

# Add capacity constraints
for i in df.index:
    demand = df.loc[i, 'Intercept'] + df.loc[i, 'Sensitivity'] * prices[i]
    model.addConstr(demand <= df.loc[i, 'Capacity'], name=f'capacity_{i}')

# Optimize the model
model.optimize()

# Print the optimal prices and total revenue
if model.status == GRB.OPTIMAL:
    print("Optimal Prices:")
    for i in df.index:
        print(f"{df.loc[i, 'Product']}: ${prices[i].X:.2f}")
    print(f"Total Revenue: ${model.ObjVal:.2f}")
else:
    print("No optimal solution found.")
