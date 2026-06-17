#!/bin/bash
# Single-node batch job for the linear-risk SA.
# Wall time: ~2h at L=150, N=512, 50 seeds, 32 CPUs.
#SBATCH --job-name=spatcoop_sa
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=04:00:00
#SBATCH --partition=thin
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

module load Python/3.11.3-GCCcore-12.3.0

# Activate the project venv created via uv
source "$HOME/.venvs/spatcoop/bin/activate"

python - <<'EOF'
from spatcoop.sa import run_sa, LINEAR_PROBLEM
from spatcoop.params import ModelParams

base  = ModelParams(L=150, n_gens=1500, measure_window=200)
seeds = list(range(50))
run_sa(LINEAR_PROBLEM, N=512, base_params=base, seeds=seeds, n_jobs=32)
print("SA complete.")
EOF
