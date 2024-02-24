from gurobipy import GRB
import gurobipy as gb

# Create the optimization model
dual_model = gb.Model("Sunnyshore Bay Financial Planning Dual")

revenues = [180000, 260000, 420000, 580000]
expenses = [300000, 400000, 350000, 200000]
interest_rates = [0.0175, 0.0225, 0.0275]
initial_cash = 140000

# Create Variables

Borrowing_Limit_May = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="Borrowing_Limit_May")
Borrowing_Limit_June = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="Borrowing_Limit_June")
Borrowing_Limit_July = dual_model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="Borrowing_Limit_July")

Cash_Balance_May = dual_model.addVar(vtype=GRB.CONTINUOUS, name="Cash_Balance_May")
Cash_Balance_June = dual_model.addVar(vtype=GRB.CONTINUOUS, name="Cash_Balance_June")
Cash_Balance_July = dual_model.addVar(vtype=GRB.CONTINUOUS, name="Cash_Balance_July")
Cash_Balance_August = dual_model.addVar(vtype=GRB.CONTINUOUS, name="Cash_Balance_August")

Min_Cash_May = dual_model.addVar(ub=0, vtype=GRB.CONTINUOUS, name="Min_Cash_May")
Min_Cash_June = dual_model.addVar(ub=0, vtype=GRB.CONTINUOUS, name="Min_Cash_June")
Min_Cash_July = dual_model.addVar(ub=0, vtype=GRB.CONTINUOUS, name="Min_Cash_July")
Min_Cash_August = dual_model.addVar(ub=0, vtype=GRB.CONTINUOUS, name="Min_Cash_August")

July_Cash_Balance_Constraint = dual_model.addVar(ub=0, vtype=GRB.CONTINUOUS, name="July_Cash_Balance_Constraint")


dual_model.setObjective((25000 * Borrowing_Limit_May) +
                   (150000 * Borrowing_Limit_June) +
                   (350000 * Borrowing_Limit_July) +
                   (25000 * Min_Cash_May) +
                   (20000 * Min_Cash_June) +
                   (35000 * Min_Cash_July) +
                   (18000 * Min_Cash_August)+
                   ((initial_cash + revenues[0] - expenses[0]) * Cash_Balance_May) +
                   ((Cash_Balance_May + revenues[1] - expenses[1]) * Cash_Balance_June) +
                   ((Cash_Balance_June + revenues[2] - expenses[2]) * Cash_Balance_July) +
                   ((Cash_Balance_July + revenues[3] - expenses[3]) * Cash_Balance_August) +
                   (0.65 * (initial_cash + revenues[0] - expenses[0] + revenues[1] - expenses[1]) * July_Cash_Balance_Constraint), gb.GRB.MAXIMIZE)



# Dual Constraints for May Loans
# Dual Constraints for May Loans
dual_model.addConstr(Cash_Balance_May - Borrowing_Limit_May <= interest_rates[0], "Dual_Constraint_may1_May")
dual_model.addConstr(Cash_Balance_June - Cash_Balance_May - Borrowing_Limit_May <= 0, "Dual_Constraint_may1_June")

dual_model.addConstr(Cash_Balance_May - Borrowing_Limit_May <= interest_rates[1], "Dual_Constraint_may2_May")
dual_model.addConstr(Cash_Balance_June - Cash_Balance_May - Borrowing_Limit_May <= 0, "Dual_Constraint_may2_June")
dual_model.addConstr(Cash_Balance_July - Cash_Balance_June - Borrowing_Limit_May <= 0, "Dual_Constraint_may2_July")

dual_model.addConstr(Cash_Balance_May - Borrowing_Limit_May <= interest_rates[2], "Dual_Constraint_may3_May")
dual_model.addConstr(Cash_Balance_June - Cash_Balance_May - Borrowing_Limit_May <= 0, "Dual_Constraint_may3_June")
dual_model.addConstr(Cash_Balance_July - Cash_Balance_June - Borrowing_Limit_May <= 0, "Dual_Constraint_may3_July")
dual_model.addConstr(Cash_Balance_August - Cash_Balance_July - Borrowing_Limit_May <= 0, "Dual_Constraint_may3_August")

# Dual Constraints for June Loans
dual_model.addConstr(Cash_Balance_June - Borrowing_Limit_June <= interest_rates[0], "Dual_Constraint_june1_June")
dual_model.addConstr(Cash_Balance_July - Cash_Balance_June - Borrowing_Limit_June <= 0, "Dual_Constraint_june1_July")

dual_model.addConstr(Cash_Balance_June - Borrowing_Limit_June <= interest_rates[1], "Dual_Constraint_june2_June")
dual_model.addConstr(Cash_Balance_July - Cash_Balance_June - Borrowing_Limit_June <= 0, "Dual_Constraint_june2_July")
dual_model.addConstr(Cash_Balance_August - Cash_Balance_July - Borrowing_Limit_June <= 0, "Dual_Constraint_june2_August")

# Dual Constraints for July Loan
dual_model.addConstr(Cash_Balance_July - Borrowing_Limit_July <= interest_rates[0], "Dual_Constraint_july1_July")
dual_model.addConstr(Cash_Balance_August - Cash_Balance_July - Borrowing_Limit_July <= 0, "Dual_Constraint_july1_August")



dual_model.optimize()
print(dual_model.printAttr('X'))