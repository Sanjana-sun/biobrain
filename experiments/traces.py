"""Randomized power/fuel traces and urgent-event schedules for the experiments.

Each seed produces a different but statistically comparable environment: a baseline
glucose supply punctuated by random famine dips, plus a random schedule of urgent
"events" (brief high-demand windows the device must respond to). Every policy is
evaluated on the *same* per-seed trace so comparisons are paired.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Trace:
    dt_s: float
    glucose: np.ndarray          # mM, per step
    demand: np.ndarray           # input-current multiplier, per step
    event_windows: list          # list of (start_idx, end_idx) for urgent events

    @property
    def duration_s(self) -> float:
        return len(self.glucose) * self.dt_s


def make_trace(
    seed: int,
    duration_s: float = 60.0,
    dt_s: float = 0.001,
    baseline_mM: float = 6.0,
    n_famines: int = 2,
    famine_depth_mM: float = 0.5,
    n_events: int = 6,
    event_dur_s: float = 1.0,
    event_demand: float = 4.0,
) -> Trace:
    rng = np.random.default_rng(seed)
    n = int(duration_s / dt_s)
    t = np.arange(n) * dt_s

    # Baseline glucose with a few smooth Gaussian famine dips at random times.
    glucose = np.full(n, baseline_mM, dtype=float)
    for _ in range(n_famines):
        center = rng.uniform(0.15, 0.85) * duration_s
        width = rng.uniform(4.0, 8.0)
        dip = (baseline_mM - famine_depth_mM) * np.exp(-((t - center) ** 2) / (2 * width ** 2))
        glucose -= dip
    glucose = np.clip(glucose, famine_depth_mM * 0.5, None)

    # Urgent events: brief high-demand windows at random times (kept non-overlapping-ish).
    demand = np.ones(n, dtype=float)
    ev_len = int(event_dur_s / dt_s)
    windows = []
    for _ in range(n_events):
        start = rng.integers(int(2.0 / dt_s), n - ev_len)
        end = start + ev_len
        demand[start:end] = event_demand
        windows.append((int(start), int(end)))
    windows.sort()

    return Trace(dt_s=dt_s, glucose=glucose, demand=demand, event_windows=windows)
