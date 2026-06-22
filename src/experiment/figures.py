"""Reproduce Fig 4 of Jonsson & Jonsson (2025): contribution vs disaster prob.

Panel A: mean individual contribution at check probabilities 0/10/40/70/100%,
         with 95% confidence intervals (cf. Fig 4A).
Panel B: round-by-round mean contribution for each probability (cf. Fig 4B).

The threshold and all other parameters are held fixed; only `disaster_prob`
varies, isolating the effect of disaster probability.

Usage:
    uv run experiment-fig4
    uv run experiment-fig4 --n-sessions 500 --output fig4.png
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from experiment.config import DEFAULT_AGENT_CONFIG, AgentConfig, TreatmentConfig
from experiment.model import ExperimentModel

# Probabilities studied in the paper's Fig 4 (0% = Control deterministic case).
DEFAULT_PROBS = (0.0, 0.1, 0.4, 0.7, 1.0)

# Paper Fig 4A reference values (mean individual contribution) for overlay.
_PAPER_FIG4A = {0.0: 11.5, 0.1: 15.6, 0.4: 15.4, 0.7: 16.7, 1.0: 16.9}


@dataclass
class ProbResult:
    """Results for one disaster probability.

    Attributes:
        grand_mean: mean individual contribution over all rounds and sessions.
        ci95: 95% confidence interval half-width across sessions.
        trend: round-by-round mean contribution (length n_rounds).
        pass_rate: fraction of fired checks passed (NaN if none fired).
    """

    grand_mean: float
    ci95: float
    trend: np.ndarray
    pass_rate: float


def disaster_prob_sweep(
    probs: tuple[float, ...] = DEFAULT_PROBS,
    agent_cfg: AgentConfig = DEFAULT_AGENT_CONFIG,
    n_sessions: int = 500,
    base_seed: int = 1000,
    threshold: float = 60.0,
) -> dict[float, ProbResult]:
    """Run the model across disaster probabilities; return per-prob results."""
    out: dict[float, ProbResult] = {}
    for p in probs:
        treatment = TreatmentConfig(
            f"{int(p * 100)}%", disaster_prob=p, threshold=threshold
        )
        session_means: list[float] = []  # per-session mean over rounds
        trends: list[list[float]] = []  # per-session round-by-round mean
        fired = passed = 0
        for i in range(n_sessions):
            m = ExperimentModel(treatment, agent_cfg, seed=base_seed + i)
            m.run()
            per_round = [float(np.mean(r)) for r in m.contrib_record]
            session_means.append(float(np.mean(per_round)))
            trends.append(per_round)
            fired += sum(m.check_fired)
            passed += sum(pp for f, pp in zip(m.check_fired, m.check_passed) if f)

        means = np.asarray(session_means)
        grand = float(means.mean())
        ci = float(1.96 * means.std(ddof=1) / np.sqrt(len(means)))
        trend = np.asarray(trends).mean(axis=0)
        pr = (passed / fired) if fired else float("nan")
        out[p] = ProbResult(grand_mean=grand, ci95=ci, trend=trend, pass_rate=pr)
    return out


# ── Plotting ─────────────────────────────────────────────────────────────────

# Dark → light blues, matching the paper's Fig 4 colour ramp.
_BLUES = ["#0b1f3a", "#1f4e79", "#3f7cb0", "#7fb0d6", "#bcd6ec"]


def plot_fig4(
    results: dict[float, ProbResult], output: Path, show_paper: bool = True
) -> None:
    """Two-panel Fig-4 reproduction (bars+CI; round-by-round trend)."""
    probs = list(results)
    labels = [f"{int(p * 100)}%" for p in probs]
    colours = _BLUES[: len(probs)]

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(13, 5))

    # Panel A — bars with 95% CI
    x = np.arange(len(probs))
    means = [results[p].grand_mean for p in probs]
    cis = [results[p].ci95 for p in probs]
    axA.bar(
        x, means, yerr=cis, capsize=4, color=colours, edgecolor="black", linewidth=0.5
    )
    if show_paper:
        paper = [_PAPER_FIG4A.get(p, np.nan) for p in probs]
        axA.plot(x, paper, "o--", color="crimson", lw=1.5, ms=6, label="paper Fig 4A")
        axA.legend(loc="lower right", fontsize=9)
    axA.set_xticks(x)
    axA.set_xticklabels(labels)
    axA.set_xlabel("Probability of a check")
    axA.set_ylabel("Mean of individual contributions")
    axA.set_ylim(0, 20)
    axA.set_title("A · Average contribution by disaster probability")

    # Panel B — round-by-round trend
    for p, colour in zip(probs, colours):
        trend = results[p].trend
        rounds = np.arange(1, len(trend) + 1)
        axB.plot(
            rounds, trend, marker="o", ms=3, color=colour, label=f"{int(p * 100)}%"
        )
    axB.set_xlabel("Round")
    axB.set_ylabel("Mean of individual contributions")
    axB.set_ylim(0, 20)
    axB.set_title("B · Contribution trend by disaster probability")
    axB.legend(loc="lower right", fontsize=9, ncol=2)

    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    print(f"Fig 4 saved to {output}")


# ── CLI ─────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="experiment-fig4",
        description="Reproduce Fig 4 (contribution vs disaster probability).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--n-sessions", type=int, default=500, metavar="N")
    p.add_argument("--seed", type=int, default=1000, metavar="N")
    p.add_argument("--output", type=Path, default=Path("fig4.png"), metavar="FILE")
    p.add_argument(
        "--no-paper", action="store_true", help="omit the paper reference overlay"
    )
    return p


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    print(f"Running disaster-probability sweep ({args.n_sessions} sessions each)...")
    results = disaster_prob_sweep(n_sessions=args.n_sessions, base_seed=args.seed)
    print(f"  {'p':>5} {'model':>7} {'±95%':>6} {'paper':>7} {'pass':>6}")
    for p, r in results.items():
        paper = _PAPER_FIG4A.get(p, float("nan"))
        pr = "  n/a" if r.pass_rate != r.pass_rate else f"{r.pass_rate:5.2f}"
        print(f"  {p:5.2f} {r.grand_mean:7.2f} {r.ci95:6.2f} {paper:7.2f} {pr:>6}")
    plot_fig4(results, args.output, show_paper=not args.no_paper)


if __name__ == "__main__":
    main()
