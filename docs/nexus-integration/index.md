# Nexus Fleet Integration

`nexus_bridge.py` coordinates dataset discovery, auto-cycle triggers, and candidate staging with the `sentinel-nexus` command hub.

## Section Navigation

- [Nexus Bridge Architecture](./nexus-bridge-architecture.md): Architectural interaction model between Forge and Nexus.
- [Dataset Discovery Watcher](./dataset-discovery-watcher.md): Linux `inotify` kernel watcher loop monitoring `/var/lib/sentinel-nexus/forge_datasets/`.
- [Parsing Curated CSV Batches](./parsing-curated-csv-batches.md): Validating sidecar `.manifest.json` SHA-256 hashes and loading 32-dim float matrices.
- [Active Learning Uncertainty Gate](./active-learning-uncertainty-gate.md): Information entropy filtering selecting boundary cases ($0.40 \le f(x) \le 0.60$).
- [Automated Wrapper Script](./automated-wrapper-script.md): `deploy/run_nexus_adaptation.sh` production wrapper and systemd timer integration.
- [Closed-Loop Validation Testing](./closed-loop-validation-testing.md): Automated parity test verifying candidate models resolve edge cases without regression.
