
import requests
from unittest.mock import Mock

from ingestion import api_client


def disable_waiting(monkeypatch):
    """Prevent real rate-limit and retry delays during tests."""
    monkeypatch.setattr(api_client, "apply_rate_limit", lambda: None)
    monkeypatch.setattr(api_client.time, "sleep", lambda seconds: None)


def make_response(status_code, headers=None):
    """Create a fake HTTP response."""
    response = Mock()
    response.status_code = status_code
    response.headers = headers or {}
    return response


# Test 1: API authentication header exists
def test_api_authentication_header():
    assert "X_API_Token" in api_client.session.headers
    assert api_client.session.headers["X_API_Token"] == api_client.API_TOKEN


# Test 2: Successful API request
def test_fetch_page_success(monkeypatch):
    disable_waiting(monkeypatch)

    expected_response = make_response(200)

    mock_get = Mock(return_value=expected_response)
    monkeypatch.setattr(api_client.session, "get", mock_get)

    response = api_client.fetch_page("customers", 1, 2)

    assert response.status_code == 200
    mock_get.assert_called_once_with(
        f"{api_client.BASE_URL}/customers",
        params={"page": 1, "limit": 2},
        timeout=30
    )


# Test 3: API request retries after HTTP 500
def test_fetch_page_retries_after_server_error(monkeypatch):
    disable_waiting(monkeypatch)

    monkeypatch.setattr(api_client, "MAX_RETRIES", 2)

    failed_response = make_response(500)
    successful_response = make_response(200)

    mock_get = Mock(
        side_effect=[failed_response, successful_response]
    )
    monkeypatch.setattr(api_client.session, "get", mock_get)

    response = api_client.fetch_page("customers", 1, 2)

    assert response.status_code == 200
    assert mock_get.call_count == 2
    failed_response.close.assert_called_once()


# Test 4: Returns final response when retries are exhausted
def test_fetch_page_retries_exhausted(monkeypatch):
    disable_waiting(monkeypatch)

    monkeypatch.setattr(api_client, "MAX_RETRIES", 2)

    failed_response = make_response(500)

    mock_get = Mock(return_value=failed_response)
    monkeypatch.setattr(api_client.session, "get", mock_get)

    response = api_client.fetch_page("customers", 1, 2)

    assert response.status_code == 500
    assert mock_get.call_count == 3


# Test 5: Non-retryable HTTP status is returned immediately
def test_fetch_page_non_retryable_error(monkeypatch):
    disable_waiting(monkeypatch)

    monkeypatch.setattr(api_client, "MAX_RETRIES", 2)

    bad_response = make_response(400)

    mock_get = Mock(return_value=bad_response)
    monkeypatch.setattr(api_client.session, "get", mock_get)

    response = api_client.fetch_page("customers", 1, 2)

    assert response.status_code == 400
    assert mock_get.call_count == 1


# Test 6: Retries after a connection timeout
def test_fetch_page_retries_after_timeout(monkeypatch):
    disable_waiting(monkeypatch)

    monkeypatch.setattr(api_client, "MAX_RETRIES", 2)

    successful_response = make_response(200)

    mock_get = Mock(
        side_effect=[
            requests.exceptions.Timeout("Request timed out"),
            successful_response
        ]
    )
    monkeypatch.setattr(api_client.session, "get", mock_get)

    response = api_client.fetch_page("customers", 1, 2)

    assert response.status_code == 200
    assert mock_get.call_count == 2


# Test 7: Raises timeout when all retries are exhausted
def test_fetch_page_timeout_exhausted(monkeypatch):
    disable_waiting(monkeypatch)

    monkeypatch.setattr(api_client, "MAX_RETRIES", 2)

    mock_get = Mock(
        side_effect=requests.exceptions.Timeout("Request timed out")
    )
    monkeypatch.setattr(api_client.session, "get", mock_get)

    try:
        api_client.fetch_page("customers", 1, 2)
        assert False, "Expected Timeout exception"
    except requests.exceptions.Timeout:
        pass

    assert mock_get.call_count == 3


# Test 8: Sends optional query parameters
def test_fetch_page_extra_params(monkeypatch):
    disable_waiting(monkeypatch)

    expected_response = make_response(200)

    mock_get = Mock(return_value=expected_response)
    monkeypatch.setattr(api_client.session, "get", mock_get)

    api_client.fetch_page(
        "customers",
        1,
        2,
        extra_params={"updated_since": "2026-11-01T00:00:00Z"}
    )

    mock_get.assert_called_once_with(
        f"{api_client.BASE_URL}/customers",
        params={
            "page": 1,
            "limit": 2,
            "updated_since": "2026-11-01T00:00:00Z"
        },
        timeout=30
    )
