from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from FloAgent.cashflow_agent import kickoff
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
app = FastAPI()
request_origin = os.getenv("request_origin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"{request_origin}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str
    userID: str
    user_name: str
    email: str

@app.post("/floAssistant")
async def ask_question(request: QuestionRequest):
    try:
        
        result = await kickoff(request.question, request.userID, request.user_name, request.email)
        return result
    except Exception as e:
        print(f"Error running your request: {e}")
        return {"error": str(e)}