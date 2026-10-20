#!/usr/bin/env bash
# ==============================================================================
# ARYORITHM TECHNOLOGIES: FORGE-CLI SYSTEM REGISTRATION SCRIPT
# Registers forge-cli globally in /usr/local/bin using the Sentinel virtualenv.
# ==============================================================================
set -euo pipefail

GREEN='\033[32m'
CYAN='\033[36m'
YELLOW='\033[33m'
RED='\033[31m'
RESET='\033[0m'

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR] Please run this script with sudo: sudo bash $0${RESET}"
    exit 1
fi

# 1. Resolve xinfer-forge repository path
FORGE_DIR=""
for candidate in "/home/kami/xinfer-forge" "$(pwd)" "/opt/sentinel-stack/src/xinfer-forge"; do
    if [ -f "${candidate}/forge/cli.py" ]; then
        FORGE_DIR="${candidate}"
        break
    fi
done

if [ -z "${FORGE_DIR}" ]; then
    echo -e "${RED}[-] Error: Could not locate xinfer-forge repository with forge/cli.py.${RESET}"
    exit 1
fi

# 2. Resolve Python virtual environment path
VENV_DIR="/opt/sentinel-stack/venv"
if [ ! -d "${VENV_DIR}" ]; then
    echo -e "${YELLOW}[*] Creating Python virtual environment at ${VENV_DIR}...${RESET}"
    mkdir -p /opt/sentinel-stack
    python3 -m venv "${VENV_DIR}"
    "${VENV_DIR}/bin/pip" install --upgrade pip setuptools wheel
    "${VENV_DIR}/bin/pip" install --no-cache-dir numpy pyyaml torch onnx onnxruntime
fi

# 3. Create global executable wrapper in /usr/local/bin/forge-cli
WRAPPER_PATH="/usr/local/bin/forge-cli"

echo -e "${CYAN}[*] Registering forge-cli globally at ${WRAPPER_PATH}...${RESET}"

cat << EOF > "${WRAPPER_PATH}"
#!/usr/bin/env bash
# Auto-generated forge-cli wrapper
source "${VENV_DIR}/bin/activate"
export PYTHONPATH="${FORGE_DIR}:${FORGE_DIR}/src:${FORGE_DIR}/forge:\${PYTHONPATH:-}"
exec "${VENV_DIR}/bin/python3" -m forge.cli "\$@"
EOF

chmod +x "${WRAPPER_PATH}"

# 4. Verify Registration
echo -e "${YELLOW}[*] Testing registered forge-cli binary...${RESET}"
if "${WRAPPER_PATH}" --help > /dev/null 2>&1; then
    echo -e "${GREEN}[+] SUCCESS: forge-cli registered successfully!${RESET}"
    echo -e "    ├── Binary Path : ${WRAPPER_PATH}"
    echo -e "    ├── Forge Repo  : ${FORGE_DIR}"
    echo -e "    └── Python Venv : ${VENV_DIR}"
    echo -e "\nYou can now run 'forge-cli --help' from any terminal directory."
else
    echo -e "${RED}[-] Error: forge-cli registration failed test execution.${RESET}"
    exit 1
fi