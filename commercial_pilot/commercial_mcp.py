"""Local, source-pinned MCP access to the first commercial audit pilot.

This operator tool performs bounded computations only. It does not authorize
agents, customer delivery, production execution, outreach or payments.
"""
from __future__ import annotations

import hashlib
import hmac
import importlib.abc
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

from commercial_pilot import audit, source_sync, verify

PROTOCOL = "2025-11-25"
HERE = Path(__file__).resolve().parent
MAX_FRAME = 300_000
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}\Z")
SERVER_INFO = {"name": "imperial-commercial-audit", "version": "0.1.0"}


def _unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("DUPLICATE_JSON_KEY")
        out[key] = value
    return out


def _reject_constant(_value):
    raise ValueError("NON_FINITE_JSON")


def _json(data):
    return json.loads(data, object_pairs_hook=_unique_object, parse_constant=_reject_constant)


def _read_pinned(root: Path, entry: dict) -> None:
    """Verify reviewed local source bytes before importing either dependency.

    The lock is not a signature and depends on a trusted local checkout.
    """
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise ValueError("DEPENDENCY_ROOT_DENIED")
    package = entry["package"]
    if package not in {"src/imperial_skill", "src/imperial_plugins"}:
        raise ValueError("DEPENDENCY_PACKAGE_DENIED")
    expected = entry["files"]
    if type(expected) is not dict:
        raise ValueError("DEPENDENCY_LOCK_DENIED")
    package_dir = root / package
    for directory in (root / "src", package_dir):
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError("DEPENDENCY_DIRECTORY_DENIED")
    expected_python = {path for path in expected if path.startswith(package + "/")}
    actual_python = {str(path.relative_to(root)) for path in package_dir.glob("*.py")}
    if actual_python != expected_python:
        raise ValueError("DEPENDENCY_SOURCE_SET_MISMATCH")
    for relative, digest in expected.items():
        allowed = (relative.startswith(package + "/") and relative.endswith(".py")) or (
            package == "src/imperial_plugins" and relative == "manifests/n8n-workflow-audit.json")
        if not allowed or ".." in Path(relative).parts or not re.fullmatch(r"[a-f0-9]{64}", digest):
            raise ValueError("DEPENDENCY_LOCK_DENIED")
        path = root / relative
        current = root
        for part in Path(relative).parts:
            current = current / part
            if current.is_symlink():
                raise ValueError("DEPENDENCY_SYMLINK_DENIED")
        if not path.is_file() or path.stat().st_size > 1_048_576:
            raise ValueError("DEPENDENCY_FILE_DENIED")
        if not hmac.compare_digest(hashlib.sha256(path.read_bytes()).hexdigest(), digest):
            raise ValueError("DEPENDENCY_HASH_MISMATCH")


class _PinnedSourceLoader(importlib.abc.Loader):
    """Compile the verified source itself; never execute a cached .pyc file."""
    def __init__(self, path, expected):
        self.path, self.expected = path, expected

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        if self.path.is_symlink() or not self.path.is_file() or self.path.stat().st_size > 1_048_576:
            raise ImportError("PINNED_MODULE_DENIED")
        source = self.path.read_bytes()
        if not hmac.compare_digest(hashlib.sha256(source).hexdigest(), self.expected):
            raise ImportError("PINNED_MODULE_CHANGED")
        exec(compile(source, str(self.path), "exec", dont_inherit=True), module.__dict__)


class _PinnedSourceFinder(importlib.abc.MetaPathFinder):
    def __init__(self, deps, paths):
        self.entries = {}
        self.packages = {"imperial_skill", "imperial_plugins"}
        for name in ("skill", "plugins"):
            entry, root = deps[name], paths[name]
            package = Path(entry["package"]).name
            prefix = entry["package"] + "/"
            for rel, digest in entry["files"].items():
                if not rel.startswith(prefix) or not rel.endswith(".py"):
                    continue
                stem = Path(rel).stem
                fullname = package if stem == "__init__" else package + "." + stem
                self.entries[fullname] = (root / rel, digest, stem == "__init__")

    def find_spec(self, fullname, path=None, target=None):
        entry = self.entries.get(fullname)
        if entry is None:
            if any(fullname == p or fullname.startswith(p + ".") for p in self.packages):
                raise ImportError("UNPINNED_MODULE_DENIED")
            return None
        source, digest, is_package = entry
        loader = _PinnedSourceLoader(source, digest)
        return importlib.util.spec_from_file_location(fullname, source, loader=loader,
            submodule_search_locations=[str(source.parent)] if is_package else None)


def load_contracts() -> tuple[dict, object]:
    """Bind the Skill contract and real plugin code to reviewed local sources."""
    lock = _json((HERE / "local_sources.lock.json").read_bytes())
    if type(lock) is not dict or lock.get("schema") != "imperial.commercial.local-source-lock.v1":
        raise ValueError("DEPENDENCY_LOCK_DENIED")
    deps = lock.get("dependencies")
    if type(deps) is not dict or set(deps) != {"skill", "plugins"}:
        raise ValueError("DEPENDENCY_LOCK_DENIED")
    paths = {}
    for name, variable in (("skill", "IMPERIAL_SKILL_ROOT"), ("plugins", "IMPERIAL_PLUGINS_ROOT")):
        raw = os.environ.get(variable)
        if not raw:
            raise ValueError("DEPENDENCY_ROOT_REQUIRED")
        paths[name] = Path(raw)
        _read_pinned(paths[name], deps[name])
    if any(k == package or k.startswith(package + ".") for k in sys.modules
           for package in ("imperial_skill", "imperial_plugins")):
        raise ValueError("PRELOADED_DEPENDENCY_DENIED")
    sys.meta_path.insert(0, _PinnedSourceFinder(deps, paths))
    from imperial_skill.bridge import to_plugins_manifest
    from imperial_skill.exams import validate_exam
    from imperial_skill.manifest import read_json_strict
    from imperial_skill.registry import SkillRegistry
    from imperial_plugins.adapters import inspect_n8n_workflow
    from imperial_plugins.core import validate_manifest

    skill = read_json_strict((HERE / "automation_audit_skill.json").read_bytes())
    exam = read_json_strict((HERE / "automation_audit_exam.json").read_bytes())
    if (skill.get("skill_id") != "imperial.skill.automation-audit"
            or skill.get("version") != "0.1.0" or skill.get("capabilities") != ["simulate:task"]
            or validate_exam(exam)["exam_sha256"] != skill.get("exam_sha256")
            or exam["skill_id"] != skill.get("skill_id") or exam["version"] != skill.get("version")):
        raise ValueError("SKILL_EXAM_BINDING_DENIED")
    registry = SkillRegistry()
    digest = registry.register(skill)
    plan = registry.resolve(tenant_id="IMPERIAL-GLOBAL", orchestrator_id="ASTRA",
                            runtime_domain="AUTOMATION_LAB", skill_id=skill["skill_id"],
                            version=skill["version"])
    if plan["execution_authorized"] is not False or plan["production_authorized"] is not False:
        raise ValueError("SKILL_PLAN_DENIED")
    converted = validate_manifest(to_plugins_manifest(skill))
    plugin_file = paths["plugins"] / "manifests/n8n-workflow-audit.json"
    plugin_bytes = plugin_file.read_bytes()
    if not hmac.compare_digest(hashlib.sha256(plugin_bytes).hexdigest(),
                               deps["plugins"]["files"]["manifests/n8n-workflow-audit.json"]):
        raise ValueError("PLUGIN_MANIFEST_CHANGED")
    n8n_plugin = validate_manifest(_json(plugin_bytes))
    if n8n_plugin["id"] != "imperial.n8n-workflow-audit":
        raise ValueError("PLUGIN_ID_DENIED")
    return ({"skill_id": skill["skill_id"], "skill_sha256": digest,
             "skill_plan_sha256": plan["plan_sha256"],
             "skill_plugin_id": converted["id"], "workflow_plugin_id": n8n_plugin["id"],
             "skill_source_commit": deps["skill"]["commit"],
             "plugin_source_commit": deps["plugins"]["commit"],
             "execution_authorized": False, "independent_human_qa": False,
             "production_authorized": False}, inspect_n8n_workflow)


NO_ARGS = {"type": "object", "properties": {}, "additionalProperties": False}
TRACE_ID = {"type": "string", "minLength": 1, "maxLength": 64,
            "pattern": "^[A-Za-z0-9][A-Za-z0-9._:-]*$"}
TRACE_SCHEMA = {"type": "object", "additionalProperties": False,
    "required": ["workflow", "events"], "properties": {"workflow": TRACE_ID,
        "events": {"type": "array", "minItems": 1, "maxItems": 2000,
            "items": {"type": "object", "additionalProperties": False,
                "required": ["id", "status", "duration_ms"], "properties": {
                    "id": TRACE_ID, "status": {"oneOf": [
                        {"type": "integer", "minimum": 100, "maximum": 599},
                        {"type": "string", "const": "timeout"}]},
                    "duration_ms": {"type": "integer", "minimum": 0, "maximum": 600000}}}}}}
NODE_ID = {"type": "string", "minLength": 1, "maxLength": 100,
           "pattern": "^[A-Za-z0-9][A-Za-z0-9_.:-]*$"}
WORKFLOW_SCHEMA = {"type": "object", "additionalProperties": False,
    "required": ["active", "nodes"], "properties": {"active": {"type": "boolean"},
        "nodes": {"type": "array", "minItems": 1, "maxItems": 100,
            "items": {"type": "object", "additionalProperties": False,
                "required": ["name", "type"], "properties": {"name": NODE_ID, "type": NODE_ID}}}}}
TOOLS = [
    {"name": "imperial_commercial_offer", "title": "Commercial audit scope",
     "description": "Show the first audit scope and verified local integration boundaries.",
     "inputSchema": NO_ARGS, "annotations": {"readOnlyHint": True, "openWorldHint": False}},
    {"name": "imperial_commercial_audit_trace", "title": "Audit a bounded event trace",
     "description": "Locally analyze synthetic or authorized redacted trace data; no delivery or payment.",
     "inputSchema": {"type": "object", "properties": {"trace": TRACE_SCHEMA},
                     "required": ["trace"], "additionalProperties": False},
     "annotations": {"readOnlyHint": True, "openWorldHint": False}},
    {"name": "imperial_commercial_inspect_workflow", "title": "Inspect workflow structure",
     "description": "Call the existing n8n plugin on sanitized node names and types only; advisory flags.",
     "inputSchema": {"type": "object", "properties": {"workflow": WORKFLOW_SCHEMA},
                     "required": ["workflow"], "additionalProperties": False},
     "annotations": {"readOnlyHint": True, "openWorldHint": False}},
    {"name": "imperial_commercial_discover_inquiries", "title": "Screen public enquiries",
     "description": "Read public GitHub issues from the fixed offer repository; return sanitized candidates only.",
     "inputSchema": NO_ARGS, "annotations": {"readOnlyHint": True, "openWorldHint": True}},
]


class CommercialServer:
    def __init__(self, contracts, inspect_workflow):
        self.contracts = contracts
        self.inspect_workflow = inspect_workflow
        self.initialized = False
        self.ready = False

    @staticmethod
    def _error(ident, code, message):
        return {"jsonrpc": "2.0", "id": ident, "error": {"code": code, "message": message}}

    @staticmethod
    def _result(ident, value):
        return {"jsonrpc": "2.0", "id": ident, "result": value}

    @staticmethod
    def _tool_result(value, error=False):
        return {"content": [{"type": "text", "text": json.dumps(value, sort_keys=True)}],
                "isError": error}

    def _offer(self):
        return {"offer_id": "IC-OFFER-001", "service": "Automation Failure Audit",
                "scope": "One bounded synthetic or authorized redacted event trace",
                "public_enquiry_form": "https://github.com/oromaskevic23-cmd/IMPERIAL-Venture-Factory/issues/new?template=commercial_audit.yml",
                "commercial_terms": "NOT_AGREED",
                "workflow_inspection": "Optional advisory, not production execution",
                "contracts": self.contracts, "customer_acceptance": "NOT_CHECKED",
                "payment_status": "NOT_CHECKED", "outreach_sent_by_this_tool": False,
                "customer_delivery_authorized": False}

    def _discover(self):
        found = source_sync.discover(source_sync.fetch_open_issues(max_issues=300))
        return {"mode": "READ_ONLY_PUBLIC_GITHUB_DISCOVERY", "offer_id": "IC-OFFER-001",
                "eligible_count": found["eligible_count"],
                "rejected_or_ignored_count": found["rejected_or_ignored_count"],
                "candidates": [{"source_ref": item["source_ref"],
                                "source_receipt_hash": item["source_receipt_hash"],
                                "state": "CANDIDATE_NOT_RECORDED_IN_CRM"}
                               for item in found["drafts"]],
                "original_source_recheck": "REQUIRED", "dispatch_allowed": False,
                "payment_status": "NOT_CHECKED"}

    def _audit_trace(self, trace):
        packet = audit.validate_packet(trace)
        source = audit.canonical(packet)
        if len(source) > audit.MAX_INPUT_BYTES:
            raise ValueError("TRACE_TOO_LARGE")
        report = audit.analyze(packet, hashlib.sha256(source).hexdigest())
        report_bytes = json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        markdown = audit.render_markdown(report).encode("utf-8")
        receipt = verify.crosscheck_values(source, report_bytes, markdown)
        return {"source_hash_basis": "canonical JSON bytes, not original file bytes",
                "report": report, "report_markdown": markdown.decode("utf-8"),
                "automated_qa": receipt, "human_qa": "NOT_VERIFIED",
                "delivery": "NOT_AUTHORIZED", "payment_status": "NOT_CHECKED"}

    def _inspect(self, workflow):
        if type(workflow) is not dict or set(workflow) != {"active", "nodes"}:
            raise ValueError("WORKFLOW_SCHEMA_DENIED")
        if type(workflow["active"]) is not bool or type(workflow["nodes"]) is not list:
            raise ValueError("WORKFLOW_SCHEMA_DENIED")
        if not 1 <= len(workflow["nodes"]) <= 100:
            raise ValueError("NODE_COUNT_DENIED")
        for node in workflow["nodes"]:
            if (type(node) is not dict or set(node) != {"name", "type"}
                    or any(type(node[k]) is not str or not IDENTIFIER.fullmatch(node[k])
                           for k in ("name", "type"))):
                raise ValueError("NODE_SCHEMA_DENIED")
        result = self.inspect_workflow(workflow)
        return {"plugin": "imperial.n8n-workflow-audit", "result": result,
                "limitations": "Node types and activation only; parameters, credentials and connections not inspected.",
                "human_qa": "NOT_VERIFIED", "production_execution": "NOT_AUTHORIZED"}

    def dispatch(self, message):
        if type(message) is not dict or message.get("jsonrpc") != "2.0" or type(message.get("method")) is not str:
            return self._error(None, -32600, "Invalid request")
        method = message["method"]
        if "id" not in message:
            if method == "notifications/initialized" and self.initialized:
                self.ready = True
            return None
        ident = message["id"]
        if type(ident) not in (int, str) and ident is not None:
            return self._error(None, -32600, "Invalid request id")
        params = message.get("params", {})
        if type(params) is not dict:
            return self._error(ident, -32602, "Invalid params")
        if method == "initialize":
            if (self.initialized or type(params.get("protocolVersion")) is not str
                    or type(params.get("capabilities")) is not dict
                    or type(params.get("clientInfo")) is not dict):
                return self._error(ident, -32602, "Invalid initialization")
            self.initialized = True
            return self._result(ident, {"protocolVersion": PROTOCOL,
                "capabilities": {"tools": {"listChanged": False}}, "serverInfo": SERVER_INFO,
                "instructions": "Local advisory tool only. No client delivery or payment authorization."})
        if method == "ping":
            return self._result(ident, {})
        if not self.ready:
            return self._error(ident, -32600, "MCP session is not initialized")
        if method == "tools/list":
            if params.get("cursor") is not None:
                return self._error(ident, -32602, "Invalid cursor")
            return self._result(ident, {"tools": TOOLS})
        if method != "tools/call":
            return self._error(ident, -32601, "Method not found")
        name, arguments = params.get("name"), params.get("arguments", {})
        if type(name) is not str or type(arguments) is not dict:
            return self._error(ident, -32602, "Invalid tool request")
        try:
            if name == "imperial_commercial_offer" and not arguments:
                result = self._offer()
            elif name == "imperial_commercial_audit_trace" and set(arguments) == {"trace"}:
                result = self._audit_trace(arguments["trace"])
            elif name == "imperial_commercial_inspect_workflow" and set(arguments) == {"workflow"}:
                result = self._inspect(arguments["workflow"])
            elif name == "imperial_commercial_discover_inquiries" and not arguments:
                result = self._discover()
            else:
                return self._error(ident, -32602, "Unknown tool or invalid arguments")
            return self._result(ident, self._tool_result(result))
        except (ValueError, TypeError, KeyError, RecursionError, OverflowError):
            return self._result(ident, self._tool_result({"error": "INPUT_REJECTED"}, error=True))
        except Exception:
            return self._result(ident, self._tool_result({"error": "INTERNAL_ERROR"}, error=True))


def main() -> int:
    try:
        contracts, inspector = load_contracts()
    except (OSError, ValueError, TypeError, KeyError, ImportError, RecursionError):
        print("Commercial MCP unavailable: check the two source-pinned dependency roots.", file=sys.stderr)
        return 2
    server = CommercialServer(contracts, inspector)
    while True:
        line = sys.stdin.buffer.readline(MAX_FRAME + 1)
        if not line:
            break
        if len(line) > MAX_FRAME or not line.endswith(b"\n"):
            response = server._error(None, -32600, "Frame too large or incomplete")
            print(json.dumps(response, separators=(",", ":")), flush=True)
            return 1
        try:
            response = server.dispatch(_json(line))
        except (ValueError, UnicodeError, RecursionError):
            response = server._error(None, -32700, "Parse error")
        if response is not None:
            print(json.dumps(response, ensure_ascii=True, separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
