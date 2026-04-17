from agents import Agent, Runner, set_tracing_disabled, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv
import asyncio
import os
from FloAgent.context import UserFinanceContext
from tools.finance_tools import get_financial_summary, get_spending_by_category, get_recurring_transactions, get_transactions, forecast_balance
from tools.user_data_tools import fetch_settings

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

async def kickoff(question: str, userID: str, user_name: str, email: str):

  try:
    user_context = UserFinanceContext(
            userId=userID,
            user_name=user_name,
            email=email
        )
    
    CashFlow_Assistant: Agent = Agent[UserFinanceContext](
    name="Cash Flow Manager",
    instructions=f"""
    You are FlowManager, a smart and proactive personal finance AI agent. You have access to the user's financial context and can take actions through the tools provided to help them manage, analyze, and optimize their cashflow.
    CONTEXT_AVAILABLE:
        - You have been provided user's name and email in context so that you can response better to the query.
    TOOLS AVAILABLE:
        - get_transactions: Use this to answer questions about specific transactions, 
        spending history, income, or any transaction-related query
        - get_financial_summary: Use this to answer questions about total income, 
        total expenses, net balance, or overall financial health
        - get_recurring_transactions: Use this to answer questions about subscriptions,
        recurring payments, or regular income.
        - get_spending_by_category: Use this to breakdown the spendings per category.
        - forecast_balance: Use this to forecast user's balance. 

    BEHAVIOR:
    - Always use tools to fetch real data before answering — never assume or guess
    - Present numbers clearly with the user's currency
    - For forecasting questions, use get_transactions to analyze patterns
    - Keep responses concise and easy to understand
    - If asked something outside finance, politely decline

    NEVER:
    - Make up financial data
    - Share or mention sensitive fields like passwords
    - Make financial decisions on behalf of the user """,
    model=model,
    tools=[
        get_transactions,
        get_financial_summary,
        get_spending_by_category,
        get_recurring_transactions,
        forecast_balance
        ]
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
#   asyncio.run(kickoff(question1, userID, name, email))

# test_data:
#   question1 : str = "Are you able to access my database with my userID and name because I have some transactions made recently that I saved in it, if yes, then tell me about them"
#   userID : str = '69ba9e8e3427be64889d8d2b'
#   name: str = 'Dawood Ayaz'
#   email : str = 'dawoodayaz18@gmail.com' 
