from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from database import DBChatSession, DBChatMessage
from rag_service import RAGService
from logger import get_logger

logger = get_logger(__name__)


async def generate_chat_response(query: str, session_id: str, db: Session, rag_service: RAGService, llm):
    db_session = db.query(DBChatSession).filter(
        DBChatSession.id == session_id).first()
    if not db_session:
        db_session = DBChatSession(id=session_id)
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

    system_instruction, docs = rag_service.generate_augmented_prompt(query)

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
            messages.append(SystemMessage(
                content="تو یک دستیار هوشمند هستی. به سوالات کاربر پاسخ بده."))

        db_messages = db_messages[::-1]

        for msg in db_messages:
            if msg.role == 'user':
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == 'ai':
                messages.append(AIMessage(content=msg.content))

        messages.append(HumanMessage(content=query))

        try:
            response_message = llm.invoke(messages)
            response_text = response_message.content
            if docs:
                sources = [doc.metadata for doc in docs]
            else:
                sources = []

        except Exception as e:
            logger.error(f"LLM Generation Error: {str(e)}")
            raise Exception(f"LLM Generation Error: {str(e)}")

    user_msg = DBChatMessage(session_id=session_id, role='user', content=query)
    ai_msg = DBChatMessage(session_id=session_id,
                           role='ai', content=response_text)

    db.add(user_msg)
    db.add(ai_msg)
    db.commit()

    return response_text, sources
