"""Second-path automated QA; does not constitute human Independent QA or Owner approval."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def crosscheck(input_path: Path, report_path: Path, receipt_path: Path) -> dict:
    if any(p.is_symlink() for p in (input_path, report_path, receipt_path)):
        raise ValueError("SYMLINK_DENIED")
    if receipt_path.exists():
        raise ValueError("RECEIPT_OVERWRITE_DENIED")
    source = input_path.read_bytes()
    report_bytes = report_path.read_bytes()
    source_data = json.loads(source)
    report = json.loads(report_bytes)
    events = source_data["events"]
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
    if any(report.get(key) != value for key, value in expected.items()):
        raise ValueError("EVIDENCE_MISMATCH")
    if not isinstance(report.get("recommendations"), list):
        raise ValueError("INVALID_REPORT")
    receipt = {
        "result": "AUTOMATED_CROSSCHECK_PASS_NOT_HUMAN_QA",
        "offer_id": "IC-OFFER-001",
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "report_sha256": hashlib.sha256(report_bytes).hexdigest(),
        "client_delivery": "NOT_AUTHORIZED",
        "payment_confirmed": False,
    }
    receipt_path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("report", type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(crosscheck(args.input, args.report, args.receipt)))
