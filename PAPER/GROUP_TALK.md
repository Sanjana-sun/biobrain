# BioBrain — group meeting talk
**Audience:** Prof. Dahiya's group (BEST Group, flexible electronics, e-skin,
synaptic transistors). Narges Pourjafarian and Dhayalan Shakthivel CC'd.
**Length:** ~10 minutes, then questions.
**Goal:** not to impress. To find out which of my assumptions a real device breaks.

---

## Slide 1 — What this is

A simulated computing unit that:
- powers itself from a glucose/oxygen biofuel cell,
- senses that same fuel as its input signal,
- and scales its own spiking rate to the energy it has left.

**This is the software half.** The hardware half is planned, not built. That's
why I'm here.

---

## Slide 2 — The mechanism

Biofuel cell → supercapacitor → LIF spiking network,
with a **metabolic regulator** in the loop reading reserve level and setting
firing rate.

The claim: a unit that throttles gracefully survives scarcity that makes a
fixed-rate or on/off unit fail.

---

## Slide 3 — Result (30 seeds, paired, bootstrap CIs)

| policy | responsiveness | brownout | min reserve |
|---|---|---|---|
| fixed-rate | 194.7 | **0.980** | 0.000 |
| power-gating | 254.3 | 0.000 | 0.140 |
| static-DVFS | **1940.8** | 0.226 | 0.000 |
| **adaptive-metabolic** | 1408.4 | **0.000** | **0.225** |

**Say this out loud, don't hide it:** static-DVFS is *more responsive than mine*
(1941 vs 1408). It just browns out 22.6% of the time. Mine gets 1408 at zero
brownout with the largest safety margin, and is 5.5x more responsive than
power-gating at equal safety.

**I own a tradeoff. I don't win outright.**

---

## Slide 4 — THE SLIDE THAT MATTERS: what I assumed

This is why I asked to come. Every one of these is a modelling convenience, and
you are the people who know which ones are false.

| # | Assumption | Why I'm unsure |
|---|---|---|
| 1 | LIF neuron: clean threshold, instant reset | Real devices have soft, variable switching |
| 2 | Membrane leakage is linear and stationary | Device leakage drifts with temperature and age |
| 3 | Supercapacitor stores/returns energy without loss | Real caps self-discharge and have ESR |
| 4 | Fuel cell output is a scalar power number | Output depends on fuel concentration, electrode area, fouling |
| 5 | Energy delivery is instantaneous | Supply arrives on a delay after demand |
| 6 | Device-to-device variation is zero | Printed/flexible devices vary a lot |

**Question for the group:** which of these six, if I modelled it honestly, would
change the *conclusion* rather than just the numbers?

My suspicion is #4 and #6. If output varies with fuel concentration, then
"fuel-as-sensor" and "fuel-as-power" are coupled in a way my model treats as
independent. And if variation is large, a controller tuned per-device may not
transfer.

---

## Slide 5 — Where a synaptic transistor changes the story

Your group builds devices with intrinsic dynamics. My regulator is an external
controller doing a job that a real substrate might do *by itself* — leakage and
state decay are already energy-dependent behaviours.

**Genuine question:** is an explicit metabolic regulator solving a problem that
the device physics already solves, differently and better?

If yes, that's a more interesting result than my current one.

---

## Slide 6 — What I'd want to do next

1. Replace my scalar fuel-cell model with a measured I-V curve from a real cell.
2. Add device variation and re-check whether one controller setting transfers.
3. Model the supply delay and see if the regulator still stabilises.

Any of these is a semester. I'd rather do the one that most threatens the result.

---

## Slide 7 — Me

MS CS at Northeastern, graduating **December 2027**, so three semesters left.
I built this on my own initiative over months with nobody assigning it. I'm
comfortable with hardware and I have never built a harvesting chain, which is
the gap I'm trying to close.

---

## Prep notes for yourself

**Have ready, in case asked:**
- Timestep and why. Read `simulation.py`.
- How static-DVFS was tuned, and whether that's fair. `experiments/robustness.py`
  sweeps it and compares against the best safe setting. Know that result.
- What the setpoint does. Ablation: removing it causes ~25% brownout.
- Why graded not binary. Ablation: ~1380 vs ~250 spikes/event at equal safety.
- The fuel-cell power figure. An earlier ~320 uW number was wrong and was
  corrected to ~180 uW/cm^2 (Rapoport 2012). Know which number is in the code now.

**If you don't know something, say so.** This room can tell instantly, and
"I don't know, that's one of the things I came to find out" is the correct answer
for a simulation looking for a hardware collaborator.

**Do not** present this as finished work looking for approval. Present it as a
model looking for the assumption that breaks it. That framing is why they'll
engage.
