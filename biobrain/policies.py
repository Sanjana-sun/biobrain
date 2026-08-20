"""Power-management policies for an energy-harvesting spiking network.

Each policy maps the current energy reserve level (0..1) to a `rate_scale` (0..1) that
gates the spiking network. These are the comparison points for the paper: our adaptive
metabolic regulator must be measured against the established alternatives, not a strawman.

Policies (all expose `.reset()` and `.rate_scale(level)`):

  FixedRate      -- always full speed. The naive baseline; ignores energy state.
  PowerGating    -- the intermittent/batteryless-computing baseline (cf. Hibernus):
                    run until the reserve drops below `low`, then halt until it refills
                    above `high` (hysteresis). Binary on/off, no graded response.
  StaticDVFS     -- run at a fixed reduced rate always. Conservative constant throttle.
  AdaptiveMetabolic -- OUR CONTRIBUTION: graded logistic throttle around a homeostatic
                    setpoint, so activity degrades smoothly and the reserve is protected
                    while still allowing bursts when reserve is healthy.
"""

from __future__ import annotations

import numpy as np


class Policy:
    name = "base"

    def reset(self) -> None:  # noqa: D401 - stateful policies override
        pass

    def rate_scale(self, level: float) -> float:
        raise NotImplementedError


class FixedRate(Policy):
    name = "fixed-rate"

    def rate_scale(self, level: float) -> float:
        return 1.0


class PowerGating(Policy):
    """Intermittent-computing baseline: hysteretic on/off around the reserve."""

    name = "power-gating"

    def __init__(self, low: float = 0.15, high: float = 0.45) -> None:
        self.low = low
        self.high = high
        self._on = True

    def reset(self) -> None:
        self._on = True

    def rate_scale(self, level: float) -> float:
        if self._on and level <= self.low:
            self._on = False
        elif (not self._on) and level >= self.high:
            self._on = True
        return 1.0 if self._on else 0.0


class StaticDVFS(Policy):
    """Constant reduced rate, chosen offline. No adaptation to reserve state."""

    name = "static-dvfs"

    def __init__(self, scale: float = 0.5) -> None:
        self.scale = float(np.clip(scale, 0.0, 1.0))

    def rate_scale(self, level: float) -> float:
        return self.scale


class AdaptiveMetabolic(Policy):
    """Our contribution: graded homeostatic throttle (logistic around setpoint)."""

    name = "adaptive-metabolic"

    def __init__(
        self,
        setpoint: float = 0.5,
        floor_scale: float = 0.05,
        gain: float = 6.0,
    ) -> None:
        self.setpoint = setpoint
        self.floor_scale = floor_scale
        self.gain = gain

    def rate_scale(self, level: float) -> float:
        x = self.gain * (level - self.setpoint)
        s = 1.0 / (1.0 + np.exp(-x))
        return float(self.floor_scale + (1.0 - self.floor_scale) * s)
