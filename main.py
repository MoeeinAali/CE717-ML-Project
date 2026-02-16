import osimport os

from dotenv import load_dotenv

from rag_service import RAGServicefrom dotenv import load_dotenvfrom dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from langchain_core.messages import HumanMessage, SystemMessagefrom rag_service import RAGServicefrom rag_service import RAGService



# Load environmentfrom langchain_openai import ChatOpenAIfrom langchain_openai import ChatOpenAI

load_dotenv()

from langchain_core.messages import HumanMessage, SystemMessagefrom langchain_core.messages import HumanMessage, SystemMessage

# --- CONFIGURATION ---

# Local Ollama config (standard OpenAI-compatible API)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama") # Key doesn't matter for local

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")# Load environment# Load environment

LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b-instruct")

load_dotenv()load_dotenv()

def main():

    print("--- Sharif University Educational Assistant (RAG Chatbot) ---")

    

    # 1. Initialize RAG# --- CONFIGURATION ---# --- CONFIGURATION ---

    rag_service = RAGService()

    # Local Ollama config (standard OpenAI-compatible API)# دریافت تنظیمات از .env یا مقادیر پیش‌فرض برای لوکال

    # 2. Initialize LLM

    # We use ChatOpenAI because it supports any OpenAI-compatible endpoint (like Ollama)OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama") # Key doesn't matter for localOPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy-key") # برای لوکال کلید مهم نیست

    print(f"Connecting to LLM: {LLM_MODEL} at {OPENAI_BASE_URL}...")

    try:OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")

        llm = ChatOpenAI(

            model=LLM_MODEL,LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b-instruct")LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b-instruct")

            temperature=0.1,

            api_key=OPENAI_API_KEY,

            base_url=OPENAI_BASE_URL,

            max_tokens=1024def main():def main():

        )

    except Exception as e:    print("--- Sharif University Educational Assistant (RAG Chatbot) ---")    print("--- Sharif University Educational Assistant (RAG Chatbot) ---")

        print(f"Initialization Error: {e}")

        return        



    print("\n✅ System Ready! Type 'exit' to quit.\n")    # 1. Initialize RAG    # 1. Initialize RAG



    # 3. Chat Loop    rag_service = RAGService()    print("Initializing RAG Service...")

    while True:

        user_query = input("\nStudent: ")        rag_service = RAGService()

        if user_query.strip().lower() in ["exit", "quit", "خروج"]:

            print("Goodbye!")    # 2. Initialize LLM    

            break

                # We use ChatOpenAI because it supports any OpenAI-compatible endpoint (like Ollama)    # 2. Initialize LLM (via LangChain ChatOpenAI)

        if not user_query.strip():

            continue    print(f"Connecting to LLM: {LLM_MODEL} at {OPENAI_BASE_URL}...")    print(f"Connecting to LLM: {LLM_MODEL} at {OPENAI_BASE_URL}...")



        print("🤖 Thinking...")    try:    try:

        

        # A. Retrieve Context        llm = ChatOpenAI(        llm = ChatOpenAI(

        final_prompt_str, docs_or_msg = rag_service.generate_augmented_prompt(user_query)

                    model=LLM_MODEL,            model=LLM_MODEL,

        if not final_prompt_str:

            # Case: No relevant docs found            temperature=0.1,            temperature=0.1,

            print(f"System: {docs_or_msg}") 

            continue            api_key=OPENAI_API_KEY,            api_key=OPENAI_API_KEY,



        # B. Generate Answer            base_url=OPENAI_BASE_URL,            base_url=OPENAI_BASE_URL,

        try:

            # Send the complete prompt (System Instr + Context + User Query) as a user message            max_tokens=1024            max_tokens=1024

            messages = [HumanMessage(content=final_prompt_str)]

                    )        )

            response = llm.invoke(messages)

                except Exception as e:        # Test connection not strictly necessary, lazy load is fine

            print(f"\nSystem: {response.content}")

                    print(f"Initialization Error: {e}")        print("LLM Initialized.")

            # C. Show Sources

            print("\n--- Sources ---")        return    except Exception as e:

            seen = set()

            for d in docs_or_msg:        print(f"Error initializing LLM: {e}")

                # Fallback to source_file or title

                src = d.metadata.get("title", d.metadata.get("source_file", "Unknown"))    print("\n✅ System Ready! Type 'exit' to quit.\n")        return

                if src not in seen:

                    print(f"- {src}")

                    seen.add(src)

                        # 3. Chat Loop    print("\n✅ System Ready! Type 'exit' to quit.\n")

        except Exception as e:

            print(f"Generation Error: {e}")    while True:

            print("Hint: Is your local LLM (Ollama) running and serving on that port?")

        user_query = input("\nStudent: ")    # 3. Chat Loop

if __name__ == "__main__":

    main()        if user_query.strip().lower() in ["exit", "quit", "خروج"]:    while True:


            print("Goodbye!")        user_query = input("\nStudent: ")

            break        if user_query.strip().lower() in ["exit", "quit", "خروج"]:

                        print("Goodbye!")

        if not user_query.strip():            break

            continue            

        if not user_query.strip():

        print("🤖 Thinking...")            continue

        

        # A. Retrieve Context        print("🤖 Thinking...")

        try:        

            final_prompt_str, docs_or_msg = rag_service.generate_augmented_prompt(user_query)        # A. Retrieve Context

        except Exception as e:        try:

            print(f"RAG Error: {e}")            final_prompt_str, docs = rag_service.generate_augmented_prompt(user_query)

            continue        except Exception as e:

                        print(f"RAG Error: {e}")

        if not final_prompt_str:            continue

            # Case: No relevant docs found            

            print(f"System: {docs_or_msg}")         if not final_prompt_str:

            continue            print(f"System: {docs}") # Error message

            continue

        # B. Generate Answer

        try:        # B. Generate Answer

            # Send the complete prompt (System Instr + Context + User Query) as a user message        try:

            messages = [HumanMessage(content=final_prompt_str)]            # ارسال کل پرامپت (شامل سیستم و کانتکست) به عنوان پیام کاربر

                        # (چون استرینگ ساخته شده کامل است)

            response = llm.invoke(messages)            messages = [

                            HumanMessage(content=final_prompt_str)

            print(f"\nSystem: {response.content}")            ]

                        

            # C. Show Sources            response = llm.invoke(messages)

            print("\n--- Sources ---")            

            seen = set()            print(f"\nSystem: {response.content}")

            for d in docs_or_msg:            

                # Fallback to source_file or title            # C. Show Sources

                src = d.metadata.get("title", d.metadata.get("source_file", "Unknown"))            print("\n--- Sources ---")

                if src not in seen:            seen = set()

                    print(f"- {src}")            for d in docs:

                    seen.add(src)                src = d.metadata.get("title", d.metadata.get("source_file", "Unknown"))

                                    if src not in seen:

        except Exception as e:                    print(f"- {src}")

            print(f"Generation Error: {e}")                    seen.add(src)

            print("Hint: Is your local LLM (Ollama) running and serving on that port?")                    

        except Exception as e:

if __name__ == "__main__":            print(f"LLM Generation Error: {e}")

    main()            print("Hint: Check if your local LLM server (e.g., Ollama) is running.")


if __name__ == "__main__":
    main()