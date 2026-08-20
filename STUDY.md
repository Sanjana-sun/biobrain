# Learning BioBrain well enough to defend it

904 lines total. Read in this order. Budget one focused day.

## 1. `biobrain/neuron.py` (62 lines) — the LIF neuron
The thing Dahiya's group will ask about first.
- What is the membrane time constant, and where does it come from?
- What happens at threshold, and what does reset do?
- Is there a refractory period? Is leakage linear?
- **What does this model assume that silicon doesn't provide?**

## 2. `biobrain/storage.py` (40) — the supercapacitor
- How is stored energy represented? Joules, volts, or a normalized reserve?
- Is leakage modeled? Real supercaps self-discharge.
- Is there an efficiency loss on charge and discharge?

## 3. `biobrain/fuel_cell.py` (57) — the glucose/O2 cell
- What power does it deliver, and what is that number based on?
- Memory note: an earlier "~320 uW" figure was **wrong** and was corrected to
  ~180 uW/cm^2 (Rapoport 2012). Confirm what the file says now.
- Is output constant, or does it vary with fuel concentration?

## 4. `biobrain/metabolism.py` (51) — the regulator. Your novel contribution.
- What is the setpoint, and what happens without it? (Ablation says ~25% brownout.)
- Is the controller proportional? Integral? What is the gain?
- Why graded rather than binary? (Ablation: ~1380 vs ~250 spikes/event.)

## 5. `biobrain/policies.py` (92) — the four baselines
- Exactly how are fixed-rate, power-gating, and static-DVFS implemented?
- **Are they fair?** This is the question a reviewer asks. If static-dvfs is
  badly tuned, your win is an artifact. Be able to say how you chose its parameters.

## 6. `biobrain/simulation.py` (99) — the loop
- What is the timestep? Why that value?
- What counts as an "event," and how is responsiveness measured?
- What defines a brownout?

## 7. `experiments/compare_policies.py` (157) — the statistics
- What is randomized across the 30 seeds? (Read `traces.py`.)
- Is the CI a normal approximation? At n=30, is that defensible?
- What does "paired" mean here, and why does it matter?

## The test: can you break it on purpose?

Once you've read all seven, do this. It's the difference between having read the
code and understanding it.

1. Open `metabolism.py`, remove or zero the setpoint, predict the brownout rate
   **before** running, then run `python -m experiments.compare_policies`.
2. Double the supercapacitor capacity. Predict which metric moves and by how much.
3. Make the regulator binary instead of graded. Predict the responsiveness drop.

If your predictions land within the right ballpark, you own this. If they don't,
you've found the module you don't actually understand yet.

## Verified numbers (re-run Aug 17 2026)

```
policy                responsiveness     brownout    min_reserve   efficiency
fixed-rate             194.7 ± 15.9       0.980       0.000         1.978
power-gating           254.3 ± 50.4       0.000       0.140         1.810
static-dvfs           1940.8 ± 129.0      0.226       0.000         1.581
adaptive-metabolic    1408.4 ± 102.7      0.000       0.225         1.687
```

**The honest headline:** static-dvfs is more responsive than ours (1941 vs 1408)
but browns out 22.6% of the time. Ours achieves 1408 at zero brownout with the
highest safety margin, and is 5.5x more responsive than power-gating at equal
safety. We own the tradeoff; we do not win outright.

Say it that way. Overclaiming here is what gets caught.
