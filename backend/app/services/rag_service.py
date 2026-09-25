import io
import json
import os
import re
from typing import List, Dict, Any, Optional

import numpy as np
import pypdf

# Lazy import for sentence_transformers and faiss to ensure smooth loading
_embedding_model = None
_faiss_module = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        print("\n[RAG] Loading embedding model: all-MiniLM-L6-v2...")
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[RAG] Embedding model loaded successfully.")
    return _embedding_model


def get_faiss():
    global _faiss_module
    if _faiss_module is None:
        import faiss
        _faiss_module = faiss
    return _faiss_module


# Path to persist the vector index and metadata
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORAGE_DIR = os.path.join(BASE_DIR, "data", "faiss_index")
INDEX_FILE = os.path.join(STORAGE_DIR, "index.faiss")
METADATA_FILE = os.path.join(STORAGE_DIR, "metadata.json")

EMBEDDING_DIM = 384


class RAGService:
    def __init__(self):
        self.storage_dir = STORAGE_DIR
        self.index_file = INDEX_FILE
        self.metadata_file = METADATA_FILE
        self.dimension = EMBEDDING_DIM
        self.chunks: List[Dict[str, Any]] = []
        self.index = None
        self._initialize_index()

    def _initialize_index(self):
        faiss = get_faiss()
        os.makedirs(self.storage_dir, exist_ok=True)

        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            try:
                print(f"[RAG] Loading existing FAISS index from {self.index_file}...")
                self.index = faiss.read_index(self.index_file)
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                print(f"[RAG] Successfully loaded {len(self.chunks)} chunks from disk.")
                return
            except Exception as e:
                print(f"[RAG] Error loading saved index: {e}. Creating a new index.")

        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks = []

    def _save_index(self):
        faiss = get_faiss()
        os.makedirs(self.storage_dir, exist_ok=True)
        if self.index is not None:
            faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)

    # ----------------------------------------------------
    # Document Text Extraction
    # ----------------------------------------------------
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        # Remove null bytes and control chars
        text = text.replace("\x00", "")
        # Normalize whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def extract_text_from_pdf(self, file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        pages_content = []
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)
        for page_num in range(1, total_pages + 1):
            page = reader.pages[page_num - 1]
            raw_text = page.extract_text() or ""
            cleaned = self.clean_text(raw_text)
            if cleaned:
                pages_content.append({
                    "source": filename,
                    "page": page_num,
                    "text": cleaned
                })
        return pages_content

    def extract_text_from_text(self, file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        try:
            raw_text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raw_text = file_bytes.decode("latin-1", errors="replace")

        cleaned = self.clean_text(raw_text)
        if not cleaned:
            return []
        return [{
            "source": filename,
            "page": 1,
            "text": cleaned
        }]

    # ----------------------------------------------------
    # Text Chunking
    # ----------------------------------------------------
    def chunk_document(
        self,
        sections: List[Dict[str, Any]],
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ) -> List[Dict[str, Any]]:
        chunks = []
        for section in sections:
            source = section["source"]
            page = section["page"]
            text = section["text"]

            if len(text) <= chunk_size:
                chunks.append({
                    "source": source,
                    "page": page,
                    "text": text
                })
                continue

            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                # Try not to split in the middle of a word if near the boundary
                if end < len(text):
                    last_space = text.rfind(" ", start, end)
                    if last_space > start + chunk_size // 2:
                        end = last_space

                chunk_str = text[start:end].strip()
                if chunk_str:
                    chunks.append({
                        "source": source,
                        "page": page,
                        "text": chunk_str
                    })

                if end >= len(text):
                    break
                start = end - chunk_overlap
                if start < 0 or start >= end:
                    start = end

        return chunks

    # ----------------------------------------------------
    # Ingestion & Indexing
    # ----------------------------------------------------
    def add_document(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        lower_name = filename.lower()
        if lower_name.endswith(".pdf"):
            sections = self.extract_text_from_pdf(file_bytes, filename)
        elif lower_name.endswith(".txt") or lower_name.endswith(".md"):
            sections = self.extract_text_from_text(file_bytes, filename)
        else:
            raise ValueError(f"Unsupported file type for '{filename}'. Supported types: .pdf, .txt, .md")

        if not sections:
            raise ValueError(f"No readable text could be extracted from '{filename}'.")

        new_chunks = self.chunk_document(sections)
        if not new_chunks:
            raise ValueError(f"No valid text chunks were created from '{filename}'.")

        # Compute embeddings for new chunks
        model = get_embedding_model()
        texts = [c["text"] for c in new_chunks]
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

        # Normalize embeddings for cosine similarity
        faiss = get_faiss()
        embeddings = embeddings.astype("float32")
        faiss.normalize_L2(embeddings)

        # Add to FAISS index
        self.index.add(embeddings)

        # Append chunks metadata
        start_id = len(self.chunks)
        for i, chunk in enumerate(new_chunks):
            chunk["id"] = start_id + i
            self.chunks.append(chunk)

        # Persist to disk
        self._save_index()

        unique_sources = list({c["source"] for c in self.chunks})
        return {
            "filename": filename,
            "chunks_added": len(new_chunks),
            "total_chunks": len(self.chunks),
            "total_documents": len(unique_sources)
        }

    # ----------------------------------------------------
    # Semantic Search
    # ----------------------------------------------------
    def similarity_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        if self.index is None or self.index.ntotal == 0 or len(self.chunks) == 0:
            return []

        model = get_embedding_model()
        query_embedding = model.encode([query.strip()], convert_to_numpy=True, show_progress_bar=False)
        query_embedding = query_embedding.astype("float32")

        faiss = get_faiss()
        faiss.normalize_L2(query_embedding)

        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx].copy()
            chunk["score"] = round(float(dist), 4)
            results.append(chunk)

        return results

    # ----------------------------------------------------
    # Status & Management
    # ----------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        unique_sources = sorted(list({c["source"] for c in self.chunks}))
        return {
            "total_documents": len(unique_sources),
            "total_chunks": len(self.chunks),
            "sources": unique_sources,
            "embedding_model": "all-MiniLM-L6-v2",
            "index_type": "FAISS IndexFlatIP (Cosine Similarity)"
        }

    def clear_index(self):
        faiss = get_faiss()
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks = []
        if os.path.exists(self.index_file):
            try:
                os.remove(self.index_file)
            except OSError:
                pass
        if os.path.exists(self.metadata_file):
            try:
                os.remove(self.metadata_file)
            except OSError:
                pass
        return {"message": "RAG index cleared successfully"}


# Singleton instance
rag_service = RAGService()
