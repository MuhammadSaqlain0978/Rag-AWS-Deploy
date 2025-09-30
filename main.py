# from fastapi import FastAPI, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Optional
# import uuid
# from datetime import datetime

# from custom_data_bot import UniversityRAGBot

# # Pydantic models
# class ChatMessage(BaseModel):
#     message: str

# class BotResponse(BaseModel):
#     response: str
#     session_id: str
#     message_id: str
#     timestamp: str

# # Store chat sessions in memory
# chat_sessions = {}

# # Initialize bot
# bot = UniversityRAGBot(api_key="3XroHID0PrEB4ouyEhBA9R60yzLIV8lf")
# bot.load_university_data(database_folder="dataset", vector_store_path="./database_vector_store")

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/")
# def home():
#     return {"message": "RAG Chatbot API is running", "status": "ready"}

# @app.post("/chat")
# def chat(request: ChatMessage):
#     try:
#         # For simplicity, create a new session for each chat
#         # In a real app, you'd use cookies/tokens for session management
#         session_id = str(uuid.uuid4())
        
#         # Get or create chat history for this session
#         if session_id not in chat_sessions:
#             chat_sessions[session_id] = []
        
#         # Get the chat history for context
#         chat_history = chat_sessions[session_id]
        
#         # Add user message to history
#         chat_sessions[session_id].append({
#             "role": "user",
#             "message": request.message,
#             "timestamp": datetime.now().isoformat()
#         })
        
#         # Get bot response WITH chat history
#         result = bot.answer_query(request.message, chat_history)
        
#         # Add bot response to history
#         chat_sessions[session_id].append({
#             "role": "assistant", 
#             "message": result['answer'],
#             "timestamp": datetime.now().isoformat()
#         })
        
#         return {
#             "response": result['answer'],
#             "session_id": session_id,
#             "message_id": str(uuid.uuid4()),
#             "timestamp": datetime.now().isoformat()
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Get chat history endpoint (for debugging)
# @app.get("/chat/history/{session_id}")
# def get_chat_history(session_id: str):
#     if session_id not in chat_sessions:
#         return {"session_id": session_id, "history": []}
    
#     return {
#         "session_id": session_id,
#         "history": chat_sessions[session_id]
#     }






































from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import os

from custom_data_bot import UniversityRAGBot

# Pydantic models - Use ChatMessage consistently
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class BotResponse(BaseModel):
    response: str
    session_id: str
    message_id: str
    timestamp: str

# Store chat sessions in memory
chat_sessions = {}

# Initialize bot
bot = UniversityRAGBot(api_key="3XroHID0PrEB4ouyEhBA9R60yzLIV8lf")
bot.load_university_data(database_folder="dataset", vector_store_path="./database_vector_store")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "RAG Chatbot API is running", "status": "ready"}

@app.post("/chat")
def chat(request: ChatMessage):  # Use ChatMessage here
    try:
        # Generate or use session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get or create chat history for this session
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
        
        # Get the chat history for context
        chat_history = chat_sessions[session_id]
        
        # Add user message to history
        chat_sessions[session_id].append({
            "role": "user",
            "message": request.message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Get bot response WITH chat history
        result = bot.answer_query(request.message, chat_history)
        
        # Add bot response to history
        chat_sessions[session_id].append({
            "role": "assistant", 
            "message": result['answer'],
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "response": result['answer'],
            "session_id": session_id,
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get chat history endpoint
@app.get("/chat/history/{session_id}")
def get_chat_history(session_id: str):
    if session_id not in chat_sessions:
        return {"session_id": session_id, "history": []}
    
    return {
        "session_id": session_id,
        "history": chat_sessions[session_id]
    }

# Clear chat history endpoint
@app.delete("/chat/history/{session_id}")
def clear_chat_history(session_id: str):
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return {"message": f"Chat history for session {session_id} cleared"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")