import os
from dotenv import load_dotenv

load_dotenv()
# Database Configuration
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chat_history.db")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # Options: 'ollama', 'openai'

# Ollama Settings
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

# OpenAI Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

# RAG Configuration
RAG_K = int(os.getenv("RAG_K", "5"))
RAG_VECTOR_DB_PATH = os.getenv("RAG_VECTOR_DB_PATH", "vector_store")
RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-large")
RAG_SCORE_THRESHOLD = float(os.getenv("RAG_SCORE_THRESHOLD", "0.1"))
