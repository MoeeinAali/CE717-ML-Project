from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from app.core.config import TELEGRAM_BOT_TOKEN
from app.services.chat_service import generate_chat_response
from app.core.database import SessionLocal
from app.core.logger import get_logger

logger = get_logger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your RAG Chatbot for the Sharif University of Technology. Ask me anything about educational regulations.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I can answer questions based on the university's educational regulations. Just type your question!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = str(update.effective_user.id)

    rag_service = context.bot_data.get("rag_service")
    llm = context.bot_data.get("llm")

    if rag_service and llm:
        await update.message.reply_chat_action(action="typing")

        db = SessionLocal()
        try:
            response_text, sources = await generate_chat_response(
                query=user_text,
                session_id=user_id,
                db=db,
                rag_service=rag_service,
                llm=llm
            )

            if sources:
                response_text += "\n\n📚 **Sources:**"

                seen_titles = set()
                unique_sources = []

                for source in sources:
                    title = source.get('title', 'Unknown Source')
                    if title not in seen_titles:
                        seen_titles.add(title)
                        unique_sources.append(source)

                for i, source in enumerate(unique_sources[:3], 1):
                    title = source.get('title', 'Unknown Source')
                    response_text += f"\n{i}. {title}"

            await update.message.reply_text(response_text, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error processing RAG request: {e}", exc_info=True)
            await update.message.reply_text("Sorry, I encountered an error while processing your request.")
        finally:
            db.close()
    else:
        logger.error("RAG Service or LLM not initialized in bot_data")
        await update.message.reply_text(f"Service temporarily unavailable.")


def create_bot_app(rag_service, llm):

    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not found. Bot will not run.")
        return None

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.bot_data["rag_service"] = rag_service
    application.bot_data["llm"] = llm

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    async def handle_non_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("لطفاً فقط پیام متنی ارسال کنید. فایل، عکس و ... پشتیبانی نمی‌شود.")

    application.add_handler(MessageHandler(
        ~filters.TEXT & ~filters.COMMAND, handle_non_text))

    return application
