from unittest.mock import MagicMock, patch


@patch("etl_service.src.db.connection.psycopg2.connect")
@patch("etl_service.src.db.connection.boto3.client")
def test_get_iam_token_connection_uses_token_as_password(mock_boto_client, mock_pg_connect):
    mock_rds = MagicMock()
    mock_rds.generate_db_auth_token.return_value = "mock-token-xyz"
    mock_boto_client.return_value = mock_rds

    from etl_service.src.db.connection import get_iam_token_connection
    get_iam_token_connection()

    mock_rds.generate_db_auth_token.assert_called_once()
    _, kwargs = mock_pg_connect.call_args
    assert kwargs["password"] == "mock-token-xyz"
    assert kwargs["sslmode"] == "require"


@patch("etl_service.src.db.connection.psycopg2.connect")
@patch("etl_service.src.db.connection.boto3.client")
def test_get_db_routes_to_iam_when_env_set(mock_boto_client, mock_pg_connect, monkeypatch):
    monkeypatch.setenv("DB_AUTH_MODE", "iam")

    mock_rds = MagicMock()
    mock_rds.generate_db_auth_token.return_value = "mock-token-xyz"
    mock_boto_client.return_value = mock_rds

    import etl_service.src.db.db as db_module
    db_module.conn = None  # reset global

    db_module.get_db()

    mock_pg_connect.assert_called_once()
    assert mock_pg_connect.call_args.kwargs["sslmode"] == "require"
