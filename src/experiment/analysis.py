"""Post-hoc Linear Contribution Profile (LCP) classification.

Replicates the typing method of Jonsson & Jonsson (2025), Fig 6: for each
participant, regress their contribution in round t on the mean contribution of
the *other* group members in round t-1 (OLS). The fitted line over the range of
possible "others' mean" values [0, endowment] is classified:

  - Free-Rider (FR)               : line lies entirely below endowment/2
  - Unconditional Cooperator (UC) : line lies entirely above endowment/2
  - Conditional Cooperator (CC)   : positive slope and the line crosses
                                    endowment/2 (both above and below)
  - Uncategorized                 : anything else (e.g. crosses with non-positive
                                    slope)

The intercept (alpha) measures willingness to cooperate when others give
nothing; the slope (beta) measures responsiveness to others' contributions.
"""

from __future__ import annotations

import numpy as np

TYPES = ("UC", "CC", "FR", "Uncategorized")


def fit_lcp(own: np.ndarray, others_prev_mean: np.ndarray) -> tuple[float, float]:
    """OLS fit of own contribution on others' previous-round mean contribution.

    Args:
        own: Contributions of the focal agent at rounds t = 1..T-1.
        others_prev_mean: Mean contribution of the other agents at rounds t-1.

    Returns:
        (alpha, beta): intercept and slope of the LCP line. If the regressor has
        zero variance (others never varied), beta = 0 and alpha = mean(own).
    """
    x = np.asarray(others_prev_mean, dtype=float)
    y = np.asarray(own, dtype=float)
    if x.size == 0:
        return 0.0, 0.0

    x_mean = x.mean()
    y_mean = y.mean()
    var_x = np.sum((x - x_mean) ** 2)
    if var_x == 0.0:
        return float(y_mean), 0.0

    beta = float(np.sum((x - x_mean) * (y - y_mean)) / var_x)
    alpha = float(y_mean - beta * x_mean)
    return alpha, beta


def classify_lcp(alpha: float, beta: float, endowment: float = 20.0) -> str:
    """Classify an LCP line into UC / CC / FR / Uncategorized (Fig 6 rules)."""
    half = endowment / 2.0
    y0 = alpha
    y_end = alpha + beta * endowment
    lo, hi = (y0, y_end) if y0 <= y_end else (y_end, y0)

    if hi <= half:
        return "FR"
    if lo >= half:
        return "UC"
    if beta > 0.0:          # crosses half with a positive slope
        return "CC"
    return "Uncategorized"


def classify_session(
    contrib_record: list[list[float]],
    endowment: float = 20.0,
) -> list[str]:
    """Classify every agent in one session from its contribution record.

    Args:
        contrib_record: rounds × agents matrix of contributions played.
        endowment: per-round endowment (sets the 50% classification line).

    Returns:
        One type label per agent. Sessions shorter than 2 rounds yield all
        "Uncategorized" (no regression possible).
    """
    mat = np.asarray(contrib_record, dtype=float)
    if mat.ndim != 2 or mat.shape[0] < 2:
        n_agents = mat.shape[1] if mat.ndim == 2 else 0
        return ["Uncategorized"] * n_agents

    n_rounds, n_agents = mat.shape
    labels: list[str] = []
    total = mat.sum(axis=1)                       # group pot per round
    for j in range(n_agents):
        own = mat[1:, j]                          # y_t, t = 1..T-1
        others_prev = (total[:-1] - mat[:-1, j]) / (n_agents - 1)  # x_{t-1}
        alpha, beta = fit_lcp(own, others_prev)
        labels.append(classify_lcp(alpha, beta, endowment))
    return labels


def type_distribution(
    sessions: list[list[list[float]]],
    endowment: float = 20.0,
) -> dict[str, float]:
    """Aggregate type proportions across many sessions.

    Args:
        sessions: list of per-session contribution records.
        endowment: per-round endowment.

    Returns:
        Proportion of agents in each of UC / CC / FR / Uncategorized
        (keys always present, summing to 1.0 when at least one agent exists).
    """
    counts = {t: 0 for t in TYPES}
    n_total = 0
    for record in sessions:
        for label in classify_session(record, endowment):
            counts[label] += 1
            n_total += 1
    if n_total == 0:
        return {t: 0.0 for t in TYPES}
    return {t: counts[t] / n_total for t in TYPES}
