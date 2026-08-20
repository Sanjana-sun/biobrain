"""Glucose / oxygen biofuel cell model.

Grounded in the real implanted-GBFC literature: an enzymatic glucose biofuel cell
implanted in a rat produced roughly 0.57 V open-circuit and ~39 uW of power
(Zebda et al., Nature Sci. Rep. 2013). MIT's silicon glucose fuel cell reached
~180 uW/cm^2 peak, up to hundreds of uW (Rapoport et al., PLOS ONE 2012).

We model instantaneous power output as enzyme-kinetics-limited (Michaelis-Menten)
in the glucose concentration, gated by oxygen availability, with realistic
measurement noise and slow electrode degradation. Output is in microwatts (uW).
"""

from __future__ import annotations

import numpy as np


class BiofuelCell:
    def __init__(
        self,
        p_max_uw: float = 320.0,     # modeling choice within the reported hundreds-of-uW range
        km_mM: float = 5.0,          # Michaelis constant (mM glucose) for half-max power
        noise_frac: float = 0.05,    # fractional Gaussian noise on output
        degradation_per_s: float = 2e-6,  # slow loss of capacity (electrode fouling)
        rng: np.random.Generator | None = None,
    ) -> None:
        self.p_max_uw = p_max_uw
        self.km_mM = km_mM
        self.noise_frac = noise_frac
        self.degradation_per_s = degradation_per_s
        self.health = 1.0  # 1.0 = pristine electrodes, decays over time
        self.rng = rng or np.random.default_rng()

    def power_uw(self, glucose_mM: float, oxygen_frac: float, dt_s: float) -> float:
        """Instantaneous electrical power (uW) available this timestep.

        glucose_mM  : glucose concentration (mM). Human blood ~4-8 mM.
        oxygen_frac : oxygen availability, 0..1 (1 = fully oxygenated).
        dt_s        : timestep length (s), used for degradation accounting.
        """
        glucose_mM = max(glucose_mM, 0.0)
        oxygen_frac = float(np.clip(oxygen_frac, 0.0, 1.0))

        # Michaelis-Menten saturation in glucose.
        mm = glucose_mM / (self.km_mM + glucose_mM)

        # Oxygen is the electron acceptor: no O2 -> no power, regardless of glucose.
        p = self.p_max_uw * mm * oxygen_frac * self.health

        # Multiplicative measurement/output noise, clamped non-negative.
        if self.noise_frac > 0:
            p *= max(0.0, 1.0 + self.rng.normal(0.0, self.noise_frac))

        # Slow irreversible electrode degradation.
        self.health = max(0.0, self.health - self.degradation_per_s * dt_s)

        return max(0.0, p)
