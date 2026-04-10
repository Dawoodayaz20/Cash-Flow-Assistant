from agents import Agent, RunContextWrapper, function_tool
from db.mongo import database
from FloAgent.context import UserFinanceContext
from bson import ObjectId

@function_tool
def fetch_settings(ctx: RunContextWrapper[UserFinanceContext]):
    """Fetch all settings for the current user."""

    print("🔧 [TOOL CALL] get_settings was executed!")
    print(f"   User ID: {ctx.context.userId}")

    print(f"DB name: {database.name}")
    print(f"Collections: {database.list_collection_names()}")

    userId = ctx.context.userId
    settings = list(database.settings.find(
        {"userId": ObjectId(userId)},
        {"_id": 0, "userId": 0}
    ))
    if not settings:
        return "No saved settings found for this user."
    
    print(f"   → Returned {len(settings)} transactions")
    return settings