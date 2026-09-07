# Contributing

## Adding or changing a template

1. Start from `templates/blank-template.xml`.
2. Store the template below `templates/<Application>/my-<Application>.xml`.
3. Add exactly one matching entry to `catalog.yaml`.
4. Describe special network, device, capability and security requirements in `<Requires>`.
5. Keep `<DateInstalled />` empty and set a direct HTTPS `<TemplateURL>`.
6. Mark credentials and webhook URLs with `Mask="true"`.
7. Run the checks below.

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate-templates.py
pytest
python scripts/generate.py --write-readme
python scripts/generate.py --check-readme
python scripts/generate.py --output _site
```

Generated website files must not be committed. GitHub Pages is deployed from an Actions artifact.

## Template health

`scripts/check-health.py` runs weekly and is review-only; it never edits a template. It reports when a container image has disappeared from its registry, when a GitHub project is gone or archived, and when any URL a template hands to Unraid stops responding. Findings collect in a single tracking issue that closes itself once the next run is clean.

For entries marked `ownership: external` it additionally compares the upstream Compose service against the template and reports image, port, volume and environment differences. Review each one against the upstream documentation before editing a template. First-party entries are skipped deliberately: their Compose file is a development artifact rather than a published contract, so comparing it reports noise.

Run it locally with:

```bash
python scripts/check-health.py --output reports/template-health.md
```

## Pull requests

Keep changes focused, explain user-facing migration steps and include screenshots when the generated website changes visibly.
