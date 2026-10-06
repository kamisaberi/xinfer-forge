# Threat Categories Covered in the Golden Attacks Suite

The golden attack corpus spans four distinct tactical categories aligned with the **MITRE ATT&CK for ICS** and **Enterprise matrices**.

---

## 1. Tactical Coverage Breakdown

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ GOLDEN ATTACKS TAXONOMY (52 Threat Vectors)                 │
 └──────────────────────────────┬──────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
 ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
 │ 1. PHYSICAL   │       │ 2. RECON &    │       │ 3. ENTERPRISE │
 │ OT PROCESS    │       │ EXPLOITATION  │       │ COMMAND & CTRL│
 └───────┬───────┘       └───────┬───────┘       └───────┬───────┘
         │                       │                       │
         ▼                       ▼                       ▼
 • Modbus Overrides (T0855) • External Port Scans   • DNS Tunneling (T1071)
 • S7 Centrifuge (T0831)     (T1046)                • HTTPS C2 Beacons
 • Triton Safety (T0843)    • EternalBlue SMB Injection• Data Exfiltration
 • IEC 104 Breaker Trips      (T1210)                 (T1048)
```

---

## 2. Detailed Threat Specifications

### Category 1: Physical Process Sabotage (Industrial OT)
* **MITRE T0855 (Unauthorized Command Message):** Modbus Function Code 16 injections attempting to write illegal setpoints to pipeline safety valves.
* **MITRE T0843 (Program Download):** Triton TriStation firmware upload sequences intended to disable Safety Instrumented Systems (SIS).
* **MITRE T0831 (Manipulation of Control):** Stuxnet-style burst attacks targeting frequency drive parameters on Siemens S7-300 controllers.

### Category 2: Network Lateral Movement & Exploitation
* **MITRE T1210 (Exploitation of Remote Services):** EternalBlue (MS17-010) kernel pool grooming packet vectors over SMB port 445.
* **MITRE T1046 (Network Service Discovery):** Fast SYN port scans and distributed sweeps targeting industrial subnets.

### Category 3: Command & Control (C2) and Exfiltration
* **MITRE T1071.001 (Web Protocols):** Cobalt Strike, Sliver, and Metasploit malleable C2 HTTP/HTTPS beacon profiles.
* **MITRE T1048.003 (Exfiltration Over Unencrypted Protocol):** Automated bulk extraction of radiological DICOM PACS files over port 104.

