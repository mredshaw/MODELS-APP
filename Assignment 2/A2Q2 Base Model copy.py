import pandas as pd
from gurobipy import Model, GRB

# Read the player data
players_df = pd.read_csv('https://raw.githubusercontent.com/mredshaw/MODELS-APP/main/Assignment%202/BasketballPlayers.csv')

players_df['Average'] = players_df.iloc[:, 2:].mean(axis=1)

# Filter players with average skill above 2.05 (without resetting the index)
filtered_players_df = players_df[players_df['Average'] > 2.05]
players_df= players_df.drop(columns=['Average'])


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

# Constraints for specific player groups (using original indices)
model.addConstr(sum(x[i] for i in range(19, 25) if i in filtered_players_df.index) <= (1 - sum(x[i] for i in range(71, 79) if i in filtered_players_df.index)), "Group_20_24")
model.addConstr(sum(x[i] for i in range(104, 115) if i in filtered_players_df.index) <= (sum(x[i] for i in range(44, 50) if i in filtered_players_df.index) + sum(x[i] for i in range(64, 70) if i in filtered_players_df.index)), "Group_105_114")

# Constraints for at least one player from each group of 10 (using original indices)
for i in range(0, max(filtered_players_df.index), 10):
    model.addConstr(sum(x[j] for j in range(i, min(i+10, max(filtered_players_df.index)+1)) if j in filtered_players_df.index) >= 1, f"Group_{i+1}_{min(i+10, max(filtered_players_df.index)+1)}")
    
# Objective function to maximize total skill ratings
skills = ['Ball Handling', 'Shooting', 'Rebounding', 'Defense', 'Athletic Ability', 'Toughness', 'Mental Acuity']
model.setObjective(sum(sum(filtered_players_df.loc[i, skill] * x[i] for skill in skills) for i in filtered_players_df.index), GRB.MAXIMIZE)

# Solve the model
model.optimize()

# Print the selected players
selected_players = [i for i in filtered_players_df.index if x[i].X > 0.5]
print("Selected players:", selected_players)
