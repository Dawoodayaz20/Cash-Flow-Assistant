from db.mongo import database;
from agents import Agent, Runner, RunContextWrapper, function_tool
from bson import ObjectId
from FloAgent.context import UserFinanceContext
from datetime import datetime

@function_tool
def get_transactions(ctx: RunContextWrapper[UserFinanceContext]):
    """Fetch all transactions for the current user."""

    print("🔧 [TOOL CALL] get_transactions was executed")
    print(f"   User ID: {ctx.context.userId}")

    print(f"DB name: {database.name}")
    print(f"Collections: {database.list_collection_names()}")

    userId = ctx.context.userId
    transactions = list(database.transactions.find(
        {"userId": ObjectId(userId)},
        {"_id": 0, "userId": 0}
    ))
    if not transactions:
        return "No transactions found for this user."
    
    print(f"   → Returned {len(transactions)} transactions")
    return transactions

@function_tool
def get_financial_summary(ctx: RunContextWrapper[UserFinanceContext]):
   """ Get total income, total expenses, and net balance for the current user. """
   
   userId = ctx.context.userId
   transactions = list(database.transactions.find(
      {"userId": ObjectId(userId)},
      {"type": 1, "amount": 1, "_id": 0}
   ))

   if not transactions:
        return "No transactions found."
   
   total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
   total_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
   net_balance = total_income - total_expenses

   return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": net_balance,
        "status": "surplus" if net_balance >= 0 else "deficit"
    }

@function_tool
def get_spending_by_category(ctx: RunContextWrapper[UserFinanceContext]):
    """Get total amount spent per category for the current user."""
    
    print("🔧 [TOOL CALL] get_spending_by_category was executed")
    
    userId = ctx.context.userId
    transactions = list(database.transactions.find(
        {"userId": ObjectId(userId), "type": "expense"},
        {"category": 1, "amount": 1, "_id": 0}
    ))
    
    if not transactions:
        return "No expense transactions found."
    
    breakdown = {}
    for t in transactions:
        category = t.get("category", "Uncategorized")
        breakdown[category] = breakdown.get(category, 0) + t["amount"]
    
    return breakdown

@function_tool
def get_recurring_transactions(ctx: RunContextWrapper[UserFinanceContext]):
    """Fetch all recurring transactions for the current user."""
    
    print("🔧 [TOOL CALL] get_recurring_transactions was executed")
    
    userId = ctx.context.userId
    transactions = list(database.transactions.find(
        {"userId": ObjectId(userId), "recurring": True},
        {"_id": 0, "userId": 0}
    ))
    
    if not transactions:
        return "No recurring transactions found."
    
    print(f"   → Returned {len(transactions)} recurring transactions")
    return transactions

@function_tool
def forecast_balance(ctx: RunContextWrapper[UserFinanceContext]):
    """Fetch current balance and all recurring transactions so the agent can forecast future balance."""
    
    print("🔧 [TOOL CALL] forecast_balance was executed")
    
    userId = ctx.context.userId
    
    all_transactions = list(database.transactions.find(
        {"userId": ObjectId(userId)},
        {"type": 1, "amount": 1, "_id": 0}
    ))
    
    current_balance = sum(
        t["amount"] if t["type"] == "income" else -t["amount"]
        for t in all_transactions
    )
    
    recurring = list(database.transactions.find(
        {"userId": ObjectId(userId), "recurring.isRecurring": True},
        {"_id": 0, "userId": 0}
    ))
    
    return {
        "current_balance": round(current_balance, 2),
        "recurring_transactions": recurring
    }

@function_tool
def detect_unusual_spending(ctx: RunContextWrapper[UserFinanceContext]):
    """Compare current month's spending per category against user-defined budget limits."""
    
    print("🔧 [TOOL CALL] detect_unusual_spending was executed")
    
    userId = ctx.context.userId
    
    # Get budget limits from settings
    settings = database.settings.find_one(
        {"userId": ObjectId(userId)},
        {"budgetLimits": 1, "_id": 0}
    )
    
    if not settings:
        return "No settings found for this user."
    
    budget_limits = settings.get("budgetLimits", {})
    
    # Get current month's expenses
    now = datetime.timezone.utcnow()
    start_of_month = datetime(now.year, now.month, 1)
    
    expenses = list(database.transactions.find(
        {
            "userId": ObjectId(userId),
            "type": "expense",
            "date": {"$gte": start_of_month}
        },
        {"category": 1, "amount": 1, "_id": 0}
    ))
    
    # Sum by category
    spending = {}
    for t in expenses:
        cat = t.get("category", "Other")
        spending[cat] = spending.get(cat, 0) + t["amount"]
    
    # Compare against budget limits
    flagged = []
    for category, spent in spending.items():
        limit = budget_limits.get(category)
        if limit and spent > limit:
            flagged.append({
                "category": category,
                "spent": round(spent, 2),
                "limit": limit,
                "over_by": round(spent - limit, 2)
            })
    
    if not flagged:
        return "No unusual spending detected this month."
    
    return flagged