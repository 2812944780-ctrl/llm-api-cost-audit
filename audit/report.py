"""Analyse a usage log and surface the three most common hidden cost sources.

Findings are *indicators*, not verdicts. Each one tells you what to look at
next; none of them claims to know your provider's internal accounting.
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

DEFAULT_RETRY_WINDOW_SECONDS = 10
CONTEXT_BLOAT_RATIO = 0.9
CACHE_VARIANCE_RATIO = 0.05
MIN_SAMPLES_FOR_VARIANCE = 5


@dataclass
class Finding:
    kind: str
    severity: str  # HIGH / MEDIUM / LOW
    detail: str
    evidence: list = field(default_factory=list)


def load(path: str | Path) -> list:
    """Read a JSONL usage log, skipping malformed lines, sorted by timestamp."""
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    rows.sort(key=lambda r: str(r.get("ts") or ""))
    return rows


def _stamp(row: dict) -> Optional[datetime]:
    raw = row.get("ts")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw))
    except ValueError:
        return None


def _int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def totals_by_tag(rows: list) -> dict:
    """Aggregate token totals per tag."""
    agg = defaultdict(lambda: {"calls": 0, "prompt": 0, "completion": 0, "total": 0})
    for row in rows:
        bucket = agg[row.get("tag") or "(untagged)"]
        bucket["calls"] += 1
        bucket["prompt"] += _int(row.get("prompt_tokens"))
        bucket["completion"] += _int(row.get("completion_tokens"))
        bucket["total"] += _int(row.get("total_tokens"))
    return dict(agg)


def detect_retries(rows: list, window_seconds: int = DEFAULT_RETRY_WINDOW_SECONDS) -> list:
    """Same task_id called more than once inside ``window_seconds``.

    A timeout can happen *after* the server generated (and billed) tokens.
    A blind retry then pays for the same work twice.
    """
    grouped = defaultdict(list)
    for row in rows:
        task = row.get("task_id")
        stamp = _stamp(row)
        if task and stamp is not None:
            grouped[task].append((stamp, row))

    evidence = []
    for task, items in grouped.items():
        items.sort(key=lambda item: item[0])
        attempts = len(items)
        if attempts < 2:
            continue
        for (prev_stamp, prev_row), (cur_stamp, cur_row) in zip(items, items[1:]):
            gap = (cur_stamp - prev_stamp).total_seconds()
            if 0 <= gap <= window_seconds:
                billed = _int(prev_row.get("total_tokens")) + _int(cur_row.get("total_tokens"))
                evidence.append(
                    f"task_id={task} attempts={attempts} gap={gap:.1f}s tokens={billed}"
                )
                break

    if not evidence:
        return []
    return [
        Finding(
            kind="retry-double-billing",
            severity="HIGH",
            detail=(
                f"{len(evidence)} task(s) were called more than once inside "
                f"{window_seconds}s. If a retry followed a timeout, the server may have "
                f"already billed the first attempt."
            ),
            evidence=evidence[:10],
        )
    ]


def detect_cache_variance(
    rows: list,
    ratio: float = CACHE_VARIANCE_RATIO,
    min_samples: int = MIN_SAMPLES_FOR_VARIANCE,
) -> list:
    """Identical tags whose prompt_tokens swing noticeably.

    A stable prompt bill means a stable prefix. Swings hint at cache hit/miss
    or a changing prefix — both mean you cannot price from a fixed unit cost.
    """
    grouped = defaultdict(list)
    for row in rows:
        if row.get("tag"):
            grouped[row["tag"]].append(row)

    evidence = []
    for tag, items in grouped.items():
        values = [_int(r.get("prompt_tokens")) for r in items]
        values = [v for v in values if v > 0]
        if len(values) < min_samples:
            continue
        mean = statistics.fmean(values)
        if mean <= 0:
            continue
        spread = statistics.pstdev(values) / mean
        if spread >= ratio:
            evidence.append(
                f"tag={tag} samples={len(values)} mean={mean:.0f} "
                f"stdev={statistics.pstdev(values):.0f} spread={spread * 100:.1f}%"
            )

    if not evidence:
        return []
    return [
        Finding(
            kind="prompt-token-variance",
            severity="MEDIUM",
            detail=(
                "Prompt tokens for the same tag vary noticeably. Cached prefixes are "
                "often billed at a lower rate, so identical requests can cost different "
                "amounts. Do not price from a fixed unit cost — track the observed ratio."
            ),
            evidence=evidence[:10],
        )
    ]


def detect_context_bloat(rows: list, ratio: float = CONTEXT_BLOAT_RATIO) -> list:
    """Calls where prompt tokens dominate the bill."""
    evidence = []
    for row in rows:
        total = _int(row.get("total_tokens"))
        prompt = _int(row.get("prompt_tokens"))
        if total > 0 and prompt / total >= ratio:
            evidence.append(
                f"ts={row.get('ts')} tag={row.get('tag')} "
                f"prompt={prompt} total={total}"
            )

    if not evidence:
        return []
    return [
        Finding(
            kind="context-bloat",
            severity="LOW",
            detail=(
                f"{len(evidence)} call(s) spent >= {ratio:.0%} of their tokens on input. "
                "Context dominates this workload — trim history, system prompt or payload "
                "before shopping for a cheaper endpoint."
            ),
            evidence=evidence[:10],
        )
    ]


def analyse(rows: list, retry_window_seconds: int = DEFAULT_RETRY_WINDOW_SECONDS) -> list:
    """Run every detector and return all findings."""
    findings = []
    findings += detect_retries(rows, retry_window_seconds)
    findings += detect_cache_variance(rows)
    findings += detect_context_bloat(rows)
    return findings


def has_high_finding(findings: list) -> bool:
    return any(f.severity == "HIGH" for f in findings)


def render(rows: list, findings: list, retry_window_seconds: int = DEFAULT_RETRY_WINDOW_SECONDS) -> str:
    """Human-readable report."""
    out = []
    out.append("=== LLM API Cost Audit " + "=" * 40)
    out.append("")

    if not rows:
        out.append("No rows found. Did you point this at the right log file?")
        return "\n".join(out)

    window_start = rows[0].get("ts")
    window_end = rows[-1].get("ts")
    out.append(f"Rows analysed: {len(rows)}   Window: {window_start} -> {window_end}")
    out.append("")

    out.append("-- Token totals by tag " + "-" * 40)
    out.append(f"{'tag':<20}{'calls':>8}{'prompt':>12}{'completion':>12}{'total':>12}")
    for tag, bucket in sorted(totals_by_tag(rows).items(), key=lambda kv: -kv[1]["total"]):
        out.append(
            f"{tag:<20}{bucket['calls']:>8}{bucket['prompt']:>12,}"
            f"{bucket['completion']:>12,}{bucket['total']:>12,}"
        )
    out.append("")

    if not findings:
        out.append("No findings. Either the workload is clean, or there is not enough")
        out.append("data yet. Keep logging — findings need repeat calls to appear.")
        return "\n".join(out)

    for index, finding in enumerate(findings, start=1):
        out.append(f"-- Finding {index}: {finding.kind}  [{finding.severity}] " + "-" * 10)
        for line in _wrap(finding.detail, 68):
            out.append(line)
        for item in finding.evidence:
            out.append(f"  {item}")
        out.append(f"  -> {_advice(finding.kind)}")
        out.append("")

    out.append("=" * 62)
    out.append("Findings are indicators, not verdicts. Verify against your own logs.")
    return "\n".join(out)


def _advice(kind: str) -> str:
    return {
        "retry-double-billing": (
            "Make retries idempotent: stamp each task with an id and check it before "
            "re-issuing the request."
        ),
        "prompt-token-variance": (
            "Log every call and compare ratios over time instead of pricing from a "
            "fixed unit cost."
        ),
        "context-bloat": (
            "Trim system prompt, history or payload — the input is the bill."
        ),
    }.get(kind, "Review the calls listed above.")


def _wrap(text: str, width: int) -> list:
    words, lines, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines
