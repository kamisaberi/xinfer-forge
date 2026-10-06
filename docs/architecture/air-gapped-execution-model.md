# 100% Air-Gapped On-Premises Execution Model

In critical infrastructure and sovereign defense installations, security appliances must operate within completely air-gapped network enclaves without wide area network (WAN) or public cloud dependencies.

`xinfer-forge` enforces an **Air-Gapped Execution Model**, guaranteeing zero telemetry leakage and $\$0.00$ cloud egress costs.

---

## 1. Network Boundary Isolation

```text
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ SECURE ON-PREMISES PERIMETER                                                │
 │                                                                             │
 │  ┌─────────────────────────┐          ┌─────────────────────────┐           │
 │  │ blackbox-sentinel (OT)  │          │ sentinel-nexus (Hub)    │           │
 │  │ IP: 10.240.0.101        │          │ IP: 10.240.0.10         │           │
 │  └────────────┬────────────┘          └────────────┬────────────┘           │
 │               │                                    │                        │
 │               │ Internal Subnet: 10.240.0.0/24     │                        │
 │               └─────────────────┬──────────────────┘                        │
 │                                 │                                           │
 │                                 ▼                                           │
 │               ┌───────────────────────────────────┐                         │
 │               │ xinfer-forge Continual AI Daemon  │                         │
 │               │ IP: 10.240.0.20                   │                         │
 │               │ • Zero Internet Connectivity      │                         │
 │               │ • Local Pre-Seeded Dependencies   │                         │
 │               │ • Local NVMe Checkpoint Storage   │                         │
 │               └───────────────────────────────────┘                         │
 └─────────────────────────────────────────────────────────────────────────────┘
                                  ║
                                  ╫ PHYSICAL AIR-GAP (NO ROUTE TO WAN)
                                  ║
                          [ PUBLIC CLOUD ]
```

---

## 2. Air-Gapped Operational Invariants

1. **Pre-Seeded Python Environment:** The isolated virtual environment (`/opt/sentinel-stack/venv`) contains all necessary binary wheels (PyTorch, ONNX, NumPy, PyYAML). No outbound calls to `pypi.org` or GitHub occur during training cycles.
2. **Local Model Caching:** Checkpoints and compiled ONNX binaries are written directly to local storage (`/var/lib/sentinel-nexus/models/`) and distributed internally over isolated subnets (`10.240.0.0/24`).
3. **Data Sovereignty Compliance:** Meets EU NIS 2 Article 21 and NIST SP 800-171 data-handling mandates by keeping training telemetry within the physical plant perimeter.

