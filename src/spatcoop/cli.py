"""Thin click CLI for spatcoop.

Commands:
    spatcoop run-single   Quick single run; prints summary to stdout.
    spatcoop run-batch    Full SA sample with checkpointing.
    spatcoop analyse      Print Sobol indices from saved results.
    spatcoop snapshot     Save strategy lattice snapshots for one run.
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
)


@click.group()
def cli():
    """spatcoop — spatial collective-risk flood ABM."""
    pass


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
@click.option("--phase", default="linear", type=click.Choice(["linear", "sigmoid"]), show_default=True)
@click.option("--N", default=64, type=int, show_default=True, help="Saltelli N; total samples = N*(k+2).")
@click.option("--L", default=150, type=int, show_default=True)
@click.option("--n-gens", default=1500, type=int, show_default=True)
@click.option("--n-seeds", default=50, type=int, show_default=True)
@click.option("--n-jobs", default=-1, type=int, show_default=True, help="-1 = all CPUs.")
@click.option("--task-id", default=None, type=int, help="SLURM array task index (0-based).")
@click.option("--n-tasks", default=None, type=int, help="Total number of SLURM array tasks.")
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
        click.echo(f"Array task {task_id}/{n_tasks}: params [{lo}:{hi}], L={l}, n_jobs={n_jobs}")
        run_batch(params_list[lo:hi], seeds, n_jobs=n_jobs)
    else:
        click.echo(f"Phase={phase}, N={n}, L={l}, n_gens={n_gens}, n_seeds={n_seeds}, n_jobs={n_jobs}")
        run_sa(problem, n, base, seeds, n_jobs=n_jobs)

    click.echo("Done.")


@cli.command("analyse")
@click.option("--phase", default="linear", type=click.Choice(["linear", "sigmoid"]), show_default=True)
@click.option("--N", default=64, type=int, show_default=True)
def analyse_cmd(phase, n):
    """Print Sobol S1 and ST from saved results/sa/sobol_*.json."""
    path = Path(f"results/sa/sobol_{phase}_N{n}.json")
    if not path.exists():
        raise click.ClickException(f"File not found: {path}. Run `spatcoop run-batch` first.")
    Si = json.loads(path.read_text())
    click.echo(f"\nSobol indices — {phase} risk, N={n}")
    click.echo(f"{'Parameter':>12}   {'S1':>8}   {'S1_CI':>8}   " f"{'ST':>8}   {'ST_CI':>8}")
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
@click.option("--snaps", default="500,1000,1500", help="Comma-separated list of generations to snapshot.")
def snapshot_cmd(l, p_max, seed, n_gens, snaps):
    """Save strategy lattice snapshots to results/figures/spatial_snapshot.pdf."""
    from spatcoop.plots import plot_spatial_snapshot

    snap_gens = [int(g) for g in snaps.split(",")]
    p = ModelParams(L=l, p_max=p_max, n_gens=n_gens)
    click.echo(f"Generating snapshots at gens {snap_gens}...")
    path = plot_spatial_snapshot(p, seed=seed, snap_gens=snap_gens)
    click.echo(f"Saved → {path}")


if __name__ == "__main__":
    cli()
