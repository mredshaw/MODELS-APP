import pandas as pd
from gurobipy import Model, GRB

# Load the dataset
df = pd.read_csv('https://raw.githubusercontent.com/mredshaw/MODELS-APP/main/Assignment%202/price_response.csv')  # Change to your file's path

# Create a Gurobi model
model = Model('Maximize Revenue Across Line Constraints')

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


# Add constraints for price ordering across product lines for the same version
model.addConstr(prices[3] - prices[0]>= 0.01, name='price_order_basic_1')  # Product 1 Basic must be priced at least $0.01 lower than Product 2 Basic
model.addConstr(prices[6] - prices[3]>= 0.01, name='price_order_basic_2')  # Product 2 Basic must be priced at least $0.01 lower than Product 3 Basic
model.addConstr(prices[4] - prices[1]>= 0.01, name='price_order_advanced_1')  # Product 1 Advanced must be priced at least $0.01 lower than Product 2 Advanced
model.addConstr(prices[7] - prices[4]>= 0.01, name='price_order_advanced_2')  # Product 2 Advanced must be priced at least $0.01 lower than Product 3 Advanced
model.addConstr(prices[5] - prices[2]>= 0.01, name='price_order_premium_1')  # Product 1 Premium must be priced at least $0.01 lower than Product 2 Premium
model.addConstr(prices[8] - prices[5]>= 0.01, name='price_order_premium_2')  # Product 2 Premium must be priced at least $0.01 lower than Product 3 Premium

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