"""Paired, multi-seed comparison of power-management policies.

For each of N random environments (seed), every policy is run on the *same* trace with
*identical* component noise, so differences are attributable to the policy alone. We
report mean +/- 95% CI across seeds and a paired comparison of our AdaptiveMetabolic
policy against each baseline.

Metrics (per run):
  responsiveness  -- mean spikes delivered per urgent-event window (higher = better)
  brownout_frac   -- fraction of time the energy reserve is critically low (<0.05)
  min_reserve     -- lowest reserve reached (safety margin; higher = better)
  efficiency      -- spikes delivered per microjoule harvested (throughput per energy)

Usage:  python -m experiments.compare_policies
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from biobrain import BiofuelCell, EnergyStore, SpikingNet
from biobrain.policies import FixedRate, PowerGating, StaticDVFS, AdaptiveMetabolic
from experiments.traces import make_trace, Trace

INPUT_CURRENT = 1.2
OXYGEN_FRAC = 1.0
BROWNOUT_LEVEL = 0.05


@dataclass
class RunMetrics:
    responsiveness: float
    brownout_frac: float
    min_reserve: float
    efficiency: float


def run_policy(trace: Trace, policy, seed: int, capacity_uj: float | None = None) -> RunMetrics:
    # Identical component noise across policies for a given seed -> paired comparison.
    rng = np.random.default_rng(seed * 7919 + 1)
    cell = BiofuelCell(rng=rng)
    store = EnergyStore() if capacity_uj is None else EnergyStore(capacity_uj=capacity_uj)
    net = SpikingNet(rng=rng)
    policy.reset()

    dt = trace.dt_s
    n = len(trace.glucose)
    spikes = np.empty(n, dtype=int)
    reserve = np.empty(n, dtype=float)
    harvested_uj = 0.0

    for i in range(n):
        power = cell.power_uw(trace.glucose[i], OXYGEN_FRAC, dt)
        harvested_uj += power * dt
        store.charge(power, dt)
        scale = policy.rate_scale(store.level)
        s = net.step(INPUT_CURRENT * trace.demand[i], dt, store, scale)
        spikes[i] = s
        reserve[i] = store.level

    ev_spikes = [int(spikes[a:b].sum()) for (a, b) in trace.event_windows]
    responsiveness = float(np.mean(ev_spikes)) if ev_spikes else 0.0
    brownout_frac = float(np.mean(reserve < BROWNOUT_LEVEL))
    min_reserve = float(reserve.min())
    total_spikes = int(spikes.sum())
    efficiency = total_spikes / harvested_uj if harvested_uj > 0 else 0.0
    return RunMetrics(responsiveness, brownout_frac, min_reserve, efficiency)


def mean_ci(x: np.ndarray) -> tuple[float, float]:
    """Mean and 95% CI half-width (normal approx; n>=20 seeds)."""
    x = np.asarray(x, dtype=float)
    m = float(x.mean())
    sem = float(x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    return m, 1.96 * sem


def paired_diff(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """Paired mean difference (a-b) and 95% CI half-width. Significant if CI excludes 0."""
    d = np.asarray(a, float) - np.asarray(b, float)
    m = float(d.mean())
    sem = float(d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 1 else 0.0
    return m, 1.96 * sem


def main(n_seeds: int = 30) -> None:
    policy_factories = [
        ("fixed-rate", FixedRate),
        ("power-gating", lambda: PowerGating(low=0.15, high=0.45)),
        ("static-dvfs", lambda: StaticDVFS(scale=0.5)),
        ("adaptive-metabolic", AdaptiveMetabolic),
    ]

    fields = ["responsiveness", "brownout_frac", "min_reserve", "efficiency"]
    results = {name: {f: [] for f in fields} for name, _ in policy_factories}

    for seed in range(n_seeds):
        trace = make_trace(seed)
        for name, factory in policy_factories:
            m = run_policy(trace, factory(), seed)
            for f in fields:
                results[name][f].append(getattr(m, f))

    # ---- Report table ----
    print(f"\nPaired comparison over {n_seeds} random environments (mean +/- 95% CI)\n")
    header = f"{'policy':<20}" + "".join(f"{f:>18}" for f in fields)
    print(header)
    print("-" * len(header))
    for name, _ in policy_factories:
        row = f"{name:<20}"
        for f in fields:
            m, ci = mean_ci(np.array(results[name][f]))
            row += f"{m:>10.3f}+-{ci:<5.3f}"
        print(row)

    # ---- Paired significance vs adaptive on the primary metric ----
    print("\nAdaptiveMetabolic vs baselines on responsiveness (spikes/event):")
    adapt = np.array(results["adaptive-metabolic"]["responsiveness"])
    for name, _ in policy_factories:
        if name == "adaptive-metabolic":
            continue
        base = np.array(results[name]["responsiveness"])
        d, ci = paired_diff(adapt, base)
        sig = "significant" if abs(d) > ci and ci > 0 else "n.s."
        print(f"  vs {name:<14}: +{d:>8.1f} +/- {ci:.1f}  ({sig})")

    # ---- Figure: responsiveness + brownout with error bars ----
    names = [n for n, _ in policy_factories]
    resp_m = [mean_ci(np.array(results[n]["responsiveness"]))[0] for n in names]
    resp_e = [mean_ci(np.array(results[n]["responsiveness"]))[1] for n in names]
    bro_m = [mean_ci(np.array(results[n]["brownout_frac"]))[0] for n in names]
    bro_e = [mean_ci(np.array(results[n]["brownout_frac"]))[1] for n in names]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    colors = ["tab:gray", "tab:blue", "tab:olive", "tab:purple"]
    ax1.bar(names, resp_m, yerr=resp_e, capsize=5, color=colors)
    ax1.set_ylabel("spikes per urgent event")
    ax1.set_title("Event responsiveness (higher = better)")
    ax1.tick_params(axis="x", rotation=20)
    ax2.bar(names, bro_m, yerr=bro_e, capsize=5, color=colors)
    ax2.set_ylabel("fraction of time in brownout")
    ax2.set_title("Brownout exposure (lower = better)")
    ax2.tick_params(axis="x", rotation=20)
    fig.suptitle(f"Policy comparison over {n_seeds} random environments (95% CI)")
    fig.tight_layout()
    fig.savefig("policy_comparison.png", dpi=130)
    print("\nwrote policy_comparison.png")


if __name__ == "__main__":
    main()
