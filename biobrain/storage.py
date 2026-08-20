"""Energy-storage layer: a supercapacitor acting as the system's 'metabolism'.

Biology doesn't run neurons straight off food; it buffers energy in ATP and spends
it in bursts. We do the same: the weak, noisy biofuel cell trickle-charges a
supercapacitor, and the spiking network spends from that reserve. This decouples the
unstable source from the load and is what makes microwatt-scale computing survivable.

Energy is tracked in microjoules (uJ).
"""

from __future__ import annotations


class EnergyStore:
    def __init__(
        self,
        capacity_uj: float = 2000.0,   # usable energy capacity (uJ)
        charge_efficiency: float = 0.85,
        initial_frac: float = 0.5,     # start half-charged
    ) -> None:
        self.capacity_uj = capacity_uj
        self.charge_efficiency = charge_efficiency
        self.energy_uj = capacity_uj * initial_frac

    @property
    def level(self) -> float:
        """State of charge, 0..1."""
        return self.energy_uj / self.capacity_uj if self.capacity_uj > 0 else 0.0

    def charge(self, power_uw: float, dt_s: float) -> None:
        """Add energy from the fuel cell over dt (power_uw in uW, uW*s = uJ)."""
        added = power_uw * dt_s * self.charge_efficiency
        self.energy_uj = min(self.capacity_uj, self.energy_uj + added)

    def draw(self, energy_uj: float) -> bool:
        """Try to spend `energy_uj`. Returns True if the reserve could cover it."""
        if energy_uj <= self.energy_uj:
            self.energy_uj -= energy_uj
            return True
        return False
