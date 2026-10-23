
import socket
from unittest.mock import Mock

import httpx

from aegisops.services import network_probes, web_probes


def test_tcp_probe_success(monkeypatch):
    mock_connection = Mock()
    mock_connection.__enter__ = Mock(
        return_value=mock_connection
    )
    mock_connection.__exit__ = Mock(
        return_value=False
    )

    monkeypatch.setattr(
        network_probes.socket,
        "create_connection",
        lambda address, timeout: mock_connection,
    )

    result = network_probes.tcp_probe("example.com", 443)

    assert result["probe"] == "tcp"
    assert result["success"] is True
    assert result["host"] == "example.com"
    assert result["port"] == 443
    mock_connection.__enter__.assert_called_once()
    mock_connection.__exit__.assert_called_once()


def test_tcp_probe_failure(monkeypatch):
    def fail_connection(address, timeout):
        raise OSError("Connection refused")

    monkeypatch.setattr(
        network_probes.socket,
        "create_connection",
        fail_connection,
    )

    result = network_probes.tcp_probe("localhost", 12345)

    assert result["success"] is False
    assert "Connection refused" in result["error"]


def test_dns_probe_success(monkeypatch):
    monkeypatch.setattr(
        network_probes.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.1", 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.1", 0)),
            (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("2001:db8::1", 0, 0, 0)),
        ],
    )

    result = network_probes.dns_probe("example.com")

    assert result["success"] is True
    assert result["addresses"] == ["192.0.2.1", "2001:db8::1"]


def test_dns_probe_failure(monkeypatch):
    def fail_lookup(*args, **kwargs):
        raise socket.gaierror("Name resolution failed")

    monkeypatch.setattr(
        network_probes.socket,
        "getaddrinfo",
        fail_lookup,
    )

    result = network_probes.dns_probe("invalid.invalid")

    assert result["success"] is False
    assert result["addresses"] == []
    assert "Name resolution failed" in result["error"]


def test_http_probe_success(monkeypatch):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.url = "https://example.com/"

    class MockClient:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, url):
            return mock_response

    monkeypatch.setattr(web_probes.httpx, "Client", MockClient)

    result = web_probes.http_probe("https://example.com")

    assert result["success"] is True
    assert result["status_code"] == 200
    assert result["final_url"] == "https://example.com/"


def test_http_probe_failure(monkeypatch):
    class MockClient:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, url):
            raise httpx.ConnectError("Connection failed")

    monkeypatch.setattr(web_probes.httpx, "Client", MockClient)

    result = web_probes.http_probe("https://example.com")

    assert result["success"] is False
    assert result["status_code"] is None
    assert "Connection failed" in result["error"]


def test_http_probe_rejects_invalid_url():
    result = web_probes.http_probe("not-a-valid-url")

    assert result["success"] is False
    assert result["status_code"] is None


def test_tls_probe_success(monkeypatch):
    certificate = {
        "notAfter": "Dec 31 23:59:59 2099 GMT",
    }

    mock_tls_socket = Mock()
    mock_tls_socket.__enter__ = Mock(return_value=mock_tls_socket)
    mock_tls_socket.__exit__ = Mock(return_value=False)
    mock_tls_socket.getpeercert.return_value = certificate
    mock_tls_socket.version.return_value = "TLSv1.3"

    mock_raw_socket = Mock()
    mock_raw_socket.__enter__ = Mock(return_value=mock_raw_socket)
    mock_raw_socket.__exit__ = Mock(return_value=False)
    

    monkeypatch.setattr(
        web_probes.socket,
        "create_connection",
        lambda address, timeout: mock_raw_socket,
    )
    monkeypatch.setattr(
        web_probes.ssl.SSLContext,
        "wrap_socket",
        lambda self, sock, server_hostname: mock_tls_socket,
    )

    result = web_probes.tls_probe("example.com")

    assert result["success"] is True
    assert result["tls_version"] == "TLSv1.3"
    assert result["certificate_expires_at"] is not None
    assert result["days_until_expiry"] > 0


def test_tls_probe_failure(monkeypatch):
    def fail_connection(address, timeout):
        raise OSError("Connection timed out")

    monkeypatch.setattr(
        web_probes.socket,
        "create_connection",
        fail_connection,
    )

    result = web_probes.tls_probe("example.com")

    assert result["success"] is False
    assert result["tls_version"] is None
    assert "Connection timed out" in result["error"]
