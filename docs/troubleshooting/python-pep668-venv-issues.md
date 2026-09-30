---

### File: `xinfer-forge/docs/troubleshooting/python-pep668-venv-issues.md`

```markdown
# Resolving Python PEP 668 Virtual Environment Issues

On modern Linux distributions (such as **Ubuntu 24.04 LTS and Ubuntu 26.04**), running `pip install` globally results in a system block:

```text
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
```

---

## 1. Architectural Solution: Isolated Virtualenv

`xinfer-forge` complies strictly with PEP 668 by isolating all Python runtimes, Torch dependencies, and ONNX binaries within **`/opt/sentinel-stack/venv`**.

Do **not** pass `--break-system-packages`, as this risks destabilizing system APT packages.

---

## 2. Rebuilding the Isolated Environment

If the virtual environment becomes corrupted:

```bash
# 1. Purge corrupted environment
sudo rm -rf /opt/sentinel-stack/venv

# 2. Re-create clean virtual environment
sudo python3 -m venv /opt/sentinel-stack/venv

# 3. Upgrade pip wheel tools
sudo /opt/sentinel-stack/venv/bin/pip install --upgrade pip setuptools wheel

# 4. Reinstall forge package
cd /opt/sentinel-stack/xinfer-forge
sudo /opt/sentinel-stack/venv/bin/pip install -r requirements.txt
sudo /opt/sentinel-stack/venv/bin/pip install -e .

# 5. Restore global symlink
sudo ln -sf /opt/sentinel-stack/venv/bin/forge-cli /usr/local/bin/forge-cli
```

---

## 3. Verifying Symlink Resolution

```bash
which forge-cli
# Expected: /usr/local/bin/forge-cli

head -n 1 /usr/local/bin/forge-cli
# Expected: #!/opt/sentinel-stack/venv/bin/python3
```
```

