import os
import json
import re
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

from app.core.config import RAG_EMBEDDING_MODEL, RAG_VECTOR_DB_PATH

load_dotenv()

DATA_DIR = os.path.join(project_root, "data")
VECTOR_DB_DIR = os.path.join(project_root, RAG_VECTOR_DB_PATH)
EMBEDDING_MODEL_NAME = RAG_EMBEDDING_MODEL


def load_documents(data_dir):
    docs = []

    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".md"):
                path = os.path.join(root, file)

                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                    text = (
                        text.replace("ي", "ی")
                        .replace("ك", "ک")
                        .replace("\u200c", " ")
                        .replace("\u200f", "")
                        .replace("*", "")
                    )
                    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)

                metadata = {}
                metadata_path = os.path.join(root, "metadata.json")

                if os.path.exists(metadata_path):
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)

                metadata["source_file"] = file
                metadata["source_path"] = path

                docs.append(
                    Document(page_content=text, metadata=metadata)
                )

    return docs


def split_documents(docs):

    headers = [
        ("#", "title"),
        ("##", "section"),
        ("###", "subsection"),
    ]

    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers
    )

    md_chunks = []
    for d in docs:
        splits = header_splitter.split_text(d.page_content)
        for s in splits:
            s.metadata.update(d.metadata)
            md_chunks.append(s)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=450,
        chunk_overlap=70,
        separators=["\n\n\n", "\n\n", "\n", "।", ".", " ", ""],
    )

    final_chunks = splitter.split_documents(md_chunks)

    for i, c in enumerate(final_chunks):
        c.metadata["chunk_id"] = i

    print("Total chunks:", len(final_chunks))
    return final_chunks


def create_vector_db(chunks):
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL_NAME
    )
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(VECTOR_DB_DIR)
    print("Vector DB saved.")


if __name__ == "__main__":
    docs = load_documents(DATA_DIR)

    if docs:
        print("Loaded:", len(docs))
        chunks = split_documents(docs)
        create_vector_db(chunks)
    else:
        print("No documents found.")
