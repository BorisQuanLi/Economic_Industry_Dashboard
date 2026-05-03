import logging
import os
from typing import Any

from astrapy import DataAPIClient
from astrapy.constants import VectorMetric
from astrapy.info import CollectionDefinition, CollectionVectorOptions, VectorServiceOptions

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "market_signals"
_COLLECTION_DEFINITION = CollectionDefinition(
    vector=CollectionVectorOptions(
        dimension=1024,
        metric=VectorMetric.COSINE,
        service=VectorServiceOptions(provider="nvidia", model_name="NV-Embed-QA"),
    )
)


class AstraVectorBuilder:
    """
    Persists alpha-signal records to Astra DB using server-side vectorization
    (NVIDIA nv-embedqa-e5-v5 via $vectorize field).

    Security Tier 3: credentials from ASTRA_DB_TOKEN / ASTRA_DB_API_ENDPOINT only.
    Idempotency: signal_id is used as document _id.
    Degraded-state: connection failures log a warning; persist_alpha_signal is a no-op.
    """

    def __init__(self) -> None:
        self.token = os.getenv("ASTRA_DB_TOKEN")
        self.endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        keyspace = os.getenv("ASTRA_DB_KEYSPACE", "alpha_signals")

        self.client = None
        self._collection = None

        if not self.token or not self.endpoint:
            logger.warning(
                "Astra DB credentials not set (ASTRA_DB_TOKEN / "
                "ASTRA_DB_API_ENDPOINT). Vector persistence disabled — "
                "operating in degraded state."
            )
            return

        try:
            self.client = DataAPIClient(self.token)
            db = self.client.get_database_by_api_endpoint(
                self.endpoint, keyspace=keyspace
            )
            self._collection = db.create_collection(
                _COLLECTION_NAME,
                definition=_COLLECTION_DEFINITION,
            )
            logger.info(
                "AstraVectorBuilder ready — keyspace=%s collection=%s",
                keyspace,
                _COLLECTION_NAME,
            )
        except Exception:
            logger.warning(
                "Astra DB connection failed. Vector persistence disabled — "
                "operating in degraded state.",
                exc_info=True,
            )
            self._collection = None

    def persist_alpha_signal(self, payload: dict[str, Any]) -> None:
        """
        Insert an alpha-signal document. Uses $vectorize to offload embedding
        to the NVIDIA nv-embedqa-e5-v5 H100-backed provider.

        Expected payload keys:
            signal_id (str): Ticker symbol — used as idempotent _id.
            content   (str): Text to embed via $vectorize.
            source    (str): Data source label.
        """
        if self._collection is None:
            return

        document = {
            "_id": payload["signal_id"],
            "$vectorize": payload["content"],
            "source": payload.get("source"),
            "metadata": {"hardware_target": "h100-tensor-core"},
        }

        try:
            self._collection.insert_one(document)
            logger.debug("Inserted alpha signal _id=%s", payload["signal_id"])
        except Exception:
            logger.warning(
                "Failed to insert alpha signal _id=%s — skipping.",
                payload.get("signal_id"),
                exc_info=True,
            )


# Singleton for the ETL pipeline
astra_builder = AstraVectorBuilder()
