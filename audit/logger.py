"""Record real token usage from any OpenAI-compatible endpoint into JSONL.

The point of this module is simple: stop estimating, start recording.
Every field written here comes from the response object itself.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def _attr(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default)


class UsageLogger:
    """Append one JSON row per API call.

    Parameters
    ----------
    path:
        Destination JSONL file. Created on first write.
    tag:
        Default label for calls that do not pass their own ``tag``.
        Use it to group calls that should be comparable (e.g. "summarise").
    """

    def __init__(self, path: str | Path = "usage.jsonl", tag: str = "") -> None:
        self.path = Path(path)
        self.tag = tag

    def log(
        self,
        response: Any,
        *,
        tag: Optional[str] = None,
        task_id: Optional[str] = None,
        model: Optional[str] = None,
        extra: Optional[dict] = None,
    ) -> Optional[dict]:
        """Write one row for ``response``. Returns the row, or None if no usage."""
        usage = _attr(response, "usage")
        if usage is None:
            return None

        row = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "tag": self.tag if tag is None else tag,
            "task_id": task_id,
            "model": model or _attr(response, "model"),
            "request_id": _attr(response, "id"),
            "prompt_tokens": _attr(usage, "prompt_tokens"),
            "completion_tokens": _attr(usage, "completion_tokens"),
            "total_tokens": _attr(usage, "total_tokens"),
            "finish_reason": self._finish_reason(response),
        }
        if extra:
            row.update(extra)

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        return row

    @staticmethod
    def _finish_reason(response: Any) -> Optional[str]:
        choices = _attr(response, "choices") or []
        if not choices:
            return None
        return _attr(choices[0], "finish_reason")
