# Command: validate-safety

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


forge-cli validate-safety: standalone golden gate audit.

## Use

Audit any weights file against the sealed corpus on demand.

## Output

Per-category pass table plus the binary APPROVED verdict.

```bash
$ forge-cli validate-safety --weights candidate.pt \
    --safety-gate configs/safety/golden_attacks.yaml
```

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
