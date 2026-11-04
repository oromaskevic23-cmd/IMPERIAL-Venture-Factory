"""Second-path automated QA; does not constitute human Independent QA or Owner approval."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _review_markdown(workflow, source_hash, counters, recommendations):
    lines = [
        "# Automation Failure Audit — evidence preview", "",
        "Classification: ADVISORY LAB REPORT. Independent QA, customer approval,",
        "delivery and payment are NOT confirmed by this tool.", "",
        f"Workflow: {workflow}", f"Input SHA-256: {source_hash}", "",
        "## Measurements", "",
    ]
    lines += [f"- {key}: {value}" for key, value in counters.items()]
    lines += ["", "## Suggested checks", ""]
    lines += [f"- {item}" for item in recommendations]
    lines += ["", "No live connectivity or production remediation was performed.", ""]
    return "\n".join(lines).encode("utf-8")


def crosscheck(input_path: Path, report_path: Path, receipt_path: Path) -> dict:
    markdown_path = report_path.with_name("report.md")
    if any(p.is_symlink() for p in (input_path, report_path, markdown_path, receipt_path)):
        raise ValueError("SYMLINK_DENIED")
    if receipt_path.exists():
        raise ValueError("RECEIPT_OVERWRITE_DENIED")
    for path in (input_path, report_path, markdown_path):
        if not path.is_file() or path.stat().st_size > 256 * 1024:
            raise ValueError("EVIDENCE_FILE_REJECTED")
    source = input_path.read_bytes()
    report_bytes = report_path.read_bytes()
    markdown_bytes = markdown_path.read_bytes()
    if len(source) > 256 * 1024 or len(report_bytes) > 256 * 1024 or len(markdown_bytes) > 256 * 1024:
        raise ValueError("EVIDENCE_TOO_LARGE")
    source_data = json.loads(source, object_pairs_hook=_unique_object)
    report = json.loads(report_bytes, object_pairs_hook=_unique_object)
    ident = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,63}\Z")
    if (type(source_data) is not dict or set(source_data) != {"workflow", "events"}
            or type(source_data["workflow"]) is not str or not ident.fullmatch(source_data["workflow"])
            or type(source_data["events"]) is not list or not 1 <= len(source_data["events"]) <= 2000):
        raise ValueError("INVALID_SOURCE")
    events = source_data["events"]
    for event in events:
        if (type(event) is not dict or set(event) != {"id", "status", "duration_ms"}
                or type(event["id"]) is not str or not ident.fullmatch(event["id"])
                or not (event["status"] == "timeout" or
                        (type(event["status"]) is int and 100 <= event["status"] <= 599))
                or type(event["duration_ms"]) is not int or not 0 <= event["duration_ms"] <= 600000):
            raise ValueError("INVALID_SOURCE")
    counters = {
        "total_events": len(events),
        "distinct_event_ids": len({e["id"] for e in events}),
        "duplicate_event_ids": len(events) - len({e["id"] for e in events}),
        "http_429": sum(1 for e in events if e["status"] == 429),
        "http_5xx": sum(1 for e in events if type(e["status"]) is int and 500 <= e["status"] <= 599),
        "timeouts": sum(1 for e in events if e["status"] == "timeout"),
        "slow_over_30s": sum(1 for e in events if e["duration_ms"] >= 30000),
    }
    expected = {
        "schema_version": "2026-10-27.1",
        "input_sha256": hashlib.sha256(source).hexdigest(),
        "workflow": source_data["workflow"],
        "offer_id": "IC-OFFER-001",
        "owner_system": "IMPERIAL_CORE",
        "classification": "ADVISORY_LAB_REPORT_NOT_CUSTOMER_ACCEPTED",
        "independent_qa": "NOT_YET_VERIFIED",
        "customer_acceptance": "NOT_RECEIVED",
        "payment_confirmed": False,
        "collected_revenue_usd": 0,
        "findings": counters,
    }
    recommendations = []
    if counters["duplicate_event_ids"]:
        recommendations.append("Verify idempotency keys and duplicate-event suppression.")
    if counters["http_429"]:
        recommendations.append("Test bounded backoff and Retry-After handling for HTTP 429.")
    if counters["http_5xx"] or counters["timeouts"]:
        recommendations.append("Review retries, circuit breaker, timeout and dead-letter handling.")
    if counters["slow_over_30s"]:
        recommendations.append("Measure latency budget and add SLA alerting.")
    if not recommendations:
        recommendations.append("Run controlled fault-injection and downstream delivery checks.")
    if (type(report) is not dict or set(report) != set(expected) | {"recommendations"}
            or report.get("payment_confirmed") is not False
            or type(report.get("collected_revenue_usd")) is not int
            or type(report.get("findings")) is not dict
            or any(type(v) is not int for v in report["findings"].values())
            or report.get("recommendations") != recommendations
            or any(report.get(key) != value for key, value in expected.items())):
        raise ValueError("EVIDENCE_MISMATCH")
    if markdown_bytes != _review_markdown(source_data["workflow"], expected["input_sha256"], counters, recommendations):
        raise ValueError("MARKDOWN_MISMATCH")
    receipt = {
        "result": "AUTOMATED_CROSSCHECK_PASS_NOT_HUMAN_QA",
        "offer_id": "IC-OFFER-001",
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "report_sha256": hashlib.sha256(report_bytes).hexdigest(),
        "markdown_sha256": hashlib.sha256(markdown_bytes).hexdigest(),
        "client_delivery": "NOT_AUTHORIZED",
        "payment_confirmed": False,
    }
    with receipt_path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("report", type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(crosscheck(args.input, args.report, args.receipt)))
