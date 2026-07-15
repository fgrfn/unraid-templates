#!/usr/bin/env python3
'''Create a review-only report of differences between templates and upstream Compose files.'''

from __future__ import annotations

import argparse
import datetime as dt
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import requests
import yaml


def normalize_env(environment: Any) -> set[str]:
    if isinstance(environment, dict):
        return {str(key) for key in environment}
    result: set[str] = set()
    if isinstance(environment, list):
        for item in environment:
            result.add(str(item).split("=", 1)[0])
    return result


def normalize_ports(ports: Any) -> set[str]:
    result: set[str] = set()
    for item in ports or []:
        if isinstance(item, dict):
            target = item.get("target")
        else:
            value = str(item).split("/")[0]
            target = value.rsplit(":", 1)[-1]
        if target is not None:
            result.add(str(target))
    return result


def normalize_volumes(volumes: Any) -> set[str]:
    result: set[str] = set()
    for item in volumes or []:
        if isinstance(item, dict):
            target = item.get("target")
        else:
            parts = str(item).split(":")
            target = parts[1] if len(parts) > 1 else parts[0]
        if target:
            result.add(str(target))
    return result


def template_state(path: Path) -> dict[str, set[str] | str]:
    template_root = ET.parse(path).getroot()
    configs = template_root.findall("Config")
    return {
        "image": (template_root.findtext("Repository") or "").strip(),
        "environment": {c.get("Target", "") for c in configs if c.get("Mode") == "env"},
        "ports": {c.get("Target", "") for c in configs if c.get("Type") == "Port"},
        "volumes": {c.get("Target", "") for c in configs if c.get("Type") == "Path"},
    }


def choose_service(services: dict, requested: str) -> tuple[str, dict]:
    if requested:
        if requested not in services:
            raise KeyError(f"service {requested!r} not found; available: {', '.join(services)}")
        return requested, services[requested]
    if len(services) != 1:
        raise KeyError(f"compose has {len(services)} services; set upstream.service in catalog.yaml")
    name = next(iter(services))
    return name, services[name]


def compare(template: dict, service: dict) -> dict[str, Any]:
    upstream = {
        "image": str(service.get("image", "")),
        "environment": normalize_env(service.get("environment")),
        "ports": normalize_ports(service.get("ports")),
        "volumes": normalize_volumes(service.get("volumes")),
    }
    ignore_env = {"TZ", "PUID", "PGID"}
    return {
        "image": {"template": template["image"], "upstream": upstream["image"]} if upstream["image"] and template["image"] != upstream["image"] else None,
        "environment_added": sorted((upstream["environment"] - template["environment"]) - ignore_env),
        "environment_template_only": sorted((template["environment"] - upstream["environment"]) - ignore_env),
        "ports_added": sorted(upstream["ports"] - template["ports"]),
        "ports_template_only": sorted(template["ports"] - upstream["ports"]),
        "volumes_added": sorted(upstream["volumes"] - template["volumes"]),
        "volumes_template_only": sorted(template["volumes"] - upstream["volumes"]),
    }


def has_drift(diff: dict[str, Any]) -> bool:
    return any(value for value in diff.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("reports/upstream-drift.md"))
    args = parser.parse_args()
    catalog = yaml.safe_load((args.repo_root / "catalog.yaml").read_text(encoding="utf-8"))

    rows: list[tuple[str, str, dict | None, str | None]] = []
    review_required = False
    for entry in catalog["templates"]:
        upstream = entry.get("upstream") or {}
        if not upstream.get("enabled"):
            continue
        try:
            response = requests.get(upstream["compose_url"], timeout=20)
            response.raise_for_status()
            compose = yaml.safe_load(response.text)
            service_name, service = choose_service(compose.get("services") or {}, upstream.get("service", ""))
            diff = compare(template_state(args.repo_root / entry["path"]), service)
            review_required |= has_drift(diff)
            rows.append((entry["id"], service_name, diff, None))
        except Exception as exc:
            review_required = True
            rows.append((entry["id"], "", None, str(exc)))

    lines = [
        "# Upstream template drift report", "",
        f"Generated: {dt.datetime.now(dt.timezone.utc).isoformat()}", "",
        "This report is review-only. No template fields are changed automatically.", "",
    ]
    for entry_id, service_name, diff, error in rows:
        lines += [f"## {entry_id}", ""]
        if error:
            lines += [f"⚠️ Upstream check failed: `{error}`", ""]
            continue
        assert diff is not None
        if not has_drift(diff):
            lines += [f"No differences detected for Compose service `{service_name}`.", ""]
            continue
        lines += [f"Compose service: `{service_name}`", ""]
        if diff["image"]:
            lines += [f"- Image: `{diff['image']['template']}` → `{diff['image']['upstream']}`"]
        for key, label in (
            ("environment_added", "Environment variables added upstream"),
            ("environment_template_only", "Environment variables only in template"),
            ("ports_added", "Container ports added upstream"),
            ("ports_template_only", "Container ports only in template"),
            ("volumes_added", "Container volumes added upstream"),
            ("volumes_template_only", "Container volumes only in template"),
        ):
            if diff[key]:
                lines.append(f"- {label}: " + ", ".join(f"`{item}`" for item in diff[key]))
        lines.append("")

    output = args.output if args.output.is_absolute() else args.repo_root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    return 2 if review_required else 0


if __name__ == "__main__":
    sys.exit(main())
