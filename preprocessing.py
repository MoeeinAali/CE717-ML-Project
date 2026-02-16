import os
import json
from dotenv import load_dotenv
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

load_dotenv()

DATA_DIR = "data"
VECTOR_DB_DIR = "vector_store"

EMBEDDING_MODEL_NAME = "text-embedding-3-small" # text-embedding-3-large 


def load_documents(data_dir):
    docs = []
    if not os.path.exists(data_dir):
        print(f"Error: Directory '{data_dir}' not found.")
        return []

    print(f"Loading documents from {data_dir}...")

    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read()

                    metadata = {}
                    metadata_path = os.path.join(root, "metadata.json")
                    if os.path.exists(metadata_path):
                        with open(metadata_path, "r", encoding="utf-8") as f:
                            metadata = json.load(f)

                    metadata["source_file"] = file

                    docs.append(Document(page_content=text, metadata=metadata))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return docs


def split_documents(docs):
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on)

    md_header_splits = []
    print("Splitting documents by headers...")
    for doc in docs:
        splits = markdown_splitter.split_text(doc.page_content)
        for split in splits:
            split.metadata.update(doc.metadata)
            md_header_splits.append(split)

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-4",
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )

    final_splits = text_splitter.split_documents(md_header_splits)
    print(f"Total chunks created: {len(final_splits)}")
    return final_splits


def create_and_save_vector_db(chunks):
    print(f"Initializing OpenAI Embeddings ({EMBEDDING_MODEL_NAME})...")

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        check_embedding_ctx_length=False
    )

    print("Creating FAISS index (Generating embeddings)...")
    try:
        if chunks:
            vector_db = FAISS.from_documents(chunks, embeddings)

            print(f"Saving vector store to '{VECTOR_DB_DIR}'...")
            vector_db.save_local(VECTOR_DB_DIR)
            print("Vector Database created successfully!")
        else:
            print("No chunks to process.")
    except Exception as e:
        print(f"Error creating vector DB: {e}")


raw_docs = load_documents(DATA_DIR)

if raw_docs:
    print(f"Loaded {len(raw_docs)} documents.")
    chunks = split_documents(raw_docs)
    create_and_save_vector_db(chunks)
else:
    print("No documents found. Please run crawler.py first.")
