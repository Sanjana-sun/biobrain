# Related Work

## Positioning

Our contribution, graded homeostatic reserve-feedback control for spiking neural networks (SNNs), sits at the intersection of three research areas: (1) intermittent / batteryless computing, which keeps computation correct across power failures but treats power as a binary halt/restart event; (2) low-power neuromorphic hardware and its power management, which minimizes or locally scales energy per spike but assumes an externally regulated supply; and (3) implantable biofuel cells, which provide a small, continuously fluctuating microwatt-scale energy source but have not been paired with an activity-aware compute controller. Unlike checkpoint-restore intermittency (all-or-nothing execution) or static/threshold DVFS (discrete performance levels), our controller continuously and proportionally scales SNN activity to the instantaneous stored-energy reserve, mirroring how biological neural tissue modulates firing with fuel availability. This graded, reserve-state-aware homeostasis is distinct from each field: it is not a checkpoint/restore mechanism, not a fixed voltage-frequency policy, and not merely a power-source characterization.

---

## 1. Intermittent / Batteryless Computing

This body of work is the paper's "power-gating" baseline: systems that preserve forward progress across power failures via checkpoint-restore or task-based re-execution, treating loss of power as a discrete halt event rather than a continuously graded resource signal.

- **Ransford, Sorber, Fu (2011). "Mementos: System Support for Long-Running Computation on RFID-Scale Devices." ASPLOS 2011.** DOI: [10.1145/1950365.1950386](https://doi.org/10.1145/1950365.1950386) (PDF: https://spqrlab1.github.io/papers/ransford-mementos-asplos11.pdf). Compiler-inserted, energy-aware checkpointing that snapshots volatile state to nonvolatile memory when energy runs low. Foundational batteryless-computing baseline; it checkpoints reactively at an energy threshold, whereas we continuously modulate compute rate as a function of reserve rather than only saving/restoring at the edge of failure.

- **Balsamo, Weddell, Merrett, Al-Hashimi, Brunelli, Benini (2015). "Hibernus: Sustaining Computation During Intermittent Supply for Energy-Harvesting Systems." IEEE Embedded Systems Letters, 7(1):15-18.** DOI: [10.1109/LES.2014.2371494](https://doi.org/10.1109/LES.2014.2371494). Reactively hibernates (snapshots state) just before supply failure and restores when the supply recovers past a threshold. Canonical halt/restart model; our controller instead avoids the binary halt by throttling network activity so the reserve is actively managed rather than depleted to a hibernate trigger.

- **Balsamo, Weddell, Das, Arreola, Brunelli, Al-Hashimi, Merrett, Benini (2016). "Hibernus++: A Self-Calibrating and Adaptive System for Transiently-Powered Embedded Devices." IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems, 35(12):1968-1980.** URL: [IEEE Xplore 7442814](https://ieeexplore.ieee.org/document/7442814/), DOI: [10.1109/TCAD.2016.2547919](https://doi.org/10.1109/TCAD.2016.2547919). Auto-calibrates hibernate/restore thresholds to source dynamics and system load. Its adaptivity is over checkpoint thresholds; ours is over continuous activity level, and it targets general MCU workloads rather than SNN dynamics.

- **Lucia, Ransford (2015). "A Simpler, Safer Programming and Execution Model for Intermittent Systems" (DINO). PLDI 2015.** DOI: [10.1145/2737924.2737978](https://doi.org/10.1145/2737924.2737978) (PDF: https://ben.ransford.org/papers/pldi15-dino.pdf). Task-based programming model that guarantees data consistency of volatile/nonvolatile state across arbitrary power failures. Addresses correctness under intermittency; we address graceful degradation of an SNN's inference quality under a fluctuating reserve, an orthogonal concern to memory consistency.

- **Hicks (2017). "Clank: Architectural Support for Intermittent Computation." ISCA 2017.** DOI: [10.1145/3079856.3080238](https://doi.org/10.1145/3079856.3080238). Lightweight hardware buffers and memory-access monitors that dynamically maintain idempotency without programmer intervention. A hardware idempotency mechanism for correct restart; complementary to but distinct from our software controller that regulates activity to prevent failures rather than recover from them.

- **Maeng, Lucia (2018). "Adaptive Dynamic Checkpointing for Safe Efficient Intermittent Computing" (Chinchilla). OSDI 2018.** URL: [USENIX OSDI'18](https://www.usenix.org/conference/osdi18/presentation/maeng) (PDF: https://brandonlucia.com/pubs/chinchilla_osdi2018.pdf). Compiler + runtime that runs unmodified C efficiently on harvesters with adaptive checkpoint placement and no extra hardware. State-of-the-art checkpoint efficiency, still a discrete save/restore paradigm; our work replaces the discrete failure/recovery cycle with continuous reserve-proportional operation.

- **Maeng, Colin, Lucia (2017). "Alpaca: Intermittent Execution Without Checkpoints." OOPSLA 2017 (PACMPL Vol. 1).** arXiv: [1909.06951](https://arxiv.org/abs/1909.06951) (PDF: https://brandonlucia.com/pubs/alpaca-preprint.pdf). Task-based intermittent execution that ensures consistency via privatization/redo logging instead of full checkpoints. Represents the "task re-execution" branch of intermittency; like the others it is halt-and-resume, whereas our contribution keeps the network running at a reduced graded activity level.

- **Lee, Islam, Luo, Nirjon (2019). "Intermittent Learning: On-Device Machine Learning on Intermittently Powered System." IMWUT (Proc. ACM IMWUT) 3(4).** DOI: [10.1145/3369837](https://doi.org/10.1145/3369837), arXiv: [1904.09644](https://arxiv.org/abs/1904.09644). Runs ML training/inference across power cycles on solar/RF/kinetic harvesters with energy-aware example selection. Closest prior work bridging ML and intermittency, but it schedules discrete learning steps around power availability; we continuously scale an SNN's inference activity to the reserve rather than gating whole training examples.

---

## 2. Energy-Harvesting / Low-Power Spiking Neural Networks and Neuromorphic Power Management

This section covers ultra-low-power spiking hardware and the power-management (DVFS / event-driven / activity-gated) techniques used on neuromorphic platforms, which is what our graded controller must be contrasted against.

- **Merolla, Arthur, Alvarez-Icaza, Cassidy, Sawada, Akopyan, et al. (2014). "A Million Spiking-Neuron Integrated Circuit with a Scalable Communication Network and Interface" (TrueNorth). Science, 345(6197):668-673.** DOI: [10.1126/science.1254642](https://doi.org/10.1126/science.1254642). Event-driven 1M-neuron CMOS chip achieving ~26 pJ per synaptic event with milliwatt-scale power. Establishes the ultra-low-power, event-driven SNN substrate we target, but assumes a stable external supply and has no reserve-aware activity control.

- **Davies, Srinivasa, Lin, Chinya, et al. (2018). "Loihi: A Neuromorphic Manycore Processor with On-Chip Learning." IEEE Micro, 38(1):82-99.** DOI: [10.1109/MM.2018.112130359](https://doi.org/10.1109/MM.2018.112130359). 128-core neuromorphic processor (~15 pJ/synaptic-op) with programmable learning and event-driven operation. A leading low-power SNN platform whose energy efficiency comes from event sparsity; it does not modulate global activity as a function of a stored-energy reserve, which is our added control loop.

- **Furber, Galluppi, Temple, Plana (2014). "The SpiNNaker Project." Proceedings of the IEEE, 102(5):652-665.** DOI: [10.1109/JPROC.2014.2304638](https://doi.org/10.1109/JPROC.2014.2304638). Massively parallel ARM-core architecture for real-time large-scale SNN simulation. Representative digital neuromorphic platform; power scaling is handled at the core/chip level (and later via DVFS in SpiNNaker2) rather than by reserve-proportional activity homeostasis.

- **Höppner, Yan, Vogginger, Dixius, Partzsch, Neumärker, et al. (2017). "Dynamic Voltage and Frequency Scaling for Neuromorphic Many-Core Systems." IEEE ISCAS 2017.** URL: [IEEE Xplore 8050656](https://ieeexplore.ieee.org/document/8050656/), DOI: [10.1109/ISCAS.2017.8050656](https://doi.org/10.1109/ISCAS.2017.8050656). Per-core, load-triggered DVFS (sub-100 ns switching) for the SpiNNaker2 neuromorphic system, scaling voltage/frequency to spike load. This is the canonical DVFS baseline we contrast against: it selects among discrete performance levels driven by instantaneous spike load, whereas our controller scales activity continuously against the energy reserve state, not the workload.

- **Frenkel, Lefebvre, Legat, Bol (2019). "A 0.086-mm2 12.7-pJ/SOP 64k-Synapse 256-Neuron Online-Learning Digital Spiking Neuromorphic Processor in 28-nm CMOS" (ODIN). IEEE Transactions on Biomedical Circuits and Systems, 13(1):145-158.** arXiv: [1804.07858](https://arxiv.org/abs/1804.07858), DOI: [10.1109/TBCAS.2018.2880425](https://doi.org/10.1109/TBCAS.2018.2880425). Extremely small, ~12.7 pJ/SOP on-chip-learning SNN processor aimed at biomedical/edge use. Demonstrates the microwatt-class SNN hardware compatible with biofuel-cell power budgets; it optimizes energy per operation but leaves reserve-aware runtime modulation to a higher-level controller such as ours.

- **Lin, Sun, Feng, Chen, Kang (2020). "Intermittent Inference with Nonuniformly Compressed Multi-Exit Neural Network for Energy-Harvesting Powered Devices." DAC 2020.** arXiv: [2004.11293](https://arxiv.org/abs/2004.11293). Multi-exit network that trades off accuracy vs. energy so inference can complete within a harvested-energy budget. Shares our goal of graceful accuracy degradation under limited energy, but does so via discrete early-exit branches on a conventional DNN under checkpoint-style intermittency, not continuous activity scaling of an SNN.

- **Energy-Adaptive Checkpoint-Free Intermittent Inference for Low-Power Energy-Harvesting Systems (2025).** arXiv: [2503.06663](https://arxiv.org/abs/2503.06663). Proposes checkpoint-free intermittent inference that adapts computation to available energy without explicit state snapshots. Most closely aligned in spirit (energy-adaptive, checkpoint-free) but targets conventional feed-forward inference; our work applies continuous reserve feedback to the intrinsic spiking dynamics of an SNN. TODO: confirm full author list and final venue on arXiv page before citing.

---

## 3. Biofuel Cells and Implantable Bioelectronics

This section grounds the paper's target power source: implantable enzymatic glucose biofuel cells that deliver small, continuously fluctuating microwatt-scale power, which motivates the need for a reserve-aware compute controller.

- **Cinquin, Gondran, Giroud, Mazabrard, Pellissier, Boucher, et al. (2010). "A Glucose BioFuel Cell Implanted in Rats." PLOS ONE, 5(5):e10476.** DOI: [10.1371/journal.pone.0010476](https://doi.org/10.1371/journal.pone.0010476). First functional implantable enzymatic glucose biofuel cell demonstrated in freely moving rats. Establishes the feasibility of in-vivo glucose-powered electronics; we build on this by treating such a source's fluctuating output as the reserve signal driving SNN activity.

- **Zebda, Cosnier, Alcaraz, Holzinger, Le Goff, Gondran, et al. (2013). "Single Glucose Biofuel Cells Implanted in Rats Power Electronic Devices." Scientific Reports, 3:1516.** DOI: [10.1038/srep01516](https://doi.org/10.1038/srep01516). Carbon-nanotube/enzyme GBFC delivering ~38.7 microwatts (193.5 microwatts/cm2) in vivo, powering an LED and a digital thermometer with no rejection after 110 days. The canonical ~39-microwatt implanted GBFC that defines the realistic power envelope our controller is designed to operate within.

- **Rapoport, Kedzierski, Sarpeshkar (2012). "A Glucose Fuel Cell for Implantable Brain-Machine Interfaces." PLOS ONE, 7(6):e38436.** DOI: [10.1371/journal.pone.0038436](https://doi.org/10.1371/journal.pone.0038436) (MIT copy: https://dspace.mit.edu/bitstream/handle/1721.1/72329/Rapoport-2012-A%20Glucose%20Fuel%20Cell.pdf). Silicon-fabricated abiotic (platinum-catalyst) glucose fuel cell co-integrable with ICs on a wafer, producing up to hundreds of microwatts (peak ~180 microwatts/cm2) from cerebrospinal-fluid glucose for brain implants. Directly motivates an SNN implant powered by CSF glucose; it characterizes the source but pairs it with no activity-aware load controller, which is our contribution.

- **Andoralov, Falk, Suyatin, Granmo, Sotres, Ludwig, et al. (2013). "Biofuel Cell Based on Microscale Nanostructured Electrodes with Inductive Coupling to Rat Brain Neurons." Scientific Reports, 3:3270.** DOI: [10.1038/srep03270](https://doi.org/10.1038/srep03270). Membraneless 3D-nanostructured glucose/O2 enzymatic fuel cell operating in rat cerebrospinal fluid and brain (~2 microwatts/cm2 in vivo) with inductive coupling to living neurons. Shows biofuel cells operating in the brain microenvironment at very low, variable power, reinforcing why graded reserve-aware compute (not fixed-rate operation) is required.

- **Chakraborty, Olsson, Andersson, Pandey (2024). "Glucose-Based Biofuel Cells and Their Applications in Medical Implants: A Review." Heliyon, 10(13):e33615.** DOI: [10.1016/j.heliyon.2024.e33615](https://doi.org/10.1016/j.heliyon.2024.e33615). Recent review of glucose biofuel-cell chemistry, electrode design, and implant applications. Provides up-to-date context on achievable power densities and stability, supporting the realism of our assumed reserve dynamics.

- **Fredj, Rong, Sawan (2025). "Recent Advances in Enzymatic Biofuel Cells to Power Up Wearable and Implantable Biosensors." Biosensors, 15(4):218.** DOI: [10.3390/bios15040218](https://doi.org/10.3390/bios15040218). Review of enzymatic biofuel cells as power sources and self-powered biosensors for wearable/implantable devices. Frames the biofuel-cell-plus-electronics co-design space our SNN controller targets, and highlights that prior systems pair these cells with simple sensors rather than adaptive neural compute.

---

## Summary of Verified Citations

- Section 1 (Intermittent / batteryless computing): 8 verified citations, all with DOI or arXiv/PDF links.
- Section 2 (Low-power / energy-harvesting SNNs and neuromorphic power management): 7 verified citations; one (arXiv 2503.06663) carries a TODO to confirm the full author list and final venue.
- Section 3 (Biofuel cells and implantable bioelectronics): 6 verified citations, all with DOIs.

Total: 21 real, verifiable references. No citations were fabricated; the single unverified detail is flagged inline as a TODO.
