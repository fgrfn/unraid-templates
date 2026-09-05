# Upstream template drift report

Generated: 2026-09-05T06:55:53.013716+00:00

This report is review-only. No template fields are changed automatically.

## bootimus

Compose service: `bootimus`

- Environment variables added upstream: `BOOTIMUS_DB_HOST`, `BOOTIMUS_DB_NAME`, `BOOTIMUS_DB_PASSWORD`, `BOOTIMUS_DB_PORT`, `BOOTIMUS_DB_SSLMODE`, `BOOTIMUS_DB_USER`
- Environment variables only in template: `BOOTIMUS_SERVER_ADDR`

## hashhive

No differences detected for Compose service `hashhive`.

## pluton

Compose service: `pluton`

- Environment variables added upstream: `IS_DOCKER`, `NODE_ENV`
- Container ports added upstream: `-5173}`
- Container ports only in template: `5173`
- Container volumes only in template: `/backup-source`, `/restore`

## reddit-wsb-crawler

Compose service: `wsb-crawler`

- Image: `ghcr.io/fgrfn/reddit-wsb-crawler:latest` → `wsb-crawler:${VERSION:-local}`
- Environment variables only in template: `ALERT_COOLDOWN_H`, `ALERT_MAX_PER_RUN`, `ALERT_MIN_ABS`, `ALERT_MIN_DELTA`, `ALERT_MIN_PRICE_MOVE`, `ALERT_RATIO`, `ALPHAVANTAGE_API_KEY`, `CRAWLER_LOOP_MODE`, `CRAWL_INTERVAL_MINUTES`, `DISCORD_STATUS_UPDATE`, `DISCORD_WEBHOOK_URL`, `NEWSAPI_KEY`, `NEWSAPI_LANG`, `NEWSAPI_WINDOW_HOURS`, `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`, `SUBREDDITS`
- Container ports added upstream: `-80}`
- Container volumes only in template: `/app/config`

## scan2target

Compose service: `scan2target`

- Image: `ghcr.io/fgrfn/scan2target:latest` → `scan2target:latest`
- Environment variables added upstream: `SCAN2TARGET_ALLOW_PRIVATE_WEBHOOKS`, `SCAN2TARGET_CORS_ORIGINS`, `SCAN2TARGET_DELIVERY_MAX_RETRIES`, `SCAN2TARGET_HA_API_KEY`, `SCAN2TARGET_JWT_SECRET`, `SCAN2TARGET_MAX_BATCH_PAGES`, `SCAN2TARGET_MAX_BATCH_PAGE_MB`, `SCAN2TARGET_MAX_REQUEST_SIZE_MB`, `SCAN2TARGET_RETRY_BASE_DELAY`, `SCAN2TARGET_RETRY_MAX_DELAY`, `SCAN2TARGET_RETRY_POLL_INTERVAL`, `SCAN2TARGET_SCAN_SESSION_TTL_HOURS`
- Container volumes added upstream: `/var/log/scan2target`
- Container volumes only in template: `/dev/bus/usb`

## twitch-drops-miner

⚠️ Upstream check failed: `404 Client Error: Not Found for url: https://raw.githubusercontent.com/fgrfn/TwitchDropsMiner/main/docker-compose.yml`

## twitch-miner-go

Compose service: `twitch-miner-go`

- Image: `ghcr.io/fgrfn/twitch-miner-go:latest` → `${TWITCH_MINER_IMAGE:-ghcr.io/guliveer/twitch-miner-go:latest}`
- Environment variables only in template: `LOG_LEVEL`
