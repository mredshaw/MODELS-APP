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
may1 = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="may1")  # 1-month loan in May
may2 = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="may2")  # 2-month loan in May
may3 = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="may3")  # 3-month loan in May
june1 = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="june1")  # 1-month loan in June
june2 = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="june2")  # 2-month loan in June
july1 = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="july1")  # 1-month loan in July

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
#Variables based on the Borrow Limit Constraints
d_borrow_limit_may = dual_model.addVar(lb=0, name="d_borrow_limit_may")
d_borrow_limit_june = dual_model.addVar(lb=0, name="d_borrow_limit_june")
d_borrow_limit_july = dual_model.addVar(lb=0, name="d_borrow_limit_july")

#Variables based on the Cash Balance Constraints

d_cash_balance_may = dual_model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY,name="d_cash_balance_may")
d_cash_balance_june = dual_model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY,name="d_cash_balance_june")
d_cash_balance_july = dual_model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY,name="d_cash_balance_july")
d_cash_balance_august = dual_model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY,name="d_cash_balance_august")


#Variables based on the Minimum Cash Balance Constraints
d_min_cash_may = dual_model.addVar(ub=0, name="d_min_cash_may")
d_min_cash_june = dual_model.addVar(ub=0, name="d_min_cash_june")
d_min_cash_july = dual_model.addVar(ub=0, name="d_min_cash_july")
d_min_cash_august = dual_model.addVar(ub=0, name="d_min_cash_august")

#Variable based on July cash requirement constraint
d_july_cash_req = dual_model.addVar(ub=0, name="d_july_cash_req")


# Dual Constraints
#Dual Constraints for may1 (1-month loan in May): Affects May and June cash balances. Limited by May borrowing limit.
dual_model.addConstr(d_cash_balance_may - d_borrow_limit_may <= interest_rates[0], "Dual_Constraint_may1_May")
dual_model.addConstr(d_cash_balance_june - d_cash_balance_may - d_borrow_limit_may <= interest_rates[0], "Dual_Constraint_may1_June")

#Dual Constraints for may2 (2-month loan in May): Affects May, June, and July cash balances. Limited by May borrowing limit.
dual_model.addConstr(d_cash_balance_may - d_borrow_limit_may <= interest_rates[1], "Dual_Constraint_may2_May")
dual_model.addConstr(d_cash_balance_june - d_cash_balance_may - d_borrow_limit_may <= interest_rates[1], "Dual_Constraint_may2_June")
dual_model.addConstr(d_cash_balance_july - d_cash_balance_june - d_borrow_limit_may <= interest_rates[1], "Dual_Constraint_may2_July")


#Dual Constraints for may3 (3-month loan in May): Affects May, June, July, and August cash balances. Limited by May borrowing limit.
dual_model.addConstr(d_cash_balance_may - d_borrow_limit_may <= interest_rates[2], "Dual_Constraint_may3_May")
dual_model.addConstr(d_cash_balance_june - d_cash_balance_may - d_borrow_limit_may <= interest_rates[2], "Dual_Constraint_may3_June")
dual_model.addConstr(d_cash_balance_july - d_cash_balance_june - d_borrow_limit_may <= interest_rates[2], "Dual_Constraint_may3_July")
dual_model.addConstr(d_cash_balance_august - d_cash_balance_july - d_borrow_limit_may <= interest_rates[2], "Dual_Constraint_may3_August")

#Dual Constraints for june1 (1-month loan in June): Affects June and July cash balances. Limited by June borrowing limit.
dual_model.addConstr(d_cash_balance_june - d_borrow_limit_june <= interest_rates[0], "Dual_Constraint_june1_June")
dual_model.addConstr(d_cash_balance_july - d_cash_balance_june - d_borrow_limit_june <= interest_rates[0], "Dual_Constraint_june1_July")

#Dual Constraints for june2 (2-month loan in June): Affects June, July, and August cash balances. Limited by June borrowing limit.
dual_model.addConstr(d_cash_balance_june - d_borrow_limit_june <= interest_rates[1], "Dual_Constraint_june2_June")
dual_model.addConstr(d_cash_balance_july - d_cash_balance_june - d_borrow_limit_june <= interest_rates[1], "Dual_Constraint_june2_July")
dual_model.addConstr(d_cash_balance_august - d_cash_balance_july - d_borrow_limit_june <= interest_rates[1], "Dual_Constraint_june2_August")

#Dual Constraints for july1 (1-month loan in July): Affects July and August cash balances. Limited by July borrowing limit.
dual_model.addConstr(d_cash_balance_july - d_borrow_limit_july - d_july_cash_req <= interest_rates[0], "Dual_Constraint_july1_July")
dual_model.addConstr(d_cash_balance_august - d_cash_balance_july - d_borrow_limit_july <= interest_rates[0], "Dual_Constraint_july1_August")

dual_obj = (
    d_borrow_limit_may * 250000 +
    d_borrow_limit_june * 150000 +
    d_borrow_limit_july * 350000 +
    d_cash_balance_may * (initial_cash + revenues[0] - expenses[0]) +
    d_cash_balance_june * (revenues[1] - expenses[1]) +
    d_cash_balance_july * (revenues[2] - expenses[2]) +
    d_cash_balance_august * (revenues[3] - expenses[3]) +
    d_min_cash_may * 25000 +
    d_min_cash_june * 20000 +
    d_min_cash_july * 35000 +
    d_min_cash_august * 18000 +
    d_july_cash_req * (0.65 * (initial_cash + revenues[0] - expenses[0] + revenues[1] - expenses[1]))
)
dual_model.setObjective(dual_obj, GRB.MAXIMIZE)



# Solving the dual model
dual_model.optimize()

# Check if the model was solved to optimality
if dual_model.status == GRB.OPTIMAL:
    # Print the optimal value of the dual objective function
    print(f"Optimal Value of Dual Objective Function: {dual_model.objVal}")

    # Print the values of the dual variables
    print("\nDual Variable Values:")
    print(f"d_borrow_limit_may: {d_borrow_limit_may.x}")
    print(f"d_borrow_limit_june: {d_borrow_limit_june.x}")
    print(f"d_borrow_limit_july: {d_borrow_limit_july.x}")
    print(f"d_cash_balance_may: {d_cash_balance_may.x}")
    print(f"d_cash_balance_june: {d_cash_balance_june.x}")
    print(f"d_cash_balance_july: {d_cash_balance_july.x}")
    print(f"d_cash_balance_august: {d_cash_balance_august.x}")
    print(f"d_min_cash_may: {d_min_cash_may.x}")
    print(f"d_min_cash_june: {d_min_cash_june.x}")
    print(f"d_min_cash_july: {d_min_cash_july.x}")
    print(f"d_min_cash_august: {d_min_cash_august.x}")
    print(f"d_july_cash_req: {d_july_cash_req.x}")
else:
    print("Model not solved to optimality.")




