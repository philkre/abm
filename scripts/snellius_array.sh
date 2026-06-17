#!/bin/bash
# Array job for L=200 or large N: splits the Sobol sample across nodes.
# Each task handles (total_samples / n_tasks) parameter points.
# After all tasks finish, run `spatcoop analyse --phase linear --N 512` locally.
#SBATCH --job-name=spatcoop_array
#SBATCH --array=0-95
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=02:00:00
#SBATCH --partition=thin
#SBATCH --output=logs/%A_%a.out
#SBATCH --error=logs/%A_%a.err

module load Python/3.11.3-GCCcore-12.3.0
source "$HOME/.venvs/spatcoop/bin/activate"

python - <<'EOF'
import os
from spatcoop.sa import sample_params, run_batch, LINEAR_PROBLEM
from spatcoop.params import ModelParams

task_id = int(os.environ["SLURM_ARRAY_TASK_ID"])
n_tasks = 96   # must match --array=0-(n_tasks-1)
N       = 512  # 3072 total samples; each task handles 3072 // 96 = 32

base    = ModelParams(L=200, n_gens=1500, measure_window=200)
seeds   = list(range(50))

params_list, _ = sample_params(LINEAR_PROBLEM, N, base)
chunk = len(params_list) // n_tasks
lo    = task_id * chunk
hi    = lo + chunk if task_id < n_tasks - 1 else len(params_list)

print(f"Task {task_id}/{n_tasks}: processing params [{lo}:{hi}]")
run_batch(params_list[lo:hi], seeds, n_jobs=32)
print(f"Task {task_id} done.")
EOF
