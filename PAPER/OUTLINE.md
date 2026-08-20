# Paper Outline (working title)

**Metabolic Self-Regulation for Energy-Harvesting Spiking Networks:
A Responsiveness-Safety Trade-off Beyond Intermittent Computing**

Format: ~6-8 page workshop paper (double-column) + arXiv. Placeholder author block:
independent researcher; seek an endorser/co-author for arXiv `cs.NE`.

---

## Abstract (~150 words)
Batteryless, energy-harvesting neuromorphic devices must compute through unstable,
microwatt power. Conventional responses either ignore the energy state (fixed-rate),
halt and restart (intermittent computing), or run at a fixed derated clock (static DVFS).
We introduce **metabolic self-regulation**: a homeostatic controller that continuously
scales a spiking network's activity to its stored-energy reserve, mimicking how neural
tissue modulates activity with fuel. Across N randomized harvested-power environments and
a [benchmark] task, metabolic regulation attains the **best responsiveness-vs-safety
trade-off**, near-maximal event responsiveness with **zero brownout** and the largest
energy safety margin, dominating the baselines on the Pareto frontier. We validate the
model on a **battery-free hardware prototype** powered by a biofuel cell, where measured
throttling tracks the simulation. We also show **fuel-as-sensor** operation: the powering
current doubles as the input signal.

## 1. Introduction
- Batteryless bioelectronics need to survive intermittent microwatt power.
- Gap: existing power management is energy-blind, binary, or static; none give graded,
  reserve-aware control for SNNs.
- Contributions (bulleted): (1) metabolic-regulation policy; (2) paired multi-seed
  Pareto evaluation vs. three baselines; (3) hardware validation; (4) fuel-as-sensor.

## 2. Related Work
- Intermittent / batteryless computing (checkpoint-restore). -> our power-gating baseline.
- Energy-harvesting & low-power SNNs; neuromorphic DVFS. -> static-DVFS baseline.
- Biofuel cells and implantable bioelectronics. -> power model + hardware grounding.
- Positioning paragraph: what is new = graded homeostatic reserve feedback for SNNs.

## 3. System Model
- Biofuel cell (Michaelis-Menten in glucose, O2 gating, noise, degradation) -- grounded
  in cited measurements.
- Supercapacitor energy store (the "metabolism" buffer).
- LIF spiking network with per-spike energy cost.
- Policies: fixed-rate, power-gating, static-DVFS, adaptive-metabolic (logistic setpoint).
- (equations for each; a system block diagram figure)

## 4. Experimental Setup
- Randomized power/fuel traces + urgent-event schedule; paired across policies.
- Benchmark task ([Google Speech Commands / N-MNIST]) under an intermittent power budget.
- Metrics: task accuracy/F1, event responsiveness, brownout fraction, min reserve,
  spikes/uJ. Stats: >=30 seeds, 95% CI, paired tests, bootstrap.

## 5. Results
- 5.1 Main comparison table (the four policies). [from compare_policies.py, upgraded]
- 5.2 Pareto frontier: responsiveness vs. brownout across a setpoint/gain sweep; ours
  dominates. [KEY FIGURE]
- 5.3 Ablations: graded vs. binary; with/without setpoint; supercap-size sweep.
- 5.4 Sensitivity: +/-50% on grounded parameters; conclusions stable.
- 5.5 Hardware validation: measured V/I, harvested trace, battery-free throttling demo,
  measured-vs-simulated overlay. [KEY FIGURE]
- 5.6 Fuel-as-sensor: powering current vs. known glucose; calibration curve.

## 6. Discussion
- Why graded beats binary under microwatt intermittency.
- Limitations: single-task hardware, small network, model idealizations.
- Toward implantable closed-loop use; safety.

## 7. Conclusion
- Metabolic regulation = a simple, biologically-grounded, Pareto-dominant power policy for
  batteryless neuromorphic devices, validated in hardware.

## Reproducibility Statement
- Public code, pinned deps, fixed seeds, measured-data CSVs, one-command figures.

## Figures (target 5-6)
1. System block diagram (fuel -> cell -> store -> regulator -> SNN -> output).
2. Single-run trace (glucose, power, reserve, spikes) -- the intuition. [have: results.png]
3. Four-policy comparison with 95% CI. [have: policy_comparison.png]
4. Pareto frontier (responsiveness vs. brownout). [to build]
5. Hardware: measured-vs-simulated throttling. [to build]
6. Fuel-as-sensor calibration. [to build]
