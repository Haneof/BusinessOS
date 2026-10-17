"""Raven v0.2.x A2A JSON-RPC adapter. Not enabled by default.

Wire format grounded in Raven's docs-site/docs/agent-protocols.md and
raven/a2a/routes_aiohttp.py at pinned Git SHA in docs/RAVEN_EVEROS.md.
Remote completion is NEVER a BusinessOS independent quality pass.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Callable
from uuid import uuid4

from .transport import IntegrationDisabled, IntegrationError, JsonTransport, LoopbackJsonTransport, require_loopback_base_url


@dataclass(frozen=True)
class RavenOutcome:
    task_id: str | None
    state: str
    text: str
    quality_verified: bool = False


class RavenA2AAdapter:
    """Operator gated A2A client. Never authorizes tools inside the Raven process."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8710",
        *,
        transport: JsonTransport | None = None,
        enabled: bool = False,
        bearer_token: str | None = None,
        approve_task: Callable[[str, str], bool] | None = None,
    ) -> None:
        self.base_url = require_loopback_base_url(base_url)
        self.transport = transport if transport is not None else LoopbackJsonTransport()
        self.enabled = enabled
        self._token = bearer_token
        self._approve_task = approve_task

    @staticmethod
    def make_request(task: str, message_id: str | None = None) -> dict[str, Any]:
        if not task.strip() or len(task) > 20000:
            raise ValueError("Task must contain 1 to 20000 characters")
        message_id = message_id or uuid4().hex
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "method": "SendMessage",
            "params": {"message": {"messageId": message_id, "role": "ROLE_USER", "parts": [{"text": task}]}},
        }

    def submit(self, task: str, *, approval_id: str) -> RavenOutcome:
        """Send only when an out-of-band operator authority approved this exact task ID.

        A callback returning True in unit tests is NOT an adequate real approval
        broker. Production must validate task digest, scope, cost and expiry.
        """
        if not self.enabled:
            raise IntegrationDisabled("Raven submission is disabled by default")
        if (not approval_id or self._approve_task is None
                or not self._approve_task(approval_id, sha256(task.encode("utf-8")).hexdigest())):
            raise PermissionError("Approved delegation receipt required")
        if not self._token:
            raise IntegrationDisabled("Raven A2A bearer token is not configured")
        payload = self.make_request(task)
        response = self.transport.post_json(
            self.base_url + "/a2a",
            payload,
            headers={"A2A-Version": "1.0", "Authorization": "Bearer " + self._token},
            timeout_s=120,
        )
        return self.parse_response(response, payload["id"])

    @staticmethod
    def parse_response(response: dict[str, Any], request_id: str) -> RavenOutcome:
        if response.get("jsonrpc") != "2.0" or response.get("id") != request_id:
            raise IntegrationError("Mismatched Raven JSON-RPC response")
        if response.get("error") is not None:
            raise IntegrationError("Raven returned an A2A error")
        result = response.get("result")
        if not isinstance(result, dict):
            raise IntegrationError("Raven result is missing")
        task = result.get("task", result)
        if not isinstance(task, dict):
            raise IntegrationError("Raven task is malformed")
        status = task.get("status", {})
        if not isinstance(status, dict):
            status = {}
        raw_state = str(status.get("state", "unknown"))
        state = raw_state.removeprefix("TASK_STATE_").lower().replace("_", "-")
        if state not in {"completed", "failed", "canceled", "working", "submitted", "input-required", "rejected", "unknown"}:
            state = "unknown"
        msg = status.get("message", {})
        if not isinstance(msg, dict):
            msg = {}
        parts = msg.get("parts", [])
        text = "\n".join(str(x["text"]) for x in parts if isinstance(x, dict) and isinstance(x.get("text"), str))[:20000]
        task_id = task.get("id")
        # Raven's completed state is only a status claim, not quality evidence.
        return RavenOutcome(task_id=str(task_id) if task_id else None, state=state, text=text, quality_verified=False)
