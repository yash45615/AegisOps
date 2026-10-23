
import socket
import ssl
import time
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit

import httpx


def http_probe(
    url: str,
    timeout: float = 5.0,
) -> dict[str, Any]:
    """Check an HTTP or HTTPS endpoint."""
    started = time.perf_counter()

    try:
        parsed = urlsplit(url)

        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Provide a valid http:// or https:// URL")

        with httpx.Client(
            timeout=timeout,
            follow_redirects=True,
        ) as client:
            response = client.get(url)

        elapsed_ms = round(
            (time.perf_counter() - started) * 1000,
            2,
        )

        return {
            "probe": "http",
            "url": url,
            "success": True,
            "status_code": response.status_code,
            "final_url": str(response.url),
            "latency_ms": elapsed_ms,
            "error": None,
        }

    except (httpx.HTTPError, ValueError) as exc:
        elapsed_ms = round(
            (time.perf_counter() - started) * 1000,
            2,
        )

        return {
            "probe": "http",
            "url": url,
            "success": False,
            "status_code": None,
            "final_url": None,
            "latency_ms": elapsed_ms,
            "error": str(exc),
        }


def tls_probe(
    hostname: str,
    port: int = 443,
    timeout: float = 5.0,
) -> dict[str, Any]:
    """Validate a server's TLS certificate and report expiry."""
    started = time.perf_counter()
    context = ssl.create_default_context()

    try:
        with socket.create_connection(
            (hostname, port),
            timeout=timeout,
        ) as raw_socket, context.wrap_socket(
            raw_socket,
            server_hostname=hostname,
        ) as tls_socket:
            certificate = tls_socket.getpeercert()
            tls_version = tls_socket.version()

        expiry_text = certificate.get("notAfter")
        expires_at = None
        days_until_expiry = None

        if expiry_text:
            expiry = datetime.strptime(
                expiry_text,
                "%b %d %H:%M:%S %Y %Z",
            ).replace(tzinfo=UTC)

            expires_at = expiry.isoformat()
            days_until_expiry = (
                expiry - datetime.now(UTC)
            ).days

        elapsed_ms = round(
            (time.perf_counter() - started) * 1000,
            2,
        )

        return {
            "probe": "tls",
            "hostname": hostname,
            "port": port,
            "success": True,
            "tls_version": tls_version,
            "certificate_expires_at": expires_at,
            "days_until_expiry": days_until_expiry,
            "latency_ms": elapsed_ms,
            "error": None,
        }

    except (OSError, ssl.SSLError, ValueError) as exc:
        elapsed_ms = round(
            (time.perf_counter() - started) * 1000,
            2,
        )

        return {
            "probe": "tls",
            "hostname": hostname,
            "port": port,
            "success": False,
            "tls_version": None,
            "certificate_expires_at": None,
            "days_until_expiry": None,
            "latency_ms": elapsed_ms,
            "error": str(exc),
        }
