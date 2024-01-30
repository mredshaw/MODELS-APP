from gurobipy import GRB
import gurobipy as gb

model = gb.Model("Sunnyshore Bay Financial Planning")

revenues = [180000, 260000, 420000, 580000]
expenses = [300000, 400000, 350000, 200000]
interest_rates = [0.0175, 0.0225, 0.0275]
initial_cash = 140000

############################################################     VARIABLES        #####################################################################

may1 = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="may1")  # 1-month loan in May
may2 = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="may2")  # 2-month loan in May
may3 = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="may3")  # 3-month loan in May
june1 = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="june1")  # 1-month loan in June
june2 = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="june2")  # 2-month loan in June
july1 = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="july1")  # 1-month loan in July


cash_balance_may = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="Cash_Balance_May")
cash_balance_june = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="Cash_Balance_June")
cash_balance_july = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="Cash_Balance_July")
cash_balance_august = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="Cash_Balance_August")



##################################################### OBJECTIVE FUNCTION #####################################################################


model.setObjective(
    may1 * (1 + interest_rates[0]) + 
    may2 * (1 + interest_rates[1]) + 
    may3 * (1 + interest_rates[2]) + 
    june1 * (1 + interest_rates[0]) + 
    june2 * (1 + interest_rates[1]) + 
    july1 * (1 + interest_rates[0]), GRB.MINIMIZE
)



##################################################### CONSTRAINTS #####################################################################


# Borrowing limits constraints
model.addConstr(may1 + may2 + may3 <= 250000, "Borrowing_Limit_May")
model.addConstr(june1 + june2 <= 150000, "Borrowing_Limit_June") # 3-month term borrowing is not allowed in June, hence borrow[1, 2] is not included
model.addConstr(july1 <= 350000, "Borrowing_Limit_July") # 2-month and 3-month term borrowings are not allowed in July, hence borrow[2, 1] and borrow[2, 2] are not included

# Cash balance constraints
model.addConstr(cash_balance_may == initial_cash + revenues[0] - expenses[0] + may1 + may2 + may3, "Cash_Balance_May")
model.addConstr(cash_balance_june == cash_balance_may + revenues[1] - expenses[1] - (may1 * (1 + interest_rates[0])) + june1 + june2, "Cash_Balance_June")
model.addConstr(cash_balance_july == cash_balance_june + revenues[2] - expenses[2] - (june1 * (1 + interest_rates[0])) - (may2 * (1 + interest_rates[1])) + july1, "Cash_Balance_July")
model.addConstr(cash_balance_august == cash_balance_july + revenues[3] - expenses[3] - (july1 * (1 + interest_rates[0])) - (june2 * (1 + interest_rates[1])) -  (may3* (1 + interest_rates[2])), "Cash_Balance_August")


# Minimum cash balance constraints
model.addConstr(cash_balance_may >= 25000, "Min_Cash_May")
model.addConstr(cash_balance_june >= 20000, "Min_Cash_June")
#model.addConstr(cash_balance_june >= 27500, "Min_Cash_June")
model.addConstr(cash_balance_july >= 35000, "Min_Cash_July")
model.addConstr(cash_balance_august >= 18000, "Min_Cash_August")

# Constraint on cash balance at end of July
model.addConstr(cash_balance_july >= 0.65 * (cash_balance_may + cash_balance_june), "July_Cash_Balance_Constraint")


##################################################### OPTIMIZE & PRINT RESULTS #####################################################################


model.optimize()

print("PRIMAL OPTIMAL OBJECTIVE VALUE",model.objVal)
print(model.printAttr('X'))


print("\n")
print("Shadow Prices:")
print(f"Borrowing_Limit_May: {model.getConstrByName('Borrowing_Limit_May').Pi}")
print(f"Borrowing_Limit_June: {model.getConstrByName('Borrowing_Limit_June').Pi}")
print(f"Borrowing_Limit_July: {model.getConstrByName('Borrowing_Limit_July').Pi}")
print(f"Cash_Balance_May: {model.getConstrByName('Cash_Balance_May').Pi}")
print(f"Cash_Balance_June: {model.getConstrByName('Cash_Balance_June').Pi}")
print(f"Cash_Balance_July: {model.getConstrByName('Cash_Balance_July').Pi}")
print(f"Cash_Balance_August: {model.getConstrByName('Cash_Balance_August').Pi}")
print(f"Min_Cash_May: {model.getConstrByName('Min_Cash_May').Pi}")
print(f"Min_Cash_June: {model.getConstrByName('Min_Cash_June').Pi}")
print(f"Min_Cash_July: {model.getConstrByName('Min_Cash_July').Pi}")
print(f"Min_Cash_August: {model.getConstrByName('Min_Cash_August').Pi}")
print(f"July_Cash_Balance_Constraint: {model.getConstrByName('July_Cash_Balance_Constraint').Pi}")






##################################################### DUAL MODEL #####################################################################
  

dual_model = gb.Model("Sunnyshore Bay Financial Planning Dual")

revenues = [180000, 260000, 420000, 580000]
expenses = [300000, 400000, 350000, 200000]
interest_rates = [0.0175, 0.0225, 0.0275]
initial_cash = 140000

############################################################ VARIABLES #####################################################################



#Setting the lower bounds or upper bounds based on the nature of the corresponding primal constraint 
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

July_Cash_Balance_Constraint = dual_model.addVar(vtype=GRB.CONTINUOUS, name="July_Cash_Balance_Shadow")


##################################################### OBJECTIVE FUNCTION #####################################################################


#Setting the dual objective function based on the primal constraints, using the constraint value as the coefficient of the corresponding dual variable

# Dual objective function
dual_model.setObjective(
    # Borrowing limits
    250000 * Borrowing_Limit_May +
    150000 * Borrowing_Limit_June +
    350000 * Borrowing_Limit_July +
    
    # Cash balance constraints (RHS values are initial_cash + revenues - expenses for each month)
    (initial_cash + revenues[0] - expenses[0]) * Cash_Balance_May +
    (Cash_Balance_May + revenues[1] - expenses[1]) * Cash_Balance_June +
    (Cash_Balance_June + revenues[2] - expenses[2]) * Cash_Balance_July +
    (Cash_Balance_July + revenues[3] - expenses[3]) * Cash_Balance_August +
    
    # Minimum cash requirements
    25000 * Min_Cash_May +
    20000 * Min_Cash_June +
    35000 * Min_Cash_July +
    18000 * Min_Cash_August +
    
    # Special July cash balance constraint
    (0.65 * (Cash_Balance_May + Cash_Balance_June)) * July_Cash_Balance_Constraint,
    
    GRB.MAXIMIZE
)



##################################################### CONSTRAINTS #####################################################################


# Setting the dual constraints based on the primal variables and the primal constraints

# Dual Constraints for Monthly Cash Flows
# Constraint for may1
dual_model.addConstr(Cash_Balance_June <= 1 + interest_rates[0], "Dual_Constraint_may1")

# Constraint for may2
dual_model.addConstr(Cash_Balance_July <=  interest_rates[1], "Dual_Constraint_may2")

# Constraint for may3
dual_model.addConstr(Cash_Balance_August <= interest_rates[2], "Dual_Constraint_may3")

# Constraint for june1
dual_model.addConstr(Cash_Balance_July - Cash_Balance_June <= 1 + interest_rates[0], "Dual_Constraint_june1")

# Constraint for june2
dual_model.addConstr(Cash_Balance_August - Cash_Balance_June <=  interest_rates[1], "Dual_Constraint_june2")

# Constraint for july1
dual_model.addConstr(Cash_Balance_August - Cash_Balance_July <= 1 + interest_rates[0], "Dual_Constraint_july1")


# Dual Constraints for loan repayments
dual_model.addConstr(Cash_Balance_June - Cash_Balance_May - Borrowing_Limit_May * (1 + interest_rates[0]) <= 0, "Repayment_Adjust_May1")
dual_model.addConstr(Cash_Balance_July - Cash_Balance_June - Borrowing_Limit_June * (1 + interest_rates[0]) <= 0, "Repayment_Adjust_June1")
dual_model.addConstr(Cash_Balance_August - Cash_Balance_July - Borrowing_Limit_July * (1 + interest_rates[0]) <= 0, "Repayment_Adjust_July1")

dual_model.addConstr(Cash_Balance_July - Cash_Balance_May - Borrowing_Limit_May * (1 + interest_rates[1]) <= 0, "Repayment_Adjust_May2")
dual_model.addConstr(Cash_Balance_August - Cash_Balance_June - Borrowing_Limit_June * (1 + interest_rates[1]) <= 0, "Repayment_Adjust_June2")

dual_model.addConstr(Cash_Balance_August - Cash_Balance_May - Borrowing_Limit_May * (1 + interest_rates[2]) <= 0, "Repayment_Adjust_May3")


# Dual Constraint for July Cash Blanace

dual_model.addConstr(0.65 * (Cash_Balance_May + Cash_Balance_June) - Cash_Balance_July <= July_Cash_Balance_Constraint, "July_Cash_Balance_Dual_Constraint")




##################################################### OPTIMIZE & PRINT RESULTS #####################################################################



dual_model.optimize()

print("DUAL OPTIMAL OBJECTIVE VALUE",dual_model.objVal)
print(dual_model.printAttr('X'))




