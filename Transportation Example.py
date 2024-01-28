"""
@author: Adam Diamant (2023)
"""

from gurobipy import GRB
import gurobipy as gb

# Create the optimization model
model = gb.Model("Transportation Problem")

# A list of list of costs
costs = [[21, 50, 40], [35, 30, 22], [55, 20, 25]]
demand = [200000, 600000, 225000]
supply = [275000, 400000, 300000]

# Create the a single class of decision variables
x = model.addVars(3, 3, lb=0, vtype=GRB.CONTINUOUS, name="Transportation Plan")

# The objective function
model.setObjective(gb.quicksum(costs[i][j]*x[i,j] for i in range(3) for j in range(3)), GRB.MINIMIZE) #costs is a dictionary, x is a python variable, so it gets called differenetly

# Add the supply constraints
for i in range(3):
    model.addConstr(gb.quicksum(x[i,j] for j in range(3)) == supply[i], name="Supply Constraint %i" %i)

# Add the demand constraints
for j in range(3):
    model.addConstr(gb.quicksum(x[i,j] for i in range(3)) <= demand[j], name="Demand Constraint %i" %j)

#another approach that does the same thing
#model.addConstr(gb.quicksum(x[i,j] for i in range(3)) <= demand[j] for j in range(3))

# Optimally solve the problem
model.optimize()

# Number of variables in the model
print("Number of Decision Variables: ", model.numVars)

# Value of the objective function
print("Total Transportation cost: ", model.objVal)

# Print the decision variables
print(model.printAttr('X'))