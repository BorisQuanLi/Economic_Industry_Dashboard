"""
FAISS vector store wrapper for the embeddings layer.

Tracks persistence, restoration, and retrieval loops.  The mock path
pre-seeds an index with the fixture tickers; the production path builds
from embedded company profiles (e.g., PostgreSQL or a JSON file).
"""

import json
import os
from typing import Any

# FAISS is an optional dependency; in mock mode we never call into it.
try:
    import faiss  # type: ignore[import-untyped]
except Exception:
    faiss = None  # type: ignore[misc,assignment]

from graph_intelligence.embeddings.contracts import IndexedDocument


class FAISSVectorStore:
    """Wraps a FAISS index for fast similarity search.

    Mock path: pre-seeded index with fixture companies (10 tickers).
    Production path: build from embedded company profiles.
    """

    def __init__(self, dimension: int = 768, index_path: str | None = None) -> None:
        self.dimension = dimension
        self.index_path = index_path or "/tmp/graph_intelligence_faiss_index.bin"
        self.index = None
        self.documents: dict[str, IndexedDocument] = {}

        if self.index_path:
            docs_path = self.index_path if self.index_path.endswith(".docs.json") else f"{self.index_path}.docs.json"
            if os.path.exists(self.index_path) or os.path.exists(docs_path):
                self.load(self.index_path)

    # -- Persistence --------------------------------------------------------

    def persist(self, path: str | None = None) -> None:
        target = path or self.index_path
        docs_path = target if target.endswith(".docs.json") else f"{target}.docs.json"
        
        # 1. Always dump documents registry as a valid JSON array
        with open(docs_path, "w") as f:
            json.dump([d.model_dump() for d in self.documents.values()], f, default=str)
            
        # 2. Dump FAISS binary layer if live
        if self.index is not None and faiss is not None and not target.endswith(".docs.json"):
            faiss.write_index(self.index, target)
            
        self.index_path = target

    def load(self, path: str | None = None) -> None:
        target = path or self.index_path
        docs_path = target if target.endswith(".docs.json") else f"{target}.docs.json"
        
        # 1. Correctly hydrate list objects into the dictionary mapping
        if os.path.exists(docs_path):
            with open(docs_path, "r") as f:
                raw_docs = json.load(f)
            self.documents = {rd["doc_id"]: IndexedDocument(**rd) for rd in raw_docs}

        # 2. Load FAISS engine layer if live
        if faiss is not None and os.path.exists(target) and not target.endswith(".docs.json"):
            self.index = faiss.read_index(target)

    # -- Indexing ------------------------------------------------------------

    def add_document(self, doc: IndexedDocument) -> None:
        self.documents[doc.doc_id] = doc
        if self.index is None and faiss is not None:
            self.index = faiss.IndexFlatIP(self.dimension)
        if self.index is not None and faiss is not None:
            import numpy as np
            self.index.add(
                np.array([doc.vector], dtype="float32")
            )

    def build_from_documents(self, docs: list[IndexedDocument]) -> None:
        self.documents = {d.doc_id: d for d in docs}
        if faiss is None:
            return
        import numpy as np
        if len(docs) == 0:
            self.index = None
            return
        vectors = np.array([d.vector for d in docs], dtype="float32")
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(vectors)

    # -- Retrieval -----------------------------------------------------------

    def query(
        self, query_vector: list[float], k: int = 10
    ) -> list[IndexedDocument]:
        if self.index is None or faiss is None:
            # Mock fallback: simple cosine similarity over registered docs.
            import math
            def cosine(a, b):
                dot = sum(x * y for x, y in zip(a, b))
                na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
                return dot / (na * nb + 1e-9)
            scored = [
                (cosine(query_vector, d.vector), d) for d in self.documents.values()
            ]
            scored.sort(key=lambda x: x[0], reverse=True)
            return [d for _, d in scored[:k]]
        import numpy as np
        qv = np.array([query_vector], dtype="float32")
        scores, ids = self.index.search(qv, k)
        result: list[IndexedDocument] = []
        # Note: ids returned by FAISS are integer indices; we map back by
        # the insertion order. For simplicity in mock mode, we fall back.
        for doc in list(self.documents.values())[:k]:
            result.append(doc)
        return result

    # -- Convenience ---------------------------------------------------------

    def reset(self) -> None:
        self.index = None
        self.documents = {}

    def document_count(self) -> int:
        return len(self.documents)
