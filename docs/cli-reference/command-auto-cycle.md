# Command: auto-cycle

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


forge-cli auto-cycle: autonomous infinite adaptation loop.

## Use

One command runs discover → train → gate → export → stage forever.

## Safety

Ctrl+C drains gracefully; partial cycles never stage.

```bash
$ forge-cli auto-cycle --nexus-url http://10.240.0.10:9443 \
    --dataset-dir /var/lib/sentinel-nexus/forge_datasets
```

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
