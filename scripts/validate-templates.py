#!/usr/bin/env python3
"""Semantic validation for Unraid v2 XML templates and catalog metadata."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

BOOLEAN_VALUES = {"true", "false"}
DISPLAY_VALUES = {"always", "advanced"}
TYPE_MODES = {
    "Port": {"tcp", "udp"},
    "Path": {"rw", "ro"},
    "Variable": {"env"},
    "Device": {"rw", "ro"},
}
REQUIRED_FIELDS = (
    "Name", "Repository", "Registry", "Network", "Shell", "Privileged",
    "Support", "Project", "ReadMe", "Overview", "Category", "TemplateURL", "Icon",
)
URL_FIELDS = ("Registry", "Support", "Project", "ReadMe", "TemplateURL", "Icon")
SENSITIVE_PATTERN = re.compile(
    r"(PASSWORD|PASS$|TOKEN|SECRET|API_KEY|API_TOKEN|PRIVATE_KEY|ENCRYPTION_KEY|WEBHOOK_URL)",
    re.IGNORECASE,
)
PLACEHOLDER_PATTERN = re.compile(r"\{\d+\}|TODO|CHANGEME", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    path: Path
    level: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.level}: {self.message}"


def text(root: ET.Element, tag: str) -> str:
    return (root.findtext(tag) or "").strip()


def validate_url(url: str, timeout: int = 8) -> str | None:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "unraid-template-validator/1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status >= 400:
                return f"HTTP {response.status}"
    except Exception as exc:
        return str(exc)
    return None


def validate_template(xml_path: Path, *, check_urls: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    try:
        tree = ET.parse(xml_path)
    except Exception as exc:
        return [Finding(xml_path, "ERROR", f"XML parsing failed: {exc}")]

    root = tree.getroot()
    if root.tag != "Container":
        findings.append(Finding(xml_path, "ERROR", "root element must be <Container>"))
    if root.get("version") != "2":
        findings.append(Finding(xml_path, "ERROR", 'Container version must be "2"'))

    serialized = xml_path.read_text(encoding="utf-8")
    match = PLACEHOLDER_PATTERN.search(serialized)
    if match:
        findings.append(Finding(xml_path, "ERROR", f"unresolved placeholder found: {match.group(0)}"))

    for field in REQUIRED_FIELDS:
        value = text(root, field)
        if not value:
            findings.append(Finding(xml_path, "ERROR", f"missing or empty <{field}>"))

    if text(root, "Privileged") not in BOOLEAN_VALUES:
        findings.append(Finding(xml_path, "ERROR", "Privileged must be true or false"))

    if text(root, "DateInstalled"):
        findings.append(Finding(xml_path, "ERROR", "DateInstalled must be empty in repository templates"))

    for field in URL_FIELDS:
        value = text(root, field)
        if value and not value.startswith("https://"):
            findings.append(Finding(xml_path, "ERROR", f"{field} must use HTTPS"))
        elif value and check_urls:
            error = validate_url(value)
            if error:
                findings.append(Finding(xml_path, "WARNING", f"{field} URL could not be verified: {error}"))

    config_keys: set[tuple[str, str]] = set()
    names: set[str] = set()
    for index, config in enumerate(root.findall("Config"), start=1):
        prefix = f"Config #{index}"
        name = (config.get("Name") or "").strip()
        target = (config.get("Target") or "").strip()
        default = config.get("Default")
        mode = (config.get("Mode") or "").strip()
        config_type = (config.get("Type") or "").strip()
        display = (config.get("Display") or "").strip()
        required = (config.get("Required") or "").strip()
        mask = (config.get("Mask") or "").strip()
        value = (config.text or "").strip()

        for attr, attr_value in (
            ("Name", name), ("Target", target), ("Default", default),
            ("Mode", mode), ("Type", config_type), ("Display", display),
            ("Required", required), ("Mask", mask),
        ):
            if attr_value is None or attr_value == "":
                if attr != "Default":
                    findings.append(Finding(xml_path, "ERROR", f"{prefix} has empty {attr}"))

        if required not in BOOLEAN_VALUES:
            findings.append(Finding(xml_path, "ERROR", f"{prefix} Required must be true or false"))
        if mask not in BOOLEAN_VALUES:
            findings.append(Finding(xml_path, "ERROR", f"{prefix} Mask must be true or false"))
        if display not in DISPLAY_VALUES:
            findings.append(Finding(xml_path, "ERROR", f"{prefix} Display must be always or advanced"))
        if config_type not in TYPE_MODES:
            findings.append(Finding(xml_path, "ERROR", f"{prefix} has unsupported Type={config_type!r}"))
        elif mode not in TYPE_MODES[config_type]:
            findings.append(Finding(xml_path, "ERROR", f"{prefix} Type={config_type} is incompatible with Mode={mode!r}"))

        if default is not None and value != default:
            findings.append(Finding(xml_path, "ERROR", f"{prefix} text value {value!r} does not match Default {default!r}"))

        key = (mode, target)
        if key in config_keys:
            findings.append(Finding(xml_path, "ERROR", f"duplicate Config target {target!r} for mode {mode!r}"))
        config_keys.add(key)

        if name in names:
            findings.append(Finding(xml_path, "ERROR", f"duplicate Config name {name!r}"))
        names.add(name)

        if SENSITIVE_PATTERN.search(target) and mask != "true":
            findings.append(Finding(xml_path, "ERROR", f"sensitive Config {target!r} must set Mask=true"))

    network = text(root, "Network")
    if network == "host" and any((c.get("Type") == "Port") for c in root.findall("Config")):
        findings.append(Finding(xml_path, "WARNING", "host-network template contains Port configs; Unraid does not publish ports in host mode"))

    webui = text(root, "WebUI")
    if webui and "[PORT:" in webui:
        port_match = re.search(r"\[PORT:(\d+)\]", webui)
        port_defaults = {c.get("Default") for c in root.findall("Config") if c.get("Type") == "Port"}
        if port_match and port_match.group(1) not in port_defaults:
            findings.append(Finding(xml_path, "ERROR", "WebUI references a port without a matching Port config"))

    return findings


def load_catalog(repo_root: Path) -> dict:
    with (repo_root / "catalog.yaml").open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("templates"), list):
        raise ValueError("catalog.yaml must contain a templates list")
    return data


def validate_repository(repo_root: Path, *, check_urls: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    templates_dir = repo_root / "templates"
    catalog_path = repo_root / "catalog.yaml"

    try:
        catalog = load_catalog(repo_root)
    except Exception as exc:
        return [Finding(catalog_path, "ERROR", f"catalog could not be loaded: {exc}")]

    catalog_paths: list[str] = []
    ids: set[str] = set()
    for entry in catalog["templates"]:
        entry_id = str(entry.get("id", "")).strip()
        path = str(entry.get("path", "")).strip()
        if not entry_id:
            findings.append(Finding(catalog_path, "ERROR", "catalog entry has no id"))
        elif entry_id in ids:
            findings.append(Finding(catalog_path, "ERROR", f"duplicate catalog id {entry_id!r}"))
        ids.add(entry_id)
        if not path:
            findings.append(Finding(catalog_path, "ERROR", f"catalog entry {entry_id!r} has no path"))
        catalog_paths.append(path)

    actual_paths = sorted(
        str(path.relative_to(repo_root)).replace("\\", "/")
        for path in templates_dir.rglob("*.xml")
        if path.name != "blank-template.xml"
    )
    if sorted(catalog_paths) != actual_paths:
        missing = sorted(set(actual_paths) - set(catalog_paths))
        stale = sorted(set(catalog_paths) - set(actual_paths))
        if missing:
            findings.append(Finding(catalog_path, "ERROR", f"templates missing from catalog: {', '.join(missing)}"))
        if stale:
            findings.append(Finding(catalog_path, "ERROR", f"catalog points to missing templates: {', '.join(stale)}"))

    names: dict[str, Path] = {}
    for relative in actual_paths:
        xml_path = repo_root / relative
        findings.extend(validate_template(xml_path, check_urls=check_urls))
        try:
            template_root = ET.parse(xml_path).getroot()
        except ET.ParseError:
            continue
        name = text(template_root, "Name")
        if name in names:
            findings.append(Finding(xml_path, "ERROR", f"duplicate template name also used by {names[name]}"))
        names[name] = xml_path

        expected_url = f"{catalog['repository']['pages_base_url'].rstrip('/')}/{relative}"
        actual_url = text(template_root, "TemplateURL")
        if actual_url != expected_url:
            findings.append(Finding(xml_path, "ERROR", f"TemplateURL must be {expected_url}"))

    if (repo_root / "docs").exists():
        findings.append(Finding(repo_root / "docs", "ERROR", "generated GitHub Pages files must not be committed"))

    return findings


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check-urls", action="store_true")
    parser.add_argument("--strict-warnings", action="store_true")
    args = parser.parse_args(argv)

    findings = validate_repository(args.repo_root, check_urls=args.check_urls)
    for finding in findings:
        print(finding)

    errors = sum(f.level == "ERROR" for f in findings)
    warnings = sum(f.level == "WARNING" for f in findings)
    template_count = len(list((args.repo_root / "templates").rglob("my-*.xml")))
    print(f"\nValidated {template_count} templates: {errors} error(s), {warnings} warning(s)")
    return 1 if errors or (args.strict_warnings and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
