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

## FINAL VERDICT after all four sweeps

The two remaining sweeps returned harder findings than the first two. Stated plainly:
**as a simulation paper, this has no novel contribution left.** Every
simulation-level claim is owned by prior art. What survives is entirely in the
hardware.

### The near-kill: ASPEN

**Calle-Ortiz, Guan, Ganesan & Nguyen (2025). "ASPEN: Adaptive Spiking with
Plasticity for Energy Aware Neuromorphic Systems."**
[arXiv:2508.11689](https://arxiv.org/abs/2508.11689), Aug 2025. Full text read.
Verbatim from the paper:

> "ASPEN dynamically adjusts the firing thresholds of spiking neurons during
> inference, enabling real-time control over spiking activity in response to
> available energy... an **energy monitor** informs an **Energy-Aware Threshold
> Adaptation** module that modulates neuron thresholds based on the **current
> energy budget**." ... "threshold modulation enables **continuous and graceful**
> control within a single model."

Validated on SynSense Xylo IMU hardware, motivated by "energy-harvesting
environments" and "battery-free wearable devices." **This is our mechanism, our
actuator, our "graded not binary" framing, one year earlier, in silicon.**

**The one and only gap:** ASPEN's energy budget is an *exogenous scalar* in a
`Select(E)` function, and the evaluation is an **open-loop threshold sweep**
(theta = 0.6 to 2.4 in 0.2 steps) that "simulates varying energy constraints."
No harvester. No supercapacitor. No measured state of charge. No closed loop.

### The crux argument is not just unoriginal, it is contradicted

**Shresthamali, Kondo & Nakamura (2017). ACM TECS 17(4), Article 39.** Verbatim:

> "The **Naive** policy is the simplest adaptive policy. It is battery-centric in
> that **the duty cycle is proportional to the battery reserve level**... While
> this policy is simple to implement, **it is not very intelligent**."

They measure it: the Naive policy has the **worst** RMS deviation from energy
neutrality of every policy tested, >23% against 3.46% for their RL policy.

So reserve-proportional control is (a) the field's named strawman baseline, and
(b) known to *lose*. The field's consensus is that **predictive** control beats
both graded and threshold. Our paper argues graded beats threshold, which is the
wrong axis entirely.

**Buchli et al. (SenSys 2014)** [10.1145/2668332.2668333](https://doi.org/10.1145/2668332.2668333)
says it directly of Vigorito and of PID-on-supercapacitor: "both of these
approaches suffer from **high duty-cycle variability**, and rely on a
well-performing battery State-of-Charge approximation algorithm." Measured
duty-cycle variance three orders of magnitude worse than their model-based scheme.

### The control law, exactly, from 2007 and 2012

- **Vigorito, Ganesan & Barto (2007), IEEE SECON, best paper.**
  [10.1109/SAHCN.2007.4292814](https://doi.org/10.1109/SAHCN.2007.4292814)
  Closed-form law `u_t = (y* - (a+c)y_t + c y*) / b` where `y_t` **is** battery
  state of charge and `u_t` **is** duty cycle. Continuous, monotone, affine in
  instantaneous reserve, gains self-tuned online. In their words: "using only the
  current battery level of the node to make duty-cycling decisions." Known in that
  literature as **ENO-Max**.
- **Le, Sentieys, Berder, Pegatoquet & Belleudy (2012), IEEE GreenCom.**
  [10.1109/GreenCom.2012.107](https://doi.org/10.1109/GreenCom.2012.107)
  A **PID controller** on supercapacitor voltage setting the node's wake-up
  period. The literal "PID on the capacitor sets the rate" claim.

Also anticipating the continuous reserve-to-rate map: **Ait Aoudia et al. (2016)**
Fuzzyman [10.1109/ICC.2016.7510767](https://doi.org/10.1109/ICC.2016.7510767);
**Peng & Low (2014)** P-FREEN [10.1016/j.adhoc.2013.08.015](https://doi.org/10.1016/j.adhoc.2013.08.015);
**Moser et al. (2007/2010)** piecewise-affine state feedback
[10.1109/TC.2009.158](https://doi.org/10.1109/TC.2009.158); and
**REHASH (Bakar et al., IMWUT 2021)** [10.1145/3478077](https://doi.org/10.1145/3478077),
which defines capacitor voltage as a proportional "signal" driving task
performance modulation, i.e. a framework in which our policy is one expressible
instance.

Reserve-state feedback setting neural computation depth: **Bullo, Jardak,
Carnelli & Gunduz (2024)** [arXiv:2411.02471](https://arxiv.org/abs/2411.02471) —
"the model to be employed, or the exit point is then dynamically chosen **based on
the energy storage and harvesting process states**." Discrete actions, DNN.

Reserve-voltage-driven continuous scaling on a real batteryless device:
**D2VFS, Maioli et al., ACM TOSN 2025** [10.1145/3714470](https://doi.org/10.1145/3714470).
Scales V/f rather than activity, which is the only daylight.

### The actuator may not even work

**"The Sparsity Ceiling: Where Spiking Networks Can and Cannot Trade Activity for
Energy" (2026)** [arXiv:2607.26648](https://arxiv.org/abs/2607.26648) finds "the
energy dividend of sparsity is not a property of SNNs but of the task":
feed-forward perception reaches ~5% firing with no accuracy loss, but recurrent
models plateau near 50% despite regularization targeting 10%. **Proportional
energy savings do not follow proportional activity reductions.** If actuator
authority saturates, a graded controller degenerates into the threshold
controller it claims to beat. Any claim now requires a **measured
actuator-authority curve**.

### Resolved: the standing TODO

**arXiv 2503.06663 is published.** Islam, Wei, Banerjee & Pan (2025),
"Energy-Adaptive Checkpoint-Free Intermittent Inference for Low Power Energy
Harvesting Systems," **ISQED 2025**, DOI
[10.1109/ISQED65160.2025.11014335](https://doi.org/10.1109/ISQED65160.2025.11014335),
all four authors at UT San Antonio. Full text read: it is a **CNN**, the words
"spike" and "neuromorphic" appear zero times, its low-energy adaptation is
**binary** (full model vs concentrated weights), and energy enters only as a
threshold admission test. **Not a threat.** Cite it and move on.

### The one genuine opening

**EDLIF and its successor** — Jaras et al. (2025), PLOS Comp Biol 21(6):e1013148
[10.1371/journal.pcbi.1013148](https://doi.org/10.1371/journal.pcbi.1013148), and
the 2021 EDLIF paper — have ATP availability **continuously** modulating
post-spike repolarization and hence firing rate. Simulation only, abstract ATP
pool. **No hardware implementation of EDLIF exists.** Also: an arXiv full-text
query for `"energy harvesting" AND "spiking neural network"` returned **zero**
results, and no biofuel-cell-powered artificial neuron or synapse was found at all.

---

## What this means, concretely

**1. The simulation paper is dead.** ASPEN owns the mechanism; Vigorito, Le,
Kansal, Fuzzyman and P-FREEN own the control law; Shresthamali shows the law
loses; REACT and Zhan own the capacitance result; SEENN, DT-SNN, Dynamic
Confidence, SpikeCP, MTT and NESTformer collectively own "scale spiking activity
to save energy." No amount of extra simulation closes this.

**2. The remaining contribution is entirely the hardware.** The narrowest
defensible claim:

> A **closed-loop** controller in which the *measured terminal voltage* of a
> physical energy reserve — a supercapacitor charged by a **biofuel cell** — is the
> controlled variable and the SNN's **firing rate** is the actuator, with
> **operational stability** (energy-neutral, brownout-free availability) as the
> objective rather than accuracy-per-joule. Demonstrated on real hardware, against
> a threshold baseline **and a predictive baseline**, with a **measured
> actuator-authority curve** showing the firing-rate knob has the dynamic range to
> regulate the reserve.

Four conditions, each closing a specific gap: (i) the reserve is physically
measured, not an exogenous budget — vs ASPEN; (ii) the network is spiking and the
actuator is activity, not V/f or model selection — vs D2VFS and Bullo; (iii) the
loop runs at inference — vs Energy-Aware Spike Budgeting; (iv) the source is a
biofuel cell, the one harvester with no artificial-neuron prior art.

Cleanest one-sentence framing: **substitute a real supercapacitor for the
simulated ATP pool in an EDLIF-style continuous energy-to-rate law, on hardware.**

**3. Three things must be added before any submission:**
- A **predictive baseline**. Without it the comparison is against exactly the two
  policies the field already knows are inferior.
- A **measured actuator-authority curve** (the Sparsity Ceiling objection).
- **Duty-cycle variance and SoC-estimation sensitivity**, which is what Buchli
  measured proportional control losing on.

**4. Rename and reposition.** The mechanism is **state-of-charge droop control**
(Lu et al. 2014). Drop "homeostatic," which requires integral feedback (Briat et
al. 2016). The contribution is a control-systems and co-design result, not an
adaptive-SNN result.

## Coverage gaps, stated honestly

Both sweeps exhausted their 200-call web-search budgets. **Not checked:** Google
Patents systematically; paywalled proceedings for **ENSsys, ISLPED, ICONS, SenSys
and EWSN** (ENSsys and ISLPED are the highest-risk unchecked venues for exactly
this idea); and **embodied-robotics work where battery level drives an SNN through
an artificial-metabolism or drive model**, which is a plausible place for a direct
hit. Also unrun: the query "closed-loop supercapacitor SoC feedback controlling a
spiking network." Run all of these before writing anything.

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
