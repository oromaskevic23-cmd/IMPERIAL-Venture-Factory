#!/usr/bin/env python3
"""Exercise the actual local MCP process using synthetic data, without side effects."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description="Run a synthetic MCP demo; optional public read-only discovery.")
parser.add_argument("--discover-public", action="store_true", help="Query the fixed public GitHub API")
options = parser.parse_args()
trace = json.loads((root / "commercial_pilot/examples/synthetic_trace.json").read_text())
workflow = {"active": False, "nodes": [
    {"name": "Trigger", "type": "n8n-nodes-base.manualTrigger"},
    {"name": "API", "type": "n8n-nodes-base.httpRequest"},
]}
messages = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-11-25", "capabilities": {},
        "clientInfo": {"name": "imperial-commercial-demo", "version": "1"}}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
        "name": "imperial_commercial_offer", "arguments": {}}},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
        "name": "imperial_commercial_inspect_workflow", "arguments": {"workflow": workflow}}},
    {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
        "name": "imperial_commercial_audit_trace", "arguments": {"trace": trace}}},
]
if options.discover_public:
    messages.append({"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {
        "name": "imperial_commercial_discover_inquiries", "arguments": {}}})
process = subprocess.run([sys.executable, "-m", "commercial_pilot.commercial_mcp"],
    input="".join(json.dumps(x) + "\n" for x in messages), text=True,
    capture_output=True, cwd=root, timeout=75 if options.discover_public else 15)
if process.returncode != 0:
    raise SystemExit("DEMO_FAILED: " + process.stderr.strip())
responses = [json.loads(line) for line in process.stdout.splitlines()]
if len(responses) != (5 if options.discover_public else 4) or any("error" in r for r in responses):
    raise SystemExit("DEMO_PROTOCOL_FAILED")
def unpack(response):
    result = response["result"]
    if result.get("isError"):
        raise ValueError("DEMO_TOOL_FAILED")
    return json.loads(result["content"][0]["text"])
offer, plugin, report = map(unpack, responses[1:4])
if (offer["offer_id"] != "IC-OFFER-001"
    or "outbound_http_requires_approval" not in plugin["result"]["static_flags"]
    or report["report"]["findings"]["total_events"] != 5
    or report["automated_qa"]["result"] != "AUTOMATED_CROSSCHECK_PASS_NOT_HUMAN_QA"):
    raise SystemExit("DEMO_EVIDENCE_FAILED")
result = {"status": "LOCAL_SYNTHETIC_DEMO_COMPLETED", "offer": offer,
    "plugin_review": plugin, "audit": report, "client_order": "NOT_ESTABLISHED",
    "payment_status": "NOT_CHECKED"}
if options.discover_public:
    discovery = unpack(responses[4])
    result["public_discovery"] = {key: discovery[key] for key in (
        "mode", "eligible_count", "rejected_or_ignored_count", "dispatch_allowed", "payment_status")}
print(json.dumps(result, indent=2, sort_keys=True))
