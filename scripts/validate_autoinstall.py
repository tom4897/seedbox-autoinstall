#!/usr/bin/env python3
"""
Validator for Ubuntu autoinstall NoCloud-Net seed directories.

Checks each host directory under cloud-init/v1/hosts/ for:
- Required files: meta-data, user-data
- meta-data minimal keys: instance-id, local-hostname (and instance-id starts with local-hostname)
- user-data: parses YAML, extracts top-level 'autoinstall' and validates it against 
    the official JSON schema.

Schema source: Canonical Subiquity Autoinstall schema (see docs link in repo).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Any, Dict, List, Tuple

import json
import difflib
import yaml
from jsonschema import Draft7Validator


def read_text(path: str) -> str:
    """Read text from a file."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def parse_kv_file(text: str) -> Dict[str, str]:
    """Very small parser for simple key: value files (like sample meta-data)."""
    result: Dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        result[key.strip()] = val.strip()
    return result


def validate_meta(meta_path: str) -> List[str]:
    """Validate meta-data file."""
    errors: List[str] = []
    text = read_text(meta_path)
    if not text:
        return ["meta-data missing or empty"]
    data = parse_kv_file(text)
    instance_id = data.get("instance-id", "").strip()
    local_hostname = data.get("local-hostname", "").strip()
    if not instance_id:
        errors.append("meta-data: missing instance-id")
    if not local_hostname:
        errors.append("meta-data: missing local-hostname")
    if instance_id and local_hostname and not instance_id.startswith(local_hostname):
        errors.append("meta-data: instance-id should start with local-hostname (hint from sample)")
    return errors


_RE_CLOUD_CONFIG = re.compile(r"^\s*#cloud-config\b", re.IGNORECASE | re.MULTILINE)


def load_schema(schema_path: str) -> Dict[str, Any]:
    """Load JSON schema from a file."""
    text = read_text(schema_path)
    if not text:
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON schema at {schema_path}: {exc}"
        ) from exc


def validate_user_data(user_path: str, schema: Dict[str, Any]) -> List[str]:
    """Validate user-data file."""
    errors: List[str] = []
    text = read_text(user_path)
    if not text:
        return ["user-data missing or empty"]

    if not _RE_CLOUD_CONFIG.search(text):
        errors.append("user-data: first line should start with #cloud-config")

    # Parse YAML cloud-config
    try:
        doc = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        return [f"user-data: invalid YAML ({exc})"]

    if not isinstance(doc, dict):
        return ["user-data: expected a YAML mapping at top-level"]

    autoinstall = doc.get("autoinstall")
    if autoinstall is None:
        errors.append("user-data: missing top-level 'autoinstall' key")
        return errors
    if not isinstance(autoinstall, dict):
        errors.append("user-data: 'autoinstall' must be a mapping/object")
        return errors

    # Enforce presence of critical section (identity) which schema treats as optional
    if "identity" not in autoinstall:
        close = difflib.get_close_matches("identity", list(autoinstall.keys()), n=1, cutoff=0.8)
        if close:
            errors.append(
                f"user-data.autoinstall: missing 'identity' (did you mean '{close[0]}'?)"
            )
        else:
            errors.append("user-data.autoinstall: missing 'identity'")

    # Validate against JSON schema (collect all errors for better output)
    validator = Draft7Validator(schema)
    msgs: List[str] = []
    for err in sorted(validator.iter_errors(autoinstall), key=lambda e: e.path):
        loc = "/".join([str(p) for p in err.path]) or "(root)"
        msgs.append(f"user-data.autoinstall: {loc}: {err.message}")
    errors.extend(msgs)

    return errors


def validate_host(host_dir: str, schema: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Validate a host directory against the schema."""
    host_name = os.path.basename(host_dir.rstrip(os.sep))
    errors: List[str] = []
    meta_path = os.path.join(host_dir, "meta-data")
    user_path = os.path.join(host_dir, "user-data")

    errors.extend(validate_meta(meta_path))
    errors.extend(validate_user_data(user_path, schema))
    return host_name, errors


def find_host_dirs(base_dir: str) -> List[str]:
    """Find all host directories under the base directory."""
    if not os.path.isdir(base_dir):
        return []
    entries = sorted(
        [
            os.path.join(base_dir, name)
            for name in os.listdir(base_dir)
            if not name.startswith(".") and not name.endswith(".tmp")
        ]
    )
    return [p for p in entries if os.path.isdir(p)]


def main() -> int:
    """Main function to validate Ubuntu autoinstall NoCloud-Net seeds."""
    parser = argparse.ArgumentParser(description="Validate Ubuntu autoinstall NoCloud-Net seeds")
    parser.add_argument(
        "--hosts-dir",
        default=os.path.join("cloud-init", "v1", "hosts"),
        help="Path to hosts directory (default: cloud-init/v1/hosts)",
    )
    parser.add_argument(
        "--schema",
        default=os.path.join("scripts", "ubuntu_autoinstall_schema.json"),
        help="Path to autoinstall JSON schema (default: scripts/ubuntu_autoinstall_schema.json)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop at the first failure and return non-zero",
    )
    args = parser.parse_args()

    try:
        schema = load_schema(args.schema)
    except Exception as exc: # pylint: disable=broad-exception-caught
        print(f"Failed to load schema: {exc}")
        return 2

    host_dirs = find_host_dirs(args.hosts_dir)
    if not host_dirs:
        print(f"No host directories found under: {args.hosts_dir}")
        return 2

    any_errors = False
    for host_dir in host_dirs:
        host_name, errors = validate_host(host_dir, schema)
        if errors:
            any_errors = True
            print(f"[FAIL] {host_name}")
            for err in errors:
                print(f"  - {err}")
            if args.fail_fast:
                break
        else:
            print(f"[OK]   {host_name}")

    return 1 if any_errors else 0


if __name__ == "__main__":
    sys.exit(main())
