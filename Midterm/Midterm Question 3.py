from gurobipy import GRB
import gurobipy as gb
import pandas as pd
import numpy as np

# Create the model
model = gb.Model("Midterm Question 3")

shift_df = pd.read_csv('/Users/mikeredshaw/Downloads/nurse_shift_costs.csv')