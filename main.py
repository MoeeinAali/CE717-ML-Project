from fastapi import FastAPI, HTTPException, Body, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
import time
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from rag_service import RAGService

SQLALCHEMY_DATABASE_URL = "sqlite:///./chat_history.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBChatSession(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("DBChatMessage", back_populates="session", cascade="all, delete-orphan")

class DBChatMessage(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    role = Column(String) # 'user' or 'ai'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("DBChatSession", back_populates="messages")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title="Sharif University Educational RAG Chatbot",
    description="A RAG-based chatbot for answering questions about Sharif University educational regulations.",
    version="1.0.0"
)

# Initialize RAG Service
# Increased k to 5 as per prompt.md recommendation
rag_service = RAGService()

# Initialize LLM (Ollama)
# Ensure you have 'ollama' running with 'qwen2.5:7b-instruct' or your preferred model
llm = ChatOllama(
    model="qwen2.5:7b-instruct",
    temperature=0.3, 
    base_url="http://127.0.0.1:11434"
)

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: List[str]


@app.get("/health")
async def root() -> bool:
    return True


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    session_id = request.session_id if request.session_id else str(uuid.uuid4())

    # Check if session exists, create if not
    db_session = db.query(DBChatSession).filter(DBChatSession.id == session_id).first()
    if not db_session:
        db_session = DBChatSession(id=session_id)
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

    # 1. Retrieve relevant documents and system instruction
    system_instruction, docs = rag_service.generate_augmented_prompt(
        request.query)

    if not system_instruction:
        # Fallback if no documents found
        response_text = "در قوانین موجود جوابی برای این سوال پیدا نکردم."
        sources = []
    else:
        # 2. Construct Messages for LLM
        messages = []

        # Add the System Message (RAG Context)
        messages.append(SystemMessage(content=system_instruction))

        # Add History (retrieve from DB, convert to LangChain messages)
        # Sort by id or created_at to ensure order
        # Fetch last 6 messages
        # Note: We query all messages for this session, sort by date, take last N
        # Ideally, we should order by id or created_at DESC, limit N, then reverse.
        
        db_messages = db.query(DBChatMessage)\
            .filter(DBChatMessage.session_id == session_id)\
            .order_by(DBChatMessage.created_at.desc())\
            .limit(6)\
            .all()
        
        # Reverse to get chronological order
        db_messages = db_messages[::-1]
        
        for msg in db_messages:
            if msg.role == 'user':
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == 'ai':
                messages.append(AIMessage(content=msg.content))

        # Add current user query
        messages.append(HumanMessage(content=request.query))

        # 3. Generate response
        try:
            response_message = llm.invoke(messages)
            response_text = response_message.content
            # Extract sources
            sources = [doc.metadata.get("source_file", "Unknown")
                       for doc in docs]
            # Deduplicate sources
            sources = list(set(sources))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"LLM Generation Error: {str(e)}")

    # Update History in DB
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
