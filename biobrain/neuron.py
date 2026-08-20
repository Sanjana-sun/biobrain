"""Leaky integrate-and-fire (LIF) spiking network with a per-spike energy cost.

Each neuron integrates input current, leaks toward rest, and fires a spike when it
crosses threshold. Every spike costs energy drawn from the EnergyStore, mirroring the
real metabolic cost of an action potential. If the reserve can't pay, the spike is
suppressed (a brownout) -- which is exactly what the metabolic regulator exists to avoid.
"""

from __future__ import annotations

import numpy as np


class SpikingNet:
    def __init__(
        self,
        n: int = 64,
        tau_m_s: float = 0.02,          # membrane time constant (s)
        v_threshold: float = 1.0,
        v_reset: float = 0.0,
        energy_per_spike_uj: float = 0.5,  # metabolic cost of one spike (uJ)
        rng: np.random.Generator | None = None,
    ) -> None:
        self.n = n
        self.tau_m_s = tau_m_s
        self.v_threshold = v_threshold
        self.v_reset = v_reset
        self.energy_per_spike_uj = energy_per_spike_uj
        self.rng = rng or np.random.default_rng()
        self.v = np.zeros(n)

    def step(
        self,
        input_current: float,
        dt_s: float,
        store,
        rate_scale: float = 1.0,
    ) -> int:
        """Advance one timestep. Returns the number of spikes that actually fired.

        input_current : drive to the neurons (arbitrary units).
        rate_scale    : 0..1 gain from the metabolic regulator. Below 1 the network
                        deliberately dampens excitability to conserve energy.
        store         : EnergyStore; spikes are only emitted if it can pay for them.
        """
        rate_scale = float(np.clip(rate_scale, 0.0, 1.0))

        # Leaky integration with a bit of per-neuron heterogeneity/noise.
        drive = input_current * rate_scale + self.rng.normal(0.0, 0.05, self.n)
        self.v += dt_s / self.tau_m_s * (-self.v + drive)

        fired = np.where(self.v >= self.v_threshold)[0]

        spikes = 0
        for _ in fired:
            # Pay the metabolic bill per spike; suppress if the reserve is empty.
            if store.draw(self.energy_per_spike_uj):
                spikes += 1
            # Reset regardless (the neuron attempted to fire).
        self.v[fired] = self.v_reset

        return spikes
