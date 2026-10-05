# Command: stage

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


forge-cli stage: remote staging to Sentinel Nexus.

## Use

Push a verified ONNX plus manifest to the Nexus staging API.

## Result

SHADOW_MODE deployment with a tracking job id.

```bash
$ forge-cli stage --model models/v2.onnx --nexus-url http://10.240.0.10:9443
```

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
