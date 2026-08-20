"""The tuning cliff: why a fixed schedule has no viable operating point.

This is the mechanism argument behind adaptive throttling, made empirically.

A static duty cycle has one knob. Sweeping it reveals a discontinuity rather
than a tradeoff curve: below the cliff the network is idle (trivially safe, but
it computes nothing), and above it the network computes but immediately
surrenders its entire energy reserve. There is no setting that both computes and
holds a safety margin.

That is not a tuning failure. It is structural. A fixed schedule must be chosen
in advance for either the worst case, which wastes the average case, or the
average case, which fails under scarcity. A closed-loop regulator is what
escapes the dichotomy, because it re-chooses continuously.

Usage:  python -m experiments.tuning_cliff
"""

from __future__ import annotations

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from biobrain.policies import StaticDVFS, AdaptiveMetabolic
from experiments.robustness import evaluate

N_SEEDS = 20
SCALES = np.arange(0.10, 0.95, 0.05)


def main() -> None:
    print(f"\nStatic-DVFS parameter sweep ({N_SEEDS} paired seeds per point)\n")
    print(f"{'scale':>7}{'responsiveness':>16}{'brownout':>11}{'min_reserve':>13}")
    print("-" * 47)

    resp, bo, mr = [], [], []
    for s in SCALES:
        r = evaluate(lambda s=s: StaticDVFS(scale=s), N_SEEDS)
        resp.append(r["responsiveness"].mean())
        bo.append(r["brownout_frac"].mean())
        mr.append(r["min_reserve"].mean())
        print(f"{s:>7.2f}{resp[-1]:>16.1f}{bo[-1]:>11.3f}{mr[-1]:>13.3f}")

    resp, bo, mr = np.array(resp), np.array(bo), np.array(mr)
    ours = evaluate(AdaptiveMetabolic, N_SEEDS)
    o_resp = ours["responsiveness"].mean()
    o_bo = ours["brownout_frac"].mean()
    o_mr = ours["min_reserve"].mean()

    # Locate the cliff: the first scale at which the policy does real work.
    working = np.where(resp > 1.0)[0]
    print("\n" + "=" * 66)
    if len(working) and working[0] > 0:
        i = working[0]
        print(f"THE CLIFF is between scale={SCALES[i-1]:.2f} and scale={SCALES[i]:.2f}:")
        print(f"  scale={SCALES[i-1]:.2f}: responsiveness {resp[i-1]:.1f}, "
              f"brownout {bo[i-1]:.3f}, reserve {mr[i-1]:.3f}  <- idle, safe by doing nothing")
        print(f"  scale={SCALES[i]:.2f}: responsiveness {resp[i]:.1f}, "
              f"brownout {bo[i]:.3f}, reserve {mr[i]:.3f}  <- computes, reserve gone")
        print(f"\nThere is no static setting in between. The knob cannot express")
        print(f"'compute and keep a margin', because it cannot respond to state.")
    else:
        print("No cliff detected in this sweep; every setting does some work.")

    print(f"\nAdaptive-metabolic, for comparison:")
    print(f"  responsiveness {o_resp:.1f}, brownout {o_bo:.3f}, reserve {o_mr:.3f}")
    if len(working):
        i = working[0]
        print(f"\nAgainst the first working static setting (scale={SCALES[i]:.2f}):")
        print(f"  it is {resp[i]/o_resp:.2f}x our responsiveness,")
        print(f"  but holds {mr[i]/o_mr if o_mr else 0:.2f}x our safety margin")
        print(f"  and browns out {bo[i]:.1%} of the time versus our {o_bo:.1%}.")
    print("=" * 66 + "\n")

    # ---- Figure ----
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))

    ax[0].plot(SCALES, resp, "o-", color="#444", label="static-DVFS")
    ax[0].axhline(o_resp, ls="--", color="#c0392b", label="adaptive-metabolic")
    ax[0].set_xlabel("static duty scale")
    ax[0].set_ylabel("responsiveness (spikes/event)")
    ax[0].set_title("A fixed schedule cannot interpolate")
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=0.3)

    ax[1].plot(bo, mr, "o-", color="#444", label="static-DVFS sweep")
    ax[1].scatter([o_bo], [o_mr], s=110, marker="*", color="#c0392b",
                  zorder=5, label="adaptive-metabolic")
    ax[1].set_xlabel("brownout fraction (lower better)")
    ax[1].set_ylabel("min reserve (higher better)")
    ax[1].set_title("Safety plane: no static point is in the good corner")
    ax[1].legend(fontsize=8)
    ax[1].grid(alpha=0.3)

    fig.suptitle("The tuning cliff: why adaptive throttling is not just better "
                 "tuning", fontsize=11)
    fig.tight_layout()
    fig.savefig("tuning_cliff.png", dpi=130)
    print("wrote tuning_cliff.png\n")


if __name__ == "__main__":
    main()
