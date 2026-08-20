"""Pareto frontier + ablation studies -- the paper's key analysis figures.

Pareto: sweep the metabolic regulator's homeostatic setpoint (and a couple of gains) and
plot each configuration in (brownout, responsiveness) space. A good policy lives in the
upper-left (high responsiveness, low brownout). We overlay the three baselines and show
the adaptive-metabolic family traces a frontier that dominates them.

Ablations:
  (a) graded vs. binary throttle       -- does the *graded* response matter, or would an
                                          on/off step at the setpoint do as well?
  (b) with vs. without homeostatic setpoint
  (c) supercapacitor size sweep        -- how much does the energy buffer matter?

Usage:  python -m experiments.pareto_ablation
"""

from __future__ import annotations

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from biobrain.policies import FixedRate, PowerGating, StaticDVFS, AdaptiveMetabolic
from experiments.traces import make_trace
from experiments.compare_policies import run_policy, mean_ci

N_SEEDS = 25


def sweep(policy_factory, capacity_uj=None, n_seeds=N_SEEDS):
    """Return dict of metric -> (mean, ci) aggregated over seeds for one config."""
    resp, bro, minr = [], [], []
    for seed in range(n_seeds):
        trace = make_trace(seed)
        m = run_policy(trace, policy_factory(), seed, capacity_uj=capacity_uj)
        resp.append(m.responsiveness)
        bro.append(m.brownout_frac)
        minr.append(m.min_reserve)
    return {
        "responsiveness": mean_ci(np.array(resp)),
        "brownout_frac": mean_ci(np.array(bro)),
        "min_reserve": mean_ci(np.array(minr)),
    }


def build_pareto(ax):
    # Adaptive-metabolic family: sweep setpoint at gain=6, plus gain variants at sp=0.5.
    setpoints = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    frontier = []
    for sp in setpoints:
        r = sweep(lambda sp=sp: AdaptiveMetabolic(setpoint=sp, gain=6.0))
        frontier.append((r["brownout_frac"][0], r["responsiveness"][0], f"sp={sp}"))
    for g in (3.0, 12.0):
        r = sweep(lambda g=g: AdaptiveMetabolic(setpoint=0.5, gain=g))
        frontier.append((r["brownout_frac"][0], r["responsiveness"][0], f"g={g:.0f}"))

    fx = [p[0] for p in frontier]
    fy = [p[1] for p in frontier]
    order = np.argsort(fx)
    ax.plot(np.array(fx)[order], np.array(fy)[order], "-o", color="tab:purple",
            label="adaptive-metabolic (swept)", zorder=3)
    for bx, by, lbl in frontier:
        ax.annotate(lbl, (bx, by), fontsize=7, xytext=(3, 3),
                    textcoords="offset points")

    # Baselines as reference points.
    baselines = [
        ("fixed-rate", FixedRate, "tab:gray", "s"),
        ("power-gating", lambda: PowerGating(0.15, 0.45), "tab:blue", "^"),
        ("static-dvfs", lambda: StaticDVFS(0.5), "tab:olive", "D"),
    ]
    for name, fac, color, marker in baselines:
        r = sweep(fac)
        ax.scatter([r["brownout_frac"][0]], [r["responsiveness"][0]],
                   c=color, marker=marker, s=90, label=name, zorder=4,
                   edgecolors="k", linewidths=0.5)

    ax.set_xlabel("brownout fraction (lower = better)")
    ax.set_ylabel("responsiveness (spikes/event, higher = better)")
    ax.set_title("Responsiveness-safety Pareto:\nadaptive family dominates upper-left")
    ax.legend(fontsize=8, loc="best")
    ax.grid(alpha=0.3)


def build_ablation_throttle(ax):
    configs = [
        ("graded\n(full)", lambda: AdaptiveMetabolic(setpoint=0.5, gain=6.0), "tab:purple"),
        ("binary\n(step)", lambda: AdaptiveMetabolic(setpoint=0.5, gain=200.0), "tab:red"),
        ("no setpoint\n(sp=0)", lambda: AdaptiveMetabolic(setpoint=0.0, gain=6.0), "tab:orange"),
    ]
    names, rm, re, bm, be = [], [], [], [], []
    for name, fac, _ in configs:
        r = sweep(fac)
        names.append(name)
        rm.append(r["responsiveness"][0]); re.append(r["responsiveness"][1])
        bm.append(r["brownout_frac"][0]); be.append(r["brownout_frac"][1])
    x = np.arange(len(names))
    ax.bar(x - 0.2, rm, 0.4, yerr=re, capsize=4, label="responsiveness", color="tab:purple")
    ax2 = ax.twinx()
    ax2.bar(x + 0.2, bm, 0.4, yerr=be, capsize=4, label="brownout frac", color="tab:red", alpha=0.7)
    ax.set_xticks(x); ax.set_xticklabels(names)
    ax.set_ylabel("responsiveness (spikes/event)")
    ax2.set_ylabel("brownout fraction")
    ax.set_title("Ablation: graded vs binary vs no-setpoint")
    ax.legend(loc="upper left", fontsize=8)
    ax2.legend(loc="upper right", fontsize=8)


def build_ablation_supercap(ax):
    caps = [500, 1000, 2000, 4000, 8000]
    rm, re, bm, be = [], [], [], []
    for c in caps:
        r = sweep(lambda: AdaptiveMetabolic(), capacity_uj=c)
        rm.append(r["responsiveness"][0]); re.append(r["responsiveness"][1])
        bm.append(r["brownout_frac"][0]); be.append(r["brownout_frac"][1])
    ax.errorbar(caps, rm, yerr=re, marker="o", color="tab:purple", label="responsiveness")
    ax.set_xlabel("supercapacitor capacity (uJ)")
    ax.set_ylabel("responsiveness (spikes/event)", color="tab:purple")
    ax.set_xscale("log")
    ax2 = ax.twinx()
    ax2.errorbar(caps, bm, yerr=be, marker="s", color="tab:red", label="brownout frac")
    ax2.set_ylabel("brownout fraction", color="tab:red")
    ax.set_title("Ablation: energy-buffer (supercap) size")
    ax.grid(alpha=0.3)


def main() -> None:
    print(f"Running Pareto + ablations ({N_SEEDS} seeds each config)...")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    build_pareto(axes[0])
    build_ablation_throttle(axes[1])
    build_ablation_supercap(axes[2])
    fig.tight_layout()
    fig.savefig("pareto_ablation.png", dpi=130)
    print("wrote pareto_ablation.png")


if __name__ == "__main__":
    main()
