from __future__ import annotations

import html
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("generate", ROOT / "scripts" / "generate-index.py")
generate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = generate
assert SPEC.loader is not None
SPEC.loader.exec_module(generate)


def build_readme():
    catalog, entries = generate.load(ROOT)
    return catalog, generate.readme_text(catalog, entries)


def test_readme_links_the_published_site():
    '''Regression: the landing page went unlinked for weeks after 8839f3a.

    The README links each template's XML below the site, so a missing link to
    the site root is easy to overlook — nothing else breaks.
    '''
    catalog, readme = build_readme()
    pages_url = catalog["repository"]["pages_base_url"].rstrip("/") + "/"
    assert f"({pages_url})" in readme


def test_readme_lists_every_catalog_entry():
    _, entries = generate.load(ROOT)
    _, readme = build_readme()
    for entry in entries:
        assert entry["Name"] in readme
        assert entry["TemplateURL"] in readme


def test_readme_reports_the_catalog_size():
    _, entries = generate.load(ROOT)
    _, readme = build_readme()
    assert f"**{len(entries)} templates**" in readme


def test_website_lists_every_catalog_entry():
    catalog, entries = generate.load(ROOT)
    page = generate.website(catalog, entries)
    assert page.count('<article class="card"') == len(entries)
    for entry in entries:
        assert entry["TemplateURL"] in page


def test_install_command_targets_the_unraid_template_directory():
    _, entries = generate.load(ROOT)
    for entry in entries:
        command = generate.install_command(entry)
        filename = Path(entry["path"]).name
        # Unraid only picks the file up under this exact name and directory.
        assert f"{generate.UNRAID_TEMPLATE_DIR}/{filename}" in command
        assert command.endswith(entry["TemplateURL"])
        assert filename.startswith("my-") and filename.endswith(".xml")


def test_website_offers_an_install_command_per_template():
    '''The gallery had download and copy-URL buttons but no ready-to-run command.'''
    catalog, entries = generate.load(ROOT)
    page = generate.website(catalog, entries)
    assert page.count('<details class="install">') == len(entries)
    for entry in entries:
        command = generate.install_command(entry)
        # Rendered into the visible block and into the clipboard button.
        assert page.count(html.escape(command)) >= 1
        assert f'data-copy="{html.escape(command, quote=True)}"' in page


def test_readme_documents_the_console_install():
    _, entries = generate.load(ROOT)
    _, readme = build_readme()
    assert "### Install from the Unraid console" in readme
    assert generate.install_command(entries[0]) in readme


def test_readme_omits_the_console_section_without_templates():
    catalog, _ = generate.load(ROOT)
    readme = generate.readme_text(catalog, [])
    assert "### Install from the Unraid console" not in readme
