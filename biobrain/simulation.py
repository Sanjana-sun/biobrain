"""Ties the four modules into one stepping system and records a trace.

Each step:
  1. fuel cell produces power from current glucose + oxygen
  2. that power trickle-charges the energy store
  3. the metabolic regulator reads the reserve -> rate_scale, and reads glucose (sensor)
  4. the spiking net runs at that rate, paying per-spike energy from the store
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from .fuel_cell import BiofuelCell
from .storage import EnergyStore
from .neuron import SpikingNet
from .metabolism import MetabolicRegulator


@dataclass
class SimConfig:
    duration_s: float = 60.0
    dt_s: float = 0.001            # 1 ms steps
    input_current: float = 1.2     # baseline drive to the network
    oxygen_frac: float = 1.0       # assume well-oxygenated unless overridden
    seed: int = 0


@dataclass
class Trace:
    t: list = field(default_factory=list)
    glucose: list = field(default_factory=list)
    power_uw: list = field(default_factory=list)
    energy_level: list = field(default_factory=list)
    rate_scale: list = field(default_factory=list)
    spikes: list = field(default_factory=list)
    glucose_sensed: list = field(default_factory=list)

    def as_arrays(self):
        return {k: np.asarray(v) for k, v in self.__dict__.items()}


class Simulation:
    def __init__(
        self,
        cfg: SimConfig | None = None,
        cell: BiofuelCell | None = None,
        store: EnergyStore | None = None,
        net: SpikingNet | None = None,
        regulator: MetabolicRegulator | None = None,
    ) -> None:
        self.cfg = cfg or SimConfig()
        rng = np.random.default_rng(self.cfg.seed)
        self.cell = cell or BiofuelCell(rng=rng)
        self.store = store or EnergyStore()
        self.net = net or SpikingNet(rng=rng)
        self.regulator = regulator or MetabolicRegulator()

    def run(
        self,
        glucose_profile: Callable[[float], float],
        demand_profile: Callable[[float], float] | None = None,
    ) -> Trace:
        """Run the sim.

        glucose_profile(t) -> glucose (mM) at time t.
        demand_profile(t)  -> input-current multiplier at time t (default 1.0).
                              Use it to inject transient 'urgent event' bursts the
                              device must respond to.
        """
        cfg = self.cfg
        tr = Trace()
        steps = int(cfg.duration_s / cfg.dt_s)

        for i in range(steps):
            t = i * cfg.dt_s
            glucose = max(0.0, glucose_profile(t))
            demand = demand_profile(t) if demand_profile is not None else 1.0

            power = self.cell.power_uw(glucose, cfg.oxygen_frac, cfg.dt_s)
            self.store.charge(power, cfg.dt_s)

            scale = self.regulator.rate_scale(self.store.level)
            sensed = self.regulator.sense_glucose(glucose)

            spikes = self.net.step(cfg.input_current * demand, cfg.dt_s, self.store, scale)

            tr.t.append(t)
            tr.glucose.append(glucose)
            tr.power_uw.append(power)
            tr.energy_level.append(self.store.level)
            tr.rate_scale.append(scale)
            tr.spikes.append(spikes)
            tr.glucose_sensed.append(sensed)

        return tr
