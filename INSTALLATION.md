# Installation

## Clone

```bash
git clone <repo-url>
cd abm
git submodule update --init
```

## Python package (`src/`)

Requires [uv](https://docs.astral.sh/uv/) and Python ≥ 3.13.

### Install

```bash
uv sync
```

This creates `.venv/` and installs `coop-disaster` (editable) plus all dependencies.

### Run

```bash
# Reproduce Fig 7 (serial, default 1000 groups × 200 rounds):
uv run coop-disaster

# Faster with parallel workers:
uv run coop-disaster --jobs 8

# Custom config:
uv run coop-disaster --n-groups 500 --n-rounds 100 --output out/fig7.png

# Skip plot, print results only:
uv run coop-disaster --no-plot

# Full options:
uv run coop-disaster --help
```

### Python API

```python
from coop_disaster import DEFAULT_CONFIG, run_sweep
from coop_disaster.plot import plot_fig7
from pathlib import Path

uc_props = [i / 100 for i in range(101)]
rates = run_sweep(uc_props, DEFAULT_CONFIG, n_jobs=4)
plot_fig7(uc_props, rates, Path("fig7.png"))
```

### Dev tools

```bash
uv run pytest          # tests (once added under tests/)
uv run black src/      # format
```

## Julia simulation (`julia_implementation/`)

Requires Julia 1.7+.

```bash
cd julia_implementation
julia --project=. -e 'using Pkg; Pkg.instantiate()'
julia --project=. --threads=auto scripts/fig7.jl
```
