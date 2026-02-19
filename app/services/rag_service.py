import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from app.core.config import RAG_VECTOR_DB_PATH, RAG_EMBEDDING_MODEL, RAG_SCORE_THRESHOLD, RAG_K
from app.core.logger import get_logger

logger = get_logger(__name__)

load_dotenv()


class RAGService(object):
    def __init__(self, vector_db_path=RAG_VECTOR_DB_PATH, embedding_model=RAG_EMBEDDING_MODEL, score_threshold=RAG_SCORE_THRESHOLD, k=RAG_K):
        self.vector_db_path = vector_db_path
        self.embedding_model_name = embedding_model

        self.vector_db = None
        self.retriever = None
        self.embeddings = None
        self.score_threshold = score_threshold
        self.k = k

        self._initialize_system()

    def _initialize_system(self):
        try:
            logger.info(
                f"Loading Embedding Model: {self.embedding_model_name}...")
            self.embeddings = OpenAIEmbeddings(
                model=self.embedding_model_name,
                check_embedding_ctx_length=False
            )

            if os.path.exists(self.vector_db_path):
                logger.info(
                    f"Loading FAISS Vector Store from {self.vector_db_path}...")
                self.vector_db = FAISS.load_local(
                    self.vector_db_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )

                self.retriever = self.vector_db.as_retriever(
                    search_type="similarity_score_threshold",
                    search_kwargs={
                        "score_threshold": self.score_threshold, "k": self.k}
                )
                logger.info("RAG Service Initialized Successfully.")
            else:
                logger.error(
                    f"Error: Vector store not found at {self.vector_db_path}. Please run preprocessing.py first.")

        except Exception as e:
            logger.error(f"Failed to initialize RAG Service: {e}")

    def _retrieve_documents(self, query):
        if not self.retriever:
            logger.warning("Retriever not initialized.")
            return []

        try:
            docs = self.retriever.invoke(query)

            if not docs:
                logger.info(
                    "No relevant documents found (similarity too low).")
                return []
            return docs

        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            return []

    def _format_docs_for_llm(self, docs):
        formatted_context = []

        for i, doc in enumerate(docs):
            source = doc.metadata.get("title", "Unknown Source")
            content = doc.page_content.replace("\n", " ").strip()

            formatted_text = f"[Source {i+1}: {source}]\n{content}\n"
            formatted_context.append(formatted_text)

        return "\n".join(formatted_context)

    def generate_augmented_prompt(self, query):
        docs = self._retrieve_documents(query)

        if not docs:
            return None, []

        context_str = self._format_docs_for_llm(docs)

        system_instruction = f"""تو هوش مصنوعی پاسخگو به سوالات آموزشی دانشگاه صنعتی شریف هستی.
                            وظیفه تو پاسخ دادن به سوالات دانشجوها *صرفاً* بر اساس متون زیر است.

                            قوانین اکید:
                            1. اگر پاسخ سوال در متن‌های زیر نیست، بگو "در قوانین موجود جوابی برای این سوال پیدا نکردم".
                            2. از خودت قانونی نساز و حدس نزن.
                            3. پاسخ را محترمانه و دقیق به زبان فارسی بده.
                            4. اگر لازم است، به نام آیین‌نامه یا قانون ارجاع بده.

                            متون قوانین (Context):
                            {context_str}
                            
                            حالا به سوال زیر پاسخ بده:
                            """
        return system_instruction, docs


if __name__ == "__main__":
    service = RAGService()
    test_query = "تعداد واحد دوره فرعی چند تاست؟"
    prompt, retrieved_docs = service.generate_augmented_prompt(test_query)

    if prompt:
        print("\n--- Generated Prompt Preview ---")
        print(prompt)

        print(f"\n--- Retrieved {len(retrieved_docs)} Sources ---")
        for d in retrieved_docs:
            print(f"- {d.metadata.get('title')}")
    else:
        print(retrieved_docs)
