from gurobipy import GRB
import gurobipy as gb
import pandas as pd
import numpy as np

# Create the model
model = gb.Model("Midterm Question 1")

requirements_df = pd.read_csv('/Users/mikeredshaw/Downloads/nutrient_requirements.csv')
content_df = pd.read_csv('/Users/mikeredshaw/Downloads/nutrient_content.csv')
preference_df = pd.read_csv('/Users/mikeredshaw/Downloads/food_preferences.csv')
categories_df = pd.read_csv('/Users/mikeredshaw/Downloads/food_categories.csv')


#Based on a dataset with 60 rows of Nutrient types
nutrient_names = requirements_df['Nutrient'].tolist()
min_requirements = requirements_df['Min_Requirement'].tolist()
max_requirements = requirements_df['Max_Requirement'].tolist()


#Based on datasets with 120 rows of food items
food_items = categories_df['Food_Item'].tolist()
is_vegetarian = categories_df['Is_Vegetarian'].tolist()
is_vegan = categories_df['Is_Vegan'].tolist()
is_kosher = categories_df['Is_Kosher'].tolist()
is_halal = categories_df['Is_Halal'].tolist()
cost_per_gram = categories_df['Cost_per_gram'].tolist()

veggie_preferance = 46160
vegan_preference = 11540
kosher_preference = 17310
halal_preference = 92320
all_preference = 577000


#Content DF is a dataset with 120 rows for Food type and 60 columns for Nutrient type showing the nutrient breakdown of each food per nutrient type


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
dietary_totals = {
    'All': 577000,
    'Vegetarian': 46160,
    'Vegan': 11540,
    'Kosher': 17310,
    'Halal': 92320
}

# Decision variables
food_quantities = model.addVars(food_items, name="Food")

# Objective function: Minimize total cost
model.setObjective(gb.quicksum(cost_per_gram[i] * food_quantities[food] for i, food in enumerate(food_items)), GRB.MINIMIZE)

# Constraints
# Nutritional balance
for i, nutrient in enumerate(nutrient_names):
    model.addConstr(gb.quicksum(content_df.loc[j, nutrient] * food_quantities[food] for j, food in enumerate(food_items)) >= min_requirements[i], f"Min_{nutrient}")
    model.addConstr(gb.quicksum(content_df.loc[j, nutrient] * food_quantities[food] for j, food in enumerate(food_items)) <= max_requirements[i], f"Max_{nutrient}")

# Dietary preferences
for preference in dietary_preferences:
    model.addConstr(gb.quicksum(food_quantities[food] for food in categories_df[categories_df[preference] == 1]['Food_Item']) <= dietary_totals[preference], f"Total_{preference}")

# Variety: Proportion of each food item less than 3%
for food in food_items:
    model.addConstr(food_quantities[food] <= 0.03 * dietary_totals['All'], f"Variety_{food}")

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


