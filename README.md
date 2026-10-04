# fgrfn Unraid Templates

[![Validate Templates](https://github.com/fgrfn/unraid-templates/actions/workflows/validate-templates.yml/badge.svg)](https://github.com/fgrfn/unraid-templates/actions/workflows/validate-templates.yml)
[![Deploy Pages](https://github.com/fgrfn/unraid-templates/actions/workflows/deploy.yml/badge.svg)](https://github.com/fgrfn/unraid-templates/actions/workflows/deploy.yml)
[![Template Health](https://github.com/fgrfn/unraid-templates/actions/workflows/template-health.yml/badge.svg)](https://github.com/fgrfn/unraid-templates/actions/workflows/template-health.yml)

Curated Docker templates for Unraid. The catalog currently contains **5 templates**.

> **Personal learning project:** Built with the help of OpenAI Codex and Claude Code as a way to experiment, learn and create something useful.

## Browse online

**[Template gallery](https://fgrfn.github.io/unraid-templates/)** — every template on one page, with search, category and network filters, and a button that copies the installation URL to the clipboard.

## Available templates

| Template | Description | Network | Web UI | Install |
|---|---|---|---|---|
| [AdGuardHub](https://github.com/fgrfn/AdGuardHub) | One dashboard to manage several AdGuard Home instances as a single system. AdGuardHub holds the filtering rules, blocklist subscriptions and instance settings, and pushes every change to all connected instances at once, so two instances kept for DNS failover can no longer overwrite each other's whitelist. | `bridge` | `http://[IP]:[PORT:80]` | [XML](https://fgrfn.github.io/unraid-templates/templates/AdGuardHub/my-AdGuardHub.xml) |
| [AliExpressCoinCollector](https://github.com/fgrfn/aliexpress-coin-collector-v2) | Collects the daily AliExpress coins on a schedule. It drives a headless mobile browser session to claim the check-in and the coin tasks, keeps the browser profile so the account is not treated as a new device, and offers a web dashboard for configuration plus a noVNC view for logins and captchas. | `bridge` | `http://[IP]:[PORT:80]` | [XML](https://fgrfn.github.io/unraid-templates/templates/AliExpressCoinCollector/my-AliExpressCoinCollector.xml) |
| [HashHive](https://github.com/fgrfn/hashhive) | Unified mining dashboard for NMMiner, Bitaxe and NerdAxe devices. It provides live statistics, device configuration, pool management, alerting and notifications through Telegram, Discord or Gotify. | `bridge` | `http://[IP]:[PORT:80]` | [XML](https://fgrfn.github.io/unraid-templates/templates/HashHive/my-HashHive.xml) |
| [RedditWSBCrawler](https://github.com/fgrfn/reddit-wsb-crawler) | Early-warning crawler for stock-ticker activity on Reddit. It analyzes mention trends, enriches them with market and news data and can send Discord alerts for unusual activity. | `bridge` | `http://[IP]:[PORT:80]` | [XML](https://fgrfn.github.io/unraid-templates/templates/RedditWSBCrawler/my-RedditWSBCrawler.xml) |
| [Scan2Target](https://github.com/fgrfn/Scan2Target) | Web-based scan server for USB and network scanners. Scan2Target discovers scanners and routes documents to file shares, mail, Paperless-ngx, webhooks and cloud providers. | `host` | `http://[IP]:8000` | [XML](https://fgrfn.github.io/unraid-templates/templates/Scan2Target/my-Scan2Target.xml) |

## Installation

### Add the complete template repository

In Unraid, open **Docker → Add Container → Template repositories** and add:

```text
https://github.com/fgrfn/unraid-templates
```

### Install a single template

Open **Docker → Add Container → Template repositories** and paste the XML URL from the table above or from the [template gallery](https://fgrfn.github.io/unraid-templates/).

### Install from the Unraid console

One line per template, run on the Unraid server. The template then appears in the template list under **Docker → Add Container**:

```bash
mkdir -p /boot/config/plugins/dockerMan/templates-user && wget -O /boot/config/plugins/dockerMan/templates-user/my-AdGuardHub.xml https://fgrfn.github.io/unraid-templates/templates/AdGuardHub/my-AdGuardHub.xml
```

The [template gallery](https://fgrfn.github.io/unraid-templates/) carries a ready-to-paste command for every template.

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
