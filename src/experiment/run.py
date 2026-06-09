"""Run all five treatments and report paper-comparable metrics.

Replicates the structure of the experimental analysis in Jonsson & Jonsson
(2025): round-by-round mean contribution (Figs 2-3), threshold check-pass rate
(58% in the paper), and the emergent UC/CC/FR type mix via LCP classification
(Fig 6 / type distributions).

Usage:
    uv run experiment-run
    uv run experiment-run --n-sessions 500 --output contributions.png
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from experiment.analysis import TYPES, type_distribution
from experiment.config import (
    DEFAULT_AGENT_CONFIG,
    AgentConfig,
    TreatmentConfig,
    TREATMENTS,
)
from experiment.model import ExperimentModel


# ── Results container ────────────────────────────────────────────────────────


@dataclass
class TreatmentResults:
    """Aggregated results for one treatment across many sessions.

    Attributes:
        df: round-by-round mean metrics, averaged over sessions.
        pass_rate: fraction of fired threshold checks the group passed
            (NaN if no check ever fired, e.g. Control).
        type_dist: proportion of agents classified UC/CC/FR/Uncategorized.
    """

    df: pd.DataFrame
    pass_rate: float
    type_dist: dict[str, float]


# ── Simulation ─────────────────────────────────────────────────────────────


def run_sessions(
    treatment: TreatmentConfig,
    agent_cfg: AgentConfig = DEFAULT_AGENT_CONFIG,
    n_sessions: int = 200,
    base_seed: int = 42,
) -> TreatmentResults:
    """Run n_sessions independent sessions; return averaged metrics + aggregates.

    Args:
        treatment: Treatment configuration.
        agent_cfg: Aspiration learning parameters.
        n_sessions: Number of independent group sessions to average over.
        base_seed: Base RNG seed; session i uses base_seed + i.
    """
    all_dfs: list[pd.DataFrame] = []
    all_records: list[list[list[float]]] = []
    n_fired = 0
    n_passed = 0

    for i in range(n_sessions):
        model = ExperimentModel(treatment, agent_cfg, seed=base_seed + i)
        model.run()
        all_dfs.append(model.datacollector.get_model_vars_dataframe())
        all_records.append(model.contrib_record)
        n_fired += sum(model.check_fired)
        n_passed += sum(
            p for f, p in zip(model.check_fired, model.check_passed) if f
        )

    stacked = pd.concat(all_dfs)
    df = stacked.groupby(stacked.index).mean()
    pass_rate = (n_passed / n_fired) if n_fired else float("nan")
    type_dist = type_distribution(all_records, treatment.endowment)
    return TreatmentResults(df=df, pass_rate=pass_rate, type_dist=type_dist)


def run_all_treatments(
    agent_cfg: AgentConfig = DEFAULT_AGENT_CONFIG,
    n_sessions: int = 200,
    base_seed: int = 42,
) -> dict[str, TreatmentResults]:
    """Run all five treatments. Returns {treatment_name: TreatmentResults}."""
    results: dict[str, TreatmentResults] = {}
    for name, treatment in TREATMENTS.items():
        t0 = time.perf_counter()
        results[name] = run_sessions(treatment, agent_cfg, n_sessions, base_seed)
        elapsed = time.perf_counter() - t0
        final_contrib = results[name].df["mean_contribution"].iloc[-1]
        pr = results[name].pass_rate
        pr_str = "  n/a" if pr != pr else f"{pr:5.2f}"
        print(
            f"  {name:8s}  final contribution={final_contrib:5.2f}  "
            f"pass_rate={pr_str}  ({elapsed:.2f}s)"
        )
    return results


# ── Reporting ────────────────────────────────────────────────────────────────

# Paper reference values for side-by-side comparison.
_PAPER_TYPE_DIST = {
    "Control": {"UC": 0.24, "CC": 0.60, "FR": 0.11, "Uncategorized": 0.05},
    # Treatments (pooled) in the paper:
    "_treatments": {"UC": 0.56, "CC": 0.36, "FR": 0.04, "Uncategorized": 0.04},
}
_PAPER_PASS_RATE = 0.58            # "in 58% of the threshold checks groups succeeded"
_PAPER_CONTRIB = {                  # Fig 3A mean individual contribution
    "Control": 12.0, "10P": 14.9, "40P": 15.1, "Impact": 14.8, "Level": 16.5,
}


def print_comparison(results: dict[str, TreatmentResults]) -> None:
    """Print model vs paper metrics for each treatment."""
    print("\n── Mean contribution (final round) vs paper Fig 3A ──")
    print(f"  {'treatment':10s} {'model':>8s} {'paper':>8s}")
    for name, res in results.items():
        model_c = res.df["mean_contribution"].iloc[-1]
        paper_c = _PAPER_CONTRIB.get(name, float("nan"))
        print(f"  {name:10s} {model_c:8.2f} {paper_c:8.2f}")

    print(f"\n── Check-pass rate vs paper ({_PAPER_PASS_RATE:.2f}) ──")
    for name, res in results.items():
        if res.pass_rate == res.pass_rate:  # not NaN
            print(f"  {name:10s} {res.pass_rate:8.2f}")

    print("\n── LCP type distribution (UC / CC / FR / Unc) ──")
    print(f"  {'treatment':10s} " + " ".join(f"{t:>6s}" for t in TYPES))
    for name, res in results.items():
        row = " ".join(f"{res.type_dist[t]:6.2f}" for t in TYPES)
        print(f"  {name:10s} {row}")
    print(
        "  paper Ctrl "
        + " ".join(f"{_PAPER_TYPE_DIST['Control'][t]:6.2f}" for t in TYPES)
    )
    print(
        "  paper Trt  "
        + " ".join(f"{_PAPER_TYPE_DIST['_treatments'][t]:6.2f}" for t in TYPES)
    )


# ── Plotting ────────────────────────────────────────────────────────────────

_COLOURS = {
    "Control": "grey",
    "10P": "steelblue",
    "40P": "darkorange",
    "Level": "forestgreen",
    "Impact": "crimson",
}


def plot_results(results: dict[str, TreatmentResults], output: Path) -> None:
    """Three panels: contribution trend, disaster rate, and LCP type mix."""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 10))

    for name, res in results.items():
        df = res.df
        colour = _COLOURS.get(name, "black")
        ax1.plot(df.index, df["mean_contribution"], label=name, color=colour, lw=2)
        ax2.plot(df.index, df["disaster_rate"], label=name, color=colour, lw=2)

    ax1.axhline(15.0, color="black", lw=1, ls="--", label="threshold/group (15)")
    ax1.set_ylabel("Mean contribution (MU)")
    ax1.set_xlabel("Round")
    ax1.set_ylim(0, 20)
    ax1.legend(loc="best", fontsize=8)
    ax1.set_title("Contribution trend (cf. Fig 3B)")

    ax2.set_ylabel("Disaster rate")
    ax2.set_xlabel("Round")
    ax2.set_ylim(0, 1)
    ax2.set_title("Disaster rate per round")

    # Type-distribution grouped bars
    names = list(results)
    x = np.arange(len(TYPES))
    width = 0.8 / max(len(names), 1)
    for k, name in enumerate(names):
        vals = [results[name].type_dist[t] for t in TYPES]
        ax3.bar(x + k * width, vals, width, label=name,
                color=_COLOURS.get(name, "black"))
    ax3.set_xticks(x + width * (len(names) - 1) / 2)
    ax3.set_xticklabels(TYPES)
    ax3.set_ylabel("Proportion of agents")
    ax3.set_ylim(0, 1)
    ax3.set_title("LCP type distribution (cf. Fig 6)")
    ax3.legend(loc="best", fontsize=8)

    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    print(f"\nPlot saved to {output}")


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
                   help="skip plot, print tables only")
    p.add_argument("--contrib-init", type=float, default=12.0, metavar="F",
                   help="initial contribution per agent (MU)")
    p.add_argument("--aspiration-lo", type=float, default=18.0, metavar="F",
                   help="lower bound of per-agent initial aspiration")
    p.add_argument("--aspiration-hi", type=float, default=30.0, metavar="F",
                   help="upper bound of per-agent initial aspiration")
    p.add_argument("--aspiration-alpha", type=float, default=0.2, metavar="F",
                   help="aspiration learning rate")
    p.add_argument("--contrib-delta", type=float, default=1.0, metavar="F",
                   help="safe-round contribution step size (MU)")
    p.add_argument("--delta-up", type=float, default=6.0, metavar="F",
                   help="upward step after a disaster (MU)")
    p.add_argument("--disaster-penalty", type=float, default=20.0, metavar="F",
                   help="bounded negative learning signal on a disaster round")
    return p


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)

    agent_cfg = AgentConfig(
        contrib_init=args.contrib_init,
        aspiration_lo=args.aspiration_lo,
        aspiration_hi=args.aspiration_hi,
        aspiration_alpha=args.aspiration_alpha,
        contrib_delta=args.contrib_delta,
        delta_up=args.delta_up,
        disaster_penalty=args.disaster_penalty,
    )

    print(f"Running {args.n_sessions} sessions per treatment...")
    print(f"  Agent config: contrib_init={agent_cfg.contrib_init}  "
          f"aspiration~U({agent_cfg.aspiration_lo},{agent_cfg.aspiration_hi})  "
          f"α={agent_cfg.aspiration_alpha}  δ={agent_cfg.contrib_delta}  "
          f"δ_up={agent_cfg.delta_up}  disaster_penalty={agent_cfg.disaster_penalty}")
    print()

    results = run_all_treatments(agent_cfg, args.n_sessions, args.seed)
    print_comparison(results)

    if not args.no_plot:
        plot_results(results, args.output)


if __name__ == "__main__":
    main()
