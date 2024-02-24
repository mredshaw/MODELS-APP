from gurobipy import GRB
import gurobipy as gb


revenues = [180000, 260000, 420000, 580000]
expenses = [300000, 400000, 350000, 200000]
interest_rates = [0.0175, 0.0225, 0.0275]
initial_cash = 140000


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
# Dual Constraints for may1 (1-month loan in May): Affects May and June cash balances. Limited by May borrowing limit.
dual_model.addConstr(d_cash_balance_may - d_borrow_limit_may <= interest_rates[0], "Dual_Constraint_may1_May")
dual_model.addConstr(-d_cash_balance_june + d_cash_balance_may - d_borrow_limit_may <= 0, "Dual_Constraint_may1_June")

# Dual Constraints for may2 (2-month loan in May): Affects May, June, and July cash balances. Limited by May borrowing limit.
dual_model.addConstr(d_cash_balance_may - d_borrow_limit_may <= interest_rates[1], "Dual_Constraint_may2_May")
dual_model.addConstr(-d_cash_balance_june + d_cash_balance_may - d_borrow_limit_may <= 0, "Dual_Constraint_may2_June")
dual_model.addConstr(-d_cash_balance_july + d_cash_balance_june - d_borrow_limit_may <= 0, "Dual_Constraint_may2_July")

# Dual Constraints for may3 (3-month loan in May): Affects May, June, July, and August cash balances. Limited by May borrowing limit.
dual_model.addConstr(d_cash_balance_may - d_borrow_limit_may <= interest_rates[2], "Dual_Constraint_may3_May")
dual_model.addConstr(-d_cash_balance_june + d_cash_balance_may - d_borrow_limit_may <= 0, "Dual_Constraint_may3_June")
dual_model.addConstr(-d_cash_balance_july + d_cash_balance_june - d_borrow_limit_may <= 0, "Dual_Constraint_may3_July")
dual_model.addConstr(-d_cash_balance_august + d_cash_balance_july - d_borrow_limit_may <= 0, "Dual_Constraint_may3_August")

# Dual Constraints for june1 (1-month loan in June): Affects June and July cash balances. Limited by June borrowing limit.
dual_model.addConstr(d_cash_balance_june - d_borrow_limit_june <= interest_rates[0], "Dual_Constraint_june1_June")
dual_model.addConstr(-d_cash_balance_july + d_cash_balance_june - d_borrow_limit_june <= 0, "Dual_Constraint_june1_July")

# Dual Constraints for june2 (2-month loan in June): Affects June, July, and August cash balances. Limited by June borrowing limit.
dual_model.addConstr(d_cash_balance_june - d_borrow_limit_june <= interest_rates[1], "Dual_Constraint_june2_June")
dual_model.addConstr(-d_cash_balance_july + d_cash_balance_june - d_borrow_limit_june <= 0, "Dual_Constraint_june2_July")
dual_model.addConstr(-d_cash_balance_august + d_cash_balance_july - d_borrow_limit_june <= 0, "Dual_Constraint_june2_August")

# Dual Constraints for july1 (1-month loan in July): Affects July and August cash balances. Limited by July borrowing limit.
dual_model.addConstr(d_cash_balance_july - d_borrow_limit_july - d_july_cash_req <= interest_rates[0], "Dual_Constraint_july1_July")
dual_model.addConstr(-d_cash_balance_august + d_cash_balance_july - d_borrow_limit_july <= 0, "Dual_Constraint_july1_August")

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


dual_model.setParam('InfUnbdInfo', 1)
# Solving the dual model
dual_model.optimize()

# Check if the model was solved to optimality
if dual_model.status == GRB.INF_OR_UNBD:
    dual_model.computeIIS()  # Compute Irreducible Inconsistent Subsystem
    dual_model.write("dual_model.ilp")  # Write the IIS to a file
    print("IIS written to file 'dual_model.ilp'")
    print("The model is either infeasible or unbounded.")
elif dual_model.status == GRB.OPTIMAL:
    print(f"Optimal Value of Dual Objective Function: {dual_model.objVal}")
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