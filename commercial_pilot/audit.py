"""IMPERIAL Core: bounded, offline automation failure audit for consented, synthetic traces.

No browsing, customer credentials, payments, outbound messaging, or code execution.
A report is advisory evidence; it is never an approved customer delivery.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

MAX_INPUT_BYTES = 256 * 1024
MAX_EVENTS = 2000
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
VERSION = "2026-10-27.1"
EVENT_KEYS = {"id", "status", "duration_ms"}
PACKET_KEYS = {"workflow", "events"}


class IntakeRejected(ValueError):
    pass


def canonical(data: object) -> bytes:
    return json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("utf-8")


def load_packet(path: Path) -> tuple[dict, str]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_INPUT_BYTES:
        raise IntakeRejected("INPUT_FILE_REJECTED")
    raw = path.read_bytes()
    if len(raw) > MAX_INPUT_BYTES:
        raise IntakeRejected("INPUT_TOO_LARGE")
    try:
        payload = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise IntakeRejected("INVALID_JSON") from exc
    if not isinstance(payload, dict) or set(payload) != PACKET_KEYS:
        raise IntakeRejected("UNEXPECTED_PACKET_FIELDS")
    if not isinstance(payload["workflow"], str) or not ID.fullmatch(payload["workflow"]):
        raise IntakeRejected("INVALID_WORKFLOW_ID")
    events = payload["events"]
    if not isinstance(events, list) or not (1 <= len(events) <= MAX_EVENTS):
        raise IntakeRejected("INVALID_EVENT_COUNT")
    for event in events:
        if not isinstance(event, dict) or set(event) != EVENT_KEYS:
            raise IntakeRejected("UNEXPECTED_EVENT_FIELDS")
        if not isinstance(event["id"], str) or not ID.fullmatch(event["id"]):
            raise IntakeRejected("INVALID_EVENT_ID")
        status = event["status"]
        if status != "timeout" and (
            not isinstance(status, int) or isinstance(status, bool) or not 100 <= status <= 599
        ):
            raise IntakeRejected("INVALID_EVENT_STATUS")
        duration = event["duration_ms"]
        if not isinstance(duration, int) or isinstance(duration, bool) or not 0 <= duration <= 600000:
            raise IntakeRejected("INVALID_DURATION")
    return payload, hashlib.sha256(raw).hexdigest()


def analyze(payload: dict, input_sha256: str) -> dict:
    events = payload["events"]
    seen: set[str] = set()
    duplicates = 0
    rate_limited = 0
    server_errors = 0
    timeouts = 0
    slow = 0
    for event in events:
        if event["id"] in seen:
            duplicates += 1
        seen.add(event["id"])
        status = event["status"]
        rate_limited += status == 429
        server_errors += isinstance(status, int) and 500 <= status <= 599
        timeouts += status == "timeout"
        slow += event["duration_ms"] >= 30000
    findings = {
        "total_events": len(events),
        "distinct_event_ids": len(seen),
        "duplicate_event_ids": duplicates,
        "http_429": rate_limited,
        "http_5xx": server_errors,
        "timeouts": timeouts,
        "slow_over_30s": slow,
    }
    recommendations = []
    if duplicates:
        recommendations.append("Verify idempotency keys and duplicate-event suppression.")
    if rate_limited:
        recommendations.append("Test bounded backoff and Retry-After handling for HTTP 429.")
    if server_errors or timeouts:
        recommendations.append("Review retries, circuit breaker, timeout and dead-letter handling.")
    if slow:
        recommendations.append("Measure latency budget and add SLA alerting.")
    if not recommendations:
        recommendations.append("Run controlled fault-injection and downstream delivery checks.")
    return {
        "schema_version": VERSION,
        "classification": "ADVISORY_LAB_REPORT_NOT_CUSTOMER_ACCEPTED",
        "owner_system": "IMPERIAL_CORE",
        "offer_id": "IC-OFFER-001",
        "workflow": payload["workflow"],
        "input_sha256": input_sha256,
        "findings": findings,
        "recommendations": recommendations,
        "independent_qa": "NOT_YET_VERIFIED",
        "customer_acceptance": "NOT_RECEIVED",
        "payment_confirmed": False,
        "collected_revenue_usd": 0,
    }


def render_markdown(report: dict) -> str:
    counts = report["findings"]
    lines = [
        "# Automation Failure Audit — evidence preview",
        "",
        "Classification: ADVISORY LAB REPORT. Independent QA, customer approval,",
        "delivery and payment are NOT confirmed by this tool.",
        "",
        f"Workflow: {report['workflow']}",
        f"Input SHA-256: {report['input_sha256']}",
        "",
        "## Measurements",
        "",
    ]
    lines += [f"- {key}: {value}" for key, value in counts.items()]
    lines += ["", "## Suggested checks", ""]
    lines += [f"- {item}" for item in report["recommendations"]]
    lines += ["", "No live connectivity or production remediation was performed.", ""]
    return "\n".join(lines)


def run(input_path: Path, output_dir: Path) -> dict:
    packet, digest = load_packet(input_path)
    report = analyze(packet, digest)
    if output_dir.is_symlink():
        raise IntakeRejected("OUTPUT_SYMLINK_DENIED")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "report.json"
    md_path = output_dir / "report.md"
    if report_path.exists() or md_path.exists():
        raise IntakeRejected("OUTPUT_EXISTS_NO_OVERWRITE")
    report_path.write_bytes(json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline, source-hashed automation trace audit")
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = run(args.input, args.out)
    print(json.dumps({"result": "LAB_REPORT_CREATED", "input_sha256": report["input_sha256"],
                      "qa": report["independent_qa"], "revenue_usd": 0}))


if __name__ == "__main__":
    main()
