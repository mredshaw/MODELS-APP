from gurobipy import GRB
import gurobipy as gb
import pandas as pd

model = gb.Model("Can2Oil Transshipment Problem")

#Loading the data from CSV files
costs_prod_to_refine_df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Assignment 1/Cost_Production_to_Refinement.csv')
costs_prod_to_transship_df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Assignment 1/Cost_Production_to_Transshipment.csv')
costs_transshipment_to_refinement_df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Assignment 1/Cost_Transshipment_to_Refinement.csv')
capacity_direct_production_df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Assignment 1/Capacity_for_Direct_Production_Facilities.csv')
capacity_transship_production_df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Assignment 1/Capacity_for_Transship_Production_Facilities.csv')
capacity_transship_distribution_df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Assignment 1/Capacity_for_Transship_Distribution_Centers.csv')
demand_refinement_df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Assignment 1/Refinement_Demand.csv')

#Print rows from CSV to check data is loaded correctly
print(costs_prod_to_refine_df.head())
print(costs_prod_to_transship_df.head())
print(costs_transshipment_to_refinement_df.head())
print(capacity_direct_production_df.head())
print(capacity_transship_production_df.head())
print(capacity_transship_distribution_df.head())
print(demand_refinement_df.head())



# Decision Variables

# Create decision variables for shipping from production facilities to refinement centers
# x[p, r] represents the quantity shipped from production facility p to refinement center r
capacity_dict_direct = capacity_direct_production_df.set_index('ProductionFacility')['Capacity'].to_dict()
production_facilities = costs_prod_to_refine_df['ProductionFacility'].unique()
refinement_centers = costs_prod_to_refine_df['RefinementCenter'].unique()
prod_refin_tuples = gb.tuplelist((p, r) for p in production_facilities for r in refinement_centers)
costs_dict = {(row['ProductionFacility'], row['RefinementCenter']): row['Cost'] for _, row in costs_prod_to_refine_df.iterrows()}
x = model.addVars(prod_refin_tuples, obj=costs_dict, lb=0, vtype=GRB.CONTINUOUS, name="Ship_Production_to_Refinement")

# Create decision variables for shipping from production facilities to Transhipment hubs
# x[p, t] represents the quantity shipped from production facility p to Transhipment hub t
production_facilities_transship = costs_prod_to_transship_df['ProductionFacility'].unique()
transshipment_hubs = costs_prod_to_transship_df['TransshipmentHub'].unique()
prod_trans_tuples = gb.tuplelist((p, t) for p in production_facilities_transship for t in transshipment_hubs)
trans_costs_dict = {(row['ProductionFacility'], row['TransshipmentHub']): row['Cost'] for _, row in costs_prod_to_transship_df.iterrows()}
y = model.addVars(prod_trans_tuples, obj=trans_costs_dict, lb=0, vtype=GRB.CONTINUOUS, name="Ship_Production_to_Transshipment")

# Create decision variables for shipping from Transhipment hubs to Refinement Centers
# x[t, r] represents the quantity shipped from transhipment hib t to refinement center r
capacity_dict_transship_distribution = capacity_transship_distribution_df.set_index('TransshipmentHub')['Capacity'].to_dict()
transship_refin_tuples = gb.tuplelist((t, r) for t in transshipment_hubs for r in refinement_centers)
transship_to_refin_costs_dict = {(row['TransshipmentHub'], row['RefinementCenter']): row['Cost']for _, row in costs_transshipment_to_refinement_df.iterrows()}
z = model.addVars(transship_refin_tuples, obj=transship_to_refin_costs_dict, lb=0, vtype=GRB.CONTINUOUS, name="Ship_Transshipment_to_Refinement")




# Objective Function

# The objective is to minimize the total transportation cost
# This is the sum of the transportation costs for all shipping routes
total_cost = gb.quicksum(x[p, r] * costs_dict[p, r] for p, r in prod_refin_tuples if (p, r) in x) + \
             gb.quicksum(y[p, t] * trans_costs_dict[p, t] for p, t in prod_trans_tuples if (p, t) in y) + \
             gb.quicksum(z[t, r] * transship_to_refin_costs_dict[t, r] for t, r in transship_refin_tuples if (t, r) in z)
model.setObjective(total_cost, GRB.MINIMIZE)


#Adding a cost penalty for transhipments. Comment out objective function when not using.
########################################################################################################
# Define the penalty for transshipments and the reward for direct shipments
transshipment_penalty = 1.5  # Cost added per unit of transshipped oil

adjusted_total_cost = total_cost + transshipment_penalty * gb.quicksum(y[p, t] for p, t in prod_trans_tuples)
#model.setObjective(adjusted_total_cost, GRB.MINIMIZE)
########################################################################################################


#Adding a reward for facilities in North America. Comment out objective function when not using.
########################################################################################################
# Define the reward for certain direct shipments
direct_shipment_reward = 0.5  # Cost reduced per unit of directly shipped oil from facilities 1-15
# Apply rewards to x variables for facilities 1-15
adjusted_rewards_total_cost = total_cost - direct_shipment_reward * gb.quicksum(x[p, r] for p, r in prod_refin_tuples if p <= 15)
#model.setObjective(adjusted_rewards_total_cost, GRB.MINIMIZE)


# Constraints

# Supply constraints for direct production facilities
for facility in production_facilities:
    if facility in capacity_dict_direct:
        model.addConstr(gb.quicksum(x[facility, center] for center in refinement_centers if (facility, center) in x) <= capacity_dict_direct[facility], name=f"Direct_Supply_Capacity_{facility}")

# Supply constraints for tranship production facilities. Ensuring that the quantity shipped does not exceed the facility's capacity
capacity_dict = capacity_transship_production_df.set_index('ProductionFacility')['Capacity'].to_dict()
for facility in production_facilities_transship:
    model.addConstr(gb.quicksum(y[facility, hub] for hub in transshipment_hubs) <= capacity_dict[facility], name=f"Supply_Capacity_{facility}")


# Capacity constraints for transshipment to distribution centers
for hub in transshipment_hubs:
    if hub in capacity_dict_transship_distribution:
        model.addConstr(gb.quicksum(z[hub, center] for center in refinement_centers if (hub, center) in z) <= capacity_dict_transship_distribution[hub], name=f"Transship_Distribution_Capacity_{hub}")

# Flow balance constraints for each transshipment center to ensure shipments in = shipment out
for hub in transshipment_hubs:
    model.addConstr( gb.quicksum(y[p, hub] for p in production_facilities_transship if (p, hub) in y) == gb.quicksum(z[hub, r] for r in refinement_centers if (hub, r) in z), name=f"Flow_Balance_{hub}")

# Convert the demand DataFrame to a dictionary for easier lookup
demand_dict = demand_refinement_df.set_index('RefinementCenter')['Demand'].to_dict()

# Demand constraints for refinement centers. Ensuring that the quantity shipped meets the demand for each center
for center in refinement_centers:
    model.addConstr((gb.quicksum(x[facility, center] for facility in production_facilities if (facility, center) in x) + 
                     gb.quicksum(z[hub, center] for hub in transshipment_hubs if (hub, center) in z)) >= demand_dict[center], name=f"Demand_{center}")



#Adding a ratio constraint for transhipments. Comment out when not using.    
#############################################################################################################################################################
tranship_ratio = 0.2  # Proportion of total shipments that can be transshipped
#model.addConstr(gb.quicksum(y[p, t] for p, t in prod_trans_tuples) <= tranship_ratio * 
#                (gb.quicksum(x[p, r] for p, r in prod_refin_tuples) + gb.quicksum(y[p, t] for p, t in prod_trans_tuples)),name="Transshipment_Ratio_Constraint")
#############################################################################################################################################################


model.optimize()

# Output Results
print("Number of Decision Variables: ", model.numVars)
print("Total Transportation cost: ", model.objVal)

# Print non-zero decision variables to understand the transportation plan
for v in model.getVars():
    if v.x > 0:
        print(f"{v.varName}: {v.x}")

# Calculate the total transshipped amount
total_transshipped = sum(y[p, t].x for p, t in y)

# Calculate the total transported amount (including both direct and transshipped shipments)
total_transported = sum(x[p, r].x for p, r in x) + total_transshipped

# Calculate the proportion of canola oil that is transshipped
proportion_transshipped = total_transshipped / total_transported if total_transported > 0 else 0

# Print the results
print("Total Transshipped Amount: ", total_transshipped)
print("Total Transported Amount: ", total_transported)
print("Proportion of Canola Oil Transshipped: ", proportion_transshipped)



if model.status == GRB.OPTIMAL:
    # Print the high and low range of optimality for the transshipment variables
    for p, t in prod_trans_tuples:
        var = y[p, t]
        if var.X > 0:  # Check if the variable is used in the solution
            print(f"Variable y[{p},{t}] transshipped amount: {var.X}")
            print(f"  Low range of optimality: {var.SAObjLow}")
            print(f"  High range of optimality: {var.SAObjUp}")
else:
    print("Model has not been solved to optimality. Cannot perform sensitivity analysis.")


