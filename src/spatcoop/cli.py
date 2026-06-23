"""Thin click CLI for spatcoop.

Commands:
    spatcoop run-single          Quick single run; prints summary to stdout.
    spatcoop run-batch           Full SA sample with checkpointing.
    spatcoop analyse             Print Sobol indices from saved results.
    spatcoop snapshot            Save strategy lattice snapshots for one run.
    spatcoop sensitivity run     Custom SA: arbitrary params, multiple output keys.
    spatcoop sensitivity analyse Re-print/recompute SA results from a saved run.
"""

from __future__ import annotations
import json
from dataclasses import asdict
from pathlib import Path

import click

from spatcoop.params import ModelParams, LINEAR, SIGMOID
from spatcoop.model import run_episode
from spatcoop.runner import save_result, run_batch
from spatcoop.sa import (
    run_sa,
    sample_params,
    LINEAR_PROBLEM,
    SIGMOID_PROBLEM,
    run_sa_custom,
    reanalyse_from_dir,
    VALID_OUTPUT_KEYS,
)

# ── Parse helpers for the sensitivity subcommands ────────────────────────────


def _parse_vary_spec(spec: str) -> tuple[str, float, float]:
    """Parse 'NAME:MIN:MAX' → (name, lo, hi)."""
    parts = spec.split(":")
    if len(parts) != 3:
        raise click.BadParameter(f"Expected NAME:MIN:MAX, got {spec!r}")
    name, lo_s, hi_s = parts
    try:
        return name, float(lo_s), float(hi_s)
    except ValueError:
        raise click.BadParameter(f"MIN and MAX must be numeric, got {spec!r}")


def _parse_fix_spec(spec: str) -> tuple[str, object]:
    """Parse 'NAME:VALUE' → (name, typed_value), casting to ModelParams field type."""
    parts = spec.split(":", 1)
    if len(parts) != 2:
        raise click.BadParameter(f"Expected NAME:VALUE, got {spec!r}")
    name, val_s = parts
    fields = ModelParams.__dataclass_fields__
    if name not in fields:
        raise click.BadParameter(
            f"Unknown parameter {name!r}. Run `spatcoop sensitivity run --help` for context."
        )
    ftype = fields[name].type
    if ftype is bool:
        val = val_s.lower() in ("1", "true", "yes")
    elif ftype is int:
        val = int(val_s)
    elif ftype is float:
        val = float(val_s)
    else:
        val = val_s
    return name, val


def _build_base_params(fix_specs: tuple[str, ...]) -> ModelParams:
    """Apply --fix overrides to a default ModelParams."""
    kw = asdict(ModelParams())
    for spec in fix_specs:
        name, val = _parse_fix_spec(spec)
        kw[name] = val
    return ModelParams(**kw)


def _print_sa_file(path: Path) -> None:
    """Pretty-print one SA result JSON file."""
    result = json.loads(path.read_text())
    method = result["method"]
    key = result["output_key"]
    names = result["problem"]["names"]

    click.echo(f"\n{'─'*60}")
    click.echo(f"  Output key : {key}")
    click.echo(
        f"  Method     : {method}  (N={result['N']}, samples={result['n_samples']}, seeds={result['n_seeds']})"
    )
    click.echo(f"{'─'*60}")

    if method == "sobol":
        click.echo(
            f"  {'Parameter':>14}  {'S1':>8}  {'S1_CI':>8}  {'ST':>8}  {'ST_CI':>8}"
        )
        click.echo("  " + "─" * 52)
        for i, name in enumerate(names):
            click.echo(
                f"  {name:>14}  {result['S1'][i]:8.3f}  {result['S1_conf'][i]:8.3f}"
                f"  {result['ST'][i]:8.3f}  {result['ST_conf'][i]:8.3f}"
            )
    elif method == "morris":
        click.echo(
            f"  {'Parameter':>14}  {'mu*':>8}  {'mu*_CI':>8}  {'sigma':>8}  {'mu':>8}"
        )
        click.echo("  " + "─" * 52)
        for i, name in enumerate(names):
            click.echo(
                f"  {name:>14}  {result['mu_star'][i]:8.3f}  {result['mu_star_conf'][i]:8.3f}"
                f"  {result['sigma'][i]:8.3f}  {result['mu'][i]:8.3f}"
            )


@click.group()
def cli():
    """spatcoop — spatial collective-risk flood ABM."""


# ── sensitivity command group ─────────────────────────────────────────────────


@cli.group("sensitivity")
def sensitivity_group():
    """Sensitivity analysis: arbitrary parameter ranges, multiple output metrics."""


@cli.command("run-single")
@click.option("--L", default=50, type=int, show_default=True)
@click.option("--p-max", default=0.5, type=float, show_default=True)
@click.option("--beta", default=2.0, type=float, show_default=True)
@click.option("--seed", default=42, type=int, show_default=True)
@click.option("--n-gens", default=1500, type=int, show_default=True)
@click.option("--eta", default=0.0, type=float, show_default=True)
@click.option("--save/--no-save", default=False, help="Save .npz checkpoint.")
def run_single(l, p_max, beta, seed, n_gens, eta, save):
    """Quick single run for development — prints summary."""
    p = ModelParams(L=l, p_max=p_max, beta=beta, n_gens=n_gens, eta=eta)
    click.echo(f"Running: L={l}, p_max={p_max}, β={beta}, η={eta}, seed={seed}")
    r = run_episode(p, seed, progress=True)
    click.echo("─" * 40)
    for k, v in r.summary.items():
        click.echo(f"  {k:20s}: {v:.4f}")
    if save:
        save_result(r)
        click.echo(f"Saved → results/raw/{p.hash()}_{seed:06d}.npz")


@cli.command("run-batch")
@click.option(
    "--phase",
    default="linear",
    type=click.Choice(["linear", "sigmoid"]),
    show_default=True,
)
@click.option(
    "--N",
    default=64,
    type=int,
    show_default=True,
    help="Saltelli N; total samples = N*(k+2).",
)
@click.option("--L", default=150, type=int, show_default=True)
@click.option("--n-gens", default=1500, type=int, show_default=True)
@click.option("--n-seeds", default=50, type=int, show_default=True)
@click.option(
    "--n-jobs", default=-1, type=int, show_default=True, help="-1 = all CPUs."
)
@click.option(
    "--task-id", default=None, type=int, help="SLURM array task index (0-based)."
)
@click.option(
    "--n-tasks", default=None, type=int, help="Total number of SLURM array tasks."
)
def run_batch_cmd(phase, n, l, n_gens, n_seeds, n_jobs, task_id, n_tasks):
    """Run the full SA sample with checkpointing.

    When --task-id and --n-tasks are given, only the corresponding chunk of the
    Saltelli sample is processed (for SLURM array jobs).
    """
    from spatcoop.runner import run_batch

    problem = LINEAR_PROBLEM if phase == "linear" else SIGMOID_PROBLEM
    base = ModelParams(
        L=l,
        n_gens=n_gens,
        risk_mode=SIGMOID if phase == "sigmoid" else LINEAR,
    )
    seeds = list(range(n_seeds))

    if task_id is not None and n_tasks is not None:
        # Array mode: slice the Saltelli sample for this task
        params_list, _ = sample_params(problem, n, base)
        chunk = len(params_list) // n_tasks
        lo = task_id * chunk
        hi = lo + chunk if task_id < n_tasks - 1 else len(params_list)
        click.echo(
            f"Array task {task_id}/{n_tasks}: params [{lo}:{hi}], L={l}, n_jobs={n_jobs}"
        )
        run_batch(params_list[lo:hi], seeds, n_jobs=n_jobs)
    else:
        click.echo(
            f"Phase={phase}, N={n}, L={l}, n_gens={n_gens}, n_seeds={n_seeds}, n_jobs={n_jobs}"
        )
        run_sa(problem, n, base, seeds, n_jobs=n_jobs)

    click.echo("Done.")


@cli.command("analyse")
@click.option(
    "--phase",
    default="linear",
    type=click.Choice(["linear", "sigmoid"]),
    show_default=True,
)
@click.option("--N", default=64, type=int, show_default=True)
def analyse_cmd(phase, n):
    """Print Sobol S1 and ST from saved results/sa/sobol_*.json."""
    path = Path(f"results/sa/sobol_{phase}_N{n}.json")
    if not path.exists():
        raise click.ClickException(
            f"File not found: {path}. Run `spatcoop run-batch` first."
        )
    Si = json.loads(path.read_text())
    click.echo(f"\nSobol indices — {phase} risk, N={n}")
    click.echo(
        f"{'Parameter':>12}   {'S1':>8}   {'S1_CI':>8}   " f"{'ST':>8}   {'ST_CI':>8}"
    )
    click.echo("─" * 58)
    for i, name in enumerate(Si["names"]):
        click.echo(
            f"{name:>12}   {Si['S1'][i]:8.3f}   {Si['S1_conf'][i]:8.3f}   "
            f"{Si['ST'][i]:8.3f}   {Si['ST_conf'][i]:8.3f}"
        )


@cli.command("snapshot")
@click.option("--L", default=50, type=int, show_default=True)
@click.option("--p-max", default=0.5, type=float, show_default=True)
@click.option("--seed", default=0, type=int, show_default=True)
@click.option("--n-gens", default=1500, type=int, show_default=True)
@click.option(
    "--snaps",
    default="500,1000,1500",
    help="Comma-separated list of generations to snapshot.",
)
def snapshot_cmd(l, p_max, seed, n_gens, snaps):
    """Save strategy lattice snapshots to results/figures/spatial_snapshot.pdf."""
    from spatcoop.plots import plot_spatial_snapshot

    snap_gens = [int(g) for g in snaps.split(",")]
    p = ModelParams(L=l, p_max=p_max, n_gens=n_gens)
    click.echo(f"Generating snapshots at gens {snap_gens}...")
    path = plot_spatial_snapshot(p, seed=seed, snap_gens=snap_gens)
    click.echo(f"Saved → {path}")


@sensitivity_group.command("run")
@click.option(
    "--vary",
    "vary_specs",
    multiple=True,
    required=True,
    metavar="NAME:MIN:MAX",
    help=(
        "Parameter to vary, with range. Repeat for multiple parameters. "
        "E.g. --vary beta:0.1:10.0 --vary T_over_E:0.4:0.9"
    ),
)
@click.option(
    "--fix",
    "fix_specs",
    multiple=True,
    metavar="NAME:VALUE",
    help="Override a base parameter (e.g. --fix L:100 --fix eta:0.1). Repeat as needed.",
)
@click.option(
    "--output-key",
    "output_keys",
    multiple=True,
    default=("resilience",),
    show_default=True,
    help=(
        f"Output metric to analyse. Repeat for multiple. "
        f"Valid: {', '.join(sorted(VALID_OUTPUT_KEYS))}"
    ),
)
@click.option(
    "--method",
    default="sobol",
    type=click.Choice(["sobol", "morris"]),
    show_default=True,
    help="Sobol: Saltelli design, O(N*(k+2)) runs. Morris: trajectory design, O(N*(k+1)) runs.",
)
@click.option(
    "--N",
    default=32,
    type=int,
    show_default=True,
    help="Base sample size N. For Sobol: total = N*(k+2); Morris: N*(k+1).",
)
@click.option(
    "--n-seeds",
    default=20,
    type=int,
    show_default=True,
    help="Number of random seeds per parameter point.",
)
@click.option(
    "--n-jobs",
    default=-1,
    type=int,
    show_default=True,
    help="Joblib parallel workers (-1 = all CPUs).",
)
@click.option(
    "--out-dir",
    default="results/sa/custom",
    type=click.Path(),
    show_default=True,
    help="Directory for run_config.json, sample_X.npy, and per-key result files.",
)
@click.option(
    "--task-id",
    default=None,
    type=int,
    help="SLURM array task index (0-based). Simulates only the corresponding slice.",
)
@click.option(
    "--n-tasks",
    default=None,
    type=int,
    help="Total SLURM array tasks. Required when --task-id is set.",
)
def sensitivity_run(
    vary_specs,
    fix_specs,
    output_keys,
    method,
    n,
    n_seeds,
    n_jobs,
    out_dir,
    task_id,
    n_tasks,
):
    """Run a custom sensitivity analysis sweep.

    Each output key gets its own result file: {out_dir}/{method}_{key}.json
    Simulations are checkpointed — re-running skips already-computed results.

    SLURM array jobs: pass --task-id $SLURM_ARRAY_TASK_ID and --n-tasks to
    distribute the sample across nodes. Run `sensitivity analyse --recompute`
    once all tasks finish.

    Example:

      spatcoop sensitivity run \\

        --vary beta:0.1:10.0 --vary p_max:0.0:1.0 \\

        --fix L:100 --fix eta:0.05 \\

        --output-key resilience --output-key n_UC \\

        --method sobol --N 32 --n-seeds 20

    """
    if (task_id is None) != (n_tasks is None):
        raise click.ClickException("--task-id and --n-tasks must be set together.")

    # Parse and validate inputs
    try:
        parsed_vary = [_parse_vary_spec(s) for s in vary_specs]
    except click.BadParameter as e:
        raise click.ClickException(str(e))

    for key in output_keys:
        if key not in VALID_OUTPUT_KEYS:
            raise click.ClickException(
                f"Unknown output key {key!r}. Valid: {', '.join(sorted(VALID_OUTPUT_KEYS))}"
            )

    try:
        base_params = _build_base_params(fix_specs)
    except click.BadParameter as e:
        raise click.ClickException(str(e))

    seeds = list(range(n_seeds))
    run_sa_custom(
        vary_specs=parsed_vary,
        N=n,
        base_params=base_params,
        seeds=seeds,
        output_keys=list(output_keys),
        method=method,
        n_jobs=n_jobs,
        out_dir=Path(out_dir),
        task_id=task_id,
        n_tasks=n_tasks,
    )


@sensitivity_group.command("analyse")
@click.option(
    "--out-dir",
    required=True,
    type=click.Path(exists=True),
    help="Directory containing run_config.json from a previous `sensitivity run`.",
)
@click.option(
    "--output-key",
    "output_keys",
    multiple=True,
    default=(),
    help="Restrict to these keys (default: all keys in run_config.json).",
)
@click.option(
    "--recompute/--no-recompute",
    default=False,
    help="Reload results from disk and recompute indices before printing.",
)
def sensitivity_analyse(out_dir, output_keys, recompute):
    """Print SA indices from a saved sensitivity run.

    By default, reads already-saved {method}_{key}.json files.
    Pass --recompute to reload simulation results from disk and recompute indices
    (useful after adding new seeds or to analyse additional output keys).
    """
    out_dir_path = Path(out_dir)

    if recompute:
        keys = list(output_keys) if output_keys else None
        reanalyse_from_dir(out_dir_path, output_keys=keys)

    # Discover result files to print
    config_path = out_dir_path / "run_config.json"
    if config_path.exists():
        config = json.loads(config_path.read_text())
        method = config["method"]
        keys_to_print = list(output_keys) if output_keys else config["output_keys"]
        result_files = [out_dir_path / f"{method}_{k}.json" for k in keys_to_print]
    else:
        # Fall back: print all *.json files except run_config.json
        result_files = [
            p
            for p in sorted(out_dir_path.glob("*.json"))
            if p.name != "run_config.json"
        ]

    missing = [p for p in result_files if not p.exists()]
    if missing:
        raise click.ClickException(
            f"Missing result files: {[str(m) for m in missing]}. "
            "Run `spatcoop sensitivity run` first, or pass --recompute."
        )

    for path in result_files:
        _print_sa_file(path)
    click.echo()


if __name__ == "__main__":
    cli()
