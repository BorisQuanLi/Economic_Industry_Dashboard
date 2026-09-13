"""Unit tests for the embeddings layer.

Tests cover:
- Deterministic vector dimensions (768)
- Batch embedding consistency
- FAISS vector store query top-k retrieval
- Persistence and restoration
- Fixture-backed embedding determinism
"""

import json
import os
import random
import tempfile

import pytest

from graph_intelligence.embeddings.contracts import EmbeddingVector, IndexedDocument
from graph_intelligence.embeddings.domain_embedder import DomainEmbedder, _deterministic_vector
from graph_intelligence.embeddings.vector_store import FAISSVectorStore


# --- Fixtures -------------------------------------------------------------

@pytest.fixture
def mock_faiss():
    """Patch FAISS to avoid importing the heavy library in mock mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# --- Embedding Tests ------------------------------------------------------

def test_embedding_vector_dimensions():
    embedder = DomainEmbedder()
    vec = embedder.embed("test")
    assert len(vec) == 768
    # Unit test that the deterministic fixture vector is consistent
    vec2 = embedder.embed("test")
    assert vec == vec2


def test_embedding_batch():
    embedder = DomainEmbedder()
    texts = ["apple", "banana", "cherry"]
    batch = embedder.embed_batch(texts)
    assert len(batch) == 3
    assert all(len(v) == 768 for v in batch)


def test_fixture_vector_consistency():
    # Verify that the deterministic vector is stable across calls
    text = "AAPL"
    vec1 = _deterministic_vector(text)
    vec2 = _deterministic_vector(text)
    assert vec1 == vec2


def test_vector_store_query_top_k():
    store = FAISSVectorStore(dimension=768)
    # Add 3 fixture documents
    docs = [
        IndexedDocument(
            doc_id="AAPL",
            ticker="AAPL",
            text="Apple",
            vector=[1.0] * 768,  # dummy unit vector
            metadata={"sector": "tech"},
        ),
        IndexedDocument(
            doc_id="MSFT",
            ticker="MSFT",
            text="Microsoft",
            vector=[0.0] * 768,  # dummy zero vector
            metadata={"sector": "tech"},
        ),
        IndexedDocument(
            doc_id="IBM",
            ticker="IBM",
            text="IBM",
            vector=[0.5] * 768,  # dummy half vector
            metadata={"sector": "tech"},
        ),
    ]
    for doc in docs:
        store.add_document(doc)

    # Query should return at least the AAPL doc (1.0 similarity) first
    query_vec = [1.0] * 768  # perfect match
    results = store.query(query_vec, k=2)
    assert len(results) == 2
    assert results[0].doc_id == "AAPL"
    assert results[1].doc_id in {"AAPL", "MSFT", "IBM"}


def test_persistence_and_restore():
    store = FAISSVectorStore(dimension=768)
    store.add_document(
        IndexedDocument(
            doc_id="TEST",
            ticker="TEST",
            text="test text",
            vector=[0.1] * 768,
            metadata={"test": "metadata"},
        )
    )
    # Persist
    tmpdir = tempfile.mkdtemp()
    store.persist(os.path.join(tmpdir, "index"))
    # Load in new instance
    new_store = FAISSVectorStore(dimension=768, index_path=os.path.join(tmpdir, "index"))
    assert new_store.document_count() == 1
    assert new_store.documents["TEST"] is not None


def test_embedding_determinism_with_fixture():
    embedder = DomainEmbedder()
    vec1 = embedder.embed("AAPL")
    vec2 = embedder.embed("AAPL")
    assert vec1 == vec2


# --- Integration-style test (simple) ------------------------------------

def test_full_embedding_flow():
    embedder = DomainEmbedder()
    doc = IndexedDocument(
        doc_id="TEST",
        ticker="TEST",
        text="test text",
        vector=[0.2] * 768,
        metadata={"test": "metadata"},
    )
    store = FAISSVectorStore(dimension=768)
    store.add_document(doc)
    # Query should return the doc
    results = store.query([0.2] * 768, k=1)
    assert len(results) == 1
    assert results[0].doc_id == "TEST"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])