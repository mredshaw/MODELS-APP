import pandas as pd
from gurobipy import Model, GRB

# Read the player data
players_df = pd.read_csv('https://raw.githubusercontent.com/mredshaw/MODELS-APP/main/Assignment%202/BasketballPlayers.csv')

# Number of players
num_players = len(players_df)

# Create the optimization model
model = Model("TrainingCampSelection")

# Create binary decision variables for each player
x = model.addVars(num_players, vtype=GRB.BINARY, name="Player")

# Pre-compute the player positions and skills
guard_players = [i for i in range(num_players) if players_df.loc[i, 'Position'] in ['G', 'G/F']]
fc_players = [i for i in range(num_players) if players_df.loc[i, 'Position'] in ['F', 'C', 'F/C']]


# Constraints for positions using pre-computed lists
model.addConstr(sum(x[i] for i in guard_players) >= 0.3 * sum(x.values()), "GuardPosition")
model.addConstr(sum(x[i] for i in fc_players) >= 0.4 * sum(x.values()), "ForwardCenterPosition")

# Constraints for skills
skills = ['Ball Handling', 'Shooting', 'Rebounding', 'Defense', 'Athletic Ability', 'Toughness', 'Mental Acuity']
avg_skill_vars = model.addVars(skills, name="AvgSkill")
skill_totals = {skill: [players_df.loc[i, skill] for i in range(num_players)] for skill in skills}

for skill in skills:
    total_skill = sum(skill_totals[skill][i] * x[i] for i in range(num_players))
    model.addConstr(avg_skill_vars[skill] * sum(x.values()) == total_skill, f"TotalSkill_{skill}")
    model.addConstr(avg_skill_vars[skill] >= 2.05, f"Skill_{skill}")

# Constraints for specific player groups
model.addConstr(sum(x[i] for i in range(19, 24)) <= (1 - sum(x[i] for i in range(71, 78))), "Group_20_24")
model.addConstr(sum(x[i] for i in range(104, 114)) <= (sum(x[i] for i in range(44, 49)) + sum(x[i] for i in range(64, 69))), "Group_105_114")

# Constraints for at least one player from each group of 10
for i in range(0, 150, 10):
    model.addConstr(sum(x[j] for j in range(i, min(i+10, num_players))) >= 1, f"Group_{i+1}_{min(i+10, num_players)}")
    
# Objective function to maximize total skill ratings
model.setObjective(sum(sum(players_df.loc[i, skill] * x[i] for skill in skills) for i in range(num_players)), GRB.MAXIMIZE)

# Solve the model
model.optimize()

# Print the selected players
selected_players = [i for i in range(num_players) if x[i].X > 0.5]
print("Selected players:", selected_players)
