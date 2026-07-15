#!/usr/bin/env python3
'''Generate README and the GitHub Pages artifact from catalog.yaml and template XML.'''

from __future__ import annotations

import argparse
import base64
import html
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml


def load(repo_root: Path) -> tuple[dict, list[dict]]:
    catalog = yaml.safe_load((repo_root / "catalog.yaml").read_text(encoding="utf-8"))
    entries: list[dict] = []
    for item in catalog["templates"]:
        path = repo_root / item["path"]
        template_root = ET.parse(path).getroot()
        metadata = {child.tag: (child.text or "").strip() for child in template_root if child.tag != "Config"}
        metadata.update(item)
        metadata["path"] = item["path"]
        metadata["webui_label"] = metadata.get("WebUI") or "Headless"
        metadata["description"] = metadata.get("Overview", "").splitlines()[0].strip()
        entries.append(metadata)
    entries.sort(key=lambda entry: entry["Name"].casefold())
    return catalog, entries


def readme_text(catalog: dict, entries: list[dict]) -> str:
    repo = catalog["repository"]
    lines = [
        f"# {repo['title']}",
        "",
        "[![Validate Templates](https://github.com/fgrfn/unraid-templates/actions/workflows/validate-templates.yml/badge.svg)](https://github.com/fgrfn/unraid-templates/actions/workflows/validate-templates.yml)",
        "[![Deploy Pages](https://github.com/fgrfn/unraid-templates/actions/workflows/deploy.yml/badge.svg)](https://github.com/fgrfn/unraid-templates/actions/workflows/deploy.yml)",
        "[![Upstream Drift](https://github.com/fgrfn/unraid-templates/actions/workflows/upstream-drift.yml/badge.svg)](https://github.com/fgrfn/unraid-templates/actions/workflows/upstream-drift.yml)",
        "",
        f"{repo['description']}. The catalog currently contains **{len(entries)} templates**.",
        "",
        "## Available templates",
        "",
        "| Template | Description | Network | Web UI | Install |",
        "|---|---|---|---|---|",
    ]
    for entry in entries:
        description = entry["description"].replace("|", r"\|")
        project = f"[{entry['Name']}]({entry['Project']})"
        install = f"[XML]({entry['TemplateURL']})"
        lines.append(f"| {project} | {description} | `{entry['Network']}` | `{entry['webui_label']}` | {install} |")

    lines += [
        "",
        "## Installation",
        "",
        "### Add the complete template repository",
        "",
        "In Unraid, open **Docker → Add Container → Template repositories** and add:",
        "",
        "```text",
        repo["github"],
        "```",
        "",
        "### Install a single template",
        "",
        "Open **Docker → Add Container → Template repositories** and paste the XML URL from the table above. Alternatively download the XML to `/boot/config/plugins/dockerMan/templates-user/`.",
        "",
        "## Development",
        "",
        "The repository uses `catalog.yaml` as its inventory. Template XML remains the source of container configuration; the README, website and deployment artifact are generated from both sources.",
        "",
        "```bash",
        "python -m pip install -r requirements-dev.txt",
        "python scripts/validate-templates.py",
        "pytest",
        "python scripts/generate-index.py --check-readme",
        "python scripts/generate-index.py --output _site",
        "```",
        "",
        "Upstream monitoring creates or updates a **draft pull request containing a drift report**. It never modifies production templates or pushes directly to `main`.",
        "",
        "## Contributing",
        "",
        "See [CONTRIBUTING.md](CONTRIBUTING.md). New templates must be added to `catalog.yaml`, pass semantic validation and include clear security and networking requirements.",
        "",
        "## License",
        "",
        "Template repository code and metadata are available under the [MIT License](LICENSE). Upstream applications retain their own licenses.",
        "",
    ]
    return "\n".join(lines)


def initials_data_uri(name: str) -> str:
    initials = "".join(part[0] for part in name.replace("-", " ").split()[:2]).upper() or "UT"
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96">'
        '<rect width="96" height="96" rx="18" fill="#ff8c2f"/>'
        f'<text x="48" y="59" text-anchor="middle" font-family="sans-serif" '
        f'font-size="34" font-weight="700" fill="white">{html.escape(initials)}</text></svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def website(catalog: dict, entries: list[dict]) -> str:
    cards = []
    filters = sorted({tag for entry in entries for tag in entry.get("tags", [])})
    for entry in entries:
        fallback = initials_data_uri(entry["Name"])
        tags = " ".join(entry.get("tags", []))
        owner_label = "Own project" if entry.get("ownership") == "first-party" else "External project"
        warning = ""
        if entry["Network"] not in {"bridge", "host", "none"}:
            warning = f'<p class="notice">Requires Docker network <code>{html.escape(entry["Network"])}</code>.</p>'
        elif entry["Network"] == "host":
            warning = '<p class="notice">Uses host networking.</p>'
        tags_html = "".join(f'<span>{html.escape(tag)}</span>' for tag in entry.get("tags", []))
        cards.append(f'''\n<article class="card" data-name="{html.escape(entry["Name"].lower())}" data-tags="{html.escape(tags.lower())}" data-network="{html.escape(entry["Network"])}" data-webui="{"yes" if entry.get("WebUI") else "no"}">\n  <header class="card-head">\n    <img src="{html.escape(entry["Icon"], quote=True)}" onerror="this.onerror=null;this.src='{fallback}'" alt="" loading="lazy">\n    <div><h2>{html.escape(entry["Name"])}</h2><span>{html.escape(owner_label)}</span></div>\n  </header>\n  <p>{html.escape(entry["description"])}</p>\n  {warning}\n  <dl>\n    <div><dt>Image</dt><dd><code>{html.escape(entry["Repository"])}</code></dd></div>\n    <div><dt>Network</dt><dd><code>{html.escape(entry["Network"])}</code></dd></div>\n    <div><dt>Web UI</dt><dd><code>{html.escape(entry["webui_label"])}</code></dd></div>\n  </dl>\n  <div class="tags">{tags_html}</div>\n  <div class="actions">\n    <a class="primary" href="{html.escape(entry["TemplateURL"], quote=True)}" download>Download XML</a>\n    <a href="{html.escape(entry["Project"], quote=True)}" target="_blank" rel="noreferrer">Project</a>\n    <button data-copy="{html.escape(entry["TemplateURL"], quote=True)}">Copy URL</button>\n  </div>\n</article>''')

    filter_options = "".join(f'<option value="{html.escape(tag.lower())}">{html.escape(tag)}</option>' for tag in filters)
    total = len(entries)
    return f'''<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<meta name="description" content="{html.escape(catalog["repository"]["description"])}">\n<title>{html.escape(catalog["repository"]["title"])}</title>\n<style>\n:root{{--accent:#ff8c2f;--bg:#f5f6f8;--panel:#fff;--text:#17191c;--muted:#646b75;--line:#dfe3e8;--notice:#fff4e8}}\n@media(prefers-color-scheme:dark){{:root{{--bg:#111315;--panel:#1b1e22;--text:#f4f5f6;--muted:#abb1ba;--line:#343940;--notice:#342619}}}}\n*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 system-ui,sans-serif}}\n.wrap{{width:min(1240px,calc(100% - 32px));margin:auto}}.hero{{padding:56px 0 28px}}h1{{font-size:clamp(2rem,6vw,4rem);margin:0}}.hero p{{color:var(--muted);max-width:720px}}\n.toolbar{{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(12px);padding:14px 0;border-bottom:1px solid var(--line)}}\n.controls{{display:grid;grid-template-columns:2fr repeat(3,1fr);gap:10px}}input,select,button,a{{font:inherit}}input,select{{width:100%;padding:11px 12px;border:1px solid var(--line);border-radius:9px;background:var(--panel);color:var(--text)}}\n.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px;padding:28px 0 60px}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px;display:flex;flex-direction:column;gap:14px}}\n.card-head{{display:flex;gap:12px;align-items:center}}.card-head img{{width:48px;height:48px;object-fit:contain;border-radius:10px;background:white;padding:4px}}h2{{margin:0;font-size:1.25rem}}.card-head span,.count{{color:var(--muted);font-size:.9rem}}\n.card p{{margin:0}}dl{{margin:0;display:grid;gap:8px}}dl div{{display:grid;grid-template-columns:72px 1fr;gap:8px}}dt{{color:var(--muted)}}dd{{margin:0;overflow-wrap:anywhere}}code{{font-size:.86em}}\n.tags{{display:flex;gap:7px;flex-wrap:wrap}}.tags span{{border:1px solid var(--line);border-radius:999px;padding:3px 8px;font-size:.78rem}}.notice{{background:var(--notice);padding:9px;border-radius:8px}}\n.actions{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:auto}}.actions a,.actions button{{border:1px solid var(--line);border-radius:8px;padding:9px;text-align:center;text-decoration:none;color:var(--text);background:transparent;cursor:pointer}}.actions .primary{{grid-column:1/-1;background:var(--accent);border-color:var(--accent);color:#111;font-weight:700}}\nfooter{{border-top:1px solid var(--line);padding:24px 0;color:var(--muted)}}[hidden]{{display:none!important}}\n@media(max-width:760px){{.controls{{grid-template-columns:1fr 1fr}}.controls input{{grid-column:1/-1}}}}\n</style>\n</head>\n<body>\n<section class="hero"><div class="wrap"><h1>{html.escape(catalog["repository"]["title"])}</h1><p>{html.escape(catalog["repository"]["description"])}. Browse, filter and copy a direct XML installation URL.</p><span class="count" id="count">{total} templates</span></div></section>\n<div class="toolbar"><div class="wrap controls">\n<input id="search" type="search" placeholder="Search templates…" aria-label="Search templates">\n<select id="tag"><option value="">All categories</option>{filter_options}</select>\n<select id="network"><option value="">All networks</option><option>bridge</option><option>host</option><option>axemobile</option></select>\n<select id="webui"><option value="">Web UI or headless</option><option value="yes">With Web UI</option><option value="no">Headless</option></select>\n</div></div>\n<main class="wrap grid" id="grid">{''.join(cards)}</main>\n<footer><div class="wrap"><a href="{html.escape(catalog["repository"]["github"])}">GitHub repository</a> · MIT licensed repository metadata</div></footer>\n<script>\nconst cards=[...document.querySelectorAll('.card')],search=document.querySelector('#search'),tag=document.querySelector('#tag'),network=document.querySelector('#network'),webui=document.querySelector('#webui'),count=document.querySelector('#count');\nfunction apply(){{let visible=0;for(const card of cards){{const ok=card.dataset.name.includes(search.value.toLowerCase())&&(!tag.value||card.dataset.tags.includes(tag.value))&&(!network.value||card.dataset.network===network.value)&&(!webui.value||card.dataset.webui===webui.value);card.hidden=!ok;if(ok)visible++}}count.textContent=`${{visible}} of {total} templates`}}\n[search,tag,network,webui].forEach(el=>el.addEventListener('input',apply));\ndocument.addEventListener('click',async e=>{{const value=e.target.dataset.copy;if(!value)return;await navigator.clipboard.writeText(value);const old=e.target.textContent;e.target.textContent='Copied';setTimeout(()=>e.target.textContent=old,1200)}});\n</script>\n</body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--write-readme", action="store_true")
    parser.add_argument("--check-readme", action="store_true")
    args = parser.parse_args()
    catalog, entries = load(args.repo_root)
    generated_readme = readme_text(catalog, entries)

    if args.write_readme:
        (args.repo_root / "README.md").write_text(generated_readme, encoding="utf-8")
    if args.check_readme:
        current = (args.repo_root / "README.md").read_text(encoding="utf-8")
        if current != generated_readme:
            print("README.md is stale; run: python scripts/generate-index.py --write-readme", file=sys.stderr)
            return 1

    if args.output:
        output = args.output if args.output.is_absolute() else args.repo_root / args.output
        if output.exists():
            shutil.rmtree(output)
        output.mkdir(parents=True)
        (output / "index.html").write_text(website(catalog, entries), encoding="utf-8")
        shutil.copytree(args.repo_root / "templates", output / "templates")
        shutil.copy2(args.repo_root / "LICENSE", output / "LICENSE.txt")
        (output / ".nojekyll").write_text("", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
