from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from FloAgent.cashflow_agent import kickoff
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str
    userId: str
    name: str
    email: str

@app.post("/floAssistant")
async def ask_question(request: QuestionRequest):
    try:
        result = await kickoff(request.question, request.userId, request.name, request.email)
        return result
    except Exception as e:
        print(f"Error running your request: {e}")
        return {"error": str(e)}