# Deploying Forge Inside the `sentinel-matrix` VMware Mesh

This tutorial demonstrates how to configure and run `xinfer-forge` inside the encapsulated digital twin testbed (`sentinel-matrix`), assigning it static IP **`10.240.0.20`** on the isolated `10.240.0.0/24` subnet.

---

## 1. Container Topology (`10.240.0.0/24`)

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ VMware Hypervisor / Docker-in-VMware Virtual Bridge         │
 ├─────────────────────────────────────────────────────────────┤
 │ Nexus Hub Container       : 10.240.0.10 (gRPC 50051 / 9443) │
 │ Forge AI Trainer Container: 10.240.0.20 (Continual Daemon)  │
 │ Traffic Generator         : 10.240.0.50 (OmniFlow Engine)   │
 │ Red-Team Adversary        : 10.240.0.99 (Malware Replay)    │
 │ Edge Node Appliances      : 10.240.0.101 - 10.240.0.103     │
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. Docker Compose Configuration (`docker-compose.matrix.yml`)

Ensure the `forge` service is defined with the correct static IP and shared dataset volume:

```yaml
  forge:
    build:
      context: ../xinfer-forge
      dockerfile: Dockerfile
    container_name: sentinel-forge
    hostname: sentinel-forge
    networks:
      matrix_net:
        ipv4_address: 10.240.0.20
    volumes:
      - /opt/sentinel-matrix/shared/datasets:/var/lib/sentinel-nexus/forge_datasets
      - /opt/sentinel-matrix/shared/models:/var/lib/sentinel-nexus/models
      - /opt/sentinel-matrix/shared/certs:/etc/sentinel/certs:ro
    environment:
      - NEXUS_API_URL=https://10.240.0.10:9443
      - FORGE_DEVICE=cpu # Or cuda if NVIDIA container toolkit is mapped
      - LOG_LEVEL=INFO
    restart: always
```

---

## 3. Launching and Validating the Mesh

```bash
# 1. Bring up the simulation grid
cd /opt/sentinel-matrix
make up

# 2. Verify network connectivity from Forge to Nexus Hub
docker exec -it sentinel-forge nc -zv 10.240.0.10 9443
# Output: Connection to 10.240.0.10 9443 port [tcp/*] succeeded!

# 3. Follow Forge continual adaptation logs
docker logs -f sentinel-forge
```
