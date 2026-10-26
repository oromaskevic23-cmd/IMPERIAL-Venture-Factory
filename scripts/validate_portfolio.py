#!/usr/bin/env python3
"""Validate Venture Factory public manifest/spec structure without network or deps."""
from __future__ import annotations
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
STAGES = {"IDEA", "DISCOVERY", "VALIDATED", "BUILD", "QA",
          "PILOT", "RELEASED", "EXIT_READY", "SOLD"}


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads((root / "portfolio/ventures.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"Cannot parse portfolio manifest: {exc}"]
    ventures = data.get("ventures")
    if not isinstance(ventures, list):
        return ["ventures must be an array"]
    if len(ventures) != 10:
        errors.append(f"Expected 10 ventures, found {len(ventures)}")
    seen_ids, seen_slugs = set(), set()
    for index, venture in enumerate(ventures, 1):
        if not isinstance(venture, dict):
            errors.append(f"Venture #{index} not object")
            continue
        prefix = venture.get("id", "UNSET")
        expected_id = f"VF-{index:02d}"
        if prefix != expected_id or prefix in seen_ids:
            errors.append(f"ID mismatch/duplicate: {prefix}, expected {expected_id}")
        seen_ids.add(prefix)
        slug = venture.get("slug")
        if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9-]+", slug):
            errors.append(f"{prefix}: invalid slug")
            continue
        if slug in seen_slugs:
            errors.append(f"{prefix}: duplicate slug")
        seen_slugs.add(slug)
        if venture.get("stage") not in STAGES:
            errors.append(f"{prefix}: unknown stage")
        tech = venture.get("technical", {})
        commercial = venture.get("commercial", {})
        governance = venture.get("governance", {})
        if not isinstance(tech, dict) or not isinstance(commercial, dict) or not isinstance(governance, dict):
            errors.append(f"{prefix}: malformed sections")
            continue
        expected_path = f"products/{slug}/SPEC.md"
        if tech.get("spec") != expected_path:
            errors.append(f"{prefix}: spec path mismatch")
            continue
        path = root / expected_path
        if not path.is_file():
            errors.append(f"{prefix}: missing {expected_path}")
        else:
            source = path.read_text(encoding="utf-8")
            if not source.startswith(f"# {prefix} —"):
                errors.append(f"{prefix}: spec ID not found")
            if "NOT BUILT" not in source:
                errors.append(f"{prefix}: spec must distinguish proposed from implemented")
        if venture.get("stage") == "IDEA" and (
            tech.get("release") != "NOT_RELEASED"
            or commercial.get("sold") is not False
            or commercial.get("revenue") != "UNVERIFIED"
        ):
            errors.append(f"{prefix}: IDEA must not claim releases, revenue or sales")
        if governance.get("operating_budget") != "FREE_ONLY":
            errors.append(f"{prefix}: budget drift requires approved policy change")
        if governance.get("asset_boundary") != "INDEPENDENT_PRODUCT_NO_IMPERIAL_CORE_ASSIGNMENT":
            errors.append(f"{prefix}: core IP boundary missing")
    for required in (
        "README.md", "SECURITY.md", "docs/ARCHITECTURE.md",
        "docs/VENTURE_AUTOPILOT.md", "docs/SECURITY_AND_ASSURANCE.md",
        "docs/EXIT_DILIGENCE.md",
    ):
        if not (root / required).is_file():
            errors.append(f"Missing governance file: {required}")
    return errors


if __name__ == "__main__":
    issues = validate()
    if issues:
        for item in issues:
            print(f"FAIL: {item}", file=sys.stderr)
        sys.exit(1)
    print("PASS: 10 venture manifests, product specs and governance checks")
