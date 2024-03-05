from gurobipy import GRB
import gurobipy as gb
import pandas as pd
import numpy as np

# Create the model
model = gb.Model("OptiDiet")

# Load data
requirements_df = pd.read_csv('/Users/mikeredshaw/Downloads/nutrient_requirements.csv')
content_df = pd.read_csv('/Users/mikeredshaw/Downloads/nutrient_content.csv')
preference_df = pd.read_csv('/Users/mikeredshaw/Downloads/food_preferences.csv')
categories_df = pd.read_csv('/Users/mikeredshaw/Downloads/food_categories.csv')

# Nutrient requirements
nutrient_names = requirements_df['Nutrient'].tolist()
min_requirements = requirements_df['Min_Requirement'].tolist()
max_requirements = requirements_df['Max_Requirement'].tolist()

# Food items and categories
food_items = categories_df['Food_Item'].tolist()
cost_per_gram = categories_df['Cost_per_gram'].tolist()
dietary_preferences = ['All', 'Vegetarian', 'Vegan', 'Kosher', 'Halal']
# Dietary preferences from preference_df

# Decision variables
food_quantities = model.addVars(food_items, lb=0, vtype=GRB.CONTINUOUS, name="Food")
total_diet_quantity = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="TotalDietQuantity")


# Hardcoded dietary preference totals
dietary_totals = {
    'Vegetarian': 46160,
    'Vegan': 11540,
    'Kosher': 17310,
    'Halal': 92320,
    'All': 577000
}

# Dietary preferences constraints
for preference in dietary_preferences:
    if preference == 'All':
        # Sum of quantities of all food items should not exceed the total for 'All' preference
        model.addConstr(gb.quicksum(food_quantities[food] for food in food_items) <= dietary_totals[preference], f"Total_{preference}")
    else:
        # Create a filtered list of food items for each specific dietary preference
        food_list = categories_df[categories_df[f'Is_{preference}'] == True]['Food_Item']
        # Sum of quantities of food items in the specific dietary list should not exceed the total for that preference
        model.addConstr(gb.quicksum(food_quantities[food] for food in food_list) <= dietary_totals[preference], f"Total_{preference}")

# Dietary preferences constraints
for preference in dietary_preferences:
    if preference == 'All':
        model.addConstr(gb.quicksum(food_quantities[food] for food in food_items) <= dietary_totals[preference], f"Total_{preference}")
    elif preference == 'Vegetarian':
        model.addConstr(gb.quicksum(food_quantities[food] for food in categories_df[categories_df['Is_Vegetarian'] == 1]['Food_Item']) <= dietary_totals[preference], f"Total_{preference}")
    elif preference == 'Vegan':
        model.addConstr(gb.quicksum(food_quantities[food] for food in categories_df[categories_df['Is_Vegan'] == 1]['Food_Item']) <= dietary_totals[preference], f"Total_{preference}")
    elif preference == 'Kosher':
        model.addConstr(gb.quicksum(food_quantities[food] for food in categories_df[categories_df['Is_Kosher'] == 1]['Food_Item']) <= dietary_totals[preference], f"Total_{preference}")
    elif preference == 'Halal':
        model.addConstr(gb.quicksum(food_quantities[food] for food in categories_df[categories_df['Is_Halal'] == 1]['Food_Item']) <= dietary_totals[preference], f"Total_{preference}")

# Objective function: Minimize total cost
model.setObjective(gb.quicksum(cost_per_gram[i] * food_quantities[food] for i, food in enumerate(food_items)), GRB.MINIMIZE)

# Nutritional balance constraints
for i, nutrient in enumerate(nutrient_names):
    model.addConstr(gb.quicksum(content_df.loc[j, nutrient] * food_quantities[food] for j, food in enumerate(food_items)) >= min_requirements[i], f"Min_{nutrient}")
    model.addConstr(gb.quicksum(content_df.loc[j, nutrient] * food_quantities[food] for j, food in enumerate(food_items)) <= max_requirements[i], f"Max_{nutrient}")

# Constraint to set total_diet_quantity to the sum of all food_quantities
model.addConstr(total_diet_quantity == gb.quicksum(food_quantities[food] for food in food_items), "TotalDietQuantity")

# Updated variety constraint: Proportion of each food item less than 3% of the actual diet plan quantity
for food in food_items:
    model.addConstr(food_quantities[food] <= 0.03 * total_diet_quantity, f"Variety_{food}")
# Optimize the model
model.optimize()

# Print the solution
if model.Status == GRB.OPTIMAL:
    print("Optimal solution found:")
    for food in food_items:
        quantity = food_quantities[food].X
        if quantity > 0:
            print(f"{food}: {quantity} grams")
else:
    print("No optimal solution found.")
