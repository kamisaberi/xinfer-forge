# Installation

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


Package setup and the PEP 668 isolated environment at /opt/sentinel-stack/venv.

## Venv

One managed environment per host; forge-cli wraps it for global terminal access.

## Verify

forge-cli --help plus the smoke adaptation below prove the install.

```bash
python3 -m venv /opt/sentinel-stack/venv
/opt/sentinel-stack/venv/bin/pip install torch onnx pyyaml
forge-cli --help
```

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
