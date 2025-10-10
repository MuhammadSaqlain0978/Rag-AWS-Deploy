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
from pop_scrap import scrape_important_announcements
import os
from apscheduler.schedulers.background import BackgroundScheduler
import threading
from combined_script import combine_dataset_files

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
bot= UniversityRAGBot(api_key="3XroHID0PrEB4ouyEhBA9R60yzLIV8lf")


# ✅ Call the combine function here before loading data
combine_dataset_files(dataset_folder="dataset", output_file="comfolder/combinedfile1.txt")

bot.load_university_data(database_folder="comfolder", vector_store_path="./database_vector_store2")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)








# =========================
# Scraping Scheduler Setup
# =========================
scheduler = BackgroundScheduler()
last_scrape_time = None  # will hold timestamp of last scrape

def scheduled_scraping_job():
    """
    Background job that runs every few hours.
    """
    global last_scrape_time
    print("\n⏰ Scheduled scraping started...")
    try:
        scrape_important_announcements(output_path="./dataset/Important Announcements.txt")
        last_scrape_time = datetime.now().isoformat()
        print(f"✅ Scraping completed successfully at {last_scrape_time}\n")
    except Exception as e:
        print(f"❌ Scraping failed: {e}\n")

# Run every 6 hours (adjust if needed)
scheduler.add_job(scheduled_scraping_job, "interval", hours=24, id="scraper_job")


# =========================
# FastAPI Events
# =========================
@app.on_event("startup")
def start_scheduler():
    print("🚀 FastAPI app starting...")
    scheduler.start()
    # Run once immediately at startup (in background)
    threading.Thread(target=scheduled_scraping_job, daemon=True).start()

@app.on_event("shutdown")
def shutdown_scheduler():
    print("🛑 Shutting down scheduler...")
    scheduler.shutdown()




# =========     Routes    =========


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
    



# Optional: manual trigger
@app.get("/announcements")
def manual_scrape():
    try:
        scrape_important_announcements("./dataset/Important Announcements.txt")
        global last_scrape_time
        last_scrape_time = datetime.now().isoformat()
        return {"status": "success", "message": "Scraping done manually", "time": last_scrape_time}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# @app.get("/scrape/status")
# def scrape_status():
#     return {"last_scrape_time": last_scrape_time}