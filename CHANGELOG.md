# Changelog

## Unreleased

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
