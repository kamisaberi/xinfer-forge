# Nexus Staging Failures & REST API Troubleshooting

This guide resolves errors encountered when `forge-cli stage` dispatches compiled ONNX models to `sentinel-nexus` on port **9443**.

---

## 1. `Connection Refused` on Port 9443

### Symptom
```text
[-] Staging failed: requests.exceptions.ConnectionError: Failed to establish a new connection: [Errno 111] Connection refused
```

### Remediation
1. Verify that `sentinel-nexus` is running:
   ```bash
   sudo systemctl status sentinel-nexus
   ```
2. Verify that the management port is listening on the host:
   ```bash
   ss -tulpn | grep 9443
   ```
3. Check firewall rules:
   ```bash
   sudo ufw status | grep 9443
   ```

---

## 2. HTTP `401 Unauthorized` / JWT Expiration

### Symptom
```text
[-] Staging failed [401]: {"detail": "Signature has expired or token is invalid"}
```

### Remediation
The Bearer token stored in `/etc/sentinel/certs/nexus_token.jwt` has expired. Regenerate the local administrative token:

```bash
nexus-ctl auth refresh-token --output /etc/sentinel/certs/nexus_token.jwt
```

---

## 3. HTTP `422 Unprocessable Entity` (Schema / Hash Mismatch)

### Cause
The streaming SHA-256 digest calculated by `sentinel-nexus` does not match the checksum recorded in `network_threat_v2.manifest.json`.

### Remediation
Ensure the model was exported cleanly without intermediate disk truncation:

```bash
forge-cli export-onnx --checkpoint /tmp/candidate.pt --output-onnx /tmp/verified.onnx
forge-cli stage --onnx-model /tmp/verified.onnx --manifest /tmp/verified.manifest.json
```

