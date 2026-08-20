# BioBrain: Research Roadmap to a Publishable Paper

Target: a peer-reviewed **workshop paper + arXiv preprint** within ~2-3 months, as an
independent author, backed by **real hardware measurements**. This is the first paper of
an intended body of work (better for an O1 case than a single result).

---

## 1. The contribution (one sentence)

> **Metabolic self-regulation** -- continuously scaling a spiking network's activity to
> its stored-energy state via a homeostatic setpoint -- gives energy-harvesting
> neuromorphic devices the **best responsiveness-vs-safety trade-off**: near-maximal
> event responsiveness with zero brownout, unlike fixed-rate, power-gating
> (intermittent-computing), or static-DVFS baselines.

Secondary contribution: **fuel-as-sensor** -- the same biofuel current that powers the
device is read as its input signal, collapsing power source and sensor into one component.

## 2. Why it is novel (positioning -- do this literature review first)

The paper lives at the intersection of three fields and must cite each so reviewers don't
call it a reinvention:

- **Intermittent / batteryless computing:** Hibernus, Mementos, Clank, checkpoint-restore.
  These are our `power-gating` baseline. Our angle: graded biological regulation instead
  of binary halt/restore.
- **Energy-harvesting SNNs / neuromorphic power management:** recent low-power spiking
  chips, DVFS for neuromorphic. Our angle: reserve-state feedback as the control variable.
- **Biofuel cells / bioelectronics:** implanted glucose fuel cells (rat, ~39 uW; MIT
  silicon cell, ~180 uW/cm^2 peak / hundreds of uW). Grounds our power model and hardware.

Deliverable: a `related_work.md` with 15-25 real citations grouped by the three fields.
(I can draft this from literature searches; every claim gets a real reference.)

## 3. Experimental plan (what makes it rigorous)

Current repo has a **preliminary** paired multi-seed comparison (see
`experiments/compare_policies.py`, 30 seeds, 95% CI). To reach publishable rigor:

1. **Real task, not a proxy.** Move from "spikes per event" to a standard SNN benchmark:
   - keyword spotting on **Google Speech Commands** (spiking model), or
   - **N-MNIST** classification.
   Metric becomes task accuracy / detection F1 *under an intermittent power budget*.
2. **Realistic power traces.** Drive the sim with measured/parameterized harvesting
   traces (from our own hardware in step 6, plus published biofuel-cell profiles), not a
   hand-drawn curve.
3. **Baselines + Pareto analysis.** Keep fixed-rate, power-gating, static-DVFS. Add a
   **setpoint / gain sweep** for our policy to draw the responsiveness-vs-brownout
   **Pareto frontier** and show our policy dominates it.
4. **Ablations.** Remove the homeostatic setpoint; remove graded (make it binary); vary
   supercap size. Show each piece earns its place.
5. **Statistics.** >=30 seeds, mean +/- 95% CI, paired tests vs each baseline. (Upgrade
   the normal-approx CI to a proper t / bootstrap; add `scipy`.)
6. **Sensitivity analysis.** Show results are robust to +/-50% on the grounded parameters
   (Km, p_max, energy-per-spike, capacity), i.e. not a tuning artifact.

## 4. Hardware validation (chosen: full measurement)

Follow `hardware/BUILD.md` (Track A microbial first -> Track B glucose). Minimum
publishable hardware result:

- Measured cell V/I curve and harvested-power trace over time.
- The MCU running the spiking + regulator firmware **battery-free**.
- A logged demonstration: starve the cell -> measured reserve drops -> measured spike
  rate throttles -> restore fuel -> recovers. Plot measured vs. simulated to validate the
  model. Model-matches-hardware is the credibility keystone.

Order parts **this week** -- microbial cultures and shipping have multi-day lead time and
are the critical path.

## 5. Timeline (aggressive but feasible, ~10-12 weeks)

| Wk | Milestone |
|----|-----------|
| 1  | Order hardware. Draft `related_work.md`. Freeze the contribution statement. |
| 2  | Stand up the standard-benchmark SNN task in sim; port policies to it. |
| 3  | Power-trace generator grounded in published + (early) measured data. |
| 4  | Full baseline + Pareto sweep + ablations in sim; lock statistics. |
| 5  | Hardware: cell producing power; harvester charging supercap (measured). |
| 6  | Hardware: MCU running firmware battery-free; log throttling demo. |
| 7  | Measured-vs-simulated validation figure. |
| 8  | Write methods + results. |
| 9  | Write intro + related work + discussion; make all figures camera-ready. |
| 10 | Internal review pass, reproducibility check, release code + data. |
| 11 | Post to arXiv; submit to target workshop. |
| 12 | Buffer. |

## 6. Venue targets (independent-author friendly)

- **arXiv** (anchor, establishes priority): categories `cs.NE` (neural/evolutionary) and
  `eess.SP`. Note: arXiv `cs.NE` may require an **endorsement** for a first-time author
  with no affiliation -- line one up early (a published author in the area).
- **Workshops** (real, fast peer review): NeurIPS/ICML workshops on efficient / new
  compute paradigms; **NICE** (Neuro-Inspired Computational Elements); **tinyML**.
- **Step-up conferences** (next paper): IEEE **BioCAS**, **ISCAS**, **IJCNN**.

## 7. Reproducibility (required for credibility)

- Public repo, pinned deps, fixed seeds, one-command reproduction of every figure.
- Release measured hardware logs (CSV) and the analysis notebook.
- A `REPRODUCE.md` mapping each paper figure to the exact command.

## 8. Risks and mitigations

- **Hardware doesn't produce enough power** -> Track A microbial is forgiving; worst case,
  emulate the measured V/I with a source-meter and still report a hardware-grounded trace.
- **arXiv endorsement blocked** -> post to a non-endorsement category or via a co-author.
- **"Reinvents intermittent computing"** -> the Pareto + graded-vs-binary ablation is the
  direct rebuttal; make it the centerpiece.
- **Scope creep** -> the standard benchmark (step 3.1) is the most likely thing to slip;
  N-MNIST is the smaller fallback if Speech Commands is too heavy.

## 9. Honest status

Done: physically-grounded simulation; four-policy paired comparison with 95% CIs showing
our policy owns the responsiveness-safety trade-off (0% brownout, highest safety margin).
Not yet done: standard-benchmark task, Pareto/ablation/sensitivity studies, hardware
measurements, related-work grounding, the write-up. Those are the gap to "publishable."
