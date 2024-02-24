import pandas as pd
from gurobipy import Model, GRB

# Read the player data
players_df = pd.read_csv('https://raw.githubusercontent.com/mredshaw/MODELS-APP/main/Assignment%202/BasketballPlayers.csv')

players_df['Average'] = players_df.iloc[:, 2:].mean(axis=1)

# Filter players with average skill above 2.05 (without resetting the index)
filtered_players_df = players_df[players_df['Average'] > 2.05]
filtered_players_df= filtered_players_df.drop(columns=['Average'])


# Number of players
num_players = len(filtered_players_df)

# Create the optimization model
model = Model("TrainingCampSelection")

# Create binary decision variables for each player (using original indices)
x = model.addVars(filtered_players_df.index, vtype=GRB.BINARY, name="Player")

# Pre-compute the player positions using original indices
guard_players = [i for i in filtered_players_df.index if filtered_players_df.loc[i, 'Position'] in ['G', 'G/F']]
fc_players = [i for i in filtered_players_df.index if filtered_players_df.loc[i, 'Position'] in ['F', 'C', 'F/C']]

# Constraints for positions using pre-computed lists
model.addConstr(sum(x[i] for i in guard_players) >= 0.3 * sum(x.values()), "GuardPosition")
model.addConstr(sum(x[i] for i in fc_players) >= 0.4 * sum(x.values()), "ForwardCenterPosition")

# If any player from 20-24 (inclusive) is invited, all players from 72-78 (inclusive) cannot be
model.addConstr(sum(x[i] for i in filtered_players_df.index if 20 <= filtered_players_df.loc[i, 'Number'] <= 24) <= (1 - sum(x[j] for j in filtered_players_df.index if 72 <= filtered_players_df.loc[j, 'Number'] <= 78)), "Group_20_24")

# If any player from 105-114 (inclusive) is invited, at least one player from 45-49 (inclusive) and 65-69 (inclusive) must be invited
for i in [idx for idx in filtered_players_df.index if 105 <= filtered_players_df.loc[idx, 'Number'] <= 114]:
    model.addConstr(x[i] <= sum(x[j] for j in filtered_players_df.index if 45 <= filtered_players_df.loc[j, 'Number'] <= 49) + sum(x[k] for k in filtered_players_df.index if 65 <= filtered_players_df.loc[k, 'Number'] <= 69), f"Group_105_114_requires_{i}")


# At least one player must be invited from: 1-10, 11-20, 21-30, ..., 131-140, 141-150
for i in range(1, 151, 10):
    model.addConstr(sum(x[j] for j in filtered_players_df.index if i <= filtered_players_df.loc[j, 'Number'] < i + 10) >= 1, f"Group_{i}_{i+9}")

    
# Objective function to maximize total skill ratings
skills = ['Ball Handling', 'Shooting', 'Rebounding', 'Defense', 'Athletic Ability', 'Toughness', 'Mental Acuity']
model.setObjective(sum(sum(filtered_players_df.loc[i, skill] * x[i] for skill in skills) for i in filtered_players_df.index), GRB.MAXIMIZE)

# Solve the model
model.optimize()

# Print the selected players
selected_players = [i for i in filtered_players_df.index if x[i].X > 0.5]
print("Selected players:", selected_players)
