"""Benchmark: FashionMNIST accuracy under an intermittent biofuel-cell power budget.

A stream of test images arrives at a fixed rate. Between arrivals the biofuel cell
charges the energy store. For each image, the power-management policy reads the reserve
and picks a compute budget (number of rate-coded frames); more frames cost more energy
but yield higher accuracy (see snn_model.py). If the reserve cannot afford the requested
budget, the device is forced down to what it can pay (possibly 0 = no answer = wrong).

We compare policies on accuracy over the whole stream and during the famine window, across
several random power environments (glucose famine timing + cell noise vary per seed).

Usage:  python -m benchmark.run_benchmark
"""

from __future__ import annotations

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from biobrain import BiofuelCell, EnergyStore
from biobrain.policies import FixedRate, PowerGating, StaticDVFS, AdaptiveMetabolic
from benchmark.snn_model import train_model, correctness_by_budget

BUDGETS = [0, 1, 2, 4, 8, 16]      # rate-coded frames (compute budget)
E_PER_FRAME_UJ = 5.0               # energy cost per frame
ARRIVAL_S = 0.5                    # one image every 0.5 s
OXYGEN = 1.0


def scale_to_budget_idx(scale: float) -> int:
    """Map a policy rate_scale in [0,1] to an index into BUDGETS."""
    return int(round(float(np.clip(scale, 0, 1)) * (len(BUDGETS) - 1)))


def glucose_at(t: float, famine_center: float) -> float:
    """Healthy 6 mM baseline with a Gaussian famine dip."""
    dip = 5.5 * np.exp(-((t - famine_center) ** 2) / (2 * 6.0 ** 2))
    return max(0.3, 6.0 - dip)


def run_stream(policy, correct, seed: int):
    rng = np.random.default_rng(seed * 104729 + 3)
    cell = BiofuelCell(rng=rng)
    store = EnergyStore()
    policy.reset()

    n = correct.shape[0]
    duration = n * ARRIVAL_S
    famine_center = rng.uniform(0.3, 0.7) * duration
    # sub-steps for charging between arrivals
    sub = 20
    dt = ARRIVAL_S / sub

    got = np.zeros(n, dtype=bool)
    in_famine = np.zeros(n, dtype=bool)
    for i in range(n):
        t = i * ARRIVAL_S
        for _ in range(sub):
            p = cell.power_uw(glucose_at(t, famine_center), OXYGEN, dt)
            store.charge(p, dt)
        in_famine[i] = abs(t - famine_center) < 8.0

        scale = policy.rate_scale(store.level)
        b_idx = scale_to_budget_idx(scale)
        # Drop to an affordable budget if necessary.
        while b_idx > 0 and BUDGETS[b_idx] * E_PER_FRAME_UJ > store.energy_uj:
            b_idx -= 1
        store.draw(BUDGETS[b_idx] * E_PER_FRAME_UJ)
        got[i] = correct[i, b_idx]

    return got, in_famine


def main(n_seeds: int = 8, n_test: int = 1200) -> None:
    print("Training / loading FashionMNIST model...")
    model = train_model()
    print("Precomputing accuracy-by-budget lookup...")
    correct, labels = correctness_by_budget(model, BUDGETS, n_test=n_test, seed=0)
    # Sanity: full-budget accuracy of the rate-coded classifier.
    print(f"  rate-coded accuracy at max budget ({max(BUDGETS)} frames): "
          f"{correct[:, -1].mean():.3f}")

    policies = [
        ("fixed-rate", FixedRate),
        ("power-gating", lambda: PowerGating(0.15, 0.45)),
        ("static-dvfs", lambda: StaticDVFS(0.5)),
        ("adaptive-metabolic", AdaptiveMetabolic),
    ]

    overall = {n: [] for n, _ in policies}
    famine = {n: [] for n, _ in policies}
    for seed in range(n_seeds):
        for name, fac in policies:
            got, fam = run_stream(fac(), correct, seed)
            overall[name].append(got.mean())
            famine[name].append(got[fam].mean() if fam.any() else np.nan)

    def mci(x):
        x = np.asarray(x, float)
        m = x.mean()
        ci = 1.96 * x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0.0
        return m, ci

    print(f"\nFashionMNIST accuracy under intermittent power ({n_seeds} seeds, 95% CI)\n")
    print(f"{'policy':<20}{'overall acc':>18}{'famine acc':>18}")
    print("-" * 56)
    names = [n for n, _ in policies]
    om, oe, fm, fe = [], [], [], []
    for name in names:
        o_m, o_c = mci(overall[name])
        f_m, f_c = mci(famine[name])
        om.append(o_m); oe.append(o_c); fm.append(f_m); fe.append(f_c)
        print(f"{name:<20}{o_m:>10.3f}+-{o_c:<5.3f}{f_m:>10.3f}+-{f_c:<5.3f}")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    x = np.arange(len(names))
    colors = ["tab:gray", "tab:blue", "tab:olive", "tab:purple"]
    ax.bar(x - 0.2, om, 0.4, yerr=oe, capsize=4, label="overall", color=colors)
    ax.bar(x + 0.2, fm, 0.4, yerr=fe, capsize=4, label="during famine",
           color=colors, alpha=0.55, hatch="//")
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=15)
    ax.set_ylabel("classification accuracy")
    ax.set_title("FashionMNIST accuracy under intermittent biofuel-cell power\n"
                 "(solid = overall, hatched = during famine; 95% CI)")
    ax.axhline(0.1, color="k", ls=":", lw=0.8, label="chance (10%)")
    ax.legend()
    fig.tight_layout()
    fig.savefig("benchmark_accuracy.png", dpi=130)
    print("\nwrote benchmark_accuracy.png")


if __name__ == "__main__":
    main()
