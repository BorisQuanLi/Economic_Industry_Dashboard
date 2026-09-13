"""Strict Pydantic contracts for the embeddings layer.

These contracts define the canonical shapes used by the domain embedder,
the FAISS vector store, and any consumer (re-ranker, workflow, evals).
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EmbeddingVector(BaseModel):
    """A single embedding vector with metadata.

    Dimensions are fixed at 768 to match sentence-transformers/all-MiniLM-L6-v2
    and the OpenAI text-embedding-3-small default when projected.
    """

    model_config = ConfigDict(extra="forbid")

    doc_id: str = Field(min_length=1)
    vector: list[float] = Field(
        min_length=768,
        max_length=768,
    )
    source: str = Field(default="unknown")


class IndexedDocument(BaseModel):
    """A document stored in the vector store.

    Wraps an embedding vector with the raw text and arbitrary metadata
    (ticker, sector, deal stage, etc.) used downstream by the re-ranker.
    """

    model_config = ConfigDict(extra="forbid")

    doc_id: str = Field(min_length=1)
    ticker: str = Field(min_length=1)
    text: str = Field(min_length=1)
    vector: list[float] = Field(
        min_length=768,
        max_length=768,
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    source: str = Field(default="unknown")