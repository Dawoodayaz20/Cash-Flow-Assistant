from agents import Agent, Runner, set_tracing_disabled, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel, function_tool, RunContextWrapper
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv
import asyncio
import os
from FloAgent.context import UserFinanceContext
from db.mongo import database
from bson import ObjectId

# RunHooks, AgentHooks,

load_dotenv(find_dotenv())
set_tracing_disabled(disabled=True)

API_KEY = os.getenv("API_KEY")

external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True,
)

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
        {"_id": 0, "userId": 0}  # exclude these fields
    ))
    if not transactions:
        return "No transactions found for this user."
    
    print(f"   → Returned {len(transactions)} transactions")  # Nice to see
    return transactions

# @function_tool
# def get_user_reminders(userId: str):
#     """Fetch user's reminders."""
#     try:
#         result = db.list_documents(
#             DOC_ID, 
#             "reminders",
#             [Query.equal("userID", userId)]
#             )
#         return result["documents"]
#     except Exception as e:
#         print(f"There was an error calling the tool:{e}")

# @function_tool
# def get_user_medicines(userId: str):
#     """Fetch user's medicines."""
#     try:
#         result = db.list_documents(
#             DOC_ID, 
#             "medicines",
#             [Query.equal("userID", userId)]
#             )
#         return result["documents"]
#     except Exception as e:
#         print(f"There was an error calling the tool:{e}")

async def kickoff(question: str, userID: str, name: str, email: str):
  
#   name: str = 'Dawood Ayaz'
#   email : str = 'dawoodayaz18@gmail.com'

  try:
    user_context = UserFinanceContext(
            userId=userID,
            name=name,
            email=email
        )
    
    CashFlow_Assistant: Agent = Agent[UserFinanceContext](
    name="Cash Flow Assistant",
    instructions=f"You are CashFlow Assistant, a smart and friendly personal finance assistant. You have access to their complete financial data through the tools provided",
    model=model,
    tools=[get_transactions]
    )

    result = await Runner.run(
      CashFlow_Assistant, 
      question,
      run_config=config,
      context= user_context 
    )
    print(result.final_output)
    return result.final_output
  except Exception as e:
      print(f"There was an error connecting the Server:{e}")

# if __name__ == '__main__':
#   question1 : str = "Are you able to access my database with my userID and name because I have some transactions made recently that I saved in it, if yes, then tell me about them"
#   userID : str = '69ba9e8e3427be64889d8d2b'
#   name: str = 'Dawood Ayaz'
#   email : str = 'dawoodayaz18@gmail.com' 
#   asyncio.run(kickoff(question1, userID, name, email))