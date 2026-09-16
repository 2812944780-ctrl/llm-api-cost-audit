"""Command line interface: ``python -m audit report usage.jsonl``."""

from __future__ import annotations

import argparse
import json
import sys

from .report import analyse, has_high_finding, load, render


def _cmd_report(args: argparse.Namespace) -> int:
    rows = load(args.log)
    findings = analyse(rows, args.window)

    if args.json:
        payload = {
            "rows": len(rows),
            "findings": [
                {
                    "kind": finding.kind,
                    "severity": finding.severity,
                    "detail": finding.detail,
                    "evidence": finding.evidence,
                }
                for finding in findings
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render(rows, findings, args.window))

    # Non-zero exit on HIGH findings so this can gate a CI job.
    return 1 if has_high_finding(findings) else 0


def _cmd_tail(args: argparse.Namespace) -> int:
    rows = load(args.log)[-args.number:]
    for row in rows:
        print(json.dumps(row, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="audit",
        description="Audit token usage and billing from a JSONL usage log.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    report = sub.add_parser("report", help="Full audit report")
    report.add_argument("log", help="Path to the JSONL usage log")
    report.add_argument("--json", action="store_true", help="Machine-readable output")
    report.add_argument(
        "--window",
        type=int,
        default=10,
        help="Retry detection window in seconds (default: 10)",
    )
    report.set_defaults(func=_cmd_report)

    tail = sub.add_parser("tail", help="Show the last N raw rows")
    tail.add_argument("log", help="Path to the JSONL usage log")
    tail.add_argument("-n", "--number", type=int, default=20, help="Row count (default: 20)")
    tail.set_defaults(func=_cmd_tail)

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
