from gurobipy import GRB
import gurobipy as gb

# Create the optimization model
model = gb.Model("Sunnyshore Bay Financial Planning")

# Monthly revenues and expenses
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
model.addConstr(cash_balance[0] == initial_cash + 180000 - 300000 + borrow[0, 0] + borrow[0, 1] + borrow[0, 2], "Cash_Balance_May")
model.addConstr(cash_balance[1] == cash_balance[0] + 260000 - 400000 - borrow[0, 0] * (1 + 0.0175) + borrow[1, 0] + borrow[1, 1], "Cash_Balance_June")
model.addConstr(cash_balance[2] == cash_balance[1] + 420000 - 350000 - borrow[1, 0] * (1 + 0.0175) - borrow[0, 1] * (1 + 0.0225) + borrow[2, 0], "Cash_Balance_July")
model.addConstr(cash_balance[3] == cash_balance[2] + 580000 - 200000 - borrow[2, 0] * (1 + 0.0175) - borrow[1, 1] * (1 + 0.0225) - borrow[0, 2] * (1 + 0.0275), "Cash_Balance_August")

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