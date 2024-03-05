import gurobipy as gb
from gurobipy import GRB
import pandas as pd


# Read the CSV file into a DataFrame
routes_df = pd.read_csv('/Users/mikeredshaw/Documents/Schulich MBAN/Models & Applications/Midterm Practice/Routes.csv')

# Initialize the model
model = gb.Model("Shuttle Service")

# Parse the routes and extract individual stops
all_stops = set()  # A set to hold all unique stops
routes = []  # A list to hold all routes as lists of stops
for route in routes_df['Routes']:
    # Assume the route string format is "['U', 'a', 'b', 'U']"
    # We need to parse it into a list of stops, e.g., ['U', 'a', 'b', 'U']
    stops = route.strip("[]").replace("'", "").split(", ")
    routes.append(stops)
    all_stops.update(stops)


# Initialize a dictionary to hold indices for routes that include each stop
route_indices_by_stop = {stop: [] for stop in all_stops}

# Populate the dictionary with indices
for i, route in enumerate(routes):
    for stop in route:
        route_indices_by_stop[stop].append(i)

# Now you have a dictionary where each key is a stop and each value is a list of route indices that include that stop
# For example, route_indices_by_stop['a'] = [0, 1, 2] means that stops 'a' is included in routes 0, 1, and 2

# Create binary decision variables for each route
x = model.addVars(len(routes), vtype=GRB.BINARY, name="x")


# Step 1: Identify all routes that include Glendon campus ('a')
glendon_routes = [i for i, route in enumerate(routes) if 'a' in route]

# Step 2: Create auxiliary binary variables for each pair of Glendon routes
glendon_pairs = model.addVars(len(glendon_routes), len(glendon_routes), vtype=GRB.BINARY, name="glendon_pairs")

# Step 3: Add constraints to activate auxiliary variables for selected routes
for i, route_i in enumerate(glendon_routes):
    for j, route_j in enumerate(glendon_routes):
        if i < j:  # Ensure each pair is only considered once
            # Auxiliary variable is 1 if both routes are selected
            model.addConstr(glendon_pairs[i, j] <= x[route_i], name=f"glendon_pair_{i}_{j}_1")
            model.addConstr(glendon_pairs[i, j] <= x[route_j], name=f"glendon_pair_{i}_{j}_2")
            
            # Add a constraint that forces the auxiliary variable to zero if either route is not selected
            model.addConstr(glendon_pairs[i, j] >= x[route_i] + x[route_j] - 1, name=f"glendon_pair_{i}_{j}_3")

# Step 4: Update the objective function to include the extra cost
extra_cost_per_pair = 350
total_extra_cost = gb.quicksum(glendon_pairs[i, j] for i in range(len(glendon_routes)) for j in range(i+1, len(glendon_routes)))

# The objective is to minimize the total maintenance cost plus the extra costs for Glendon campus pairs
maintenance_cost = gb.quicksum(routes_df['Cost'][i] * x[i] for i in range(len(routes)))
extra_glendon_cost = extra_cost_per_pair * total_extra_cost  # This was calculated in the previous step

# Define a subsidy amount per qualifying stop
subsidy_per_stop = 50

# Create a variable for each stop to count the number of routes serving it
stops_served_count = {stop: gb.quicksum(x[i] for i in range(len(routes)) if stop in routes[i]) for stop in all_stops if stop != 'U'}

# Create a binary variable for each stop to indicate if it qualifies for the subsidy (served by at least 3 routes)
stop_subsidy_qualification = model.addVars(all_stops.difference(['U']), vtype=GRB.BINARY, name="stop_subsidy_qual")

# Add constraints for the binary subsidy qualification variables
for stop in stops_served_count:
    model.addConstr(stops_served_count[stop] >= 3 * stop_subsidy_qualification[stop], name=f"subsidy_qual_{stop}")

# Update the objective function to include the subsidy
total_subsidy = gb.quicksum(subsidy_per_stop * stop_subsidy_qualification[stop] for stop in stops_served_count)


# Update the objective function
model.setObjective(maintenance_cost + extra_glendon_cost - total_subsidy, GRB.MINIMIZE)


# Constraint: Each stop is served by at least one route
for stop in all_stops:
    if stop != 'U':  # Exclude the starting point (Keele Campus)
        model.addConstr(gb.quicksum(x[i] for i, route in enumerate(routes) if stop in route) >= 1, name=f"serve_{stop}")

# Now we can proceed with optimization
model.optimize()


# Other constraints related to the Glendon campus and subsidies will go here

# Optimize the model
model.optimize()

# Check the solution
if model.status == GRB.OPTIMAL:
    selected_routes = [i for i in range(len(routes)) if x[i].X > 0.5]
    print("Selected Routes:")
    for i in selected_routes:
        print(f"Route {i+1}: {routes[i]}")

print("Number of Decision Variables:", model.numVars)
print(model.ObjVal)