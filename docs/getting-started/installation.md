# Package Installation & Virtual Environment Setup

To comply with modern Linux system package standards (PEP 668), `xinfer-forge` is installed within a dedicated, isolated virtual environment at `/opt/sentinel-stack/venv`.

---

## 1. Automatic Provisioning via `sentinel-stack`

If you are using the unified `sentinel-stack` meta-installer, `xinfer-forge` is compiled, installed, and symlinked automatically:

```bash
cd /opt/sentinel-stack
sudo ./install.sh --tier 4
```

---

## 2. Manual Installation Steps

To install `xinfer-forge` manually from source:

```bash
# 1. Install system prerequisites
sudo apt-get update && sudo apt-get install -y \
    python3-full \
    python3-venv \
    python3-pip \
    build-essential \
    git

# 2. Create the system-wide isolated virtual environment
sudo mkdir -p /opt/sentinel-stack
sudo python3 -m venv /opt/sentinel-stack/venv

# 3. Upgrade pip and core build tools
sudo /opt/sentinel-stack/venv/bin/pip install --upgrade pip setuptools wheel

# 4. Clone repository
git clone https://github.com/kamisaberi/xinfer-forge.git
cd xinfer-forge

# 5. Install package in editable or production mode
sudo /opt/sentinel-stack/venv/bin/pip install -r requirements.txt
sudo /opt/sentinel-stack/venv/bin/pip install .

# 6. Create system symlink for global CLI access
sudo ln -sf /opt/sentinel-stack/venv/bin/forge-cli /usr/local/bin/forge-cli
```

---

## 3. Verifying CLI Accessibility

Confirm that `forge-cli` is accessible globally:

```bash
forge-cli --version
```

### Expected Output
```text
xinfer-forge version 2.4.0 (Aryorithm Continual AI Engine)
```

