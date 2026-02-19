# SharifAC RAG Chatbot 🎓🤖

SharifAC RAG Chatbot is an intelligent assistant designed to help students of **Sharif University of Technology (SUT)** navigate through the complex educational regulations, bylaws, and guidelines.

By leveraging **Retrieval-Augmented Generation (RAG)**, this chatbot provides accurate, citation-backed answers based on the university's official documents. It is available as a **Web Widget** and a **Telegram Bot**.


## 🚀 Features

- **📚 RAG-Powered Answers:** Retrieves relevant clauses from official PDF/Markdown documents before generating a response.
- **🔗 Source Citations:** Every answer includes links or references to the specific regulation used.
- **💬 Multi-Platform Support:**
  - **Web Widget:** specific UI with a floating chat bubble for university websites.
  - **Telegram Bot:** Interactive bot for easy access via mobile.
- **🧠 Flexible LLM Support:** Supports both **OpenAI (GPT-4o)** and **Ollama (Local Models like Qwen2.5)**.
- **📊 Observability:** Integrated with **Langfuse** for tracing, monitoring, and evaluating chat sessions.
- **💾 Conversation History:** Maintains chat history using SQLite (configurable to Postgres) for context-aware follow-up questions.
- **🐳 Docker Ready:** Fully containerized setup for easy deployment.


## 🛠 Tech Stack

- **Language:** Python 3.10+
- **Framework:** `FastAPI`
- **LLM Orchestration:** `LangChain`
- **Vector Database:** `FAISS` (CPU)
- **Embeddings:** OpenAI `text-embedding-3-large` (configurable)
- **LLM Providers:** OpenAI API / Ollama
- **Database:** `SQLite` / `PostgreSQL` (via SQLAlchemy)
- **Observability:** `Langfuse` (Self-hosted via Docker)
- **Frontend:** Plain `HTML/JS/CSS` (Embedded Widget)
- **Bot Framework:** `python-telegram-bot`


## 🏗 Architecture & Workflow

```mermaid
graph TD
    subgraph "1. Data Acquisition"
        A[Website (ac.sharif.edu)] -->|Crawler requests| B[HTML Fetcher]
        B -->|BeautifulSoup| C[Content Parser]
        C -->|markdownify| D[Markdown Converter]
        D -->|Save| E[Raw Data (data/*.md)]
    end

    subgraph "2. Data Processing & Indexing"
        E -->|Load| F[Text Loader]
        F -->|Header Split| G[MarkdownHeaderTextSplitter]
        G -->|Recursive Split| H[RecursiveCharacterTextSplitter]
        H -->|Chunk| I[Text Chunks]
        I -->|OpenAI Embeddings| J[Vector Represantion]
        J -->|Index| K[FAISS Vector Store]
    end

    subgraph "3. RAG Inference"
        L[User Query] -->|Embed| M[Query Vector]
        M -->|Similarity Search| K
        K -->|Retrieve Top-K| N[Relevant Context]
        N & L -->|Augment Prompt| O[Contextualized Prompt]
        O -->|LLM Interface| P[LLM (OpenAI/Ollama)]
        P -->|Stream| Q[Final Answer + Citations]
    end

    subgraph "4. Observability"
        O & P -->|Trace| R[Langfuse]
        R -->|Monitor| S[Logs & Cost Analysis]
    end
```

### 1. Data Acquisition (Crawler)
The crawling module (`app/data/crawler.py`) is responsible for fetching the latest educational regulations from the university's official website (**ac.sharif.edu**).
- **Fetcher:** Uses `requests` to download pages.
- **Parser:** `BeautifulSoup` extracts the main content (`#writr__main`) and cleans up unnecessary elements.
- **Converter:** `markdownify` transforms the HTML content into clean **Markdown** files, preserving structure (headers, lists, tables).
- **Storage:** Each regulation is saved in `data/{Title}/` along with a `metadata.json` containing the source URL and date.

### 2. Data Processing & Indexing
Before the chatbot can answer, the raw data must be processed (`app/data/preprocessing.py`).
- **Loading:** Reads all Markdown files from the `data/` directory.
- **Chunking:** Uses **LangChain's** `MarkdownHeaderTextSplitter` and `RecursiveCharacterTextSplitter` to break documents into smaller, meaningful chunks based on headers and logical sections.
- **Embedding:** Converts text chunks into vector embeddings using `text-embedding-3-large` (OpenAI).
- **Vector Store:** Stores these vectors in a local **FAISS** index for fast similarity search.

### 3. RAG Pipeline
When a user asks a question:
1. **Query Embedding:** The question is converted into a vector.
2. **Retrieval:** The system searches the FAISS index for the top `k` (default: 5) most similar chunks.
3. **Augmentation:** A system prompt is constructed, combining the user's question with the retrieved context.
4. **Generation:** The LLM (GPT-4o or Ollama) generates a response based *only* on the provided context.
5. **Citation:** The source of each retrieved chunk is appended to the final answer.

### 4. Observability with Langfuse
All interactions are traced using **Langfuse**. This allows us to:
- Monitor **LLM latency** and **cost**.
- Debug retrieval quality by inspecting the chunks passed to the LLM.
- **Feedback Collection:** Evaluate query performance.


## 📂 Project Structure

```bash
SharifAC-RAG-Chatbot/
├── app/
│   ├── bot/                 # Telegram Bot logic
│   ├── core/                # Config, Database, Logger
│   ├── data/                # Crawlers and Preprocessing scripts
│   ├── services/            # RAG, Chat Service, LLM logic
│   ├── static/              # Web Widget (JS/CSS)
│   └── main.py              # FastAPI Entry point
├── data/                    # Markdown/JSON files of regulations
├── vector_store/            # FAISS Index storage
├── notebooks/               # Jupyter Notebooks for testing & experiments
├── docker-compose.yml       # Docker services (Ollama, Langfuse, Postgres)
├── requirements.txt         # Python dependencies
└── run.py                   # Main runner script
```


## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/moeeinaali/SharifAC-RAG-Chatbot.git
cd SharifAC-RAG-Chatbot
```

### 2. Environment Setup
Create a `.env` file in the root directory:
```env
# LLM Configuration
LLM_PROVIDER=openai  # or 'ollama'
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Ollama Config (if provider is ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct

# RAG Configuration
RAG_K=5
RAG_SCORE_THRESHOLD=0.4
RAG_EMBEDDING_MODEL=text-embedding-3-large

# Database
DATABASE_URL=sqlite:///./chat_history.db

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Langfuse (Optional - for Observability)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com 
```

### 3. Install Dependencies
It is recommended to use a virtual environment.
```bash
python -m venv venv
source venv/bin/activate  
pip install -r requirements.txt
```

### 4. Run with Docker (Optional - for Langfuse/Ollama)

```bash
docker-compose up -d
```

### 5. Run the Application
You can start the FastAPI server and Telegram bot concurrently:
```bash
python run.py
```
- **API:** `http://localhost:8000`
- **Swagger UI:** `http://localhost:8000/docs`
- **Telegram Bot:** Starts automatically if token is provided.

## 📖 Usage

### Embed the Widget
Add the following script to your HTML file to include the chatbot widget:
```html
<script src="http://localhost:8000/static/widget.js"></script>
```


## 🧪 Testing
- Check `test-notebook.ipynb` for running sample queries and evaluating the RAG performance interactively.

- Send a POST request to chat endpoint. use `/docs` swagger API documentations.

- Send your question to Telegram-Bot.
