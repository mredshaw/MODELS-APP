from gurobipy import GRB
import gurobipy as gb
import pandas as pd

model = gb.Model("Can2Oil Transshipment Problem")

costs_df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Assignment 1/Cost_Production_to_Refinement.csv')
costs_transshipment_df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Assignment 1/Cost_Production_to_Transshipment.csv')
costs_transshipment_to_refinement_df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Assignment 1/Cost_Transshipment_to_Refinement.csv')
capacity_transship_production_df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Assignment 1/Capacity_for_Transship_Production_Facilities.csv')
demand_refinement_df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Assignment 1/Refinement_Demand.csv')

print(costs_df.head())
print(costs_transshipment_df.head())
print(costs_transshipment_to_refinement_df.head())
print(capacity_transship_production_df.head())
print(demand_refinement_df.head())


# First, we need to create tuples for the indices
production_facilities = costs_df['ProductionFacility'].unique()
refinement_centers = costs_df['RefinementCenter'].unique()
prod_refin_tuples = gb.tuplelist((p, r) for p in production_facilities for r in refinement_centers)

# Now we need to create a dictionary for the costs, keyed by these tuples
costs_dict = {(row['ProductionFacility'], row['RefinementCenter']): row['Cost'] for _, row in costs_df.iterrows()}


x = model.addVars(prod_refin_tuples, 
                  obj=costs_dict, 
                  lb=0, vtype=GRB.CONTINUOUS, 
                  name="Ship_Production_to_Refinement")

# Create tuples for the indices
production_facilities_transship = costs_transshipment_df['ProductionFacility'].unique()
transshipment_hubs = costs_transshipment_df['TransshipmentHub'].unique()
prod_trans_tuples = gb.tuplelist((p, t) for p in production_facilities_transship for t in transshipment_hubs)


# Create a dictionary for the costs, keyed by these tuples
trans_costs_dict = {(row['ProductionFacility'], row['TransshipmentHub']): row['Cost'] for _, row in costs_transshipment_df.iterrows()}

# Now we can define the decision variables for shipping from production facilities to transshipment centers
y = model.addVars(prod_trans_tuples, 
                  obj=trans_costs_dict, 
                  lb=0, vtype=GRB.CONTINUOUS, 
                  name="Ship_Production_to_Transshipment")

# Create tuples for the indices
transship_refin_tuples = gb.tuplelist(
    (t, r) for t in transshipment_hubs for r in refinement_centers
)

# Create a dictionary for the costs, keyed by these tuples
transship_to_refin_costs_dict = {
    (row['TransshipmentHub'], row['RefinementCenter']): row['Cost']
    for _, row in costs_transshipment_to_refinement_df.iterrows()
}


# Now we can define the decision variables for shipping from transshipment centers to refinement centers
z = model.addVars(transship_refin_tuples, 
                  obj=transship_to_refin_costs_dict, 
                  lb=0, vtype=GRB.CONTINUOUS, 
                  name="Ship_Transshipment_to_Refinement")



total_cost = gb.quicksum(x[p, r] * costs_dict[p, r] for p, r in prod_refin_tuples if (p, r) in x) + \
             gb.quicksum(y[p, t] * trans_costs_dict[p, t] for p, t in prod_trans_tuples if (p, t) in y) + \
             gb.quicksum(z[t, r] * transship_to_refin_costs_dict[t, r] for t, r in transship_refin_tuples if (t, r) in z)

model.setObjective(total_cost, GRB.MINIMIZE)


# Convert the capacity DataFrame to a dictionary for easier lookup
capacity_dict = capacity_transship_production_df.set_index('ProductionFacility')['Capacity'].to_dict()


# Update supply constraints for production facilities that ship to transshipment centers
for facility in production_facilities_transship:
    model.addConstr(
        gb.quicksum(y[facility, hub] for hub in transshipment_hubs)
        <= capacity_dict[facility],
        name=f"Supply_Capacity_{facility}"
    )

# Define the capacities for the transshipment centers as a dictionary
transship_capacities = {1: 1317, 2: 1453}

# Update transshipment constraints for transshipment centers
for hub in transshipment_hubs:
    model.addConstr(
        gb.quicksum(z[hub, center] for center in refinement_centers) 
        <= transship_capacities[hub],
        name=f"Transshipment_Capacity_{hub}"
    )


# Convert the demand DataFrame to a dictionary for easier lookup
demand_dict = demand_refinement_df.set_index('RefinementCenter')['Demand'].to_dict()

# Update demand constraints for refinement centers
for center in refinement_centers:
    model.addConstr(
        (gb.quicksum(x[facility, center] for facility in production_facilities if (facility, center) in x) +
         gb.quicksum(z[hub, center] for hub in transshipment_hubs if (hub, center) in z))
        >= demand_dict[center],
        name=f"Demand_{center}"
    )

# The objective function is already set through the 'obj' parameter in the decision variables

# Optimally solve the problem
model.optimize()

# Number of variables in the model
print("Number of Decision Variables: ", model.numVars)

# Value of the objective function
print("Total Transportation cost: ", model.objVal)

# Print the decision variables
for v in model.getVars():
    if v.x > 0:
        print(f"{v.varName}: {v.x}")