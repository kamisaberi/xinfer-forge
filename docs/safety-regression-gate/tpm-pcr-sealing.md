---

### File: `xinfer-forge/docs/safety-regression-gate/tpm-pcr-sealing.md`

```markdown
# TPM 2.0 PCR Sealing of the Golden Attack Corpus

To prevent adversaries with local root access from modifying `configs/safety/golden_attacks.yaml` to weaken the gate's checks, the corpus is cryptographically sealed against **TPM 2.0 Platform Configuration Register 7 (PCR 7)** and **PCR 14**.

---

## 1. Hardware Sealing Architecture

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ golden_attacks.yaml (52 Vectors)                            │
 └──────────────────────────────┬──────────────────────────────┘
                                │ Calculate SHA-256 Digest
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ Physical TPM 2.0 Silicon (/dev/tpmrm0)                      │
 │  - Sealed under PCR 7 (Secure Boot Policy) & PCR 14         │
 │  - Unseals validation key ONLY if firmware state is untampered
 └──────────────────────────────┬──────────────────────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼ Firmware Authentic                            ▼ Host Modified
 ┌─────────────────────────────┐         ┌─────────────────────────────┐
 │ TPM Releases Validation Key │         │ TPM Blocks Unsealing        │
 │ Safety Gate Arming Succeeded│         │ Forge Refuses to Execute    │
 └─────────────────────────────┘         └─────────────────────────────┘
```

---

## 2. Integrity Verification Command

Verify that the local golden attack corpus matches the hardware-sealed measurement:

```bash
forge-cli validate-safety --verify-tpm-seal
```

### Expected Output
```text
[*] Querying /dev/tpmrm0 for PCR 14 Golden Measurement...
[+] Hardware Sealed Hash : e9a2c31e847b2c94b13a7b41e2d90100...
[+] Local YAML File Hash : e9a2c31e847b2c94b13a7b41e2d90100...
[+] Status: GOLDEN ATTACK CORPUS IS IMMUTABLE AND AUTHENTICATED BY SILICON.
```
```

