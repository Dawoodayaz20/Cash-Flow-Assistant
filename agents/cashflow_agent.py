from agents import Agent, Runner, set_tracing_disabled, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel, function_tool, RunContextWrapper
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv
import asyncio
import os
from context import UserData, UserFinanceContext
from db.mongo import db
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
    userId = ctx.context.userId
    transactions = list(db.transactions.find(
        {"userId": ObjectId(userId)},
        {"_id": 0, "userId": 0}  # exclude these fields
    ))
    if not transactions:
        return "No transactions found for this user."
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

async def kickoff(question: str):

  try:
    Medical_Assistant: Agent = Agent(
    name="AI Assistant",
    instructions=f"You are a helpful AI assistant",
    model=model,
    )

    result = await Runner.run(
      Medical_Assistant, 
      question,
      run_config=config
    )
    print(result.final_output)
    return result.final_output
  except Exception as e:
      print(f"There was an error connecting the Server:{e}")

# ". After checking all the data of the user, provide personalized medical advice and answer health-related questions based on the provided {user_data}, {user_diet}, and {illnesses}. Ensure your advice is tailored to the user's age, health condition, diet, and known allergies. Always prioritize the user's safety and well-being. Do not provide a diagnosis or prescribe medication. If a question is outside your scope, advise the user to consult a medical professional."

if __name__ == '__main__':
  question1 : str = "How can I create an AI model through openai-agents sdk, briefly answer in simple steps."
  asyncio.run(kickoff(question1))