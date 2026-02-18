from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from sqlalchemy.orm import Session
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from rag_service import RAGService
from database import DBChatSession, DBChatMessage, get_db, init_db
from config import (
    LLM_PROVIDER, OLLAMA_MODEL, OLLAMA_BASE_URL, 
    OPENAI_API_KEY, OPENAI_MODEL, LLM_TEMPERATURE
)
from chat_service import generate_chat_response
from telegram_bot import create_bot_app
from contextlib import asynccontextmanager
from logger import get_logger

logger = get_logger(__name__)

init_db()

# Initialize Services Globaly
rag_service = RAGService()
llm = None
bot_app = None

# Initialize LLM
if LLM_PROVIDER == "openai":
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required for OpenAI provider.")
    logger.info(f"Initializing OpenAI LLM with model: {OPENAI_MODEL}")
    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=LLM_TEMPERATURE,
        api_key=OPENAI_API_KEY
    )
else:
    logger.info(f"Initializing Ollama LLM with model: {OLLAMA_MODEL}")
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        temperature=LLM_TEMPERATURE, 
        base_url=OLLAMA_BASE_URL
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Bot
    global bot_app
    bot_app = create_bot_app(rag_service, llm)
    
    if bot_app:
        logger.info("Starting Telegram Bot...")
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling()
    
    yield
    
    # Shutdown
    if bot_app:
        logger.info("Stopping Telegram Bot...")
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()

app = FastAPI(
    title="SharifAC RAG Chatbot",
    description="A RAG-based chatbot for answering questions about Sharif University educational regulations.",
    version="1.0.0",
    lifespan=lifespan
)

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: List[Dict]


@app.get("/health")
async def root() -> bool:
    return True


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    session_id = request.session_id if request.session_id else str(uuid.uuid4())

    try:
        response_text, sources = await generate_chat_response(
            query=request.query,
            session_id=session_id,
            db=db,
            rag_service=rag_service,
            llm=llm
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        sources=sources
    )


@app.delete("/history/{session_id}")
async def clear_history(session_id: str, db: Session = Depends(get_db)):
    db_session = db.query(DBChatSession).filter(DBChatSession.id == session_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()
        return {"message": "Chat history cleared."}
    raise HTTPException(status_code=404, detail="Session ID not found")
