from gurobipy import Model, GRB
import numpy as np
import pandas as pd

# Define the price response function coefficients for the two products
df = pd.read_csv('https://raw.githubusercontent.com/mredshaw/MODELS-APP/main/Assignment%202/price_response.csv')  # Change to your file's path

intercepts = df['Intercept'].to_numpy()
sensitivities = abs(df['Sensitivity'].to_numpy())
capacities = df['Capacity'].to_numpy()

a1, a2, b1, b2 = intercepts[0], intercepts[1], sensitivities[0], sensitivities[1]

# Define the initial prices for both products
initial_prices = np.array([0, 0])

# Define the step size and stopping criterion for the gradient descent
step_size = 0.001
stopping_criterion = 1e-6

# Define the demand functions for the two products
def demand(p, a, b):
    return a + b * p

# Define the gradient of the objective function
def gradient(p):
    return np.array([a1 - 2 * b1 * p[0], a2 - 2 * b2 * p[1]])

# Initialize the prices
prices = initial_prices

# Create the Gurobi model and variables outside of the loop
m = Model('Projection')
m.setParam('OutputFlag', 0) # Suppress Gurobi output

p1 = m.addVar(lb=0, name="p1")
p2 = m.addVar(lb=0, name="p2")

m.addConstr(a1 - b1 * p1 >= 0, "DemandNonNegativityBasic")
m.addConstr(a2 - b2 * p2 >= 0, "DemandNonNegativityAdvanced")
m.addConstr(p2 - p1 >= 0.01, "PriceOrdering")

iteration_counter = 0

# List to store revenue at each iteration
revenues = []

# Start the projected gradient descent algorithm
while True:
    iteration_counter += 1  # Increment the counter
    # Compute the gradient at the current prices
    grad = gradient(prices)
    
    # Take a step in the direction of the gradient
    new_prices = prices + step_size * grad
    
    # Update the model with the new objective function
    m.setObjective((p1 - new_prices[0])*(p1 - new_prices[0]) +
                   (p2 - new_prices[1])*(p2 - new_prices[1]),
                   GRB.MINIMIZE)

    # Optimize the model
    m.optimize()
    
    # Extract the projected prices
    projected_prices = np.array([p1.X, p2.X])
    
    # Calculate and store the revenue at the current prices
    current_revenue = projected_prices[0] * (a1 - b1 * projected_prices[0]) + projected_prices[1] * (a2 - b2 * projected_prices[1])
    revenues.append(current_revenue)
    
    # Check the stopping criterion
    if np.linalg.norm(prices - projected_prices) < stopping_criterion:
        break
    
    # Update the prices
    prices = projected_prices
    if iteration_counter % 10 == 0:  # Print every 10 iterations to track progress
        print(f'Iteration {iteration_counter}: Prices = {prices}, Revenue = {current_revenue}')

# Print the final prices and revenue
print("\n")
print(f'The model ran {iteration_counter} iterations.')
print("Optimal prices found:", prices)
print("Optimal revenue:", revenues[-1])


