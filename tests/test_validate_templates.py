from __future__ import annotations

import importlib.util
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "scripts" / "validate-templates.py")
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


def write_template(path: Path, *, target: str = "PASSWORD", mask: str = "true", required: str = "true") -> None:
    path.write_text(
        f'''<?xml version="1.0"?>
<Container version="2">
  <Name>Test</Name>
  <Repository>owner/image:latest</Repository>
  <Registry>https://example.com/registry</Registry>
  <Network>bridge</Network>
  <Shell>sh</Shell>
  <Privileged>false</Privileged>
  <Support>https://example.com/support</Support>
  <Project>https://example.com/project</Project>
  <ReadMe>https://example.com/readme</ReadMe>
  <Overview>Test template.</Overview>
  <Category>Tools:</Category>
  <WebUI />
  <TemplateURL>https://example.com/template.xml</TemplateURL>
  <Icon>https://example.com/icon.png</Icon>
  <DateInstalled />
  <Config Name="Secret" Target="{target}" Default="" Mode="env" Description="Secret" Type="Variable" Display="always" Required="{required}" Mask="{mask}" />
</Container>''',
        encoding="utf-8",
    )


def messages(findings):
    return [finding.message for finding in findings if finding.level == "ERROR"]


def test_repository_templates_are_valid():
    findings = validator.validate_repository(ROOT)
    assert not [finding for finding in findings if finding.level == "ERROR"]


def test_sensitive_variable_requires_mask(tmp_path):
    path = tmp_path / "template.xml"
    write_template(path, mask="false")
    assert any("Mask=true" in message for message in messages(validator.validate_template(path)))


def test_boolean_placeholders_are_rejected(tmp_path):
    path = tmp_path / "template.xml"
    write_template(path, required="{7}")
    errors = messages(validator.validate_template(path))
    assert any("unresolved placeholder" in message for message in errors)
    assert any("Required must be true or false" in message for message in errors)


def test_duplicate_config_target_is_rejected(tmp_path):
    path = tmp_path / "template.xml"
    write_template(path, target="TOKEN")
    tree = ET.parse(path)
    template_root = tree.getroot()
    duplicate = ET.fromstring(
        '<Config Name="Second" Target="TOKEN" Default="" Mode="env" Description="Second" Type="Variable" Display="advanced" Required="false" Mask="true" />'
    )
    template_root.append(duplicate)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    assert any("duplicate Config target" in message for message in messages(validator.validate_template(path)))


def test_date_installed_must_be_empty(tmp_path):
    path = tmp_path / "template.xml"
    write_template(path)
    tree = ET.parse(path)
    template_root = tree.getroot()
    template_root.find("DateInstalled").text = "123456"
    tree.write(path, encoding="utf-8", xml_declaration=True)
    assert any("DateInstalled must be empty" in message for message in messages(validator.validate_template(path)))
