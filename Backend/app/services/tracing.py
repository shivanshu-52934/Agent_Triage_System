import json
import os
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


TRACE_FILE = Path(os.getenv("TRACE_FILE", "agent_traces.jsonl"))


def estimate_tokens(value: Any) -> int:
    text = json.dumps(value, default=str) if not isinstance(value, str) else value
    return max(1, len(text.split()))


def _write_span(span: Dict[str, Any]) -> None:
    TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with TRACE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(span, default=str) + "\n")


@contextmanager
def trace_span(agent: str, input_data: Any = None, retry_count: int = 0):
    start = time.time()
    span = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "input_tokens": estimate_tokens(input_data or ""),
        "retry_count": retry_count,
        "success": False,
    }

    try:
        yield span
        span["success"] = True
    except Exception as exc:
        span["error"] = str(exc)
        raise
    finally:
        span["latency_ms"] = round((time.time() - start) * 1000, 2)
        _write_span(span)


def read_traces(limit: int = 100) -> List[Dict[str, Any]]:
    if not TRACE_FILE.exists():
        return []

    with TRACE_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]

    traces = []
    for line in lines:
        try:
            traces.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return traces


def clear_traces() -> None:
    if TRACE_FILE.exists():
        TRACE_FILE.unlink()
