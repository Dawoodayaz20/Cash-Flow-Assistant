from dataclasses import dataclass

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