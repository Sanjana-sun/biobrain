"""Robustness checks: bootstrap CIs and a baseline-fairness sweep.

Two open items from PAPER/ROADMAP.md are addressed here.

1. Bootstrap confidence intervals. compare_policies.py uses a normal
   approximation (1.96 * SEM), which is defensible at n=30 but assumes
   approximate normality. Metrics like brownout_frac are bounded in [0, 1] and
   frequently degenerate (all zeros), where the normal approximation is simply
   wrong. We report percentile bootstrap intervals instead, which make no
   distributional assumption.

2. Baseline fairness. The headline comparison fixes StaticDVFS(scale=0.5) and
   PowerGating(low=0.15, high=0.45). Those are hand-chosen, and a reviewer's
   first objection is that our policy only wins because the baselines are badly
   tuned. We therefore sweep each baseline's own parameters, select the best
   configuration *for that baseline* under a safety constraint, and re-run the
   comparison against that best-case opponent.

Usage:  python -m experiments.robustness
"""

from __future__ import annotations

import numpy as np

from biobrain.policies import PowerGating, StaticDVFS, AdaptiveMetabolic
from experiments.compare_policies import run_policy
from experiments.traces import make_trace

N_SEEDS = 30
N_BOOT = 10000
BROWNOUT_TOLERANCE = 0.01  # a policy is "safe" if brownout_frac <= this
RNG = np.random.default_rng(12345)


# ---------------------------------------------------------------- bootstrap

def bootstrap_ci(x, n_boot: int = N_BOOT, alpha: float = 0.05):
    """Percentile bootstrap CI for the mean. No normality assumption.

    Returns (mean, lo, hi). Degenerate input (zero variance) yields lo == hi ==
    mean, which is the correct answer rather than a spurious interval.
    """
    x = np.asarray(x, dtype=float)
    m = float(x.mean())
    if len(x) < 2 or np.allclose(x, x[0]):
        return m, m, m
    idx = RNG.integers(0, len(x), size=(n_boot, len(x)))
    boot_means = x[idx].mean(axis=1)
    lo = float(np.percentile(boot_means, 100 * alpha / 2))
    hi = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))
    return m, lo, hi


def bootstrap_paired_ci(a, b, n_boot: int = N_BOOT, alpha: float = 0.05):
    """Percentile bootstrap CI for the paired mean difference (a - b)."""
    d = np.asarray(a, float) - np.asarray(b, float)
    m = float(d.mean())
    if len(d) < 2 or np.allclose(d, d[0]):
        return m, m, m
    idx = RNG.integers(0, len(d), size=(n_boot, len(d)))
    boot = d[idx].mean(axis=1)
    lo = float(np.percentile(boot, 100 * alpha / 2))
    hi = float(np.percentile(boot, 100 * (1 - alpha / 2)))
    return m, lo, hi


# ---------------------------------------------------------------- evaluation

def evaluate(factory, n_seeds: int = N_SEEDS):
    """Run a policy factory across seeds; return dict of metric -> array."""
    fields = ["responsiveness", "brownout_frac", "min_reserve", "efficiency"]
    out = {f: [] for f in fields}
    for seed in range(n_seeds):
        trace = make_trace(seed)
        m = run_policy(trace, factory(), seed)
        for f in fields:
            out[f].append(getattr(m, f))
    return {f: np.asarray(v, dtype=float) for f, v in out.items()}


# ---------------------------------------------------------------- sweeps

def sweep_static_dvfs():
    """StaticDVFS has one knob: the fixed duty scale."""
    return [(f"static-dvfs(scale={s:.2f})", (lambda s=s: StaticDVFS(scale=s)))
            for s in np.arange(0.10, 0.95, 0.05)]


def sweep_power_gating():
    """PowerGating has two: the off and on thresholds. Require high > low."""
    combos = []
    for low in np.arange(0.05, 0.40, 0.05):
        for high in np.arange(low + 0.10, 0.75, 0.05):
            combos.append((f"power-gating(low={low:.2f},high={high:.2f})",
                           (lambda lo=low, hi=high: PowerGating(low=lo, high=hi))))
    return combos


def best_safe(candidates, n_seeds: int = N_SEEDS):
    """Pick the candidate with highest responsiveness among those that are safe.

    Safe means brownout_frac <= BROWNOUT_TOLERANCE. If none qualify, fall back to
    the lowest-brownout candidate so the comparison is still against that
    baseline's most defensible setting.
    """
    scored = []
    for name, factory in candidates:
        res = evaluate(factory, n_seeds)
        scored.append((name, factory, res,
                       float(res["brownout_frac"].mean()),
                       float(res["responsiveness"].mean())))
    safe = [s for s in scored if s[3] <= BROWNOUT_TOLERANCE]
    pool = safe if safe else scored
    key = (lambda s: -s[4]) if safe else (lambda s: s[3])
    pool = sorted(pool, key=key)
    return pool[0], len(safe), len(scored)


# ---------------------------------------------------------------- main

def main() -> None:
    print(f"\nRobustness checks: {N_SEEDS} paired seeds, "
          f"{N_BOOT} bootstrap resamples, safety tolerance "
          f"brownout <= {BROWNOUT_TOLERANCE}\n")

    ours = evaluate(AdaptiveMetabolic)

    # ---- 1. Bootstrap CIs for our policy ----
    print("=" * 78)
    print("1. BOOTSTRAP CONFIDENCE INTERVALS (adaptive-metabolic)")
    print("=" * 78)
    print(f"{'metric':<18}{'mean':>10}{'boot 95% CI':>26}{'normal approx':>22}")
    print("-" * 78)
    for f, arr in ours.items():
        m, lo, hi = bootstrap_ci(arr)
        sem = arr.std(ddof=1) / np.sqrt(len(arr)) if len(arr) > 1 else 0.0
        print(f"{f:<18}{m:>10.3f}{f'[{lo:.3f}, {hi:.3f}]':>26}"
              f"{f'+-{1.96 * sem:.3f}':>22}")
    print("\nNote: where a metric is degenerate (e.g. brownout_frac all zeros) the")
    print("bootstrap correctly reports a zero-width interval; the normal")
    print("approximation reports the same, but only by accident.\n")

    # ---- 2. Baseline fairness sweep ----
    print("=" * 78)
    print("2. BASELINE FAIRNESS: is our win an artifact of baseline tuning?")
    print("=" * 78)

    for label, sweep in [("static-dvfs", sweep_static_dvfs()),
                         ("power-gating", sweep_power_gating())]:
        (name, factory, res, bo, resp), n_safe, n_total = best_safe(sweep)
        print(f"\n{label}: swept {n_total} configurations, "
              f"{n_safe} met the safety tolerance")
        print(f"  best defensible config: {name}")
        print(f"    responsiveness {resp:.1f}, brownout {bo:.3f}")

        d, dlo, dhi = bootstrap_paired_ci(ours["responsiveness"],
                                          res["responsiveness"])
        verdict = "SIGNIFICANT" if (dlo > 0 or dhi < 0) else "not significant"
        sign = "more" if d > 0 else "less"
        print(f"  ours vs best: {d:+.1f} responsiveness "
              f"[{dlo:+.1f}, {dhi:+.1f}]  ({verdict})")
        print(f"    -> adaptive-metabolic is {abs(d):.1f} spikes/event {sign} "
              f"responsive than the\n       best safely-tuned {label}.")

    print("\n" + "=" * 78)
    print("Interpretation")
    print("=" * 78)
    print("The headline comparison uses one hand-picked setting per baseline. This")
    print("sweep replaces each baseline with its own best safe configuration, which")
    print("is the strongest form of the comparison. Read the signs above: a")
    print("positive difference that survives this test is the claim worth making.")
    print("A negative one means the baseline, properly tuned, is better on")
    print("responsiveness and our contribution is the safety margin instead.\n")


if __name__ == "__main__":
    main()
