import gurobipy as gp
import numpy as np
import pandas as pd
import gurobipy as GRB

# Create a new model
model = GRB.model('Q1')

costs = [[0.05, 0.05, 0.05, 0.05, 0.05, 0.06, 0.06, 0.06, 0.06, 0.06, 0.07, 0.07, 0.07, 0.07, 0.07, 0.08, 0.08, 0.08, 0.08, 0.08, 0.09, 0.09, 0.09, 0.09, 0.09, 0.10, 0.10, 0.10, 0.10, 0.10],
         [0.08, 0.08, 0.08, 0.08, 0.08, 0.05, 0.05, 0.05, 0.05, 0.05, 0.09, 0.09, 0.09, 0.09, 0.09, 0.10, 0.10, 0.10, 0.10, 0.10, 0.07, 0.07, 0.07, 0.07, 0.07, 0.06, 0.06, 0.06, 0.06, 0.06]]

# Create variables
x = model.addMVar(2, 29, vtype=GRB.CONTINUOUS, name="x")

# Set objective
model.setObjective(gp.quicksum(costs[i][j] * x[i, j] for i in range(2) for j in range(29)), GRB.MINIMIZE)


model.addConstr(gp.quicksum(x[0, j] for j in range(29)) == 1)