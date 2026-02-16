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

init_db()

app = FastAPI(
    title="SharifAC RAG Chatbot",
    description="A RAG-based chatbot for answering questions about Sharif University educational regulations.",
    version="1.0.0"
)

rag_service = RAGService()

if LLM_PROVIDER == "openai":
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required for OpenAI provider.")
    print(f"Initializing OpenAI LLM with model: {OPENAI_MODEL}")
    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=LLM_TEMPERATURE,
        api_key=OPENAI_API_KEY
    )
else:
    print(f"Initializing Ollama LLM with model: {OLLAMA_MODEL}")
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        temperature=LLM_TEMPERATURE, 
        base_url=OLLAMA_BASE_URL
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

    db_session = db.query(DBChatSession).filter(DBChatSession.id == session_id).first()
    if not db_session:
        db_session = DBChatSession(id=session_id)
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

    system_instruction, docs = rag_service.generate_augmented_prompt(
        request.query)

    db_messages = db.query(DBChatMessage)\
        .filter(DBChatMessage.session_id == session_id)\
        .order_by(DBChatMessage.created_at.desc())\
        .limit(6)\
        .all()
    
    has_history = len(db_messages) > 0

    if not system_instruction and not has_history:
        response_text = "در قوانین موجود جوابی برای این سوال پیدا نکردم."
        sources = []
    else:
        messages = []

        if system_instruction:
            messages.append(SystemMessage(content=system_instruction))
        else:
            messages.append(SystemMessage(content="تو یک دستیار هوشمند هستی. به سوالات کاربر پاسخ بده."))

        db_messages = db_messages[::-1]
        
        for msg in db_messages:
            if msg.role == 'user':
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == 'ai':
                messages.append(AIMessage(content=msg.content))

        messages.append(HumanMessage(content=request.query))

        try:
            response_message = llm.invoke(messages)
            response_text = response_message.content
            if docs:
                 sources = [doc.metadata for doc in docs]
            else:
                 sources = []
            
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"LLM Generation Error: {str(e)}")

    user_msg = DBChatMessage(session_id=session_id, role='user', content=request.query)
    ai_msg = DBChatMessage(session_id=session_id, role='ai', content=response_text)
    
    db.add(user_msg)
    db.add(ai_msg)
    db.commit()

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
