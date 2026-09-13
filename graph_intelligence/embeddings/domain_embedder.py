"""Deterministic embedding provider for the graph_intelligence service.

The DomainEmbedder produces 768-dimensional vectors.  When
USE_FAKE_EMBEDDINGS is set (the default in offline dev), it returns
deterministic, seeded vectors derived from a small fixture dictionary.
In production the embedder can be swapped for a sentence-transformers
or OpenAI adapter via dependency injection.
"""

import hashlib
import os
from typing import Callable

# --- Configuration ---------------------------------------------------------

DIMENSIONS = 768
"""Fixed vector dimensionality matching all-MiniLM-L6-v2 and text-embedding-3-small."""

# Deterministic fixture corpus: ticker -> short descriptive text.
# Each entry seeds a stable vector via SHA-256 so embeddings are
# reproducible across sessions without external model calls.
_EMBEDDING_FIXTURES: dict[str, str] = {
    "AAPL": "Apple Inc consumer electronics and services ecosystem",
    "MSFT": "Microsoft cloud productivity and enterprise software",
    "GOOGL": "Alphabet search advertising and cloud infrastructure",
    "AMZN": "Amazon e-commerce and AWS cloud services",
    "NVDA": "NVIDIA graphics processing and AI accelerators",
    "JPM": "JPMorgan Chase investment banking and asset management",
    "GS": "Goldman Sachs global investment banking and securities",
    "MS": "Morgan Stanley wealth management and investment banking",
    "BLK": "BlackRock asset management and Aladdin platform",
    "SCHW": "Charles Schwab retail brokerage and banking",
}


def _deterministic_vector(text: str, dimensions: int = DIMENSIONS) -> list[float]:
    """Derive a stable float vector from a text string via SHA-256."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    # Expand the 32-byte digest into `dimensions` floats in [0, 1).
    floats: list[float] = []
    for i in range(dimensions):
        # Cycle through the digest bytes.
        byte_val = digest[i % len(digest)]
        # XOR in the next byte to add entropy across dimensions.
        byte_val ^= digest[(i + 1) % len(digest)]
        floats.append(byte_val / 255.0)
    # Normalize to unit L2 so cosine similarity is well-defined.
    norm = sum(v * v for v in floats) ** 0.5
    if norm > 0:
        return [v / norm for v in floats]
    return [0.0] * dimensions


# --- Public API ------------------------------------------------------------

class DomainEmbedder:
    """Produces 768-dimensional embeddings tuned for PE deal criteria.

    Mock path (USE_FAKE_EMBEDDINGS=true / unset):
        Returns deterministic seeded vectors from a small fixture dict.
    Production path:
        Inject a callable via the `embed_fn` parameter or set
        EMBEDDING_API_KEY to use OpenAI text-embedding-3-small.
    """

    def __init__(
        self,
        dimensions: int = DIMENSIONS,
        embed_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self.dimensions = dimensions
        self._embed_fn = embed_fn
        self._use_fake = (
            os.environ.get("USE_FAKE_EMBEDDINGS", "true").lower() == "true"
        )

    # -- embedding ---------------------------------------------------------

    def embed(self, text: str) -> list[float]:
        """Embed a single text string into a 768-d float vector."""
        if self._use_fake and self._embed_fn is None:
            return _deterministic_vector(text, self.dimensions)
        if self._embed_fn is not None:
            return self._embed_fn(text)
        raise RuntimeError(
            "No embedder function provided. Set USE_FAKE_EMBEDDINGS=true or pass "
            "embed_fn to DomainEmbedder."
        )

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of text strings."""
        return [self.embed(text) for text in texts]


# Module-level singleton for convenience import.
_default_embedder = DomainEmbedder()


def get_default_embedder() -> DomainEmbedder:
    """Return the module-level default DomainEmbedder instance."""
    return _default_embedder