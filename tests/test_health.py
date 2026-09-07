from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("health", ROOT / "scripts" / "check-health.py")
health = importlib.util.module_from_spec(SPEC)
# dataclasses resolves annotations through sys.modules, so register before exec.
sys.modules[SPEC.name] = health
assert SPEC.loader is not None
SPEC.loader.exec_module(health)


def test_normalize_env_formats():
    assert health.normalize_env({"A": "1", "B": None}) == {"A", "B"}
    assert health.normalize_env(["A=1", "B"]) == {"A", "B"}


def test_normalize_port_formats():
    assert health.normalize_ports(["8080:80", "8443:443/tcp", {"target": 9000}]) == {"80", "443", "9000"}


def test_normalize_ports_expands_variable_defaults():
    '''Regression: "${PORT:-5173}" used to be read as the port "-5173}".'''
    assert health.normalize_ports(["${PORT:-5173}"]) == {"5173"}
    assert health.normalize_ports(["${PORT:-8080}:80"]) == {"80"}
    assert health.normalize_ports(["${HOST_PORT-3000}:3000/udp"]) == {"3000"}


def test_normalize_ports_skips_unresolvable_variables():
    assert health.normalize_ports(["${PORT}"]) == set()


def test_normalize_volume_formats():
    assert health.normalize_volumes(["./data:/data", {"target": "/config"}]) == {"/data", "/config"}


def test_compare_reports_added_values():
    template = {"image": "owner/app:old", "environment": {"A"}, "ports": {"80"}, "volumes": {"/data"}}
    service = {
        "image": "owner/app:new",
        "environment": {"A": "1", "B": "2"},
        "ports": ["8080:80", "8443:443"],
        "volumes": ["./data:/data", "./config:/config"],
    }
    diff = health.compare(template, service)
    assert diff["image"]
    assert diff["environment_added"] == ["B"]
    assert diff["ports_added"] == ["443"]
    assert diff["volumes_added"] == ["/config"]


def test_compare_expands_image_variables():
    template = {"image": "ghcr.io/owner/app:latest", "environment": set(), "ports": set(), "volumes": set()}
    service = {"image": "${APP_IMAGE:-ghcr.io/owner/app:latest}"}
    assert health.compare(template, service)["image"] is None


def test_parse_image_variants():
    assert health.parse_image("ghcr.io/fgrfn/app:latest") == ("ghcr.io", "fgrfn/app", "latest")
    assert health.parse_image("owner/app:1.2.3") == ("docker.io", "owner/app", "1.2.3")
    assert health.parse_image("nginx") == ("docker.io", "library/nginx", "latest")
    # Regression: the tag's colon must not be read as a registry host:port pair.
    assert health.parse_image("nginx:latest") == ("docker.io", "library/nginx", "latest")
    assert health.parse_image("localhost:5000/app:1.0") == ("localhost:5000", "app", "1.0")
    assert health.parse_image("ghcr.io/fgrfn/app") == ("ghcr.io", "fgrfn/app", "latest")
    assert health.parse_image("ghcr.io/fgrfn/app@sha256:abc") == ("ghcr.io", "fgrfn/app", "sha256:abc")


def test_report_marks_healthy_and_unhealthy_entries():
    healthy = health.EntryReport(entry_id="fine")
    broken = health.EntryReport(entry_id="rotten", problems=["image `x` no longer exists in ghcr.io"])
    assert not healthy.needs_review
    assert broken.needs_review

    report = health.build_report([healthy, broken])
    assert "1 of 2 templates need review" in report
    assert "no longer exists" in report


def test_report_is_clean_when_everything_resolves():
    assert "All 1 templates look healthy." in health.build_report([health.EntryReport(entry_id="fine")])


def test_url_belongs_to_repository():
    repo = ("fgrfn", "reddit-wsb-crawler")
    assert health.url_belongs_to("https://github.com/fgrfn/reddit-wsb-crawler", repo)
    assert health.url_belongs_to("https://github.com/fgrfn/reddit-wsb-crawler/issues", repo)
    assert health.url_belongs_to("https://github.com/fgrfn/reddit-wsb-crawler#readme", repo)
    assert health.url_belongs_to("https://raw.githubusercontent.com/fgrfn/reddit-wsb-crawler/main/logo.png", repo)


def test_url_belongs_to_rejects_other_repositories():
    repo = ("fgrfn", "reddit-wsb-crawler")
    # A neighbouring repository whose name merely starts the same must not match.
    assert not health.url_belongs_to("https://github.com/fgrfn/reddit-wsb-crawler-docs", repo)
    assert not health.url_belongs_to("https://github.com/someone/reddit-wsb-crawler", repo)
    assert not health.url_belongs_to("https://cdn.example.com/logo.png", repo)
    assert not health.url_belongs_to("https://github.com/fgrfn/reddit-wsb-crawler", None)
    assert not health.url_belongs_to("", repo)


def test_repository_of_parses_project_urls():
    assert health.repository_of("https://github.com/fgrfn/hashhive") == ("fgrfn", "hashhive")
    assert health.repository_of("https://github.com/fgrfn/hashhive.git") == ("fgrfn", "hashhive")
    assert health.repository_of("https://example.com/project") is None
    assert health.repository_of("") is None
