from gurobipy import GRB
import gurobipy as gb

# Create the optimization model for the dual problem
dual_model = gb.Model("Dual of Question 2: Sunnyshore Bay")

# Create dual variables for each constraint in the primal model
y_May_Balance = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="May_Balance_Dual")
y_June_Balance = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="June_Balance_Dual")
y_July_Balance = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="July_Balance_Dual")
y_August_Balance = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="August_Balance_Dual")
y_May_Cash_Flow = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="May_Cash_Flow_Dual")
y_June_Cash_Flow = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="June_Cash_Flow_Dual")
y_July_Cash_Flow = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="July_Cash_Flow_Dual")
y_August_Cash_Flow = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="August_Cash_Flow_Dual")
y_May_Borrowing = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="May_Borrowing_Dual")
y_June_Borrowing = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="June_Borrowing_Dual")
y_July_Borrowing = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="July_Borrowing_Dual")
y_August_Borrowing = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="August_Borrowing_Dual")
y_Ratio_Constraint = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="Ratio_Constraint_Dual")

# Set the objective function for the dual problem (minimize)
dual_model.setObjective(
    140000*y_May_Balance + 260000*y_June_Balance + 420000*y_July_Balance + 580000*y_August_Balance
    + 25000*y_May_Cash_Flow + 20000*y_June_Cash_Flow + 35000*y_July_Cash_Flow + 18000*y_August_Cash_Flow
    + 250000*y_May_Borrowing + 150000*y_June_Borrowing + 350000*y_July_Borrowing
    + 0.65*y_Ratio_Constraint, GRB.MINIMIZE
)

# Add dual constraints for each primal variable
dual_model.addConstr(-y_May_Balance + y_June_Balance + y_July_Balance + y_August_Balance - y_May_Cash_Flow - y_May_Borrowing == -1, "May_Dual_Constraint")
dual_model.addConstr(-1.0175*y_May_Balance + y_June_Balance - y_July_Balance - 1.0225*y_August_Balance + y_June_Cash_Flow + y_June_Borrowing == 1.0225, "June_Dual_Constraint")
dual_model.addConstr(-1.0175*y_May_Balance + 1.0175*y_June_Balance + y_July_Balance - 1.0175*y_August_Balance + y_July_Cash_Flow + y_July_Borrowing == 1.0175, "July_Dual_Constraint")
dual_model.addConstr(-1.0225*y_May_Balance + 1.0175*y_June_Balance + 1.0225*y_July_Balance - y_August_Balance + y_August_Cash_Flow + y_August_Borrowing == 1.0225, "August_Dual_Constraint")
dual_model.addConstr(-0.65*y_Ratio_Constraint == 0, "Ratio_Constraint_Dual")

# Optimally solve the dual problem
dual_model.optimize()

# The status of the model (Optimization Status Codes)
print("Dual Model Status: ", dual_model.status)

# Number of variables in the model
print("Number of Dual Variables: ", dual_model.numVars)

# Value of the objective function
print("Dual Objective Value: ", round(dual_model.objVal, 2))

# Print the dual variables
print(dual_model.printAttr('X'))