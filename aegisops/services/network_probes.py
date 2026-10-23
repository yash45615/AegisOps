
import socket
import time
from typing import Any


def tcp_probe(
    host: str,
    port: int,
    timeout: float = 2.0,
) -> dict[str, Any]:
    """Check whether a TCP connection can be established."""
    started = time.perf_counter()

    try:
        with socket.create_connection(
            (host, port),
            timeout=timeout,
        ):
            elapsed_ms = round(
                (time.perf_counter() - started) * 1000,
                2,
            )

        return {
            "probe": "tcp",
            "host": host,
            "port": port,
            "success": True,
            "latency_ms": elapsed_ms,
            "error": None,
        }

    except (OSError, TimeoutError) as exc:
        elapsed_ms = round(
            (time.perf_counter() - started) * 1000,
            2,
        )

        return {
            "probe": "tcp",
            "host": host,
            "port": port,
            "success": False,
            "latency_ms": elapsed_ms,
            "error": str(exc),
        }


def dns_probe(hostname: str) -> dict[str, Any]:
    """Resolve a hostname and return its unique IP addresses."""
    started = time.perf_counter()

    try:
        results = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )

        addresses = sorted(
            {
                result[4][0]
                for result in results
            }
        )

        elapsed_ms = round(
            (time.perf_counter() - started) * 1000,
            2,
        )

        return {
            "probe": "dns",
            "hostname": hostname,
            "success": bool(addresses),
            "addresses": addresses,
            "latency_ms": elapsed_ms,
            "error": None if addresses else "No addresses found",
        }

    except (OSError, UnicodeError) as exc:
        elapsed_ms = round(
            (time.perf_counter() - started) * 1000,
            2,
        )

        return {
            "probe": "dns",
            "hostname": hostname,
            "success": False,
            "addresses": [],
            "latency_ms": elapsed_ms,
            "error": str(exc),
        }
