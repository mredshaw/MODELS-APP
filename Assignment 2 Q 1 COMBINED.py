print("############################################################# PART A #############################################################")

from gurobipy import Model, GRB
import numpy as np
import pandas as pd

# Given parameters from the dataset
a1, b1 = 35234.54578551236, -45.89644971  # Basic version
a2, b2 = 37790.24083213697, -8.227794173  # Advanced version

# Create a new model
m = Model("TechEssentials Pricing")

# Add decision variables
p1 = m.addVar(name="p1", lb=0)  # Price for Basic version
p2 = m.addVar(name="p2", lb=0)  # Price for Advanced version

# Set the objective function to maximize revenue
m.setObjective(p1 * (a1 + b1 * p1) + p2 * (a2 + b2 * p2), GRB.MAXIMIZE)

# Add constraints
m.addConstr(a1 + b1 * p1 >= 0, "DemandNonNegativityBasic")
m.addConstr(a2 + b2 * p2 >= 0, "DemandNonNegativityAdvanced")
m.addConstr(p2 >= p1, "PriceOrdering")

# Optimize the model
m.optimize()

# Print the optimal prices
if m.status == GRB.OPTIMAL:
    print(f"Optimal Price for Basic Version (p1): ${p1.X:.2f}")
    print(f"Optimal Price for Advanced Version (p2): ${p2.X:.2f}")
else:
    print("No optimal solution found.")

print("############################################################# PART B #############################################################")
    
# Define the price response function coefficients for the two products
a1, b1 = 35234.54578551236, 45.89644971
a2, b2 = 37790.24083213697, 8.227794173

# Define the initial prices for both products
initial_prices = np.array([0, 0])

# Define the step size and stopping criterion for the gradient descent
step_size = 0.001
stopping_criterion = 1e-6

# Define the demand functions for the two products
def demand(p, a, b):
    return a - b * p

# Define the gradient of the objective function
def gradient(p):
    return np.array([a1 - 2 * b1 * p[0], a2 - 2 * b2 * p[1]])

# Initialize the prices
prices = initial_prices

# Start the projected gradient descent algorithm
while True:
    # Compute the gradient at the current prices
    grad = gradient(prices)
    
    # Take a step in the direction of the gradient
    new_prices = prices + step_size * grad
    
    # Define a quadratic model in Gurobi to project the prices onto the feasible set
    m = Model('Projection')
    
    # Add variables for the projected prices
    p1 = m.addVar(lb=0, name="p1")
    p2 = m.addVar(lb=0, name="p2")
    
    # Add the constraint that p2 should be higher than p1
    m.addConstr(p2 >= p1, "price_ordering")
    
    # Set the objective to minimize the distance to the new prices obtained from the gradient step
    m.setObjective((p1 - new_prices[0])*(p1 - new_prices[0]) +
                   (p2 - new_prices[1])*(p2 - new_prices[1]),
                   GRB.MINIMIZE)
    
    # Optimize the model
    m.optimize()
    
    # Extract the projected prices
    projected_prices = np.array([p1.X, p2.X])
    
    # Check the stopping criterion
    if np.linalg.norm(prices - projected_prices) < stopping_criterion:
        break
    
    # Update the prices
    prices = projected_prices

# Print the final prices
print(prices)


print("######################################################## PART C ###############################################################")

# Load the dataset

df = pd.read_csv('https://github.com/mredshaw/MODELS-APP/blob/main/price_response.csv')  # Change to your file's path

# Create a Gurobi model
model = Model('Maximize Revenue Within Line Constraints')

# Convert dataframe columns to arrays
intercepts = df['Intercept'].to_numpy()
sensitivities = df['Sensitivity'].to_numpy()
capacities = df['Capacity'].to_numpy()

# Add price variables for each product
prices = model.addVars(len(df), name='price', lb=0)

# Define the objective function (total revenue)
revenue = sum((intercepts[i] + sensitivities[i] * prices[i]) * prices[i] for i in range(len(df)))
model.setObjective(revenue, GRB.MAXIMIZE)

# Add capacity constraints
for i in range(len(df)):
    demand = intercepts[i] + sensitivities[i] * prices[i]
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



print("######################################################## PART D ###############################################################")
    

model = Model('Maximize Revenue Across Line Constraints')

# Convert dataframe columns to arrays
intercepts = df['Intercept'].to_numpy()
sensitivities = df['Sensitivity'].to_numpy()
capacities = df['Capacity'].to_numpy()

# Add price variables for each product
prices = model.addVars(len(df), name='price', lb=0)

# Define the objective function (total revenue)
revenue = sum((intercepts[i] + sensitivities[i] * prices[i]) * prices[i] for i in range(len(df)))
model.setObjective(revenue, GRB.MAXIMIZE)

# Add capacity constraints
for i in range(len(df)):
    demand = intercepts[i] + sensitivities[i] * prices[i]
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
