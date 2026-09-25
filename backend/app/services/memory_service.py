import json
import os
import time
from typing import List, Dict, Any, Optional

import numpy as np

from app.services.rag_service import get_embedding_model, get_faiss

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEMORY_STORAGE_DIR = os.path.join(BASE_DIR, "data", "memory_index")
MEMORY_INDEX_FILE = os.path.join(MEMORY_STORAGE_DIR, "memory.faiss")
MEMORY_METADATA_FILE = os.path.join(MEMORY_STORAGE_DIR, "memory_metadata.json")
EMBEDDING_DIM = 384


class MemoryService:
    def __init__(self):
        self.storage_dir = MEMORY_STORAGE_DIR
        self.index_file = MEMORY_INDEX_FILE
        self.metadata_file = MEMORY_METADATA_FILE
        self.dimension = EMBEDDING_DIM
        self.memories: List[Dict[str, Any]] = []
        self.index = None
        self._initialize_index()

    def _initialize_index(self):
        faiss = get_faiss()
        os.makedirs(self.storage_dir, exist_ok=True)

        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            try:
                print(f"[RAG Memory] Loading memory index from {self.index_file}...")
                self.index = faiss.read_index(self.index_file)
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    self.memories = json.load(f)
                print(f"[RAG Memory] Loaded {len(self.memories)} past interview memories.")
                return
            except Exception as e:
                print(f"[RAG Memory] Error loading memory index: {e}. Reinitializing.")

        self.index = faiss.IndexFlatIP(self.dimension)
        self.memories = []

    def _save_index(self):
        faiss = get_faiss()
        os.makedirs(self.storage_dir, exist_ok=True)
        if self.index is not None:
            faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

    def record_turn(
        self,
        role: str,
        question: str,
        user_answer: str,
        evaluation: Dict[str, Any],
        difficulty: str = "Medium"
    ) -> Dict[str, Any]:
        """
        Embed and persist an interview Q&A turn along with its score and feedback.
        """
        score = evaluation.get("overall_score", 0)
        strengths = evaluation.get("strengths", [])
        weaknesses = evaluation.get("weaknesses", [])
        suggestion = evaluation.get("improvement_suggestion", "")

        memory_text = (
            f"Target Role: {role}\n"
            f"Difficulty: {difficulty}\n"
            f"Question: {question}\n"
            f"Candidate Answer: {user_answer}\n"
            f"Performance Score: {score}/10\n"
            f"Identified Strengths: {', '.join(strengths) if strengths else 'None'}\n"
            f"Identified Weaknesses: {', '.join(weaknesses) if weaknesses else 'None'}\n"
            f"Improvement Tip: {suggestion}"
        )

        model = get_embedding_model()
        embedding = model.encode([memory_text], convert_to_numpy=True, show_progress_bar=False)
        embedding = embedding.astype("float32")

        faiss = get_faiss()
        faiss.normalize_L2(embedding)

        self.index.add(embedding)

        entry = {
            "id": len(self.memories),
            "timestamp": time.time(),
            "role": role,
            "question": question,
            "answer_preview": user_answer[:150] + ("..." if len(user_answer) > 150 else ""),
            "score": score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "text": memory_text
        }
        self.memories.append(entry)
        self._save_index()

        print(f"[RAG Memory] Successfully recorded memory for question: '{question[:50]}...'")
        return entry

    def retrieve_memories(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve top-k most relevant past interview turns using semantic similarity.
        """
        if not query or not query.strip():
            return []

        if self.index is None or self.index.ntotal == 0 or len(self.memories) == 0:
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
            if idx < 0 or idx >= len(self.memories):
                continue
            item = self.memories[idx].copy()
            item["similarity"] = round(float(dist), 4)
            results.append(item)

        return results

    def get_status(self) -> Dict[str, Any]:
        scores = [m["score"] for m in self.memories if "score" in m]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

        all_weaknesses = []
        for m in self.memories:
            for w in m.get("weaknesses", []):
                if w and w not in all_weaknesses:
                    all_weaknesses.append(w)

        return {
            "total_memories": len(self.memories),
            "average_past_score": avg_score,
            "recent_questions": [m["question"] for m in self.memories[-5:]],
            "past_weaknesses": all_weaknesses[-6:]
        }

    def clear_memory(self):
        faiss = get_faiss()
        self.index = faiss.IndexFlatIP(self.dimension)
        self.memories = []
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
        return {"message": "RAG interview memory cleared successfully"}


memory_service = MemoryService()
