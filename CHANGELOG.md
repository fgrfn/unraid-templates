# Changelog

## Unreleased

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
