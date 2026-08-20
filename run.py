"""Run the BioBrain scenario and plot the results.

Scenario: glucose availability starts healthy, crashes to near-starvation mid-run
(as it would if the host fasted or blood flow dropped), then recovers. We run the
system twice:

  * REGULATED  -- the metabolic regulator is active (BioBrain's novel behavior)
  * NAIVE      -- regulator disabled (always full speed), the conventional approach

The point: the naive system browns out and its spikes flatline once the reserve is
drained. The regulated system throttles early, protects its reserve, keeps computing
through the famine, and recovers -- exactly how biological tissue rides out low fuel.
"""

from __future__ import annotations

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from biobrain import BiofuelCell, EnergyStore, SpikingNet, MetabolicRegulator
from biobrain.simulation import Simulation, SimConfig


EVENT_START, EVENT_END = 37.5, 38.5  # urgent event during deep famine


def glucose_profile(t: float) -> float:
    """Healthy -> famine (t in [20,40]) -> recovery. Units: mM."""
    if t < 20.0:
        return 6.0
    if t < 40.0:
        # smooth crash to ~0.5 mM and back
        phase = (t - 20.0) / 20.0
        return 0.5 + 5.5 * (np.cos(np.pi * phase) * 0.5 + 0.5)
    return 6.0


def demand_profile(t: float) -> float:
    """A 4x urgent-input burst at deep famine: an event the device must respond to."""
    return 4.0 if EVENT_START <= t <= EVENT_END else 1.0


def run_variant(regulated: bool) -> dict:
    cfg = SimConfig(duration_s=60.0, dt_s=0.001, seed=1)
    rng = np.random.default_rng(cfg.seed)
    regulator = MetabolicRegulator()
    if not regulated:
        # Disable regulation: always full speed regardless of reserve.
        regulator.floor_scale = 1.0
        regulator.gain = 0.0
    sim = Simulation(
        cfg=cfg,
        cell=BiofuelCell(rng=rng),
        store=EnergyStore(),
        net=SpikingNet(rng=rng),
        regulator=regulator,
    )
    return sim.run(glucose_profile, demand_profile).as_arrays()


def spike_rate(spikes: np.ndarray, dt_s: float, window_s: float = 1.0) -> np.ndarray:
    """Smoothed population spike rate (spikes/s) via a moving average."""
    w = max(1, int(window_s / dt_s))
    kernel = np.ones(w) / (w * dt_s)
    return np.convolve(spikes, kernel, mode="same")


def main() -> None:
    reg = run_variant(regulated=True)
    naive = run_variant(regulated=False)
    dt = 0.001
    t = reg["t"]

    fig, axes = plt.subplots(4, 1, figsize=(10, 11), sharex=True)

    axes[0].plot(t, reg["glucose"], color="tab:green")
    axes[0].axvspan(20, 40, color="tab:red", alpha=0.08)
    axes[0].set_ylabel("glucose (mM)")
    axes[0].set_title("Fuel availability (famine shaded)")

    axes[1].plot(t, reg["power_uw"], color="tab:blue", alpha=0.6)
    axes[1].set_ylabel("cell power (uW)")
    axes[1].set_title("Biofuel cell output")

    axes[2].plot(t, reg["energy_level"], label="regulated", color="tab:purple")
    axes[2].plot(t, naive["energy_level"], label="naive", color="tab:gray", ls="--")
    axes[2].axhline(0.0, color="k", lw=0.6)
    axes[2].set_ylabel("energy reserve")
    axes[2].set_title("Energy reserve: regulated protects itself, naive browns out")
    axes[2].legend(loc="upper right")

    axes[3].plot(t, spike_rate(reg["spikes"], dt), label="regulated", color="tab:purple")
    axes[3].plot(t, spike_rate(naive["spikes"], dt), label="naive", color="tab:gray", ls="--")
    axes[3].axvspan(EVENT_START, EVENT_END, color="tab:orange", alpha=0.25)
    axes[3].set_ylabel("spike rate (Hz)")
    axes[3].set_xlabel("time (s)")
    axes[3].set_title(
        "Response to urgent event in famine (orange): regulated answers, naive can't"
    )
    axes[3].legend(loc="upper right")

    fig.tight_layout()
    fig.savefig("results.png", dpi=130)
    print("wrote results.png")

    # Quick numeric summary.
    def total(x):
        return int(np.sum(x))

    print(f"total spikes  regulated: {total(reg['spikes']):>7}")
    print(f"total spikes  naive    : {total(naive['spikes']):>7}")
    fam = (t >= 20) & (t <= 40)
    print(f"famine spikes regulated: {total(reg['spikes'][fam]):>7}")
    print(f"famine spikes naive    : {total(naive['spikes'][fam]):>7}")
    ev = (t >= EVENT_START) & (t <= EVENT_END)
    print(f"event spikes  regulated: {total(reg['spikes'][ev]):>7}  <- responds")
    print(f"event spikes  naive    : {total(naive['spikes'][ev]):>7}  <- brownout")
    print(f"min reserve   regulated: {reg['energy_level'].min():.3f}")
    print(f"min reserve   naive    : {naive['energy_level'].min():.3f}")


if __name__ == "__main__":
    main()
