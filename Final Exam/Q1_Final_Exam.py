from gurobipy import GRB
import gurobipy as gb
import pandas as pd
import numpy as np
import math
import random

# Create the optimization model
model = gb.Model("EcoGreen_Expansion")

#Has columns Province Index,	Demand.
demand = pd.read_csv('/Users/mikeredshaw/Desktop/Models Final Exam/ecogreen_energy_demand.csv')

#Has columns Plant Location,	Fixed,	Capacity,	Province 1,	Province 2,	Province 3,	Province 4,	Province 5,	Province 6,	Province 7,	Province 8,	Province 9,	Province 10.
supply = pd.read_csv('/Users/mikeredshaw/Desktop/Models Final Exam/ecogreen_energy_supply.csv')

print("Shape of supply DataFrame:", supply.shape)
print("Shape of demand DataFrame:", demand.shape)

# Decision Variables
x = model.addVars(supply.shape[0], vtype=GRB.BINARY, name="Open_Plant")
y = model.addVars(supply.shape[0], demand.shape[0], vtype=GRB.INTEGER, name="Energy_Supplied")


fixed_cost = gb.quicksum(supply.loc[i, "Fixed"] * x[i] for i in supply.index)
variable_cost = gb.quicksum(supply.loc[i, f"Province {j+1}"] * y[i, j] for i in supply.index for j in range(10))


model.setObjective(fixed_cost + variable_cost, GRB.MINIMIZE)

#Capacity Constraint
model.addConstrs((gb.quicksum(y[i, j] for j in range(10)) <= supply.loc[i, "Capacity"] * x[i] for i in supply.index), "Capacity")


#Demand Satisfaction
model.addConstrs((gb.quicksum(y[i, j] for i in supply.index) == demand.loc[j, "Demand"] for j in demand.index), "Demand")


#Exclusive site choices
model.addConstr(x[9] <= 1 - x[14] )
model.addConstr(x[9] <= 1 - x[19] )


#Conditional site openings:
model.addConstr(x[2] <= x[3], "Site_3_4")  # Site 3 requires site 4
model.addConstr(x[2] <= x[4], "Site_3_5")  # Site 3 requires site 5
model.addConstr(x[4] <= x[7] + x[8], "Site_5_8_9")  # Site 5 requires site 8 or 9

#Region A & B Ratio
model.addConstr(gb.quicksum(x[i] for i in range(10)) <= 2 * gb.quicksum(x[i] for i in range(10, 20)), "Region_Ratio")

#Minimum output from sites 1-5
model.addConstr(gb.quicksum(y[i, j] for i in range(5) for j in range(10)) >= 0.3 * gb.quicksum(y[i, j] for i in supply.index for j in range(10)), "Min_Output_1_5")

# Check Maximum Energy Contribution Constraint for each plant

for j in range(demand.shape[0]):  # For each province
    for i in range(supply.shape[0]):  # For each plant
        model.addConstr(y[i, j] <= 0.5 * demand.loc[j, "Demand"], f"Max_Contribution_Plant_{i+1}_Province_{j+1}")

model.optimize()

if model.status == GRB.OPTIMAL:
    optimal_cost = model.ObjVal
    print("Optimal Cost:", optimal_cost)
else:
    print("Model is infeasible! No optimal cost found.")


# Print Opened Plants (x_i)
print("Opened Plants:")
for i in supply.index:
    if x[i].x > 0.5:  # Check if plant is open
        print(f"Plant {i+1} at location {supply.loc[i, 'Plant Location']}")

# Print Energy Supplied (y_ij)
print("\nEnergy Supplied (GWh):")
for i in supply.index:
    for j in demand.index:
        if y[i, j].x > 0:  # Check if energy is supplied
            print(f"Plant {i+1} to Province {j+1}: {y[i, j].x:.2f}")


print("#" * 40)
# Calculate Total Output (All Sites) 
total_output_all = 0
for i in supply.index:
    for j in demand.index:
        total_output_all += y[i, j].x
print("Total Output All: ",total_output_all)

# Calculate Total Output (Sites 1-5)
total_output_sites_1_5 = 0
for i in range(5):  # Adjust upper bound of range if sites 1-5 have different indices
    for j in range(10):
        total_output_sites_1_5 += y[i, j].x  

print("Total output from sites 1-5:", total_output_sites_1_5, "GWh") 

# Check Minimum Output Constraint
if (total_output_sites_1_5 / total_output_all) >= 0.30:
    print("Minimum output constraint is satisfied")
else:
    print("Minimum output constraint is violated")

# Retrieve Demand Data
demand_data = demand.loc[:, "Demand"].to_numpy()  # Assuming "Demand" is the column name

# Check Maximum Energy Contribution Constraint
# Correctly accessing 'Demand' from demand DataFrame
for province_index in range(demand.shape[0]):  # As you have 10 provinces
    province_demand = demand.loc[province_index, "Demand"]
    for plant_index in range(supply.shape[0]):  # As you have 20 plants
        energy_from_plant = y[plant_index, province_index].x
        if model.status == GRB.OPTIMAL and energy_from_plant > 0.5 * province_demand:
            print(f"Maximum contribution constraint violated for Plant {plant_index + 1} to Province {province_index + 1}: {energy_from_plant} GWh exceeds 50% of {province_demand} GWh")


# Print Demand Check
for j in demand.index:
    total_demand_satisfied = sum(y[i, j].x for i in supply.index)
    print(f"Province {j+1} Demand: {demand.loc[j, 'Demand']}, Satisfied: {total_demand_satisfied} (Pass: {total_demand_satisfied == demand.loc[j, 'Demand']})")


    # Print Capacity Check
for i in supply.index:
    total_supply_plant_i = sum(y[i, j].x for j in range(10))
    print(f"Plant {i+1} Capacity: {supply.loc[i, 'Capacity']}, Supply: {total_supply_plant_i} (Pass: {total_supply_plant_i <= supply.loc[i, 'Capacity']})")

num_decision_vars = model.NumVars
print("Minimum number of decision variables:", num_decision_vars)


if model.status == GRB.OPTIMAL:
    open_plants = sum(x[i].x > 0.5 for i in supply.index)
    print("Number of power plants established:", open_plants) 
else:
    print("Model is infeasible! Cannot determine the number of opened plants.")




if model.status == GRB.OPTIMAL:
    plants_per_province = []
    for province_index in range(demand.shape[0]):
        num_plants_supplying = sum(y[i, province_index].x > 0 for i in supply.index)
        plants_per_province.append(num_plants_supplying)

    highest_count = max(plants_per_province)
    lowest_count = min(plants_per_province)

    print("Highest number of plants supplying a province:", highest_count)
    print("Lowest number of plants supplying a province:", lowest_count) 
else:
    print("Model is infeasible! Cannot analyze energy distribution.")


model.optimize() # Assuming you've already solved the model initially

if model.status == GRB.OPTIMAL:
    optimal_value = model.ObjVal
    tolerance = 0.01  

    # New variable for the objective value
    obj_value = model.addVar(lb=-GRB.INFINITY, name="objective_value") 
    model.setObjective(obj_value, GRB.MINIMIZE) # Or GRB.MAXIMIZE if needed

    # Constrain the objective value
    model.addConstr(obj_value >= optimal_value * (1 - tolerance))
    model.addConstr(obj_value <= optimal_value * (1 + tolerance))


    # Parameter Settings
    model.setParam("PoolSearchMode", 2)  
    model.setParam("PoolSolutions", 100) 

    # Find Alternative Solutions
    model.optimize()

    print(f"Number of feasible solutions within 1% of optimal: {model.SolCount}")

    for i in range(model.SolCount):
        model.setParam("SolutionNumber", i)
        print(f"Solution {i+1} Objective Value: {model.PoolObjVal}")
    else:
        print("Original model is infeasible. Cannot search for alternate solutions.")
