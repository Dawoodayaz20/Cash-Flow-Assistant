# from agents import Agent, Runner, set_tracing_disabled, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
# from dataclasses import dataclass
# from dotenv import load_dotenv, find_dotenv
# import asyncio
# import os
# from FloAgent.context import UserFinanceContext, ChatHistoryItem
# from tools.get_chats import get_session_messages, format_history
# from tools.finance_tools import get_financial_summary, get_spending_by_category, get_recurring_transactions, get_transactions, forecast_balance, prepare_transaction
# from tools.user_data_tools import fetch_settings

# load_dotenv(find_dotenv())

# async def kickoff(question: str, userID: str, user_name: str, email: str, session_id: str):
#   API_KEY = os.getenv("API_KEY")
  
#   external_client = AsyncOpenAI(
#     api_key=API_KEY,
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
#   )
    
#   model = OpenAIChatCompletionsModel(
#     model="gemini-3.6-flash",
#     openai_client=external_client
#   )
    
#   config = RunConfig(
#     model=model,
#     model_provider=external_client,
#     tracing_disabled=True,
#   )
  
#   set_tracing_disabled(disabled=True)

#   history = get_session_messages(userID, session_id)
#   # print(history)

#   try:
#     user_context = UserFinanceContext(
#             userId=userID,
#             user_name=user_name,
#             email=email,
#             chat_history=[ChatHistoryItem(**msg) for msg in history],
#             proposal = None
#         )

#     General_Assistant : Agent = Agent[UserFinanceContext](
#        name="General_Assistant",
#        instructions="""
#             You are a helpful general assistant.
#             Answer greetings, general knowledge questions, accounting concepts, and app navigation queries.
#             You have access to the user's financial data.
#             You have been provided the chat_history in context with user's data 
#            """,
#        handoff_description="Handles general queries, greetings, app navigation, and financial questions not related to personal data."
#     )
    
#     Financial_Assistant: Agent = Agent[UserFinanceContext](
#     name="Finance_Manager",
#     instructions=f"""
#     You are Finance Manager, a smart and proactive personal finance AI agent. You have access to the user's financial context and can take actions through the tools provided to help them manage, analyze, and optimize their cashflow.
#     CONTEXT_AVAILABLE:
#         - You have been provided user_data and chat_history in context so that you can response better to the query. You are allowed to share it with the user.
#     TOOLS AVAILABLE:
#         - get_transactions: Use this to answer questions about specific transactions, spending history, income, or any transaction-related query. 
#         - get_financial_summary: Use this to answer questions about total income, total expenses, net balance, or overall financial health
#         - get_recurring_transactions: Use this to answer questions about subscriptions, recurring payments, or regular income.
#         - get_spending_by_category: Use this to breakdown the spendings per category.
#         - forecast_balance: Use this to forecast user's balance. 
#         - prepare_transaction: You can prepare a transaction proposal to be reviewed and saved by the user. Ask the user for specific details to prepare that proposal.

#     CHAT HISTORY:
#     - You have access to the user's previous messages in this session.
#     - Use it to maintain conversation continuity and avoid asking for info already provided.
#     - Do NOT repeat or summarize the history unless explicitly asked.

#     BEHAVIOR:
#     - Always use tools to fetch real data before answering — never assume or guess
#     - Never hallucinate
#     - Always respond to the user using chat history given in context 
#     - Present numbers clearly with the user's currency
#     - For forecasting questions, use get_transactions to analyze patterns
#     - Keep responses concise and easy to understand
#     - If asked something outside finance, politely decline

#     NEVER:
#     - Make up financial data
#     - Share or mention sensitive fields like passwords
#     - Make financial decisions on behalf of the user """,
#     model=model,
#     tools=[
#         get_transactions,
#         get_financial_summary,
#         get_spending_by_category,
#         get_recurring_transactions,
#         forecast_balance,
#         prepare_transaction
#         ],
#     handoff_description="Handles cashflow analysis, expenses, budgets, invoices, and any personal financial data queries."
#     )

#     Triage_Agent : Agent = Agent(
#         name="Triage_Agent",
#         instructions="""
#             You are a silent routing agent. 
#             DO NOT respond to the user directly.
#             DO NOT explain or announce the handoff.
#             ONLY route to the correct agent immediately.
            
#             Rules:
#             - Use chat_history context to better understand the intent if the current message is ambiguous.
#             - Route to "Finance_Manager" ONLY if the user is asking about THEIR OWN financial data (their transactions, their expenses, their cashflow, their balance)
#             - Route EVERYTHING else to "General_Assistant", including general knowledge, accounting standards, greetings, app navigation
#             """,
#         handoffs=[General_Assistant, Financial_Assistant]
#     )

#     history_str = format_history(user_context.chat_history)

#     input_with_history = f"""
#         PREVIOUS CONVERSATION:
#         {history_str}

#         CURRENT MESSAGE:
#         {question}
#     """ 

#     result = await Runner.run(
#       Triage_Agent, 
#       input_with_history,
#       run_config=config,
#       context= user_context 
#     )
#     print(result.final_output)
#     print(result.last_agent.name)
#     return {
#        "reply": result.final_output,
#        "proposal": user_context.proposal.model_dump() if user_context.proposal else None,
#       }
#   except Exception as e:
#     print(f"There was an error connecting the Server:{e}")
#     if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
#         raise RuntimeError("rate_limit_exceeded") from e
#     raise

from agents import Agent, Runner, set_tracing_disabled, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
from openai import RateLimitError
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv
import asyncio
import json
import os
from FloAgent.context import UserFinanceContext, ChatHistoryItem
from tools.get_chats import get_session_messages, format_history
from tools.finance_tools import get_financial_summary, get_spending_by_category, get_recurring_transactions, get_transactions, forecast_balance, prepare_transaction
from tools.user_data_tools import fetch_settings

load_dotenv(find_dotenv())


def sse(data: dict) -> str:
  """Format one dict as a Server-Sent Event line."""
  return f"data: {json.dumps(data)}\n\n"


async def kickoff(question: str, userID: str, user_name: str, email: str, session_id: str):
  """Async generator: yields SSE events while the agent runs."""
  API_KEY = os.getenv("API_KEY")

  external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
  )

  model = OpenAIChatCompletionsModel(
    model="gemini-3.6-flash",
    openai_client=external_client
  )

  config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True,
  )

  set_tracing_disabled(disabled=True)

  try:
    # moved inside try so a failure here also reaches the frontend as an error event
    history = get_session_messages(userID, session_id)

    user_context = UserFinanceContext(
            userId=userID,
            user_name=user_name,
            email=email,
            chat_history=[ChatHistoryItem(**msg) for msg in history],
            proposal = None
        )

    General_Assistant : Agent = Agent[UserFinanceContext](
       name="General_Assistant",
       instructions="""
            You are a helpful general assistant.
            Answer greetings, general knowledge questions, accounting concepts, and app navigation queries.
            You have access to the user's financial data.
            You have been provided the chat_history in context with user's data 
           """,
       handoff_description="Handles general queries, greetings, app navigation, and financial questions not related to personal data."
    )

    Financial_Assistant: Agent = Agent[UserFinanceContext](
    name="Finance_Manager",
    instructions=f"""
    You are Finance Manager, a smart and proactive personal finance AI agent. You have access to the user's financial context and can take actions through the tools provided to help them manage, analyze, and optimize their cashflow.
    CONTEXT_AVAILABLE:
        - You have been provided user_data and chat_history in context so that you can response better to the query. You are allowed to share it with the user.
    TOOLS AVAILABLE:
        - get_transactions: Use this to answer questions about specific transactions, spending history, income, or any transaction-related query. 
        - get_financial_summary: Use this to answer questions about total income, total expenses, net balance, or overall financial health
        - get_recurring_transactions: Use this to answer questions about subscriptions, recurring payments, or regular income.
        - get_spending_by_category: Use this to breakdown the spendings per category.
        - forecast_balance: Use this to forecast user's balance. 
        - prepare_transaction: You can prepare a transaction proposal to be reviewed and saved by the user. Ask the user for specific details to prepare that proposal.

    CHAT HISTORY:
    - You have access to the user's previous messages in this session.
    - Use it to maintain conversation continuity and avoid asking for info already provided.
    - Do NOT repeat or summarize the history unless explicitly asked.

    BEHAVIOR:
    - Always use tools to fetch real data before answering — never assume or guess
    - Never hallucinate
    - Always respond to the user using chat history given in context 
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
        forecast_balance,
        prepare_transaction
        ],
    handoff_description="Handles cashflow analysis, expenses, budgets, invoices, and any personal financial data queries."
    )

    Triage_Agent : Agent = Agent(
        name="Triage_Agent",
        instructions="""
            You are a silent routing agent. 
            DO NOT respond to the user directly.
            DO NOT explain or announce the handoff.
            ONLY route to the correct agent immediately.
            
            Rules:
            - Use chat_history context to better understand the intent if the current message is ambiguous.
            - Route to "Finance_Manager" ONLY if the user is asking about THEIR OWN financial data (their transactions, their expenses, their cashflow, their balance)
            - Route EVERYTHING else to "General_Assistant", including general knowledge, accounting standards, greetings, app navigation
            """,
        handoffs=[General_Assistant, Financial_Assistant]
    )

    history_str = format_history(user_context.chat_history)

    input_with_history = f"""
        PREVIOUS CONVERSATION:
        {history_str}

        CURRENT MESSAGE:
        {question}
    """ 

    # NOTE: run_streamed is NOT awaited. The work happens as we iterate stream_events().
    result = Runner.run_streamed(
      Triage_Agent,
      input_with_history,
      run_config=config,
      context=user_context
    )

    async for event in result.stream_events():
      # A new agent took over (skip the very first event, which is just Triage starting)
      if event.type == "agent_updated_stream_event":
        if event.new_agent.name != "Triage_Agent":
          yield sse({"type": "handoff", "agent": event.new_agent.name})

      elif event.type == "run_item_stream_event":
        if event.name == "tool_called":
          yield sse({"type": "tool_called", "tool": event.item.raw_item.name})
        elif event.name == "tool_output":
          yield sse({"type": "tool_done"})

    print(result.final_output)
    print(result.last_agent.name)

    # Final event: same shape as the old JSON response, plus a type
    yield sse({
      "type": "final",
      "reply": result.final_output,
      "proposal": user_context.proposal.model_dump() if user_context.proposal else None,
    })

  except RateLimitError:
    yield sse({
      "type": "error",
      "code": "rate_limit",
      "message": "You've exceeded your API quota. Please try again later or start a new chat."
    })
  except Exception as e:
    print(f"There was an error connecting the Server:{e}")
    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
      yield sse({
        "type": "error",
        "code": "rate_limit",
        "message": "API quota exceeded. Try again shortly."
      })
    else:
      yield sse({"type": "error", "code": "server_error", "message": str(e)})