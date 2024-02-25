import pandas as pd
from gurobipy import Model, GRB

# Read the player data
players_df = pd.read_csv('https://raw.githubusercontent.com/mredshaw/MODELS-APP/main/Assignment%202/BasketballPlayers.csv')

players_df['Average'] = players_df.iloc[:, 2:].mean(axis=1)

# Filter players with average skill above 2.05 (without resetting the index)
filtered_players_df = players_df[players_df['Average'] > 2.05]
filtered_players_df = filtered_players_df.drop(columns=['Average'])

# Number of players
num_players = len(filtered_players_df)

# Create the optimization model
model = Model("TrainingCampSelection")

# Create binary decision variables for each player (using original indices)
x = model.addVars(filtered_players_df.index, vtype=GRB.BINARY, name="Player")

# Pre-compute the player positions using original indices
guards = [i for i in filtered_players_df.index if filtered_players_df.loc[i, 'Position'] in ['G', 'G/F']]
forwards_centers = [i for i in filtered_players_df.index if filtered_players_df.loc[i, 'Position'] in ['F', 'C', 'F/C']]

# Total number of players selected
total_players_selected = sum(x[i] for i in filtered_players_df.index)

# At least 30% of the invitations should go to guards
model.addConstr(sum(x[i] for i in guards) >= 0.3 * total_players_selected, "Min_30_percent_guards")

# At least 40% of the invitations should go to forwards/centers
model.addConstr(sum(x[i] for i in forwards_centers) >= 0.4 * total_players_selected, "Min_40_percent_forwards_centers")

# Limit the total number of invitations to 21
#model.addConstr(total_players_selected <= 21, "Total_Invitations_Limit")

# If any player from 20-24 (inclusive) is invited, all players from 72-78 (inclusive) cannot be, and vice versa
model.addConstr(sum(x[i] for i in filtered_players_df.index if 20 <= filtered_players_df.loc[i, 'Number'] <= 24) + sum(x[j] for j in filtered_players_df.index if 72 <= filtered_players_df.loc[j, 'Number'] <= 78) <= 1, "Group_20_24_vs_72_78")


# If any player from 105-114 (inclusive) is invited, at least one player from 45-49 (inclusive) and 65-69 (inclusive) must be invited
for i in [idx for idx in filtered_players_df.index if 105 <= filtered_players_df.loc[idx, 'Number'] <= 114]:
    model.addConstr(x[i] <= sum(x[j] for j in filtered_players_df.index if 45 <= filtered_players_df.loc[j, 'Number'] <= 49) + sum(x[k] for k in filtered_players_df.index if 65 <= filtered_players_df.loc[k, 'Number'] <= 69), f"Group_105_114_requires_{i}")


# At least one player must be invited from: 1-10, 11-20, 21-30, ..., 131-140, 141-150
for i in range(1, 151, 10):
    model.addConstr(sum(x[j] for j in filtered_players_df.index if i <= filtered_players_df.loc[j, 'Number'] < i + 10) >= 1, f"Group_{i}_{i+9}")


# Update the model
model.update()

# Print the number of constraints in the model
print("Number of constraints after adding:", len(model.getConstrs()))

# Check if there are any constraints in the model
constraints = model.getConstrs()
if not constraints:
    raise ValueError("No constraints found in the model")
last_feasible_solution = constraints[0]

# Change the objective function to minimize the total number of players selected
model.setObjective(total_players_selected, GRB.MINIMIZE)

# Find the smallest number of players that can be selected without causing infeasibility
min_players_selected = num_players
infeasible_constraint = None

for i in range(num_players, 0, -1):
    model.update()
    model.optimize()

    if model.status == GRB.INFEASIBLE:
        infeasible_constraint = model.getConstrs()[model.getConstrs().index(last_feasible_solution) + 1].ConstrName
        break
    elif model.status == GRB.OPTIMAL:
        min_players_selected = i
        # Update last_feasible_solution only if it's not the last constraint
        if model.getConstrs().index(last_feasible_solution) + 1 < len(model.getConstrs()):
            last_feasible_solution = model.getConstrs()[model.getConstrs().index(last_feasible_solution) + 1]


print(f"Minimum number of players that can be selected without causing infeasibility: {min_players_selected}")
if infeasible_constraint:
    print(f"The constraint that caused infeasibility: {infeasible_constraint}")
