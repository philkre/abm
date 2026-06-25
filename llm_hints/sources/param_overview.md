In Sensitivitiy Analysis

| **Param** | **Range** | **Meaning** |
| --- | --- | --- |
| `beta` | [0.1, 10.0] | Fermi selection strength |
| `p_max` | [0.0, 1.0] | max flood probability |
| `T_over_E` | [0.4, 0.9] | threshold ratio (`T = 5·value`) |
| `ell` | [0.0, 1.0] | loss fraction per flood |

Fixed during SA

| **Param** | **Value** |
| --- | --- |
| `L` | 200 (150 for compute-heavy sweeps) |
| `n_gens` | 1500 |
| `measure_window` | 200 |
| `env_update_every` (τ) | 1 |
| `mu` | 0.01 |
| `c_bar` | 0.75 |
| `R` | 0.0 |
| `w0` | 1.0 |
| `wealth_mode` | `"ou"` |
| `b` | 1.0 |
| `sigma` | 0.1 |
| `kappa` | 0.2 |
| `delta` | 0.03 |
| `gamma` | 0.03 |
| `eta` | 0.03 (headline) / 0.0 (ablation) |
| `lambda_mode` | `"homogeneous"` |
| `lambda_mean` | 1.0 |
| `lambda_max` | 4.0 |
| `risk_mode` | `"linear"` |
| `p_min` | 0.0 |
| `initial_mix` | `"equal"` (or `"thirds"` for 3-strategy) |
| `k`, `e0` | unused (linear ignores them) |
| `g` | 0.015 (inert under OU) |