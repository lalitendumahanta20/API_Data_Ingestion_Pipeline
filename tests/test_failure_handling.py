
import pytest
import requests
from unittest.mock import Mock
from unittest.mock import patch
from ingestion import ingest
from ingestion import api_client


def disable_waiting(monkeypatch):
    monkeypatch.setattr(
        api_client,
        "apply_rate_limit",
        lambda: None
    )
    monkeypatch.setattr(
        api_client.time,
        "sleep",
        lambda seconds: None
    )


def test_api_server_failure(monkeypatch):
    """Verify that repeated HTTP 500 responses are returned after retries."""

    disable_waiting(monkeypatch)

    monkeypatch.setattr(api_client, "MAX_RETRIES", 2)

    failed_response = Mock()
    failed_response.status_code = 500
    failed_response.headers = {}

    mock_get = Mock(return_value=failed_response)

    monkeypatch.setattr(
        api_client.session,
        "get",
        mock_get
    )

    response = api_client.fetch_page(
        "customers",
        1,
        2
    )

    assert response.status_code == 500
    assert mock_get.call_count == 3


def test_api_connection_failure(monkeypatch):
    """Verify that connection errors are raised after retries."""

    disable_waiting(monkeypatch)

    monkeypatch.setattr(api_client, "MAX_RETRIES", 2)

    mock_get = Mock(
        side_effect=requests.exceptions.ConnectionError(
            "API server unavailable"
        )
    )

    monkeypatch.setattr(
        api_client.session,
        "get",
        mock_get
    )

    with pytest.raises(requests.exceptions.ConnectionError):
        api_client.fetch_page(
            "customers",
            1,
            2
        )

    assert mock_get.call_count == 3


def test_api_timeout_failure(monkeypatch):
    """Verify that timeout errors are raised after retries."""

    disable_waiting(monkeypatch)

    monkeypatch.setattr(api_client, "MAX_RETRIES", 2)

    mock_get = Mock(
        side_effect=requests.exceptions.Timeout(
            "API request timed out"
        )
    )

    monkeypatch.setattr(
        api_client.session,
        "get",
        mock_get
    )

    with pytest.raises(requests.exceptions.Timeout):
        api_client.fetch_page(
            "customers",
            1,
            2
        )

    assert mock_get.call_count == 3
    
def test_pipeline_database_connection_failure():
    
    from unittest.mock import patch
    from ingestion import ingest

    with patch(
       "ingestion.ingest.get_connection",
        side_effect=Exception("Database connection failed")
    ) as mock_connection:

        ingest.run_pipeline()
        mock_connection.assert_called_once()
