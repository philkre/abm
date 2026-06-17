"""Validation tests — marked slow; run with: pytest -m slow."""

import pytest
from spatcoop.validate import (
    validate_jonsson,
    validate_ding_c_phase,
    DING_BASE,
    DING_DELTA_SWEEP,
)
from spatcoop.params import ModelParams
from spatcoop.model import run_episode


@pytest.mark.slow
def test_jonsson_qualitative():
    """Risk run cooperation > 0.5; control run < 0.3."""
    assert validate_jonsson(tol_coop=0.5, seed=0)


@pytest.mark.slow
def test_ding_c_phase_exists_at_L200():
    """At δ=0.021, γ=0.04, L=200: UC fraction > 0.7 after 3000 generations."""
    assert validate_ding_c_phase(delta=0.021, seed=0, coop_threshold=0.7)


@pytest.mark.slow
def test_ding_d_phase_at_low_delta():
    """At very low δ, defectors should dominate."""
    p = ModelParams(**DING_BASE, delta=0.005)
    r = run_episode(p, seed=0)
    uc_frac = r.summary["n_UC"] / (200 ** 2)
    assert uc_frac < 0.3, f"Expected D dominance but UC frac = {uc_frac:.3f}"
