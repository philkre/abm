#!/usr/bin/env bash
# Set up the Python runtime needed by the coop-disaster ABM on Snellius.
#
# Run this ONCE on a Snellius login node (e.g. snellius.surf.nl). It does NOT
# run any simulations — those must be submitted through Slurm (sbatch), never
# on the login node. After this script finishes, .venv is ready and
# `uv run spatcoop` (or any other entry point) will work inside a Slurm job.
#
# What it does:
#   1. Loads the Snellius 2024 software stack. Attempts to load a Python 3.13
#      module; if unavailable, uv installs Python 3.13 automatically.
#      (pyproject.toml requires-python >=3.13)
#   2. Installs `uv` to ~/.local/bin if not already on PATH.
#   3. Runs `uv sync` to create .venv and install all dependencies from
#      uv.lock (mesa, numba, scipy, pandas, salib, ...).
#   4. Smoke-tests the venv by importing the core packages.
#
# Usage:
#   bash scripts/snellius_setup.sh
#
# Re-running is safe: module load is idempotent, uv install is skipped if
# already present, and `uv sync` only changes the venv when uv.lock has changed.

set -euo pipefail

############################################
# 0. sanity: are we on a Snellius login node?
############################################
HOSTNAME_SHORT="$(hostname -s)"
case "$HOSTNAME_SHORT" in
    int*|login*|tcn*|gcn*|hcn*|fcn*)
        echo "[setup] Host: $HOSTNAME_SHORT — looks like a Snellius node."
        ;;
    *)
        echo "[setup] Warning: host '$HOSTNAME_SHORT' does not match a typical"
        echo "        Snellius login pattern (int*/login*). Continue only if"
        echo "        you are sure this is the right machine."
        ;;
esac

if [[ "$HOSTNAME_SHORT" == tcn* || "$HOSTNAME_SHORT" == gcn* ]]; then
    echo "[setup] You appear to be on a COMPUTE node. This setup script is"
    echo "        meant for the LOGIN node. Submit it via Slurm only if you"
    echo "        know what you are doing."
fi

############################################
# 1. project root (script lives in scripts/)
############################################
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"
echo "[setup] Project root: $PROJECT_ROOT"

if [[ ! -f pyproject.toml ]]; then
    echo "[setup] ERROR: pyproject.toml not found in $PROJECT_ROOT" >&2
    exit 1
fi

############################################
# 2. load Snellius modules (Lmod)
############################################
# pyproject.toml requires Python >=3.13. Try to load it from the cluster
# module system; if the module is unavailable uv will install Python 3.13
# automatically in the next step.
echo "[setup] Loading modules from the 2024 Snellius stack ..."

# `module` is a shell function defined by /etc/profile.d/lmod.sh; make sure
# it is available even when this script is run with a non-interactive shell.
if ! command -v module >/dev/null 2>&1; then
    if [[ -f /etc/profile.d/lmod.sh ]]; then
        # shellcheck disable=SC1091
        source /etc/profile.d/lmod.sh
    elif [[ -f /usr/share/lmod/lmod/init/bash ]]; then
        # shellcheck disable=SC1091
        source /usr/share/lmod/lmod/init/bash
    else
        echo "[setup] WARNING: 'module' command not found; continuing without"
        echo "        Lmod. uv will manage Python 3.13 itself."
    fi
fi

if command -v module >/dev/null 2>&1; then
    module purge
    module load 2024
    # Try Python 3.13 from the 2024 stack. If the exact name has shifted, run
    # `module spider Python/3.13` on the login node and update the line below.
    if module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null; then
        echo "[setup] Loaded Python 3.13 from module system."
    else
        echo "[setup] Python 3.13 module not found in the 2024 stack."
        echo "        uv will install Python 3.13 automatically."
    fi

    echo "[setup] Loaded modules:"
    module list 2>&1 | sed 's/^/        /'
fi

############################################
# 3. install uv (user-local, no sudo)
############################################
export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
    echo "[setup] 'uv' not found — installing to ~/.local/bin via the"
    echo "        official installer (no sudo, no system changes)."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "[setup] uv already installed: $(uv --version)"
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "[setup] ERROR: uv installation appears to have failed." >&2
    exit 1
fi

############################################
# 4. ensure Python 3.13 is available
############################################
# If no Python 3.13 module was loaded above, let uv fetch it.
if ! python3 --version 2>&1 | grep -q "^Python 3\.13"; then
    echo "[setup] Python 3.13 not on PATH — asking uv to install it ..."
    uv python install 3.13
fi

PYTHON_BIN="$(uv python find 3.13)"
echo "[setup] Using Python: $PYTHON_BIN ($(${PYTHON_BIN} --version 2>&1))"

############################################
# 5. create .venv and install deps from uv.lock
############################################
echo "[setup] Running 'uv sync' (creates .venv, installs locked deps) ..."
uv sync --python "$PYTHON_BIN"

############################################
# 6. smoke test
############################################
echo "[setup] Verifying that core packages import cleanly ..."
uv run --python "$PYTHON_BIN" python - <<'PY'
import sys
print(f"python: {sys.version.split()[0]}")
import numpy, scipy, pandas, matplotlib, networkx
import mesa, numba, tqdm, click, salib
print(f"numpy:      {numpy.__version__}")
print(f"scipy:      {scipy.__version__}")
print(f"pandas:     {pandas.__version__}")
print(f"mesa:       {mesa.__version__}")
print(f"numba:      {numba.__version__}")
print(f"networkx:   {networkx.__version__}")
PY

############################################
# 7. create the logs directory
############################################
# Slurm opens logs/%j.out and logs/%j.err before the job script body runs,
# so the directory must exist at submission time, not inside the job script.
mkdir -p "$PROJECT_ROOT/logs"
echo "[setup] Created logs/ directory: $PROJECT_ROOT/logs"

echo
echo "[setup] Done. Next steps:"
echo "  - To use the venv interactively:  source .venv/bin/activate"
echo "  - To run a one-off command:       uv run spatcoop --help"
echo "  - Do NOT run simulations on the login node. Submit via Slurm (sbatch)."
