"""Cross-repository checks against pinned IMPERIAL Skill and Plugins sources."""
import hashlib
import importlib._bootstrap_external
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = Path(os.environ["IMPERIAL_SKILL_ROOT"])
PLUGINS = Path(os.environ["IMPERIAL_PLUGINS_ROOT"])
INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2025-11-25", "capabilities": {},
    "clientInfo": {"name": "imperial-independent-test", "version": "1"}}}
READY = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def call(ident, name, arguments):
    return {"jsonrpc": "2.0", "id": ident, "method": "tools/call",
            "params": {"name": name, "arguments": arguments}}


def run_protocol(messages, env=None):
    data = "".join(json.dumps(message) + "\n" for message in messages)
    process = subprocess.run([sys.executable, "-m", "commercial_pilot.commercial_mcp"],
                             input=data, text=True, capture_output=True, cwd=ROOT,
                             env=env or os.environ.copy(), timeout=15)
    return process, [json.loads(line) for line in process.stdout.splitlines()]


def tool_data(message):
    return json.loads(message["result"]["content"][0]["text"])


class CommercialIntegrationTests(unittest.TestCase):
    def test_full_stdio_flow_uses_skill_real_plugin_and_audit(self):
        trace = json.loads((ROOT / "commercial_pilot/examples/synthetic_trace.json").read_text())
        workflow = {"active": False, "nodes": [
            {"name": "Trigger", "type": "n8n-nodes-base.manualTrigger"},
            {"name": "API", "type": "n8n-nodes-base.httpRequest"},
        ]}
        messages = [INIT, READY, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                    call(3, "imperial_commercial_offer", {}),
                    call(4, "imperial_commercial_inspect_workflow", {"workflow": workflow}),
                    call(5, "imperial_commercial_audit_trace", {"trace": trace})]
        proc, output = run_protocol(messages)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(output), 5)  # the initialized notification has no response
        self.assertEqual(output[0]["result"]["protocolVersion"], "2025-11-25")
        self.assertEqual(len(output[1]["result"]["tools"]), 4)
        offer = tool_data(output[2])
        self.assertEqual(offer["contracts"]["skill_id"], "imperial.skill.automation-audit")
        self.assertFalse(offer["contracts"]["execution_authorized"])
        self.assertEqual(offer["payment_status"], "NOT_CHECKED")
        plugin = tool_data(output[3])
        self.assertEqual(plugin["plugin"], "imperial.n8n-workflow-audit")
        self.assertIn("outbound_http_requires_approval", plugin["result"]["static_flags"])
        self.assertFalse(plugin["result"]["approved_for_unattended_execution"])
        result = tool_data(output[4])
        expected = {"total_events": 5, "distinct_event_ids": 4, "duplicate_event_ids": 1,
                    "http_429": 1, "http_5xx": 1, "timeouts": 1, "slow_over_30s": 1}
        self.assertEqual(result["report"]["findings"], expected)
        self.assertEqual(result["automated_qa"]["result"], "AUTOMATED_CROSSCHECK_PASS_NOT_HUMAN_QA")
        self.assertEqual(result["automated_qa"]["markdown_sha256"],
                         hashlib.sha256(result["report_markdown"].encode()).hexdigest())
        self.assertEqual(result["human_qa"], "NOT_VERIFIED")
        self.assertEqual(result["delivery"], "NOT_AUTHORIZED")

    def test_real_skill_exam_matches_two_synthetic_cases(self):
        sys.path.insert(0, str(SKILL / "src"))
        from imperial_skill.exams import grade_offline_exam
        from imperial_skill.manifest import canonical_json
        exam = json.loads((ROOT / "commercial_pilot/automation_audit_exam.json").read_text())
        traces = [json.loads((ROOT / ("commercial_pilot/examples/" + name)).read_text())
                  for name in ("synthetic_trace.json", "clean_trace.json")]
        proc, out = run_protocol([INIT, READY] + [
            call(i + 2, "imperial_commercial_audit_trace", {"trace": trace})
            for i, trace in enumerate(traces)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        answers = {case: canonical_json(tool_data(result)["report"]["findings"])
                   for case, result in zip(("faults-detected", "clean-trace"), out[1:])}
        grade = grade_offline_exam(exam, answers)
        self.assertTrue(grade["reference_match_pass"])
        self.assertFalse(grade["professional_certified"])
        self.assertFalse(grade["execution_authorized"])

    def test_protocol_and_data_boundaries(self):
        workflow = {"active": False, "nodes": [{"name": "Node", "type": "n8n-nodes-base.code",
                                               "credentials": {"secret": "must-not-be-logged"}}]}
        bad_trace = {"workflow": "DEMO", "events": [{"id": "a", "status": 200,
                      "duration_ms": 1, "token": "must-not-be-logged"}]}
        notification = call(99, "imperial_commercial_audit_trace", {"trace": bad_trace})
        del notification["id"]
        proc, out = run_protocol([
            {"jsonrpc": "2.0", "id": 8, "method": "tools/list"}, INIT, READY, notification,
            call(2, "imperial_commercial_audit_trace", {"trace": bad_trace}),
            call(3, "imperial_commercial_inspect_workflow", {"workflow": workflow}),
            call(4, "imperial_commercial_offer", {"token": "must-not-be-logged"}),
            call(5, "imperial_send_money", {}),
        ])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(out), 6)
        self.assertEqual(out[0]["error"]["code"], -32600)
        self.assertTrue(out[2]["result"]["isError"])
        self.assertTrue(out[3]["result"]["isError"])
        self.assertEqual(out[4]["error"]["code"], -32602)
        self.assertEqual(out[5]["error"]["code"], -32602)
        self.assertNotIn("must-not-be-logged", proc.stdout + proc.stderr)

    def test_missing_or_tampered_dependency_fails_before_import(self):
        env = os.environ.copy()
        env.pop("IMPERIAL_SKILL_ROOT", None)
        proc, out = run_protocol([INIT], env)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(out, [])
        with tempfile.TemporaryDirectory() as temp:
            changed = Path(temp) / "plugins"
            shutil.copytree(PLUGINS / "src", changed / "src", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copytree(PLUGINS / "manifests", changed / "manifests")
            marker = Path(temp) / "executed"
            init = changed / "src/imperial_plugins/__init__.py"
            init.write_text(init.read_text() + f"\nopen({str(marker)!r}, 'w').write('bad')\n")
            env = os.environ.copy()
            env["IMPERIAL_PLUGINS_ROOT"] = str(changed)
            proc, out = run_protocol([INIT], env)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(out, [])
            self.assertFalse(marker.exists())

    def test_oversize_frame_stops_the_process(self):
        proc = subprocess.run([sys.executable, "-m", "commercial_pilot.commercial_mcp"],
            input='{"data":"' + ('x' * 300_001) + '"}\n', text=True,
            capture_output=True, cwd=ROOT, env=os.environ.copy(), timeout=15)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(json.loads(proc.stdout)["error"]["code"], -32600)

    def test_duplicate_json_keys_are_rejected_without_echoing_input(self):
        raw = '{"jsonrpc":"2.0","id":1,"id":2,"method":"must-not-be-logged"}\n'
        proc = subprocess.run([sys.executable, "-m", "commercial_pilot.commercial_mcp"],
            input=raw, text=True, capture_output=True, cwd=ROOT, env=os.environ.copy(), timeout=15)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["error"]["code"], -32700)
        self.assertNotIn("must-not-be-logged", proc.stdout + proc.stderr)

    def test_untrusted_bytecode_is_never_executed(self):
        with tempfile.TemporaryDirectory() as temp:
            copied = Path(temp) / "plugins"
            shutil.copytree(PLUGINS / "src", copied / "src", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copytree(PLUGINS / "manifests", copied / "manifests")
            source = copied / "src/imperial_plugins/__init__.py"
            marker = Path(temp) / "bytecode-executed"
            code = compile(f"open({str(marker)!r}, 'w').write('bad')", str(source), "exec")
            cache = Path(importlib.util.cache_from_source(str(source)))
            cache.parent.mkdir()
            stat = source.stat()
            cache.write_bytes(importlib._bootstrap_external._code_to_timestamp_pyc(
                code, int(stat.st_mtime), stat.st_size))
            env = os.environ.copy()
            env["IMPERIAL_PLUGINS_ROOT"] = str(copied)
            proc, out = run_protocol([INIT, READY, call(2, "imperial_commercial_offer", {})], env)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertFalse(marker.exists())
            self.assertEqual(tool_data(out[1])["offer_id"], "IC-OFFER-001")

    def test_discovery_returns_only_sanitized_unrecorded_candidates(self):
        from commercial_pilot.commercial_mcp import CommercialServer
        from commercial_pilot.source_sync import GITHUB_API, REPO, CONSENT
        issue = {"number": 91, "url": GITHUB_API + "/issues/91",
                 "html_url": "https://github.com/" + REPO + "/issues/91",
                 "user": {"login": "example-user", "type": "User"}, "labels": [], "state": "open",
                 "title": "[Audit request] Intermittent webhook errors",
                 "body": "\n".join(["### What should be assessed?", "One webhook or API integration",
                     "### Public, non-confidential description of the problem", "Duplicates and HTTP 429.",
                     "### Expected first deliverable", "Diagnostic report and reproducible synthetic test",
                     "### Public issue privacy and scope confirmation", *CONSENT])}
        server = CommercialServer({}, lambda _: {})
        server.initialized = server.ready = True
        with patch("commercial_pilot.source_sync.fetch_open_issues", return_value=[issue]) as fetch:
            result = tool_data(server.dispatch(call(7, "imperial_commercial_discover_inquiries", {})))
        fetch.assert_called_once_with(max_issues=300)
        self.assertEqual(result["eligible_count"], 1)
        self.assertEqual(result["candidates"][0]["state"], "CANDIDATE_NOT_RECORDED_IN_CRM")
        self.assertFalse(result["dispatch_allowed"])
        self.assertNotIn("example-user", json.dumps(result))
        self.assertNotIn("Duplicates", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
