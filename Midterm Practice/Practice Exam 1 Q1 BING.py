import gurobipy as grb

# Create a new model
model = grb.Model("VaccineTransport")

# Decision variables
airports = ["BillyBishop", "TorontoPearson"]
sites = range(1, 30)
x = model.addVars(airports, sites, lb=0, vtype=grb.GRB.INTEGER, name="Doses")

# Objective function: Minimize transportation cost
Billy_Bishop_Toronto_City_Airport_costs = [0.05, 0.05, 0.05, 0.05, 0.05, 0.06, 0.06, 0.06, 0.06, 0.06, 0.07, 0.07, 0.07, 0.07, 0.07, 0.08, 0.08, 0.08, 0.08, 0.08, 0.09, 0.09, 0.09, 0.09, 0.09, 0.1, 0.1, 0.1, 0.1]
Toronto_Pearson_Airport_costs = [0.08, 0.08, 0.08, 0.08, 0.08, 0.05, 0.05, 0.05, 0.05, 0.05, 0.09, 0.09, 0.09, 0.09, 0.09, 0.1, 0.1, 0.1, 0.1, 0.1, 0.07, 0.07, 0.07, 0.07, 0.07, 0.06, 0.06, 0.06, 0.06]


model.setObjective(grb.quicksum(costs[airport, j] * x[airport, j] for airport in airports for j in sites), sense=grb.GRB.MINIMIZE)

# Supply constraints
model.addConstr(grb.quicksum(x["BillyBishop", j] for j in sites) <= 100000, name="Supply_BillyBishop")
model.addConstr(grb.quicksum(x["TorontoPearson", j] for j in sites) <= 250000, name="Supply_TorontoPearson")

# Demand constraints
model.addConstr(grb.quicksum(x[airport, j] for airport in airports for j in range(1, 6)) == 50000, name="Demand_Sites1_5")
# Similar constraints for other site groups

# Difference constraint for sites 1-5
model.addConstr(grb.abs_(grb.quicksum(x["BillyBishop", j] for j in range(1, 6)) - grb.quicksum(x["TorontoPearson", j] for j in range(1, 6))) <= 4800, name="Difference_Sites1_5")

# Ratio constraint for sites 26-29 and 16-20
model.addConstr(0.8 * grb.quicksum(x["TorontoPearson", j] for j in range(26, 30)) >= grb.quicksum(x["BillyBishop", j] for j