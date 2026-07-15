# fgrfn Unraid Templates

[![Validate Templates](https://github.com/fgrfn/unraid-templates/actions/workflows/validate-templates.yml/badge.svg)](https://github.com/fgrfn/unraid-templates/actions/workflows/validate-templates.yml)
[![Deploy Pages](https://github.com/fgrfn/unraid-templates/actions/workflows/deploy.yml/badge.svg)](https://github.com/fgrfn/unraid-templates/actions/workflows/deploy.yml)
[![Upstream Drift](https://github.com/fgrfn/unraid-templates/actions/workflows/upstream-drift.yml/badge.svg)](https://github.com/fgrfn/unraid-templates/actions/workflows/upstream-drift.yml)

Curated Docker templates for Unraid. The catalog currently contains **9 templates**.

## Available templates

| Template | Description | Network | Web UI | Install |
|---|---|---|---|---|
| [AxeMobile](https://github.com/IsSasoriDev/AxeMobile) | AxeMobile is a dashboard for monitoring and managing Bitaxe and NerdAxe Bitcoin miners. It provides live hashrate, temperature and power data, network discovery, performance presets, firmware updates, Bitcoin network statistics and a mining calculator. | `axemobile` | `http://[IP]:[PORT:3847]` | [XML](https://fgrfn.github.io/unraid-templates/templates/AxeMobile/my-AxeMobile.xml) |
| [AxePoolStratum](https://github.com/IsSasoriDev/AxeMobile) | AxePoolStratum is the companion stratum server for AxeMobile. It connects Bitaxe and NerdAxe miners to a Bitcoin node and exposes mining statistics to the AxeMobile dashboard. | `axemobile` | `Headless` | [XML](https://fgrfn.github.io/unraid-templates/templates/AxeMobile/my-AxePoolStratum.xml) |
| [Bootimus](https://github.com/garybowers/bootimus) | Modern PXE and HTTP boot server with embedded iPXE bootloaders, SQLite support and a web administration interface. It includes distributions, diagnostics, per-client access control, authentication, hardware inventory and boot logs. | `bridge` | `http://[IP]:[PORT:8081]` | [XML](https://fgrfn.github.io/unraid-templates/templates/Bootimus/my-Bootimus.xml) |
| [HashHive](https://github.com/fgrfn/hashhive) | Unified mining dashboard for NMMiner, Bitaxe and NerdAxe devices. It provides live statistics, device configuration, pool management, alerting and notifications through Telegram, Discord or Gotify. | `bridge` | `http://[IP]:[PORT:8000]` | [XML](https://fgrfn.github.io/unraid-templates/templates/HashHive/my-HashHive.xml) |
| [Pluton](https://github.com/plutonhq/pluton) | Self-hosted backup management platform based on Restic and Rclone. Pluton provides encrypted incremental backups, replication, retention schedules, restore workflows, notifications, retries and event scripts through a web interface. | `bridge` | `http://[IP]:[PORT:5173]` | [XML](https://fgrfn.github.io/unraid-templates/templates/Pluton/my-Pluton.xml) |
| [RedditWSBCrawler](https://github.com/fgrfn/reddit-wsb-crawler) | Early-warning crawler for stock-ticker activity on Reddit. It analyzes mention trends, enriches them with market and news data and can send Discord alerts for unusual activity. | `bridge` | `Headless` | [XML](https://fgrfn.github.io/unraid-templates/templates/RedditWSBCrawler/my-RedditWSBCrawler.xml) |
| [Scan2Target](https://github.com/fgrfn/Scan2Target) | Web-based scan server for USB and network scanners. Scan2Target discovers scanners and routes documents to file shares, mail, Paperless-ngx, webhooks and cloud providers. | `host` | `http://[IP]:8000` | [XML](https://fgrfn.github.io/unraid-templates/templates/Scan2Target/my-Scan2Target.xml) |
| [TwitchDropsMiner](https://github.com/fgrfn/TwitchDropsMiner) | Twitch Drops Miner farms eligible Twitch drops without keeping a stream open. It discovers campaigns, changes channels automatically, persists OAuth state and offers webhook notifications and a web interface. | `bridge` | `http://[IP]:[PORT:8080]` | [XML](https://fgrfn.github.io/unraid-templates/templates/TwitchDropsMiner/my-TwitchDropsMiner.xml) |
| [TwitchMinerGo](https://github.com/Guliveer/twitch-miner-go) | Resource-efficient Twitch channel-points miner written in Go. It supports multiple accounts, predictions, drops, raids, notifications and an analytics web interface. | `bridge` | `http://[IP]:[PORT:8080]` | [XML](https://fgrfn.github.io/unraid-templates/templates/TwitchMinerGo/my-TwitchMinerGo.xml) |

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

Upstream monitoring creates or updates a **draft pull request containing a drift report**. It never modifies production templates or pushes directly to `main`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). New templates must be added to `catalog.yaml`, pass semantic validation and include clear security and networking requirements.

## License

Template repository code and metadata are available under the [MIT License](LICENSE). Upstream applications retain their own licenses.
