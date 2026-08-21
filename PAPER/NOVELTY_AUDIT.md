# Novelty audit, Aug 2026

Four independent literature sweeps against the three claims in the paper. All
DOIs below were verified against CrossRef, Europe PMC, or the arXiv API by the
sweeps that found them.

**Summary: all three claims as currently written are unsafe. A narrower paper
survives, and one finding is stronger than anything currently claimed.**

---

## Claim 1 — "mirrors how biological neural tissue modulates firing with fuel
availability"

**Status: contradicted. Already withdrawn from the repo.**

- **Padamsey et al. (2022), *Neuron* 110(2):280-296.e10.**
  [10.1016/j.neuron.2021.10.024](https://doi.org/10.1016/j.neuron.2021.10.024)
  Food restriction in mouse V1 cut AMPA conductance and synaptic ATP use by 29%,
  paid for by a 32% broadening of orientation tuning. Verbatim: "neurons spiked at
  similar rates as controls but spent less ATP on underlying excitatory currents."
  **Cortex defended firing rate and sacrificed precision. We do the reverse.**
- **Howarth et al. (2012)** [10.1038/jcbfm.2012.35](https://doi.org/10.1038/jcbfm.2012.35):
  spikes are only ~21% of cortical signalling ATP; postsynaptic receptors are 50%.
  Throttling rate is the *weaker* lever.
- **Turrigiano (2008)** / **Hengen et al. (2016)**: a dedicated homeostat defends a
  firing-rate set point and would actively oppose our intervention.
- **Attwell et al. (2010)** / **Nippert et al. (2023)**: the physiological response
  to low fuel is supply-side. Cortex *vasodilated* under hypoglycemia rather than
  reducing computation.

**What survives:** the normative argument. **Levy & Baxter (1996)**
[10.1162/neco.1996.8.3.531](https://doi.org/10.1162/neco.1996.8.3.531) proves
optimal firing rate *falls* as per-spike cost *rises*. **Lennie (2003)** derives a
~0.16 spikes/s/neuron budget. **Tanner et al. (2011)**
[10.1523/JNEUROSCI.5951-10.2011](https://doi.org/10.1523/JNEUROSCI.5951-10.2011)
shows genuine closed-loop metabolic feedback: a neuron's own spiking depletes
submembrane ATP, opening K_ATP channels. That is enough for a normative framing
and no more. (Note: this literature is widely miscited as "Levy & Baddeley." The
second author is Baxter.)

---

## Claim 2 — "fuel-as-sensor": the glucose that powers the device is also the input

**Status: not novel. Twenty-five years old, and the strong form is published.**

- **Katz, Bückmann & Willner (2001), *JACS* 123(43):10752-10753.**
  [10.1021/ja0167102](https://doi.org/10.1021/ja0167102) The founding
  demonstration: a glucose/O2 cell whose output *is* the analyte signal.
- **Zhou & Dong (2011), *Acc. Chem. Res.* 44(11):1232-1243.**
  [10.1021/ar200096g](https://doi.org/10.1021/ar200096g) Names the category
  **"self-powered logic biosensors"**: biofuel cells whose biochemical inputs are
  processed as Boolean variables and whose power output is the computed result.
- **Zhou, Kuralay, Windmiller & Wang (2012), *Chem. Commun.* 48(32):3815-3817.**
  [10.1039/c2cc30464c](https://doi.org/10.1039/c2cc30464c) A biofuel cell with an
  internal DNAzyme logic system whose power output follows a truth table.
- **Slaughter & Kulkarni (2017), *Sci. Rep.* 7:1471.**
  [10.1038/s41598-017-01665-9](https://doi.org/10.1038/s41598-017-01665-9) The cell
  powers a microelectronic device *and* the capacitor charge/discharge frequency
  encodes glucose. 37.66 Hz/mM·cm², 1-20 mM.
- **Shitanda et al. (2021), *ACS Sensors* 6(9):3409-3415.**
  [10.1021/acssensors.1c01266](https://doi.org/10.1021/acssensors.1c01266) A BFC
  powers a wireless transmitter whose transmission frequency encodes urine glucose.

**Two problems worse than the novelty gap:**

1. **Structural identifiability, not noise.** **Zebda et al. (2018)**
   [10.1016/j.bioelechem.2018.05.011](https://doi.org/10.1016/j.bioelechem.2018.05.011)
   report that fibrous encapsulation thickens over weeks and throttles glucose
   transport to the electrode. That multiplies the fuel-to-power transfer function
   by an unobservable, drifting, monotonically worsening gain. In a fuel-as-sensor
   architecture, signal, power, and gain are the *same measurement*, so **there is
   no reference channel left to recalibrate against.**
2. **The O2 confound.** These are glucose/O2 cells. Power depends on both, so the
   device cannot distinguish a glucose drop from a local pO2 drop. **Jin et al.
   (2020)** [10.1016/j.bios.2020.112493](https://doi.org/10.1016/j.bios.2020.112493)
   models oxygen starvation explicitly and shows sensitivity and dynamic range are
   *independently tunable* — which also means our scalar abstraction is strictly
   weaker than a 2020 result.

**Reality check on the power budget.** Our default 320 µW is optimistic by a wide
margin. Tear glucose gives **~1 µW/cm²** with a >20 h half-life (**Falk et al.
2012**). Implanted glucose gives ~194 µW/cm² (**Zebda et al. 2013**) but the only
2-month in-vivo telemetry study duty-cycled at **30 min/day** (**El Ichi-Ribault
et al. 2018** [10.1016/j.electacta.2018.02.156](https://doi.org/10.1016/j.electacta.2018.02.156)),
a factor of ~48 below continuous.

**Narrowest defensible version:** that the powered computation is *non-trivial*
(not a logic gate, not a relaxation oscillator) and the fuel signal enters as a
*continuous-valued* input. That claim requires citing all five papers above in the
same paragraph and saying exactly what they did not do.

---

## Claim 3 — "graded homeostatic reserve-feedback control"

**Status: the control law is textbook. Two papers are close enough to require a
direct response.**

**What the mechanism is actually called:** **state-of-charge droop control.**
- **Lu et al. (2014), *IEEE TIE* 61(6):2804-2815.**
  [10.1109/TIE.2013.2279374](https://doi.org/10.1109/TIE.2013.2279374) Makes the
  droop coefficient a function of measured SoC so delivered power scales with
  reserve. This is our control law, as standard practice in DC microgrids.

**Novelty threats, ranked:**

1. **ASPEN (2025)** [arXiv:2508.11689](https://arxiv.org/abs/2508.11689) — *Adaptive
   Spiking with Plasticity for Energy Aware Neuromorphic Systems.* Makes the
   **neuronal firing threshold a runtime-controllable energy knob** in an SNN,
   trading spike count against accuracy with no retraining. **Same substrate, same
   idea of a dialable SNN energy knob.** The sweep could not retrieve full text.
   **Read this before submitting.** If ASPEN also closes a loop on measured
   reserve, our contribution collapses to the setpoint formalism.
2. **Vigorito, Ganesan & Barto (2007), IEEE SECON, pp. 21-30.**
   [10.1109/SAHCN.2007.4292814](https://doi.org/10.1109/SAHCN.2007.4292814)
   Setpoint-tracking control of an energy buffer by modulating compute duty cycle,
   using linear-quadratic tracking with online system identification. Best paper.
   **A better controller than ours, nineteen years earlier.**
3. **Islam et al. (2025)** [arXiv:2503.06663](https://arxiv.org/abs/2503.06663) —
   energy-adaptive checkpoint-free intermittent inference. Read available energy,
   scale the amount of neural computation. Same concept on DNNs, one year earlier.
   (This resolves the standing TODO: authors are Islam, Wei, Banarjee, Pan; arXiv
   preprint only, no venue found.)
4. **REACT (Williams & Hicks, ASPLOS 2024)**
   [10.1145/3620666.3651370](https://doi.org/10.1145/3620666.3651370) — continuously
   varies total capacitance against net input power, improving event responsiveness
   **7.7x**. Together with **Zhan et al. (2022)**
   [10.1109/TCAD.2021.3068946](https://doi.org/10.1109/TCAD.2021.3068946) and
   **Capybara (Colin et al., ASPLOS 2018)**
   [10.1145/3173162.3173210](https://doi.org/10.1145/3173162.3173210), **this kills
   our supercapacitor-sizing finding as a novel result.**

**Two technical corrections we should make before anyone else does:**

- **"Homeostatic" is the wrong word.** A pure proportional law has a structural
  steady-state offset of roughly `disturbance / K_p`; it cannot hold the setpoint
  under sustained net-power disturbance. Homeostasis with zero steady-state error
  requires *integral* feedback (**Briat, Gupta & Khammash, 2016**
  [10.1016/j.cels.2016.01.004](https://doi.org/10.1016/j.cels.2016.01.004)). Either
  add an integral term or rename the setpoint a droop reference and report the offset.
- **The capacitor-size finding is a plant property, not a result.** Capacitance sets
  the dominant plant time constant, so loop bandwidth scales as 1/C at fixed gain.
  Normalize gain by capacitance and show responsiveness becomes size-invariant;
  otherwise it reads as rediscovering τ = RC.

**Untested failure modes** the sweep flagged, all worth an experiment: steady-state
droop error; limit cycling at high gain (report gain and phase margin); integrator
windup under rate saturation; brownout chatter without hysteresis; loss of control
authority at low SoC when fixed leakage dominates; a **throttling death spiral**
where lowering the rate stretches an inference over more wall-clock time and raises
per-inference leakage energy; and load-correlated SoC measurement error from IR drop.

---

## What actually survives, and the better paper hiding in this

**The strongest finding in the repo is not any of the three claims.** It is the
**tuning cliff** (`experiments/tuning_cliff.py`): a static duty cycle has *no
viable operating point*. Below scale 0.20 the network is idle and trivially safe;
at 0.25 it computes but its reserve collapses to 0.038 and it browns out. Nothing
in between exists, because a fixed knob cannot observe the reserve.

That is a mechanism argument about open-loop versus closed-loop control under a
non-forecastable signal, and it is not in any of the prior art above.

**The reframe this audit supports:**

1. **Lead with the cliff**, framed as: forecastable disturbances permit scheduling;
   a reserve is not forecastable, because the only way it grows is by not spending
   it. Open-loop control has no viable point in that regime. That distinguishes us
   from every carbon-aware and solar-aware scheduler, which adapt to *external,
   predictable* signals.
2. **Implement the Padamsey policy as a competing baseline.** Cortex preserves rate
   and cuts precision. Nobody has compared rate-throttling against
   precision-throttling under a hard brownout floor. This turns the most damaging
   finding into the paper's most interesting experiment, and it requires adding a
   synaptic-conductance energy term the model currently lacks — which is also the
   Howarth (2012) correction, since synapses are 50% of the ATP and we charge only
   for spikes.
3. **Demote fuel-as-sensor to a design note**, citing Katz 2001, Zhou & Dong 2011,
   Slaughter 2017, and Shitanda 2021, and stating the identifiability problem
   plainly rather than presenting it as a feature.
4. **Rename the controller** SoC droop control, cite Lu 2014 and Vigorito 2007,
   and position the contribution as the *actuator* (spike rate) plus the cliff
   result, not the control law.

**One query the sweep could not run before exhausting its budget:** "closed-loop
supercapacitor SoC feedback controlling a spiking network." Run that before
submitting. It is the exact phrasing that would surface a direct hit.
