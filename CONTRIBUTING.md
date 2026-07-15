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

## Upstream changes

The scheduled upstream check only creates a drift report in a draft pull request. Review every reported image, port, volume or environment change against the upstream documentation before editing a template.

## Pull requests

Keep changes focused, explain user-facing migration steps and include screenshots when the generated website changes visibly.
