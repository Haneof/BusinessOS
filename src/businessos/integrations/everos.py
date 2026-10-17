"""EverOS /api/v2 memory adapter. No credentials, actions or finance authority stored here."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

from .transport import IntegrationDisabled, IntegrationError, JsonTransport, LoopbackJsonTransport, require_loopback_base_url

_SCOPE = re.compile(r"[A-Za-z0-9_.-]{1,128}\Z")


def _scope(value: str) -> str:
    if not isinstance(value, str) or not _SCOPE.fullmatch(value) or value in {".", ".."}:
        raise ValueError("Invalid EverOS scope/owner identifier")
    return value


@dataclass(frozen=True)
class MemoryHit:
    kind: str
    id: str
    project_id: str
    text: str
    source_timestamp: str | None
    independently_verified: bool = False


class EverOSMemoryAdapter:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        *,
        transport: JsonTransport | None = None,
        enabled: bool = False,
        authorize_write: Callable[[str], bool] | None = None,
    ) -> None:
        self.base_url = require_loopback_base_url(base_url)
        self.transport = transport if transport is not None else LoopbackJsonTransport()
        self.enabled = enabled
        self._authorize_write = authorize_write

    def _post(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            raise IntegrationDisabled("EverOS is disabled by default")
        result = self.transport.post_json(self.base_url + path, data, headers={}, timeout_s=30)
        wrapped = result.get("data")
        if not isinstance(wrapped, dict):
            raise IntegrationError("EverOS response is missing the v2 data envelope")
        return wrapped

    def search(
        self,
        query: str,
        *,
        project_id: str,
        agent_id: str | None = None,
        user_id: str | None = None,
        top_k: int = 5,
        method: str = "keyword",
    ) -> tuple[MemoryHit, ...]:
        if bool(agent_id) == bool(user_id):
            raise ValueError("Exactly one of agent_id/user_id is required")
        if not query or len(query) > 4096 or not 1 <= top_k <= 20:
            raise ValueError("Invalid search query or result limit")
        if method not in {"keyword", "hybrid", "vector"}:
            raise ValueError("Unsupported EverOS search method")
        project_id = _scope(project_id)
        owner_key = "agent_id" if agent_id else "user_id"
        owner = _scope(agent_id or user_id or "")
        data = self._post("/api/v2/memory/search", {
            owner_key: owner, "app_id": "businessos", "project_id": project_id,
            "query": query, "method": method, "top_k": top_k,
        })
        names = ("agent_cases", "agent_skills") if agent_id else ("episodes", "profiles")
        hits: list[MemoryHit] = []
        for name in names:
            rows = data.get(name, [])
            if not isinstance(rows, list):
                raise IntegrationError("EverOS returned malformed memory entries")
            for row in rows:
                if not isinstance(row, dict):
                    continue
                # Fail closed on a response claiming records from another scope.
                if row.get("app_id") != "businessos" or row.get("project_id") != project_id:
                    raise IntegrationError("Cross-project EverOS result refused")
                if row.get(owner_key) != owner:
                    raise IntegrationError("Cross-owner EverOS result refused")
                content = row.get("episode") or row.get("content") or row.get("approach") or row.get("summary") or row.get("description") or ""
                text = str(content)[:4000]
                hits.append(MemoryHit(kind=name, id=str(row.get("id", "")), project_id=project_id,
                                      text=text, source_timestamp=row.get("timestamp"), independently_verified=False))
        return tuple(hits[:top_k])

    def record_sanitized_summary(
        self,
        *,
        session_id: str,
        project_id: str,
        user_id: str,
        summary: str,
        timestamp_ms: int,
        approval_id: str,
    ) -> str:
        """Stage only redacted summaries. The calling verifier retains original evidence.

        This writes an EverOS USER-track episode, not an agent skill/case.
        True agent-case extraction requires an independently sanitized tool
        trajectory and separate integration, not a single summary message.
        """
        if not approval_id or self._authorize_write is None or not self._authorize_write(approval_id):
            raise PermissionError("Independent memory-write authorization required")
        if not summary or len(summary) > 4000 or not isinstance(timestamp_ms, int) or timestamp_ms < 1_000_000_000_000:
            raise ValueError("Invalid sanitized summary or timestamp")
        sid = _scope(session_id)
        data = self._post("/api/v2/memory/add", {
            "app_id": "businessos", "project_id": _scope(project_id), "session_id": sid,
            "defer_extraction": True,
            "messages": [{"sender_id": _scope(user_id), "role": "user", "timestamp": timestamp_ms, "content": summary}],
        })
        if data.get("status") != "accumulated" or data.get("message_count") != 1:
            raise IntegrationError("EverOS did not acknowledge staging the summary")
        return "accumulated_not_yet_extracted"

    def flush(self, *, session_id: str, project_id: str, approval_id: str) -> str:
        if not approval_id or self._authorize_write is None or not self._authorize_write(approval_id):
            raise PermissionError("Independent memory-write authorization required")
        result = self._post("/api/v2/memory/flush", {
            "app_id": "businessos", "project_id": _scope(project_id), "session_id": _scope(session_id),
        })
        status = result.get("status")
        if status not in {"extracted", "no_extraction"}:
            raise IntegrationError("EverOS flush returned an invalid status")
        # Indexing is asynchronous even if markdown has persisted.
        return str(status)
