from pymongo import MongoClient
from bson import ObjectId
from FloAgent.context import ChatHistoryItem
from db.mongo import database
import json

chat_collection = database["chats"]

def get_session_messages(user_id: str, session_id: str) -> str:
    chat = chat_collection.find_one(
        {
            "user_id": ObjectId(user_id),
            "sessions.session_id": session_id
        },
        {"sessions.$": 1}
    )

    if not chat or not chat.get("sessions"):
        return []

    session = chat["sessions"][0]

    return [
        {"role": msg["role"], "content": msg["content"]}
        for msg in session.get("messages", [])
    ]

def format_history(history: list[ChatHistoryItem]) -> str:
    return "\n".join([f"{msg.role}: {msg.content}" for msg in history])

# 69ba9e8e3427be64889d8d2b
# 694c1bba-56ae-4663-8236-93970e496953

# Response_Data:
### "{\"session_id\": \"694c1bba-56ae-4663-8236-93970e496953\", 
# \"title\": \"How Are You\\n\", \"messages\": [{\"id\": \"8bbce344-8992-47f8-bea6-dc0974a5707a\", 
# \"role\": \"user\", \"content\": \"hey how are you doing today\", 
# \"timestamp\": \"2026-05-01T19:29:24.740000\"}, 
# {\"id\": \"15e83961-862e-4e44-96cb-ee4bbf448a85\", 
# \"role\": \"assistant\", \"content\": \"Hello! I'm doing well, thank you for asking. I'm ready to assist you with any questions or tasks you might have. How can I help you today?\", 
# \"timestamp\": \"2026-05-01T19:29:37.106000\"}]}"