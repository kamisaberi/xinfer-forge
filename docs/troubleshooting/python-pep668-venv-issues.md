# Python PEP 668 venv Issues

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


Fixing Ubuntu 24.04/26.04 externally-managed-environment errors.

## Rule

Never --break-system-packages; use the managed venv.

## Fix

Recreate the venv if a stray global install poisoned resolution.

```bash
$ python3 -m venv /opt/sentinel-stack/venv
$ /opt/sentinel-stack/venv/bin/pip install torch onnx
```

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
