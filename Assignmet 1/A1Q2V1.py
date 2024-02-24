from gurobipy import GRB
import gurobipy as gb

# Create the optimization model
model = gb.Model("Sunnyshore Bay Financial Planning")

# Monthly revenues and expenses
revenues = [180000, 260000, 420000, 580000]
expenses = [300000, 400000, 350000, 200000]
interest_rates = [0.0175, 0.0225, 0.0275]
initial_cash = 140000

##################################################### DECISION VARIABLES #####################################################################

# Amount borrowed in each month under different terms (1m, 2m, 3m)
borrow = model.addVars(4, 3, lb=0, vtype=GRB.CONTINUOUS, name="Borrow")

# Cash balance at the end of each month
cash_balance = model.addVars(4, lb=0, vtype=GRB.CONTINUOUS, name="Cash_Balance")

##################################################### OBJECTIVE FUNCTION #####################################################################

total_repayment = (
    # Repayments for May
    borrow[0, 0] * (1 + 0.0175) + borrow[0, 1] * (1 + 0.0225) + borrow[0, 2] * (1 + 0.0275) +  # All loan options are available in May

    # Repayments for June
    borrow[1, 0] * (1 + 0.0175) + borrow[1, 1] * (1 + 0.0225) +  # only 1 month and 2 month loan options are available in June

    # Repayments for July
    borrow[2, 0] * (1 + 0.0175)  # Only 1 month loan option is available in July
)
model.setObjective(total_repayment, GRB.MINIMIZE)

##################################################### CONSTRAINTS #####################################################################

# Add the cash balance constraints
model.addConstr(cash_balance[0] == initial_cash + revenues[0] - expenses[0] + borrow[0, 0] + borrow[0, 1] + borrow[0, 2], "Cash_Balance_May")
model.addConstr(cash_balance[1] == cash_balance[0] + revenues[1] - expenses[1] - borrow[0, 0] * (1 + 0.0175) + borrow[1, 0] + borrow[1, 1], "Cash_Balance_June")
model.addConstr(cash_balance[2] == cash_balance[1] + revenues[2] - expenses[2] - borrow[1, 0] * (1 + 0.0175) - borrow[0, 1] * (1 + 0.0225) + borrow[2, 0], "Cash_Balance_July")
model.addConstr(cash_balance[3] == cash_balance[2] + revenues[3] - expenses[3] - borrow[2, 0] * (1 + 0.0175) - borrow[1, 1] * (1 + 0.0225) - borrow[0, 2] * (1 + 0.0275), "Cash_Balance_August")

# Borrowing limits constraints
model.addConstr(borrow[0, 0] + borrow[0, 1] + borrow[0, 2] <= 250000, "Borrowing_Limit_May")
model.addConstr(borrow[1, 0] + borrow[1, 1] <= 150000, "Borrowing_Limit_June") # 3-month term borrowing is not allowed in June, hence borrow[1, 2] is not included
model.addConstr(borrow[2, 0] <= 350000, "Borrowing_Limit_July") # 2-month and 3-month term borrowings are not allowed in July, hence borrow[2, 1] and borrow[2, 2] are not included


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

print("Number of Constraints: ", model.numConstrs)
# Print model status
print("Model Status: ", model.status)

# Check if the model was solved to optimality
if model.status == GRB.OPTIMAL:
    # Print the value of the objective function
    print("Optimal Total Repayment: ", model.objVal)

    # Print the borrowed amounts
    print("\nBorrowed Amounts:")
    for m in range(4):
        for t in range(3):
            if borrow[m, t].X > 0:
                print(f" Month {m+1}, Term {t+1} months: ${borrow[m, t].X:.2f}")

    # Print the cash balances
    print("\nCash Balances:")
    for m in range(4):
        print(f" End of Month {m+1}: ${cash_balance[m].X:.2f}")

    # Print all decision variables
    print("\nDecision Variables:")
    for var in model.getVars():
        print(f"{var.varName}: {var.X}")
else:
    print("Model not solved to optimality")


##################################################### DUAL MODEL #####################################################################
    


# Dual Variables
d_cash_balance = model.addVars(4, lb=-GRB.INFINITY, name="d_cash_balance")
d_borrow_limit_may = model.addVar(lb=-GRB.INFINITY, name="d_borrow_limit_may")
d_borrow_limit_june = model.addVar(lb=-GRB.INFINITY, name="d_borrow_limit_june")
d_borrow_limit_july = model.addVar(lb=-GRB.INFINITY, name="d_borrow_limit_july")
d_min_cash = model.addVars(4, lb=-GRB.INFINITY, name="d_min_cash")
d_july_cash_req = model.addVar(lb=-GRB.INFINITY, name="d_july_cash_req")
min_cash_balances = [25000, 20000, 35000, 18000]


# Dual Objective Function
dual_obj = (
    d_cash_balance[0] * (initial_cash + revenues[0] - expenses[0]) +
    d_cash_balance[1] * (revenues[1] - expenses[1]) +
    d_cash_balance[2] * (revenues[2] - expenses[2]) +
    d_cash_balance[3] * (revenues[3] - expenses[3]) +
    d_borrow_limit_may * 250000 +
    d_borrow_limit_june * 150000 +
    d_borrow_limit_july * 350000 +
    sum(d_min_cash[i] * min_cash_balances[i] for i in range(4)) +
    d_july_cash_req * (0.65 * (initial_cash + revenues[0] - expenses[0] + revenues[1] - expenses[1]))
)
model.setObjective(dual_obj, GRB.MAXIMIZE)


# Dual Constraints for Borrowing
for i in range(4):
    for t in range(3):
        if i - t >= 0:  # Ensure the borrowing term does not exceed the month
            # Retrieve the appropriate dual variable for borrowing limit constraints
            borrow_limit_dual_var = d_borrow_limit_may if i - t == 0 else d_borrow_limit_june if i - t == 1 else d_borrow_limit_july if i - t == 2 else 0
            
            constraint_expr = d_cash_balance[i - t] - d_cash_balance[i] - borrow_limit_dual_var
            if i == 2 and t == 0:
                constraint_expr -= d_july_cash_req
            
            model.addConstr(
                constraint_expr <= interest_rates[t],
                f"Dual_Constraint_borrow_{i+1}_{t+1}"
            )




# Solve the dual model
model.optimize()

# Check if the model was solved to optimality
if model.status == GRB.OPTIMAL:
    # Print the value of the dual objective function
    print("Optimal Value of Dual Objective: ", model.objVal)

    # Print the shadow prices (dual variable values)
    print("\nShadow Prices:")
    print("d_cash_balance May: ", d_cash_balance[0].X)
    print("d_cash_balance June: ", d_cash_balance[1].X)
    print("d_cash_balance July: ", d_cash_balance[2].X)
    print("d_cash_balance August: ", d_cash_balance[3].X)
    print("d_borrow_limit May: ", d_borrow_limit_may.X)
    print("d_borrow_limit June: ", d_borrow_limit_june.X)
    print("d_borrow_limit July: ", d_borrow_limit_july.X)
    for i in range(4):
        print(f"d_min_cash Month {i+1}: ", d_min_cash[i].X)
    print("d_july_cash_req: ", d_july_cash_req.X)

else:
    print("Model not solved to optimality")




