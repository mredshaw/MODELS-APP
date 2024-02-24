import pandas as pd
from gurobipy import Model, GRB

# Load the dataset
df = pd.read_csv('https://raw.githubusercontent.com/mredshaw/MODELS-APP/main/Assignment%202/price_response.csv')  # Change to your file's path

# Create a Gurobi model
model = Model('Maximize Revenue Within Line Constraints')

# Convert dataframe columns to arrays
intercepts = df['Intercept'].to_numpy()
sensitivities = abs(df['Sensitivity'].to_numpy())
capacities = df['Capacity'].to_numpy()

# Add price variables for each product
prices = model.addVars(len(df), name='price', lb=0)

# Define the objective function (total revenue)
revenue = sum((intercepts[i] - sensitivities[i] * prices[i]) * prices[i] for i in range(len(df)))
model.setObjective(revenue, GRB.MAXIMIZE)

# Add capacity constraints
for i in range(len(df)):
    demand = intercepts[i] - sensitivities[i] * prices[i]
    model.addConstr(demand <= capacities[i], name=f'capacity_{i}')


#Add constraints for price ordering within each product line
num_products_per_line = 3
for i in range(0, len(df), num_products_per_line):
    model.addConstr(prices[i+1] - prices[i] >= 0.01, name=f'price_order_{i}_basic_advanced')
    model.addConstr(prices[i+2] - prices[i+1] >= 0.01, name=f'price_order_{i}_advanced_premium')


# Optimize the model
model.optimize()

# Print the optimal prices and total revenue
if model.status == GRB.OPTIMAL:
    print("Optimal Prices:")
    for i in range(len(df)):
        print(f"{df.loc[i, 'Product']}: ${prices[i].X:.2f}")
    print(f"Total Revenue: ${model.ObjVal:.2f}")
else:
    print("No optimal solution found.")