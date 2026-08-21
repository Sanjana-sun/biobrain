# BioBrain

**[Interactive demo →](https://sanjana-sun.github.io/biobrain/)** — the simulation
runs live in the browser: adjust cell power, store capacity and regulator
parameters, run the four-policy comparison with bootstrap CIs, and sweep the
static duty scale to see the tuning cliff.


A brain-inspired (neuromorphic) computing unit that **powers itself from glucose and
oxygen**, **senses that same fuel as its input**, and **automatically scales its own
thinking speed to how much energy is available** — the way biological neural tissue does.

This repo is the **software half** of a hybrid prototype: a physically-grounded
simulation of the whole system. The **hardware half** (a real biofuel cell powering a
load) is specified in [`hardware/BUILD.md`](hardware/BUILD.md).

## Why this is novel

The individual pieces are proven in the literature:

- Glucose biofuel cells have powered electronics *inside a living rat* (~39 uW).
- MIT built a silicon glucose fuel cell to power brain implants (~180 uW/cm^2 peak;
  up to hundreds of uW, Rapoport et al., PLOS ONE 2012).
- Ultra-low-power spiking-neuron chips exist.

What has **not** shipped is the clean fusion of the two into one self-regulating unit.
BioBrain models exactly that, with two features that are the actual research thesis:

1. **Metabolic self-regulation.** The network's firing rate scales with available
   energy. Fuel high -> it thinks fast. Fuel low -> it drops to a survival trickle
   instead of browning out. This turns the biofuel cell's biggest weakness (tiny,
   unstable power) into biological behavior.
2. **Fuel-as-sensor.** The glucose that powers the chip is *also* the input signal.
   Power source and sensor collapse into one component (e.g. a self-powered glucose
   monitor).

## Architecture

```
  glucose + O2                                        spikes / output
       |                                                     ^
       v                                                     |
 [ BiofuelCell ] --power--> [ EnergyStore ] --budget--> [ SpikingNet ]
   fuel_cell.py             (supercap, ATP     storage.py    neuron.py
                             analog)                |
       |                                            |
       +--glucose level as signal--> [ MetabolicRegulator ] <--energy level--+
                                        metabolism.py
                                     (scales compute rate; the novel part)
```

## Run it

```bash
pip install -r requirements.txt
python run.py
```

This runs a scenario where glucose availability rises and falls over time and produces
`results.png` showing the cell output, the energy reserve, and how the network throttles
its own spiking to stay alive — the metabolic-regulation behavior in action.

## Reproducing the results

Every figure is produced by one command with fixed seeds:

```bash
python run.py                                  # results.png  -- single-run intuition
python -m experiments.compare_policies         # policy_comparison.png -- 4 policies, 30 seeds, 95% CI
python -m experiments.pareto_ablation          # pareto_ablation.png -- Pareto frontier + ablations
python -m experiments.robustness               # bootstrap CIs + baseline-fairness sweep
python -m benchmark.run_benchmark              # benchmark_accuracy.png -- FashionMNIST under intermittent power
```

### Policy comparison, verbatim (30 paired seeds, mean +/- 95% CI)

| policy | responsiveness | brownout_frac | min_reserve | efficiency |
|---|---|---|---|---|
| fixed-rate | 194.7 +/- 15.9 | **0.980** +/- 0.000 | 0.000 | 1.978 |
| power-gating | 254.3 +/- 50.4 | 0.000 +/- 0.000 | 0.140 | 1.810 |
| static-dvfs | **1940.8** +/- 129.0 | 0.226 +/- 0.023 | 0.000 | 1.581 |
| **adaptive-metabolic** | 1408.4 +/- 102.7 | **0.000** +/- 0.000 | **0.225** | 1.687 |

**Read this honestly.** static-dvfs is *more* responsive than ours (1941 vs 1408);
it simply browns out 22.6% of the time and keeps no safety margin. Ours reaches
1408 at zero brownout with the largest minimum reserve, and is 5.5x more
responsive than power-gating at equal (zero) brownout. **We own the
responsiveness-safety tradeoff; we do not win outright.**

`experiments/robustness.py` stress-tests that claim two ways: percentile
bootstrap CIs instead of a normal approximation (which is invalid for bounded,
often-degenerate metrics like brownout_frac), and a sweep over each baseline's
own parameters so the comparison runs against each baseline's *best safe*
configuration rather than one hand-picked setting.

Headline findings (see `PAPER/`):
- Among zero-brownout policies, adaptive-metabolic is ~5.6x more responsive than
  power-gating at equal safety (Pareto).
- Ablation: the *graded* throttle matters (graded ~1380 vs binary ~250 spikes/event at
  the same zero brownout); the homeostatic setpoint prevents ~25% brownout.
- On FashionMNIST under an intermittent biofuel-cell budget, adaptive-metabolic gives the
  best overall (0.841) and famine-time (0.824) accuracy; binary power-gating collapses to
  0.246 during scarcity. (Honest caveat: because all graded policies degrade gracefully,
  adaptive's margin over fixed-rate on this easy task is small; the sharp separation is in
  the safety/brownout metrics and would widen on harder tasks / tighter power.)

## Files

| File | Role |
|------|------|
| `biobrain/fuel_cell.py` | glucose/O2 biofuel cell: uW output, noise, depletion |
| `biobrain/storage.py`   | supercapacitor energy reserve (ATP analog) |
| `biobrain/neuron.py`    | leaky integrate-and-fire spiking network, energy cost per spike |
| `biobrain/metabolism.py`| metabolic regulator (novel feature) |
| `biobrain/simulation.py`| ties it together, steps the whole system |
| `biobrain/policies.py`  | baseline + adaptive power-management policies |
| `run.py`                | single-run scenario + plots |
| `experiments/`          | multi-seed comparison, Pareto frontier, ablations |
| `benchmark/`            | FashionMNIST rate-coded SNN under intermittent power |
| `hardware/BUILD.md`     | physical Tier-2 build plan |
| `PAPER/`                | roadmap, outline, verified related-work review |
