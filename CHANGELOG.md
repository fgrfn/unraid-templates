# Changelog

## Unreleased

- Added the AdGuardHub template.
- Added the AliExpressCoinCollector template, with its icon served from this repository because the application's own repository is private.
- Fixed the RedditWSBCrawler template: it had no Port config and an empty `<WebUI>`, so the dashboard the application serves was unreachable. `WSB_AUTH_TOKEN` was hidden behind the advanced toggle although `WSB_HOST` is `0.0.0.0`, and the required `/app/config` volume is never used by the application.
- Rewrote the Scan2Target `<Requires>` note. It claimed host networking was required; a custom network such as `br0` or `br0.20` works too, and is the way out of a port conflict on 8000. The note now names the three conditions that decide it.
- Exposed four security-relevant Scan2Target settings the template did not offer: `SCAN2TARGET_JWT_SECRET` and `SCAN2TARGET_HA_API_KEY` (both masked), `SCAN2TARGET_ALLOW_PRIVATE_WEBHOOKS` and `SCAN2TARGET_CORS_ORIGINS`.
- Added a log volume for `/var/log/scan2target`. The template already pointed `SCAN2TARGET_LOG_DIR` there but never mounted it, so logs were lost whenever the container was recreated.
- Limited the gitleaks push trigger to `main`. A branch push, its pull request and the merge ran the scan three times per change, which is why it had 217 runs against validate's 93.
- Added a concurrency group to gitleaks so quick successive pushes cancel each other instead of queueing.
- Added `timeout-minutes` to the gitleaks and validate jobs; without it a hung job runs for the 360-minute default.
- Restricted the `_site` preview artifact to pull requests. On `main` the deploy publishes the real site.
- Added a ready-to-paste install command per template. The gallery shows it under "Install from the Unraid console" with a copy button, and the README documents the pattern. It writes the XML straight to `/boot/config/plugins/dockerMan/templates-user/`, so no manual file handling is needed.
- Linked the published GitHub Pages gallery from the README again. The link was dropped in 8839f3a when the README moved to the generator, so the site went unreferenced while still being built and deployed.
- Added `tests/test_generate.py`, covering the site link, the catalog listing and the rendered gallery.
- Bumped `actions/setup-python` from v6 to v7 across all three workflows that use it.
- Added `visibility: private` to catalog entries. The health check reports findings about a deliberately private project as notes rather than problems, while the image, the template URL and links hosted elsewhere stay hard checks.
- Marked `reddit-wsb-crawler` private; its GitHub project is not public, so its project, support, readme and icon links cannot resolve.
- Removed the TwitchDropsMiner template; its upstream repository no longer exists.
- Replaced the upstream drift check with `scripts/check-health.py`, which verifies that each template's container image, GitHub project and outbound URLs still resolve, and reports Compose drift for external entries only.
- Fixed Compose port and volume parsing: `${PORT:-8080}` was read as the container port `-8080}`.
- Replaced the daily drift pull request with a weekly run that maintains one tracking issue and closes it once every template is healthy again.
- Removed the AxeMobile, AxePoolStratum, Bootimus, Pluton and TwitchMinerGo templates; the catalog now covers first-party applications only.
- Removed the scheduled `twitch-miner-go` image build, which published a third-party project to this repository's registry.
- Derived the website network filter from the catalog instead of a hard-coded option list.
- Moved the repository notice into `catalog.yaml` so the generated README matches the committed one again.
- Removed BitaxeDiscordBot, Bambuddy and Netzbremse templates and their remaining assets.
- Added semantic template validation, automated tests and downloadable CI validation reports.
- Added `catalog.yaml` as the repository inventory.
- Replaced committed Pages output with an Actions deployment artifact.
- Replaced direct template mutation with review-only upstream drift pull requests.
- Added searchable and filterable GitHub Pages output.
- Standardized remaining template metadata and installation requirements.
