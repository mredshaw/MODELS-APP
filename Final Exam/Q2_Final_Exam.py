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

big_M = max(gallons_used)
# Decision Variables
x = model.addVar(vtype=GRB.CONTINUOUS, name="Preorder")
y_phil = model.addVars(len(probabilities), vtype=GRB.CONTINUOUS, name="Phil")
y_rosso = model.addVars(len(probabilities), vtype=GRB.CONTINUOUS, name="Rosso")
y_monogram = model.addVars(len(probabilities), vtype=GRB.CONTINUOUS, name="Monogram")
b_rosso = model.addVars(len(probabilities), vtype=GRB.BINARY, name="B_Rosso") #Set to ensure minimum order is satisfied
b_monogram = model.addVars(len(probabilities), vtype=GRB.BINARY, name="B_Monogram") #Set to ensure minimum order is satisfied

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
    model.addConstr(y_rosso[n] <= big_M * b_rosso[n], name=f"Max_Order_Rosso_{n}")
    model.addConstr(y_monogram[n] <= big_M * b_monogram[n], name=f"Max_Order_Monogram_{n}")


# Solve the model
model.optimize()


if model.status == GRB.OPTIMAL:
    optimal_cost = model.ObjVal
    print("Optimal Cost:", optimal_cost)
else:
    print("Model is infeasible! No optimal cost found.")
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

num_decision_vars = model.NumVars
print("Minimum number of decision variables:", num_decision_vars)






# Define a function to run the optimization for different pre-order prices
def find_break_even_preorder_price(low_price, high_price, increment):
    current_price = low_price
    while current_price <= high_price:
        # Set the pre-order price
        price_preorder = current_price

        # Update the objective function with the new price
        model.setObjective(
            price_preorder * x +
            quicksum(probabilities[n] * (price_phil * y_phil[n] +
                                         price_rosso * y_rosso[n] +
                                         price_monogram * y_monogram[n])
                     for n in range(len(probabilities))),
            GRB.MINIMIZE
        )

        # Solve the model
        model.optimize()

        # Check if we're still ordering any coffee in advance
        if x.X == 0:
            # Found the break-even point
            return current_price
        
        # Increment the price
        current_price += increment

    return "No break-even point found within the given price range."

# Example usage: find the break-even price between $95 and $200, checking every 5 cents
break_even_price = find_break_even_preorder_price(95, 200, 0.05)
print(f"Break-even preorder price: ${break_even_price:.2f}")


# Assuming you've already solved the stochastic model and stored the objective value as 'optimal_cost'

# Calculate the Expected Value with Perfect Foresight (WS)
ws = sum(probabilities[n] * (gallons_used[n] * price_preorder) for n in range(len(probabilities)))

# Calculate EVPI
evpi = optimal_cost - ws

print(f"Expected Value with Perfect Foresight (WS): {ws}")
print(f"Expected Value of Perfect Information (EVPI): {evpi}")


# Calculate the average demand
average_demand = sum(probabilities[n] * gallons_used[n] for n in range(len(probabilities)))

# Solve the deterministic model using the average demand
mean_model = Model("MeanValueProblem")
x_mean = mean_model.addVar(vtype=GRB.CONTINUOUS, name="Preorder")

# Objective function - only preordering cost since we assume average demand is always met
mean_model.setObjective(price_preorder * x_mean, GRB.MINIMIZE)

# Average demand constraint - we need to have enough coffee for the average demand
mean_model.addConstr(x_mean >= average_demand, name="Average_Demand")

# Solve the model
mean_model.optimize()

# EEV is the objective value of solving the mean value problem
eev = mean_model.ObjVal if mean_model.status == GRB.OPTIMAL else None

# EVSS is the objective value from the original stochastic solution
evss = optimal_cost

# Calculate VSS
vss = evss - eev if eev is not None else None

print(f"Expected Ex-ante Value (EEV): {eev}")
print(f"Value of the Stochastic Solution (VSS): {vss}")


