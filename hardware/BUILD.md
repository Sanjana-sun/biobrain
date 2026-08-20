# BioBrain Hardware Build Plan (Tier 2)

The goal of the physical half is modest but real and demonstrable:

> **A biofuel cell that harvests energy from fuel + oxygen, buffers it in a
> supercapacitor ("metabolism"), and uses it to run a low-power spiking-neuron circuit
> that throttles itself when energy is low** — the same metabolic-regulation behavior
> proven in the software model.

You will not implant anything or match a real brain. You *will* have a self-contained,
battery-free device on your bench that computes on harvested biochemical energy and
visibly slows down and recovers as fuel changes. That is a legitimate, filmable
proof-of-concept and a strong portfolio/hackathon artifact.

---

## The signal chain

```
[ fuel cell ] -> [ energy harvester IC ] -> [ supercapacitor ] -> [ MCU / neuron circuit ] -> [ LED / display ]
   ~0.3-0.7 V         boosts to 3.3 V          the "metabolism"      spiking + regulation      the "output"
   tens of uW         + regulates                  buffer               firmware
```

The trick with microwatt sources: you cannot run a chip directly off them. You
**accumulate** energy in the supercap over seconds/minutes, then the harvester releases
a usable 3.3 V burst. This is literally the `EnergyStore` module in hardware.

---

## Bill of materials

### Track A — easiest, safest, cheapest (microbial fuel cell)

| Part | Example | Approx. cost | Notes |
|------|---------|-------------|-------|
| Microbial fuel cell kit | MudWatt / MFC classroom kit | $30-40 | Bacteria in mud oxidize organics; O2 is the acceptor at the cathode. Genuinely "oxygen + fuel". |
| Energy harvester eval board | TI **BQ25504** or **BQ25570** EVM | $30-50 | Boosts sub-volt input to 3.3 V; has MPPT + storage management. This is the heart of the build. |
| Supercapacitor | 0.1-1 F, 5.5 V | $2-5 | The metabolism buffer. |
| Ultra-low-power MCU | **MSP430** LaunchPad or **Arduino Nano 33 (deep-sleep)** | $10-20 | Runs the LIF-neuron + regulator firmware. |
| Output | LED + small OLED (SSD1306) | $5-10 | LED blink = spikes; OLED shows energy level / rate. |
| Misc | wires, breadboard, multimeter (you have) | - | |

**Total: ~$80-125.** Best starting point. Slow to spin up (bacteria need days) but forgiving and non-toxic.

### Track B — closer to the "brain" story (enzymatic glucose fuel cell)

Swap the microbial kit for an enzymatic glucose cell so the fuel is literally glucose:

| Part | Example | Approx. cost | Notes |
|------|---------|-------------|-------|
| Glucose oxidase (anode enzyme) | lab supplier | $20-40 | Oxidizes glucose. |
| Laccase or bilirubin oxidase (cathode) | lab supplier | $30-60 | Reduces O2 — the oxygen half. |
| Carbon cloth / buckypaper electrodes | - | $15-30 | High surface area for enzyme loading. |
| Osmium redox mediator or CNT ink | - | $20-50 | Shuttles electrons; optional but boosts output. |
| Glucose + phosphate buffer | - | $10 | The fuel. |

Rest of the chain (harvester, supercap, MCU, output) is identical to Track A. **Total: ~$150-300.** More finicky and needs basic wet-lab care, but it is the real glucose/oxygen story.

> Start with Track A to get the *electronics* chain working end to end, then swap in the
> Track B cell. Debugging bacteria and enzymes at the same time as firmware is painful.

---

## Build order (each step is independently verifiable)

1. **Prove the cell.** Assemble the fuel cell. With a multimeter, confirm open-circuit
   voltage (expect ~0.3-0.7 V) and a short-circuit current in the uA-mA range. If you
   see nothing here, nothing downstream will work.
2. **Prove harvesting.** Wire the cell into the BQ25504/570 board, attach the supercap.
   Watch the supercap voltage climb over minutes on a multimeter. This is `EnergyStore`
   charging in real life.
3. **Prove a load runs.** Set the harvester's output to 3.3 V. Confirm it eventually
   fires up and can blink one LED. Now you have battery-free computing.
4. **Load the firmware.** Flash the MCU with the LIF-neuron + regulator code
   (`firmware/` — port of `biobrain/neuron.py` + `metabolism.py`). LED blinks = spikes.
5. **Demonstrate regulation.** Read the supercap voltage on an ADC pin. Map it to a
   `rate_scale` exactly like `MetabolicRegulator.rate_scale()`. Now: cover/starve the
   cell (remove fuel or block O2) and watch the blink rate slow and the OLED reserve
   drop; restore fuel and watch it speed back up. **That is the whole thesis, physical.**
6. **(Novel bonus) Fuel-as-sensor.** The harvester's input current tracks fuel
   concentration. Sample it and display it as a glucose readout — the same signal that
   powers the device now also reports the fuel level. One component, two jobs.

---

## Firmware sketch (maps 1:1 to the sim)

```c
// pseudo-C for the MCU loop
float reserve = read_supercap_voltage() / VMAX;      // EnergyStore.level
float scale   = FLOOR + (1-FLOOR) / (1+expf(-GAIN*(reserve-SETPOINT))); // regulator
if (rand01() < BASE_RATE * scale && reserve > SPIKE_COST) {
    spike();                 // blink LED / drive output
    reserve -= SPIKE_COST;   // per-spike energy cost
}
float glucose = read_harvester_input_current() * K;  // fuel-as-sensor
draw_oled(reserve, scale, glucose);
sleep_ms(TICK);              // deep sleep between ticks to stay in budget
```

The constants (`FLOOR`, `GAIN`, `SETPOINT`, `SPIKE_COST`, `BASE_RATE`) are the same knobs
you already tuned in the Python model — start from those values.

---

## Safety notes

- **Track A** (mud/microbes) is essentially harmless. Wash hands; don't ingest.
- **Track B** enzymes and mediators: wear gloves and goggles, follow each reagent's
  safety sheet, dispose per your institution's rules. Osmium mediators in particular
  are toxic — buckypaper/CNT-only designs avoid them.
- Voltages here are tiny (< 6 V) and currents are microamps to milliamps: no shock
  hazard. The supercap can dump current if shorted, so don't short it.

---

## What "done" looks like

A short video: the device sitting on your desk with no battery, blinking (spiking); you
starve the fuel cell and the blinking slows and the reserve bar drops; you feed it and it
speeds back up. Caption it with the one-line thesis and you have demonstrated, in the real
world, a self-powered neuromorphic unit that regulates its own metabolism.
