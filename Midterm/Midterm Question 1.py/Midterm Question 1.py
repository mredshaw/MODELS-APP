from gurobipy import GRB
import gurobipy as gb
import pandas as pd
import numpy as np

# Create the model
model = gb.Model("Midterm Question 1")

routes_df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Midterm Practice/Routes.csv')