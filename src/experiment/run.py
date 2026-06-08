"""Run all five treatments and plot mean contribution over rounds.

Replicates the structure of Figs 3-5 from Jonsson & Jonsson (2025):
round-by-round mean contribution across many independent sessions per treatment.

Usage:
    uv run experiment-run
    uv run experiment-run --n-sessions 500 --output contributions.png
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from experiment.config import (
    DEFAULT_AGENT_CONFIG,
    AgentConfig,
    TreatmentConfig,
    TREATMENTS,
)
from experiment.model import ExperimentModel


# ── Simulation ─────────────────────────────────────────────────────────────


def run_sessions(
    treatment: TreatmentConfig,
    agent_cfg: AgentConfig = DEFAULT_AGENT_CONFIG,
    n_sessions: int = 200,
    base_seed: int = 42,
) -> pd.DataFrame:
    """Run n_sessions independent sessions and return round-by-round mean metrics.

    Args:
        treatment: Treatment configuration.
        agent_cfg: Aspiration learning parameters.
        n_sessions: Number of independent group sessions to average over.
        base_seed: Base RNG seed; each session uses base_seed + session_index.

    Returns:
        DataFrame indexed by round (0 = initial state) with columns:
        mean_contribution, group_pot, disaster_rate, mean_wealth, mean_aspiration.
        Values are averaged across all sessions.
    """
    all_dfs: list[pd.DataFrame] = []
    for i in range(n_sessions):
        model = ExperimentModel(treatment, agent_cfg, seed=base_seed + i)
        model.run()
        df = model.datacollector.get_model_vars_dataframe()
        all_dfs.append(df)

    # Stack and average across sessions
    stacked = pd.concat(all_dfs)
    return stacked.groupby(stacked.index).mean()


def run_all_treatments(
    agent_cfg: AgentConfig = DEFAULT_AGENT_CONFIG,
    n_sessions: int = 200,
    base_seed: int = 42,
) -> dict[str, pd.DataFrame]:
    """Run all five treatments. Returns {treatment_name: DataFrame}."""
    results: dict[str, pd.DataFrame] = {}
    for name, treatment in TREATMENTS.items():
        t0 = time.perf_counter()
        results[name] = run_sessions(treatment, agent_cfg, n_sessions, base_seed)
        elapsed = time.perf_counter() - t0
        final_contrib = results[name]["mean_contribution"].iloc[-1]
        print(f"  {name:8s}  final contribution={final_contrib:.2f}  ({elapsed:.2f}s)")
    return results


# ── Plotting ────────────────────────────────────────────────────────────────

# Match paper's treatment colours roughly
_COLOURS = {
    "Control": "grey",
    "10P": "steelblue",
    "40P": "darkorange",
    "Level": "forestgreen",
    "Impact": "crimson",
}


def plot_results(
    results: dict[str, pd.DataFrame],
    output: Path,
) -> None:
    """Plot mean contribution and disaster rate over rounds for all treatments."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)

    for name, df in results.items():
        rounds = df.index
        colour = _COLOURS.get(name, "black")
        ax1.plot(rounds, df["mean_contribution"], label=name, color=colour, lw=2)
        ax2.plot(rounds, df["disaster_rate"], label=name, color=colour, lw=2)

    ax1.axhline(15.0, color="black", lw=1, ls="--", label="threshold/group_size (15)")
    ax1.set_ylabel("Mean contribution (MU)")
    ax1.set_ylim(0, 20)
    ax1.legend(loc="upper right", fontsize=9)
    ax1.set_title("Experiment ABM — aspiration learning across treatments")

    ax2.set_ylabel("Disaster rate")
    ax2.set_xlabel("Round")
    ax2.set_ylim(0, 1)

    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output}")


# ── CLI ─────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="experiment-run",
        description="Run the experiment ABM across all five treatments.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--n-sessions", type=int, default=200, metavar="N",
                   help="independent sessions per treatment")
    p.add_argument("--seed", type=int, default=42, metavar="N",
                   help="base RNG seed")
    p.add_argument("--output", type=Path, default=Path("experiment_results.png"),
                   metavar="FILE", help="output plot path")
    p.add_argument("--no-plot", action="store_true",
                   help="skip plot, print table only")
    p.add_argument("--contrib-init", type=float, default=12.0, metavar="F",
                   help="initial contribution per agent (MU)")
    p.add_argument("--aspiration-init", type=float, default=8.0, metavar="F",
                   help="initial aspiration level (MU)")
    p.add_argument("--aspiration-alpha", type=float, default=0.2, metavar="F",
                   help="aspiration learning rate")
    p.add_argument("--contrib-delta", type=float, default=1.0, metavar="F",
                   help="contribution step size per round (MU)")
    return p


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)

    agent_cfg = AgentConfig(
        contrib_init=args.contrib_init,
        aspiration_init=args.aspiration_init,
        aspiration_alpha=args.aspiration_alpha,
        contrib_delta=args.contrib_delta,
    )

    print(f"Running {args.n_sessions} sessions per treatment...")
    print(f"  Agent config: contrib_init={agent_cfg.contrib_init}  "
          f"α={agent_cfg.aspiration_alpha}  δ={agent_cfg.contrib_delta}")
    print()

    results = run_all_treatments(agent_cfg, args.n_sessions, args.seed)

    if not args.no_plot:
        plot_results(results, args.output)


if __name__ == "__main__":
    main()
