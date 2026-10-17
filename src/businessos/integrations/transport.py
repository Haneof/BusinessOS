"""Small HTTP/JSON seam: loopback only, no redirects, bounded responses.

This is a defense-in-depth component, not an OS sandbox. Processes that may
run tools must have independently enforced filesystem and network permissions.
"""

from __future__ import annotations

import json
import socket
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


MAX_REQUEST_BYTES = 64 * 1024
MAX_RESPONSE_BYTES = 256 * 1024


class IntegrationError(RuntimeError):
    """A predictable, secret-free error visible to the coordinating agent."""


class IntegrationDisabled(IntegrationError):
    """The operator has not enabled this integration."""


class JsonTransport(Protocol):
    def post_json(
        self, url: str, payload: dict[str, Any], *, headers: dict[str, str], timeout_s: float
    ) -> dict[str, Any]: ...


def require_loopback_base_url(url: str) -> str:
    """Only direct loopback service URLs may be used in the Phase-A prototype."""
    parsed = urlsplit(url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "::1"}:
        raise ValueError("Integration endpoint must use loopback HTTP")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Credentials, query strings, and fragments are not allowed")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid integration port") from exc
    if port is None or not (0 < port < 65536):
        raise ValueError("Integration endpoint requires an explicit port")
    if parsed.path not in {"", "/"}:
        raise ValueError("Integration base URL must not contain a path")
    return url.rstrip("/")


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


class LoopbackJsonTransport:
    """Standard-library transport; never loads host proxy settings or follows redirects."""

    def post_json(
        self, url: str, payload: dict[str, Any], *, headers: dict[str, str], timeout_s: float
    ) -> dict[str, Any]:
        parsed = urlsplit(url)
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "::1"}:
            raise IntegrationError("Refusing non-loopback HTTP request")
        if parsed.username or parsed.password or parsed.fragment or parsed.query:
            raise IntegrationError("Invalid destination URL")
        if not 0 < timeout_s <= 300:
            raise ValueError("Invalid request timeout")
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        if len(encoded) > MAX_REQUEST_BYTES:
            raise IntegrationError("Request exceeds size limit")
        request = Request(url, data=encoded, method="POST", headers={"Content-Type": "application/json", **headers})
        opener = build_opener(ProxyHandler({}), _NoRedirect())
        try:
            with opener.open(request, timeout=timeout_s) as response:
                content = response.read(MAX_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            raise IntegrationError(f"HTTP request refused (status={exc.code})") from None
        except (URLError, TimeoutError, socket.timeout, OSError):
            raise IntegrationError("Local integration is unavailable") from None
        if len(content) > MAX_RESPONSE_BYTES:
            raise IntegrationError("Integration response exceeds size limit")
        try:
            result = json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise IntegrationError("Integration returned invalid JSON") from None
        if not isinstance(result, dict):
            raise IntegrationError("Integration response must be a JSON object")
        return result
