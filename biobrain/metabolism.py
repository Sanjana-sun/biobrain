"""Metabolic regulator -- the novel core of BioBrain.

Biological neural tissue does not brown out when fuel dips; it modulates its own
activity. This regulator does two things no off-the-shelf neuromorphic system does
together:

1. METABOLIC SELF-REGULATION: it converts the current energy reserve into a
   `rate_scale` (0..1) that throttles the spiking network. High reserve -> think fast.
   Low reserve -> drop toward a survival trickle, protecting the reserve from a
   brownout. A homeostatic setpoint pulls the reserve toward a healthy midband.

2. FUEL-AS-SENSOR: the glucose concentration that *powers* the device is also read as
   an *input signal*. The same molecule is both battery and data, so the device can be,
   e.g., a self-powered glucose monitor with no separate sensor.
"""

from __future__ import annotations

import numpy as np


class MetabolicRegulator:
    def __init__(
        self,
        setpoint: float = 0.5,        # target energy reserve level (0..1)
        floor_scale: float = 0.05,    # minimum activity (survival trickle)
        gain: float = 6.0,            # how sharply activity ramps with reserve
        glucose_ref_mM: float = 6.0,  # reference glucose for the sensor readout
    ) -> None:
        self.setpoint = setpoint
        self.floor_scale = floor_scale
        self.gain = gain
        self.glucose_ref_mM = glucose_ref_mM

    def rate_scale(self, energy_level: float) -> float:
        """Map energy reserve (0..1) -> compute rate scale (floor..1).

        A logistic around the setpoint: below setpoint activity falls off fast to
        protect the reserve; above it, activity saturates toward full speed.
        """
        x = self.gain * (energy_level - self.setpoint)
        s = 1.0 / (1.0 + np.exp(-x))
        return float(self.floor_scale + (1.0 - self.floor_scale) * s)

    def sense_glucose(self, glucose_mM: float) -> float:
        """Fuel-as-sensor: normalized glucose readout derived from the same fuel.

        Returns glucose relative to the reference (1.0 == reference level). In a real
        device this comes from the fuel cell's own current, so no extra sensor exists.
        """
        return glucose_mM / self.glucose_ref_mM if self.glucose_ref_mM > 0 else 0.0
