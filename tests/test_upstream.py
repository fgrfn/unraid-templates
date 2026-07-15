from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("upstream", ROOT / "scripts" / "check-upstream.py")
upstream = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(upstream)


def test_normalize_env_formats():
    assert upstream.normalize_env({"A": "1", "B": None}) == {"A", "B"}
    assert upstream.normalize_env(["A=1", "B"]) == {"A", "B"}


def test_normalize_port_formats():
    assert upstream.normalize_ports(["8080:80", "8443:443/tcp", {"target": 9000}]) == {"80", "443", "9000"}


def test_normalize_volume_formats():
    assert upstream.normalize_volumes(["./data:/data", {"target": "/config"}]) == {"/data", "/config"}


def test_compare_reports_added_values():
    template = {"image": "owner/app:old", "environment": {"A"}, "ports": {"80"}, "volumes": {"/data"}}
    service = {"image": "owner/app:new", "environment": {"A": "1", "B": "2"}, "ports": ["8080:80", "8443:443"], "volumes": ["./data:/data", "./config:/config"]}
    diff = upstream.compare(template, service)
    assert diff["image"]
    assert diff["environment_added"] == ["B"]
    assert diff["ports_added"] == ["443"]
    assert diff["volumes_added"] == ["/config"]
