---

### File: `xinfer-forge/docs/safety-regression-gate/alert-dispatch-on-regression.md`

```markdown
# Alert Dispatch on Regression: CISO Escalation Protocol

A failure at the safety gate is treated as a suspected **Adversarial Data Poisoning Attack** rather than an ordinary training error. When the purge circuit fires, `xinfer-forge` dispatches high-priority incident notifications to the central fleet hub (`sentinel-nexus`).

---

## 1. Incident Escalation Sequence

```text
 [ Purge Circuit Fired in xinfer-forge ]
                    │
                    ▼ Dispatches HTTP POST /api/v1/alerts/poisoning
 ┌─────────────────────────────────────────────────────────────┐
 │ Sentinel-Nexus Fleet Command (Port 50051 / 9443)            │
 └──────────────────┬──────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
 ┌──────────────┐        ┌──────────────┐
 │ Web Console  │        │ SIEM Forward │
 │ Red Banner   │        │ (CEF / LEEF) │
 └──────────────┘        └──────┬───────┘
                                │
                                ▼
 [ Enterprise Security Operations Center (CISO Escalation) ]
```

---

## 2. Poisoning Alert Payload (`PoisoningIncident.json`)

```json
{
  "event_type": "ADVERSARIAL_POISONING_ATTEMPT",
  "appliance_id": "edge-substation-alpha",
  "timestamp_ns": 1791172800184000000,
  "failed_corpus_vectors": [
    {
      "attack_id": "ICS-T0855-INDUSTROYER2",
      "observed_mse": 0.0412,
      "required_threshold": 0.0820,
      "severity": "CRITICAL"
    }
  ],
  "mitigation_action": "CANDIDATE_WEIGHTS_PURGED",
  "batch_origin": "/var/lib/sentinel-nexus/forge_datasets/forge_dataset_8f1c.csv",
  "active_model_retained": "network_threat_v1.onnx"
}
```

The source CSV dataset that produced the poisoned weights is moved to `/var/lib/sentinel-nexus/quarantine/` for forensic review by threat intelligence analysts.
```

