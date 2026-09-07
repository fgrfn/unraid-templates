#!/usr/bin/env python3
'''Report templates whose upstream application, image or links have gone stale.

The check is review-only: it never edits a template. It answers two questions
per catalog entry:

* Is the application still there? The container image must resolve in its
  registry, the GitHub project must exist and not be archived, and every URL
  the template hands to Unraid must respond. An entry marked
  ``visibility: private`` is expected to be unreachable from outside, so
  findings about that repository are reported as notes rather than problems.
  Everything else about it, including URLs hosted elsewhere, is still checked.
* Has an external project changed its Compose file? Drift is only meaningful
  for entries marked ``ownership: external``; a first-party Compose file is a
  development artifact, not a published contract, so comparing it produces
  noise rather than signal.
'''

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests
import yaml

USER_AGENT = "unraid-template-health/1"
TIMEOUT = 20

# ``${PORT:-8080}`` and ``${PORT-8080}`` collapse to their default, ``${PORT}``
# to an empty string. Without this a Compose port of "${PORT:-8080}" was read
# as the literal container port "-8080}".
VARIABLE_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::?-([^}]*))?\}")
GITHUB_REPO_PATTERN = re.compile(r"^https://github\.com/([^/]+)/([^/#?]+)")

MANIFEST_ACCEPT = ", ".join(
    (
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.v2+json",
    )
)
REGISTRIES = {
    "ghcr.io": ("https://ghcr.io/token?service=ghcr.io&scope=repository:{name}:pull", "https://ghcr.io"),
    "docker.io": (
        "https://auth.docker.io/token?service=registry.docker.io&scope=repository:{name}:pull",
        "https://registry-1.docker.io",
    ),
}

# Checked because Unraid follows them from the template itself.
LINK_FIELDS = ("Project", "Support", "ReadMe", "Icon", "TemplateURL")


@dataclass
class EntryReport:
    entry_id: str
    problems: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def needs_review(self) -> bool:
        return bool(self.problems)


def expand_variables(value: str) -> str:
    return VARIABLE_PATTERN.sub(lambda match: match.group(2) or "", str(value))


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
            value = expand_variables(item).split("/")[0]
            target = value.rsplit(":", 1)[-1]
        target = str(target).strip() if target is not None else ""
        if target:
            result.add(target)
    return result


def normalize_volumes(volumes: Any) -> set[str]:
    result: set[str] = set()
    for item in volumes or []:
        if isinstance(item, dict):
            target = item.get("target")
        else:
            parts = expand_variables(item).split(":")
            target = parts[1] if len(parts) > 1 else parts[0]
        if target:
            result.add(str(target))
    return result


def parse_image(repository: str) -> tuple[str, str, str]:
    '''Split an image reference into (registry host, repository name, reference).'''
    remainder = repository.strip()
    head, separator, tail = remainder.partition("/")
    # A registry host only exists when something follows it, otherwise the
    # colon in "nginx:latest" would be mistaken for a host:port pair.
    if separator and ("." in head or ":" in head or head == "localhost"):
        host, remainder = head, tail
    else:
        host = "docker.io"
    if "@" in remainder:
        name, _, reference = remainder.partition("@")
    elif ":" in remainder.rsplit("/", 1)[-1]:
        name, _, reference = remainder.rpartition(":")
    else:
        name, reference = remainder, "latest"
    if host == "docker.io" and "/" not in name:
        name = f"library/{name}"
    return host, name, reference


def image_exists(repository: str) -> tuple[str | None, str | None]:
    '''Return (problem, note) for the container image a template pulls.'''
    host, name, reference = parse_image(repository)
    if host not in REGISTRIES:
        return None, f"image `{repository}` sits on {host}, which this check cannot query"
    token_url, base_url = REGISTRIES[host]
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    try:
        token_response = session.get(token_url.format(name=name), timeout=TIMEOUT)
        # Registries answer the token request itself with 401/403 when the
        # repository is unknown or private, so the manifest is never reached.
        if token_response.status_code in {401, 403}:
            return f"image `{repository}` is missing or not publicly readable in {host}", None
        token_response.raise_for_status()
        token = token_response.json().get("token") or token_response.json().get("access_token", "")
        response = session.head(
            f"{base_url}/v2/{name}/manifests/{reference}",
            headers={"Authorization": f"Bearer {token}", "Accept": MANIFEST_ACCEPT},
            timeout=TIMEOUT,
            allow_redirects=True,
        )
    except Exception as exc:
        return f"registry request failed: {exc}", None
    if response.status_code == 404:
        return f"image `{repository}` no longer exists in {host}", None
    if response.status_code == 401:
        return f"image `{repository}` is not publicly readable in {host}", None
    if response.status_code >= 400:
        return f"image `{repository}` returned HTTP {response.status_code} from {host}", None
    return None, None


def github_project_status(project_url: str) -> tuple[str | None, str | None]:
    '''Return (problem, note) for the GitHub project a template points at.'''
    match = GITHUB_REPO_PATTERN.match(project_url or "")
    if not match:
        return None, None
    owner, repo = match.group(1), match.group(2).removesuffix(".git")
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}", headers=headers, timeout=TIMEOUT
        )
    except Exception as exc:
        return f"GitHub API request failed: {exc}", None
    if response.status_code == 404:
        return f"project `{owner}/{repo}` no longer exists or is private", None
    if response.status_code >= 400:
        return f"GitHub API returned HTTP {response.status_code} for `{owner}/{repo}`", None
    data = response.json()
    if data.get("archived"):
        return f"project `{owner}/{repo}` is archived upstream", None
    pushed_at = data.get("pushed_at")
    if not pushed_at:
        return None, None
    last_push = dt.datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
    days = (dt.datetime.now(dt.timezone.utc) - last_push).days
    return None, f"last upstream push {days} days ago ({last_push.date()})"


def repository_of(project_url: str) -> tuple[str, str] | None:
    match = GITHUB_REPO_PATTERN.match(project_url or "")
    if not match:
        return None
    return match.group(1), match.group(2).removesuffix(".git")


def url_belongs_to(url: str, repository: tuple[str, str] | None) -> bool:
    """True when the URL is served by the given GitHub repository."""
    if not repository or not url:
        return False
    owner, repo = repository
    pattern = rf"^https://(github\.com|raw\.githubusercontent\.com)/{re.escape(owner)}/{re.escape(repo)}([/#?]|$)"
    return bool(re.match(pattern, url, re.IGNORECASE))


def check_link(url: str) -> str | None:
    if not url:
        return None
    try:
        response = requests.head(url, timeout=TIMEOUT, allow_redirects=True, headers={"User-Agent": USER_AGENT})
        if response.status_code in {403, 405, 501}:
            response = requests.get(
                url, timeout=TIMEOUT, allow_redirects=True, headers={"User-Agent": USER_AGENT}, stream=True
            )
    except Exception as exc:
        return f"request failed: {exc}"
    if response.status_code >= 400:
        return f"HTTP {response.status_code}"
    return None


def template_state(path: Path) -> dict[str, Any]:
    template_root = ET.parse(path).getroot()
    configs = template_root.findall("Config")
    state: dict[str, Any] = {
        "image": (template_root.findtext("Repository") or "").strip(),
        "environment": {c.get("Target", "") for c in configs if c.get("Mode") == "env"},
        "ports": {c.get("Target", "") for c in configs if c.get("Type") == "Port"},
        "volumes": {c.get("Target", "") for c in configs if c.get("Type") == "Path"},
    }
    for link_field in LINK_FIELDS:
        state[link_field] = (template_root.findtext(link_field) or "").strip()
    return state


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
        "image": expand_variables(service.get("image", "")),
        "environment": normalize_env(service.get("environment")),
        "ports": normalize_ports(service.get("ports")),
        "volumes": normalize_volumes(service.get("volumes")),
    }
    ignore_env = {"TZ", "PUID", "PGID"}
    image_changed = bool(upstream["image"]) and template["image"] != upstream["image"]
    return {
        "image": {"template": template["image"], "upstream": upstream["image"]} if image_changed else None,
        "environment_added": sorted((upstream["environment"] - template["environment"]) - ignore_env),
        "environment_template_only": sorted((template["environment"] - upstream["environment"]) - ignore_env),
        "ports_added": sorted(upstream["ports"] - template["ports"]),
        "ports_template_only": sorted(template["ports"] - upstream["ports"]),
        "volumes_added": sorted(upstream["volumes"] - template["volumes"]),
        "volumes_template_only": sorted(template["volumes"] - upstream["volumes"]),
    }


def has_drift(diff: dict[str, Any]) -> bool:
    return any(value for value in diff.values())


def describe_drift(diff: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    if diff["image"]:
        lines.append(f"Image: `{diff['image']['template']}` → `{diff['image']['upstream']}`")
    for key, label in (
        ("environment_added", "Environment variables added upstream"),
        ("environment_template_only", "Environment variables only in template"),
        ("ports_added", "Container ports added upstream"),
        ("ports_template_only", "Container ports only in template"),
        ("volumes_added", "Container volumes added upstream"),
        ("volumes_template_only", "Container volumes only in template"),
    ):
        if diff[key]:
            lines.append(f"{label}: " + ", ".join(f"`{item}`" for item in diff[key]))
    return lines


def check_entry(entry: dict, repo_root: Path) -> EntryReport:
    report = EntryReport(entry_id=entry["id"])
    state = template_state(repo_root / entry["path"])
    # A private project is unreachable from outside by design. Findings about
    # that repository are expected, so they are recorded as notes; the image,
    # the template URL and any link hosted elsewhere are still hard checks.
    private_repository = repository_of(state["Project"]) if entry.get("visibility") == "private" else None

    problem, note = image_exists(state["image"])
    if problem:
        report.problems.append(problem)
    if note:
        report.notes.append(note)

    problem, note = github_project_status(state["Project"])
    if problem:
        if private_repository:
            report.notes.append(f"{problem} (expected: the catalog marks it private)")
        else:
            report.problems.append(problem)
    if note:
        report.notes.append(note)

    for link_field in LINK_FIELDS:
        if failure := check_link(state[link_field]):
            finding = f"`<{link_field}>` is unreachable ({failure}): {state[link_field]}"
            if url_belongs_to(state[link_field], private_repository):
                report.notes.append(f"{finding} (expected: the catalog marks the project private)")
            else:
                report.problems.append(finding)

    upstream = entry.get("upstream") or {}
    if entry.get("ownership") == "external" and upstream.get("enabled"):
        try:
            response = requests.get(
                upstream["compose_url"], timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}
            )
            response.raise_for_status()
            compose = yaml.safe_load(response.text)
            service_name, service = choose_service(compose.get("services") or {}, upstream.get("service", ""))
            diff = compare(state, service)
            if has_drift(diff):
                report.problems.append(f"Compose service `{service_name}` drifted from the template:")
                report.problems += [f"  - {line}" for line in describe_drift(diff)]
        except Exception as exc:
            report.problems.append(f"upstream Compose check failed: {exc}")

    return report


def build_report(reports: list[EntryReport]) -> str:
    needs_review = [report for report in reports if report.needs_review]
    lines = [
        "# Template health report",
        "",
        f"Generated: {dt.datetime.now(dt.timezone.utc).isoformat()}",
        "",
        "This report is review-only. No template is changed automatically.",
        "",
    ]
    if not needs_review:
        lines += [f"All {len(reports)} templates look healthy.", ""]
    else:
        lines += [f"{len(needs_review)} of {len(reports)} templates need review.", ""]
    for report in reports:
        lines += [f"## {report.entry_id}", ""]
        if report.problems:
            lines += [f"- ⚠️ {problem}" if not problem.startswith("  ") else problem for problem in report.problems]
        else:
            lines.append("- ✅ Image, project and links all resolve.")
        lines += [f"- {note}" for note in report.notes]
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("reports/template-health.md"))
    args = parser.parse_args()

    catalog = yaml.safe_load((args.repo_root / "catalog.yaml").read_text(encoding="utf-8"))
    reports = [check_entry(entry, args.repo_root) for entry in catalog["templates"]]

    output = args.output if args.output.is_absolute() else args.repo_root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_report(reports), encoding="utf-8")

    for report in reports:
        for problem in report.problems:
            print(f"{report.entry_id}: {problem.strip()}", file=sys.stderr)
    return 2 if any(report.needs_review for report in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
