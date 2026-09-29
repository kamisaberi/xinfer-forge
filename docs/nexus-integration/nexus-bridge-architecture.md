### Part 6: Nexus Fleet Integration (`nexus-integration/*`)

This section contains 6 technical implementation guides detailing the bidirectional bridge between `xinfer-forge` and `sentinel-nexus`: the bridge service architecture, inotify dataset discovery, CSV batch parsing, active learning uncertainty gating, the autonomous wrapper execution script, and closed-loop validation verification.

---

### File: `xinfer-forge/docs/nexus-integration/nexus-bridge-architecture.md`

```markdown
# Nexus Bridge Architecture (`forge/nexus_bridge.py`)

`nexus_bridge.py` operates as an internal communication client within `xinfer-forge`. It coordinates filesystem discovery of newly curated datasets written by `sentinel-nexus` (`DatasetCurator.cpp`), submits candidate artifacts to the fleet staging API, and monitors canary rollout progression.

---

## 1. Architectural Interaction Model

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ Sentinel-Nexus Hub (Tier 6 Command Plane)                   │
 │  - DatasetCurator.cpp writes curated datasets to disk       │
 │  - Exposes REST API on Port 9443 (/api/v1/ota/stage)        │
 └──────────────────────▲──────────────────────────────┬───────┘
                        │                              │
         POST /ota/stage│                              │ Emits Batches to:
         Artifact Staging│                              │ /var/lib/sentinel-nexus/
                        │                              │ forge_datasets/
                        │                              ▼
 ┌──────────────────────┴──────────────────────────────────────┐
 │ xinfer-forge: nexus_bridge.py Subsystem                     │
 ├─────────────────────────────────────────────────────────────┤
 │ 1. Inotify Watcher : Traps IN_CLOSE_WRITE on new CSVs       │
 │ 2. Batch Validator : Checks SHA-256 in .manifest.json       │
 │ 3. Dispatcher      : Triggers forge-cli training pipeline   │
 │ 4. REST Stager     : Transmits network_threat_v2.onnx to Hub│
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. Invariants & Resiliency

1. **Atomic File Ingestion:** The bridge ignores partial writes by reacting only to the Linux kernel `IN_CLOSE_WRITE` inotify event.
2. **Crash Resilience:** If `nexus_bridge.py` restarts mid-adaptation, it checks for `.lock` state files to avoid duplicate training passes over the same dataset.
3. **Decoupled Failure Domains:** If the Nexus HTTP endpoint is unreachable, the compiled ONNX model remains cached locally on disk ready for deferred transmission.
```

