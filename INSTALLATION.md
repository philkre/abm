# Installation

## Clone

```bash
git clone <repo-url>
cd abm
git submodule update --init   # pulls src/condcoop (Jonsson & Jonsson well-mixed reference, used for validation)
```

## LLM instruction symlinks (Windows)

`CLAUDE.md` and `.github/copilot-instructions.md` are symlinks to `llm_hints/llm_instructions.md`. On macOS/Linux these resolve automatically. On Windows, Git does not create real symlinks by default, so the files may appear as text stubs containing the target path.

**Fix (run once, as Administrator or with Developer Mode enabled):**

```powershell
git config --global core.symlinks true

Remove-Item CLAUDE.md, .github\copilot-instructions.md -ErrorAction SilentlyContinue
New-Item -ItemType SymbolicLink -Path CLAUDE.md                      -Target llm_hints\llm_instructions.md
New-Item -ItemType SymbolicLink -Path .github\copilot-instructions.md -Target ..\llm_hints\llm_instructions.md
```

Alternatively, enable [Windows Developer Mode](https://learn.microsoft.com/en-us/windows/apps/get-started/enable-your-device-for-development) so symlink creation doesn't require elevation, then re-clone.

## Python package (`src/spatcoop/` — canonical)

Requires [uv](https://docs.astral.sh/uv/) and Python ≥ 3.13.

```bash
uv sync
```

This creates `.venv/` and installs `spatcoop` (editable) plus all dependencies (NumPy/Numba,
SALib, click, matplotlib, joblib, mesa, scienceplots).

**Windows note:** `uv sync` / `uv run` can fail behind a TLS-intercepting proxy. If so, use the
venv's Python directly instead of `uv run`, and set `PYTHONUTF8=1` to avoid codec errors on `β`/`η`
in CLI output:

```powershell
$env:PYTHONUTF8 = "1"
.venv\Scripts\python.exe -m spatcoop.cli <command>
```

### Run

```bash
# Single run (timeseries → results/figures/)
uv run spatcoop run-single --L 50 --n-gens 500 --seed 0

# Full command list
uv run spatcoop --help
uv run spatcoop sensitivity --help
```

Key commands: `run-single` (one episode), `run-batch` (checkpointed batch with seeds),
`sensitivity run`/`sensitivity analyse` (custom SA sweeps — see below), `param-sweep`,
`plot-ops`/`plot-sa`/`spectrum`/`snapshot-fields` (figures from saved results).

### Sensitivity analysis

The report's PAWN+Sobol' results are already committed (`results/sa/`); reproduce the figures in
seconds, or re-run from scratch, or resume the proposed extended design — exact commands in
[`scripts/SCRIPTS.md`](scripts/SCRIPTS.md).

### Tests

```bash
uv run pytest          # tests/ — model invariants, kernel equivalence, verification suite
uv run black src/      # format
```

## NetLogo (`netlogo/spatcoop_v2.nlogo`)

Interactive 1:1 replica of `src/spatcoop/model.py` with SA parameters as sliders and
Cooperative/Collapse phase presets. Open with the [NetLogo](https://ccl.northwestern.edu/netlogo/)
desktop app (6.4+); headless-run instructions are in `ABM/NetLogo/NETLOGO.md` in the parent course
workspace (outside this repo).

## Legacy / archived modules (`archive/`)

`coop_disaster` (well-mixed Jonsson & Jonsson replica), `spatial` (Mesa precursor to `spatcoop`),
the Julia implementation, and superseded exploratory scripts have been moved to `archive/` —
kept for provenance, not part of the active workflow. They are not covered by `pyproject.toml`'s
build/install path; treat them as reference code, not a supported entry point.
