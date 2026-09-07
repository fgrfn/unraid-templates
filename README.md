# fgrfn Unraid Templates

[![Validate Templates](https://github.com/fgrfn/unraid-templates/actions/workflows/validate-templates.yml/badge.svg)](https://github.com/fgrfn/unraid-templates/actions/workflows/validate-templates.yml)
[![Deploy Pages](https://github.com/fgrfn/unraid-templates/actions/workflows/deploy.yml/badge.svg)](https://github.com/fgrfn/unraid-templates/actions/workflows/deploy.yml)
[![Template Health](https://github.com/fgrfn/unraid-templates/actions/workflows/template-health.yml/badge.svg)](https://github.com/fgrfn/unraid-templates/actions/workflows/template-health.yml)

Curated Docker templates for Unraid. The catalog currently contains **3 templates**.

> **Personal learning project:** Built with the help of OpenAI Codex and Claude Code as a way to experiment, learn and create something useful.

## Available templates

| Template | Description | Network | Web UI | Install |
|---|---|---|---|---|
| [HashHive](https://github.com/fgrfn/hashhive) | Unified mining dashboard for NMMiner, Bitaxe and NerdAxe devices. It provides live statistics, device configuration, pool management, alerting and notifications through Telegram, Discord or Gotify. | `bridge` | `http://[IP]:[PORT:8000]` | [XML](https://fgrfn.github.io/unraid-templates/templates/HashHive/my-HashHive.xml) |
| [RedditWSBCrawler](https://github.com/fgrfn/reddit-wsb-crawler) | Early-warning crawler for stock-ticker activity on Reddit. It analyzes mention trends, enriches them with market and news data and can send Discord alerts for unusual activity. | `bridge` | `Headless` | [XML](https://fgrfn.github.io/unraid-templates/templates/RedditWSBCrawler/my-RedditWSBCrawler.xml) |
| [Scan2Target](https://github.com/fgrfn/Scan2Target) | Web-based scan server for USB and network scanners. Scan2Target discovers scanners and routes documents to file shares, mail, Paperless-ngx, webhooks and cloud providers. | `host` | `http://[IP]:8000` | [XML](https://fgrfn.github.io/unraid-templates/templates/Scan2Target/my-Scan2Target.xml) |

## Installation

### Add the complete template repository

In Unraid, open **Docker → Add Container → Template repositories** and add:

```text
https://github.com/fgrfn/unraid-templates
```

### Install a single template

Open **Docker → Add Container → Template repositories** and paste the XML URL from the table above. Alternatively download the XML to `/boot/config/plugins/dockerMan/templates-user/`.

## Development

The repository uses `catalog.yaml` as its inventory. Template XML remains the source of container configuration; the README, website and deployment artifact are generated from both sources.

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate-templates.py
pytest
python scripts/generate-index.py --check-readme
python scripts/generate-index.py --output _site
```

A weekly health check verifies that every template still resolves: the container image exists in its registry, the GitHub project is present and not archived, and the project, support, readme, icon and template URLs all respond. It is review-only and tracks findings in a single issue that closes itself once everything is healthy.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). New templates must be added to `catalog.yaml`, pass semantic validation and include clear security and networking requirements.

## License

Template repository code and metadata are available under the [MIT License](LICENSE). Upstream applications retain their own licenses.
