from dataclasses import dataclass
from typing import Literal
from pydantic import BaseModel, Field

TxType = Literal["income", "expense"]
Frequency = Literal["weekly", "monthly", "yearly"]    

class TransactionForm(BaseModel):
    type: TxType
    amount: float
    category: str
    note: str | None
    date: str
    isRecurring: bool
    frequency: Frequency | None
    endDate: str | None

@dataclass
class ChatHistoryItem:
    role: str
    content: str

@dataclass
class ChatHistoryContext:
    messages: list[ChatHistoryItem]

@dataclass
class UserFinanceContext:
    userId: str
    user_name: str
    email: str
    chat_history: list[ChatHistoryItem] = None
    proposal: TransactionForm | None = None