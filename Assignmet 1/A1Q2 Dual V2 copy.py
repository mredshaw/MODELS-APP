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

July_Cash_Balance_Shadow = dual_model.addVar(vtype=GRB.CONTINUOUS, name="July_Cash_Balance_Shadow")


dual_model.setObjective(
    # Borrowing limits
    250000 * Borrowing_Limit_May +
    150000 * Borrowing_Limit_June +
    350000 * Borrowing_Limit_July +

    # Cash balance (initial cash + revenues - expenses)
    (initial_cash + revenues[0] - expenses[0]) * Cash_Balance_May +
    (Cash_Balance_May + revenues[1] - expenses[1]) * Cash_Balance_June +
    (Cash_Balance_June + revenues[2] - expenses[2]) * Cash_Balance_July +
    (Cash_Balance_July + revenues[3] - expenses[3]) * Cash_Balance_August +

    # Minimum cash requirements
    25000 * Min_Cash_May +
    20000 * Min_Cash_June +
    35000 * Min_Cash_July +
    18000 * Min_Cash_August +
    
    # Special cash balance constraint for July
    (0.65 * (Cash_Balance_May + Cash_Balance_June)) * July_Cash_Balance_Shadow,
    
    GRB.MAXIMIZE
)

# Dual Constraints for May Loans
# Dual Constraints for May Loans
dual_model.addConstr(Cash_Balance_May + Borrowing_Limit_May <= 1 + interest_rates[0], "CF_May1")
dual_model.addConstr(Cash_Balance_June + Borrowing_Limit_May <= interest_rates[1], "CF_May2")
dual_model.addConstr(Cash_Balance_July + Borrowing_Limit_May <= interest_rates[2], "CF_May3")

dual_model.addConstr(Cash_Balance_June + Borrowing_Limit_June <= 1 + interest_rates[0], "CF_June1")
dual_model.addConstr(Cash_Balance_July + Borrowing_Limit_June <= interest_rates[1], "CF_June2")

dual_model.addConstr(Cash_Balance_July + Borrowing_Limit_July <= 1 + interest_rates[0], "CF_July1")


dual_model.addConstr(Cash_Balance_June - Cash_Balance_May - Borrowing_Limit_May * (1 + interest_rates[0]) <= 0, "Repayment_Adjust_May1")
dual_model.addConstr(Cash_Balance_July - Cash_Balance_June - Borrowing_Limit_June * (1 + interest_rates[0]) <= 0, "Repayment_Adjust_June1")
dual_model.addConstr(Cash_Balance_August - Cash_Balance_July - Borrowing_Limit_July * (1 + interest_rates[0]) <= 0, "Repayment_Adjust_July1")

dual_model.addConstr(Cash_Balance_July - Cash_Balance_May - Borrowing_Limit_May * (1 + interest_rates[1]) <= 0, "Repayment_Adjust_May2")
dual_model.addConstr(Cash_Balance_August - Cash_Balance_June - Borrowing_Limit_June * (1 + interest_rates[1]) <= 0, "Repayment_Adjust_June2")
dual_model.addConstr(Cash_Balance_August - Cash_Balance_May - Borrowing_Limit_May * (1 + interest_rates[2]) <= 0, "Repayment_Adjust_May3")

dual_model.addConstr(0.65 * (Cash_Balance_May + Cash_Balance_June) - Cash_Balance_July <= July_Cash_Balance_Shadow, "July_Cash_Balance_Dual_Constraint")

# Assuming Min_Cash variables represent the shadow prices for minimum cash constraints
dual_model.addConstr(Min_Cash_May <= 25000, "Min_Cash_Requirement_May")
dual_model.addConstr(Min_Cash_June <= 20000, "Min_Cash_Requirement_June")
dual_model.addConstr(Min_Cash_July <= 35000, "Min_Cash_Requirement_July")
dual_model.addConstr(Min_Cash_August <= 18000, "Min_Cash_Requirement_August")



dual_model.optimize()
print(dual_model.printAttr('X'))