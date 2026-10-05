# Cryptographic Hashing (SHA-256)

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


Generating checksum manifests to prevent in-flight tampering.

## Manifest

Hash plus byte size plus opset version, signed per release.

## Check

Nexus and appliances re-hash on receipt; mismatches abort.

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
