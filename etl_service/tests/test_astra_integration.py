import os
import pytest
from unittest.mock import MagicMock, patch
from etl_service.src.adapters.astra_vector_builder import AstraVectorBuilder


def test_astra_vector_builder_initialization_security_tier_3():
    """Verify ASTRA_DB_TOKEN is the credential key (Security Tier 3)."""
    with patch.dict(os.environ, {"ASTRA_DB_TOKEN": "AstraCS:test_token", "ASTRA_DB_API_ENDPOINT": "https://test.com"}):
        builder = AstraVectorBuilder()
        assert builder.token == "AstraCS:test_token"
        assert "ASTRA_DB_TOKEN" in str(os.environ)


@patch("etl_service.src.adapters.astra_vector_builder.DataAPIClient")
def test_vectorize_payload_structure(mock_client):
    """Verify idempotency (_id = signal_id) and $vectorize pattern."""
    with patch.dict(os.environ, {
        "ASTRA_DB_TOKEN": "test",
        "ASTRA_DB_API_ENDPOINT": "https://test.com",
    }):
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client.return_value.get_database_by_api_endpoint.return_value = mock_db
        mock_db.create_collection.return_value = mock_collection

        builder = AstraVectorBuilder()
        builder.persist_alpha_signal({
            "signal_id": "NVDA",
            "content": "Nvidia high performance compute signal",
            "source": "AlphaVantage",
        })

        args, _ = mock_collection.insert_one.call_args
        doc = args[0]

        assert doc["_id"] == "NVDA"
        assert "$vectorize" in doc
        assert doc["metadata"]["hardware_target"] == "h100-tensor-core"


def test_persist_alpha_signal_degraded_state():
    """persist_alpha_signal must be a no-op when credentials are absent."""
    with patch.dict(os.environ, {}, clear=True):
        builder = AstraVectorBuilder()
        assert builder._collection is None
        # Must not raise
        builder.persist_alpha_signal({"signal_id": "AAPL", "content": "test", "source": "x"})


@pytest.mark.skip(reason="Manual integration test for GCP us-east1 endpoint")
def test_live_astra_connection_gcp():
    builder = AstraVectorBuilder()
    try:
        coll = builder.initialize_storage()
        assert coll is not None
    except Exception as e:
        pytest.fail(f"Degraded state logic failed to handle connection: {e}")
