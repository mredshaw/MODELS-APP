from gurobipy import GRB
import gurobipy as gb

# Create the optimization model
model = gb.Model("Sunnyshore Bay Financial Planning")

revenues = [180000, 260000, 420000, 580000]
expenses = [300000, 400000, 350000, 200000]
interest_rates = [0.0175, 0.0225, 0.0275]
initial_cash = 140000

##################################################### DECISION VARIABLES #####################################################################

# Amount borrowed in each month under different terms (1m, 2m, 3m)
may1 = model.addVar(vtype=GRB.CONTINUOUS, name="may1")  # 1-month loan in May
may2 = model.addVar(vtype=GRB.CONTINUOUS, name="may2")  # 2-month loan in May
may3 = model.addVar(vtype=GRB.CONTINUOUS, name="may3")  # 3-month loan in May
june1 = model.addVar(vtype=GRB.CONTINUOUS, name="june1")  # 1-month loan in June
june2 = model.addVar(vtype=GRB.CONTINUOUS, name="june2")  # 2-month loan in June
july1 = model.addVar(vtype=GRB.CONTINUOUS, name="july1")  # 1-month loan in July

# Cash balance at the end of each month
cash_balance = model.addVars(4, lb=0, vtype=GRB.CONTINUOUS, name="Cash_Balance")

##################################################### OBJECTIVE FUNCTION #####################################################################

model.setObjective(((may1 * (1 + interest_rates[0])) + (may2 * (1 + interest_rates[1])) + (may3 * (1 + interest_rates[2])) + (june1 * (1 + interest_rates[0])) + (june2 * (1 + interest_rates[1])) + (july1 * (1 + interest_rates[0]))), GRB.MINIMIZE)

##################################################### CONSTRAINTS #####################################################################

# Borrowing limits constraints
model.addConstr(may1 + may2 + may3 <= 250000, "Borrowing_Limit_May")
model.addConstr(june1 + june2 <= 150000, "Borrowing_Limit_June") # 3-month term borrowing is not allowed in June, hence borrow[1, 2] is not included
model.addConstr(july1 <= 350000, "Borrowing_Limit_July") # 2-month and 3-month term borrowings are not allowed in July, hence borrow[2, 1] and borrow[2, 2] are not included

# Cash balance constraints
model.addConstr(cash_balance[0] == initial_cash + revenues[0] - expenses[0] + may1 + may2 + may3, "Cash_Balance_May")
model.addConstr(cash_balance[1] == cash_balance[0] + revenues[1] - expenses[1] - (may1 * (1 + interest_rates[0])) + june1 + june2, "Cash_Balance_June")
model.addConstr(cash_balance[2] == cash_balance[1] + revenues[2] - expenses[2] - (june1 * (1 + interest_rates[0])) - (may2 * (1 + interest_rates[1])) + july1, "Cash_Balance_July")
model.addConstr(cash_balance[3] == cash_balance[2] + revenues[3] - expenses[3] - (july1 * (1 + interest_rates[0])) - (june2 * (1 + interest_rates[1])) -  (may3* (1 + interest_rates[2])), "Cash_Balance_August")

# Minimum cash balance constraints
model.addConstr(cash_balance[0] >= 25000, "Min_Cash_May")
model.addConstr(cash_balance[1] >= 20000, "Min_Cash_June")
#model.addConstr(cash_balance[1] >= 27500, "Min_Cash_June")
model.addConstr(cash_balance[2] >= 35000, "Min_Cash_July")
model.addConstr(cash_balance[3] >= 18000, "Min_Cash_August")

# Constraint on cash balance at end of July
model.addConstr(cash_balance[2] >= 0.65 * (cash_balance[0] + cash_balance[1]), "July_Cash_Balance_Constraint")


# Solve the model
model.optimize()

# Print results
if model.status == GRB.OPTIMAL:
    # Optimal decision variables
    print(f"may1 (May 1-month loan): {may1.x}")
    print(f"may2 (May 2-month loan): {may2.x}")
    print(f"may3 (May 3-month loan): {may3.x}")
    print(f"june1 (June 1-month loan): {june1.x}")
    print(f"june2 (June 2-month loan): {june2.x}")
    print(f"july1 (July 1-month loan): {july1.x}")

    # Optimal objective value
    print(f"Optimal Total Repayment: {model.objVal}")
    
    # Shadow prices
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
else:
    print("Model not solved to optimality.")


##################################################### DUAL MODEL #####################################################################
    


dual_model = gb.Model("Sunnyshore Bay Financial Planning - Dual")

# Dual variables for each constraint in the primal model
d_borrow_limit_may = model.addVar(name="d_borrow_limit_may")
d_borrow_limit_june = model.addVar(name="d_borrow_limit_june")
d_borrow_limit_july = model.addVar(name="d_borrow_limit_july")




y_borrow_limit_may = dual_model.addVar(name="y_borrow_limit_may")
y_borrow_limit_june = dual_model.addVar(name="y_borrow_limit_june")
y_borrow_limit_july = dual_model.addVar(name="y_borrow_limit_july")
y_cash_balance_may = dual_model.addVar(name="y_cash_balance_may")
y_cash_balance_june = dual_model.addVar(name="y_cash_balance_june")
y_cash_balance_july = dual_model.addVar(name="y_cash_balance_july")
y_cash_balance_august = dual_model.addVar(name="y_cash_balance_august")
y_min_cash_may = dual_model.addVar(name="y_min_cash_may")
y_min_cash_june = dual_model.addVar(name="y_min_cash_june")
y_min_cash_july = dual_model.addVar(name="y_min_cash_july")
y_min_cash_august = dual_model.addVar(name="y_min_cash_august")
y_july_cash_balance = dual_model.addVar(name="y_july_cash_balance")

# Dual Objective Function
# It maximizes the sum of the constraints multiplied by their respective dual variables
dual_model.setObjective(
    (250000 * y_borrow_limit_may) + 
    (150000 * y_borrow_limit_june) + 
    (350000 * y_borrow_limit_july) + 
    (initial_cash + revenues[0] - expenses[0] + y_cash_balance_may) + 
    (revenues[1] - expenses[1] + y_cash_balance_june) + 
    (revenues[2] - expenses[2] + y_cash_balance_july) + 
    (revenues[3] - expenses[3] + y_cash_balance_august) + 
    (25000 * y_min_cash_may) + 
    (20000 * y_min_cash_june) + 
    (35000 * y_min_cash_july) + 
    (18000 * y_min_cash_august) + 
    (0.65 * ((initial_cash + revenues[0] - expenses[0] + revenues[1] - expenses[1]) * y_july_cash_balance)), 
    GRB.MAXIMIZE
)

# Dual Constraints
# They correspond to the primal decision variables and their coefficients in the primal constraints
dual_model.addConstr(y_cash_balance_may - y_borrow_limit_may - y_min_cash_may - y_july_cash_balance <= interest_rates[0], "dual_constr_may1")
dual_model.addConstr(y_cash_balance_may - y_borrow_limit_may - y_min_cash_may - y_july_cash_balance <= interest_rates[1], "dual_constr_may2")
dual_model.addConstr(y_cash_balance_may - y_borrow_limit_may - y_min_cash_may - y_july_cash_balance <= interest_rates[2], "dual_constr_may3")
dual_model.addConstr(y_cash_balance_june - y_borrow_limit_june - y_min_cash_june <= interest_rates[0], "dual_constr_june1")
dual_model.addConstr(y_cash_balance_june - y_borrow_limit_june - y_min_cash_june <= interest_rates[1], "dual_constr_june2")
dual_model.addConstr(y_cash_balance_july - y_borrow_limit_july - y_min_cash_july <= interest_rates[0], "dual_constr_july1")

# Solving the dual model
dual_model.optimize()

# Printing dual model results
if dual_model.status == GRB.OPTIMAL:
    print("Optimal Value of Dual Objective: ", dual_model.objVal)
    print("Dual Variable Values:")
    print("y_borrow_limit_may: ", y_borrow_limit_may.x)
    print("y_borrow_limit_june: ", y_borrow_limit_june.x)
    print("y_borrow_limit_july: ", y_borrow_limit_july.x)
    # ... (Print other dual variable values similarly)
else:
    print("Dual Model not solved to optimality.")




