from gurobipy import Model, GRB
import numpy as np

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
