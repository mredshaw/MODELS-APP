import gurobipy as gb
from gurobipy import GRB
import pandas as pd

# Read the CSV file
df = pd.read_csv("/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Midterm Practice/sp500_data.csv")

# Extract the Price and PercentReturn values
prices = df['Price'].tolist()
percent_returns = df['PercentReturn'].tolist()
# Extract sector and location information
sectors = df['GICS Sector'].tolist()
locations = df['Location of Headquarters'].tolist()

# Total investment amount
total_investment = 10000000
max_investment_per_stock = 600000

# Create a new model
model = gb.Model("Investment Portfolio")

# Decision variables
x = model.addVars(67, lb=0, vtype=GRB.CONTINUOUS, name="Investment_Amount")

# Objective function
model.setObjective(gb.quicksum((percent_returns[i]/100) * x[i] for i in range(67)), GRB.MAXIMIZE)

# Constraints
# Total investment constraint
model.addConstr(gb.quicksum(x[i] for i in range(67)) == total_investment, "Total_Investment")

# Individual stock investment constraint

model.addConstrs(x[i] <= max_investment_per_stock for i in range(67))

# Sector investment constraints
telecom_indices = [i for i, sector in enumerate(sectors) if sector == "Telecommunications Services"]
it_indices = [i for i, sector in enumerate(sectors) if sector == "Information Technology"]
discretionary_indices = [i for i, sector in enumerate(sectors) if sector == "Consumer Discretionary"]
staples_indices = [i for i, sector in enumerate(sectors) if sector == "Consumer Staples"]
energy_indices = [i for i, sector in enumerate(sectors) if sector == "Energy"]


model.addConstr(gb.quicksum(x[i] for i in telecom_indices) <= 500000, "Telecom_Investment")
model.addConstr(gb.quicksum(x[i] for i in it_indices) >= 0.75 * gb.quicksum(x[i] for i in telecom_indices), "IT_Investment")
model.addConstr(gb.quicksum(x[i] for i in energy_indices) >= 1000000, "Energy_Investment")

# Consumer sectors difference constraint
model.addConstr(gb.quicksum(x[i] for i in discretionary_indices) - gb.quicksum(x[i] for i in staples_indices) <= 200000, "Consumer_Difference_Upper")
model.addConstr(gb.quicksum(x[i] for i in staples_indices) - gb.quicksum(x[i] for i in discretionary_indices) <= 200000, "Consumer_Difference_Lower")

# Location-based investment constraint
ny_indices = [i for i, location in enumerate(locations) if location == "New York, New York"]
model.addConstr(gb.quicksum(x[i] for i in ny_indices) >= 300000, "NY_Investment")

# Optimally solve the problem
model.optimize()

print(model.printAttr('X'))

# Value of the objective function
print("Expected 1-year Return: ", round(model.objVal, 2))

# Print the investment amounts and company headquarters
print("Investment Portfolio:")
for i in range(67):
    if x[i].x > 0:
        print(f"Company {i+1}: ${x[i].x}, Headquarters: {locations[i]}")

print(f"-"*50)
for constr in model.getConstrs():
        print(f"Constraint: {constr.ConstrName}, Shadow Price: {constr.Pi}")


# Print the sensitivity analysis report for the objective function coefficients
if model.status == GRB.OPTIMAL:
    print("Sensitivity Analysis Report for Objective Function Coefficients:")
    print("{:<15} {:<15} {:<15} {:<15}".format("Company", "Coefficient", "Allowable Decrease", "Allowable Increase"))
    for i in range(67):
        print("{:<15} {:<15.2f} {:<15.2f} {:<15.2f}".format(f"Company {i+1}", percent_returns[i], x[i].SAObjLow, x[i].SAObjUp))
