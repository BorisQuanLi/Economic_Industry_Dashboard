"""
graph_intelligence.embeddings

Domain embedding vectors and vector-store wrappers for PE relationship intelligence.
Exposed contracts, embedders, and the FAISS vector store.
"""

from graph_intelligence.embeddings.contracts import EmbeddingVector, IndexedDocument
from graph_intelligence.embeddings.domain_embedder import DomainEmbedder
from graph_intelligence.embeddings.vector_store import FAISSVectorStore

__all__ = [
    "EmbeddingVector",
    "IndexedDocument",
    "DomainEmbedder",
    "FAISSVectorStore",
]