/* BioBrain simulation engine, ported from the Python reference implementation.
 *
 * Equations, parameters and update order match biobrain/*.py exactly. The only
 * deliberate difference is the pseudo-random number generator: NumPy's PCG64
 * cannot be reproduced in the browser, so this uses mulberry32 with Box-Muller
 * normals. Results are therefore statistically equivalent to the Python but not
 * bit-identical. Every structural claim on this page reproduces; the third
 * decimal place may not.
 */

// ---------------------------------------------------------------- PRNG

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

class RNG {
  constructor(seed) {
    this.u = mulberry32(seed);
    this.spare = null;
  }
  normal(mu = 0, sigma = 1) {
    if (this.spare !== null) {
      const s = this.spare;
      this.spare = null;
      return mu + sigma * s;
    }
    let u, v, s;
    do {
      u = this.u() * 2 - 1;
      v = this.u() * 2 - 1;
      s = u * u + v * v;
    } while (s === 0 || s >= 1);
    const m = Math.sqrt((-2 * Math.log(s)) / s);
    this.spare = v * m;
    return mu + sigma * u * m;
  }
  uniform(lo, hi) { return lo + (hi - lo) * this.u(); }
  int(lo, hi) { return Math.floor(this.uniform(lo, hi)); }
}

const clip = (x, lo, hi) => Math.min(hi, Math.max(lo, x));

// ---------------------------------------------------------------- components

class BiofuelCell {
  // Michaelis-Menten in glucose, gated by oxygen, with noise and slow fouling.
  constructor({ pMaxUw = 320, kmMM = 5.0, noiseFrac = 0.05,
                degradationPerS = 2e-6, rng } = {}) {
    Object.assign(this, { pMaxUw, kmMM, noiseFrac, degradationPerS, rng });
    this.health = 1.0;
  }
  powerUw(glucoseMM, oxygenFrac, dtS) {
    const g = Math.max(glucoseMM, 0);
    const o2 = clip(oxygenFrac, 0, 1);
    const mm = g / (this.kmMM + g);
    let p = this.pMaxUw * mm * o2 * this.health;
    if (this.noiseFrac > 0) {
      p *= Math.max(0, 1 + this.rng.normal(0, this.noiseFrac));
    }
    this.health = Math.max(0, this.health - this.degradationPerS * dtS);
    return Math.max(0, p);
  }
}

class EnergyStore {
  // Supercapacitor. Energy in microjoules.
  constructor({ capacityUj = 2000, chargeEfficiency = 0.85, initialFrac = 0.5 } = {}) {
    this.capacityUj = capacityUj;
    this.chargeEfficiency = chargeEfficiency;
    this.energyUj = capacityUj * initialFrac;
  }
  get level() { return this.capacityUj > 0 ? this.energyUj / this.capacityUj : 0; }
  charge(powerUw, dtS) {
    this.energyUj = Math.min(this.capacityUj,
      this.energyUj + powerUw * dtS * this.chargeEfficiency);
  }
  draw(energyUj) {
    if (energyUj <= this.energyUj) { this.energyUj -= energyUj; return true; }
    return false;
  }
}

class SpikingNet {
  // Leaky integrate-and-fire, per-spike energy cost paid from the store.
  constructor({ n = 64, tauMs = 0.02, vThreshold = 1.0, vReset = 0.0,
                energyPerSpikeUj = 0.5, rng } = {}) {
    Object.assign(this, { n, tauMs, vThreshold, vReset, energyPerSpikeUj, rng });
    this.v = new Float64Array(n);
  }
  step(inputCurrent, dtS, store, rateScale = 1.0) {
    const rs = clip(rateScale, 0, 1);
    const k = dtS / this.tauMs;
    let spikes = 0, attempted = 0;
    for (let i = 0; i < this.n; i++) {
      const drive = inputCurrent * rs + this.rng.normal(0, 0.05);
      this.v[i] += k * (-this.v[i] + drive);
    }
    for (let i = 0; i < this.n; i++) {
      if (this.v[i] >= this.vThreshold) {
        attempted++;
        // Pay the metabolic bill; the spike is suppressed if the reserve is empty.
        if (store.draw(this.energyPerSpikeUj)) spikes++;
        this.v[i] = this.vReset;   // reset regardless: the neuron attempted to fire
      }
    }
    return { spikes, attempted };
  }
}

// ---------------------------------------------------------------- policies

const POLICIES = {
  'fixed-rate': {
    label: 'Fixed rate',
    blurb: 'Always full speed. Ignores energy state entirely.',
    make: () => ({ reset() {}, rateScale: () => 1.0 }),
  },
  'power-gating': {
    label: 'Power gating',
    blurb: 'The intermittent-computing baseline (cf. Hibernus). Run until the reserve '
         + 'falls below low, halt until it refills past high. Binary, with hysteresis.',
    make: ({ low = 0.15, high = 0.45 } = {}) => {
      let on = true;
      return {
        reset() { on = true; },
        rateScale(level) {
          if (on && level <= low) on = false;
          else if (!on && level >= high) on = true;
          return on ? 1.0 : 0.0;
        },
      };
    },
  },
  'static-dvfs': {
    label: 'Static DVFS',
    blurb: 'A constant reduced rate, chosen offline. No response to reserve state.',
    make: ({ scale = 0.5 } = {}) => ({ reset() {}, rateScale: () => clip(scale, 0, 1) }),
  },
  'adaptive-metabolic': {
    label: 'Adaptive metabolic',
    blurb: 'The contribution. A graded logistic throttle around a homeostatic '
         + 'setpoint, so activity degrades smoothly and the reserve is defended.',
    make: ({ setpoint = 0.5, floorScale = 0.05, gain = 6.0 } = {}) => ({
      reset() {},
      rateScale(level) {
        const s = 1 / (1 + Math.exp(-gain * (level - setpoint)));
        return floorScale + (1 - floorScale) * s;
      },
    }),
  },
};

// ---------------------------------------------------------------- traces

function makeTrace(seed, {
  durationS = 60, dtS = 0.001, baselineMM = 6.0, nFamines = 2,
  famineDepthMM = 0.5, nEvents = 6, eventDurS = 1.0, eventDemand = 4.0,
} = {}) {
  const rng = new RNG(seed + 1);
  const n = Math.round(durationS / dtS);
  const glucose = new Float64Array(n).fill(baselineMM);
  const demand = new Float64Array(n).fill(1.0);

  for (let f = 0; f < nFamines; f++) {
    const center = rng.uniform(0.15, 0.85) * durationS;
    const width = rng.uniform(4.0, 8.0);
    const amp = baselineMM - famineDepthMM;
    for (let i = 0; i < n; i++) {
      const t = i * dtS;
      glucose[i] -= amp * Math.exp(-((t - center) ** 2) / (2 * width * width));
    }
  }
  const floor = famineDepthMM * 0.5;
  for (let i = 0; i < n; i++) glucose[i] = Math.max(glucose[i], floor);

  const evLen = Math.round(eventDurS / dtS);
  const windows = [];
  for (let e = 0; e < nEvents; e++) {
    const start = rng.int(Math.round(2.0 / dtS), n - evLen);
    const end = start + evLen;
    for (let i = start; i < end; i++) demand[i] = eventDemand;
    windows.push([start, end]);
  }
  windows.sort((a, b) => a[0] - b[0]);
  return { dtS, glucose, demand, windows, durationS };
}

// ---------------------------------------------------------------- run

const BROWNOUT_LEVEL = 0.05;

function runPolicy(trace, policy, seed, {
  inputCurrent = 1.2, oxygenFrac = 1.0, capacityUj = 2000,
  pMaxUw = 320, energyPerSpikeUj = 0.5, sampleEvery = 20,
} = {}) {
  const rng = new RNG(seed);
  const cell = new BiofuelCell({ pMaxUw, rng });
  const store = new EnergyStore({ capacityUj });
  const net = new SpikingNet({ energyPerSpikeUj, rng });
  policy.reset();

  const n = trace.glucose.length;
  const dtS = trace.dtS;

  let brownoutSteps = 0, minReserve = 1.0, totalSpikes = 0;
  let harvestedUj = 0, suppressed = 0;
  const series = { t: [], glucose: [], power: [], level: [], rate: [], spikes: [] };

  const eventSpikes = new Array(trace.windows.length).fill(0);
  let wi = 0;

  for (let i = 0; i < n; i++) {
    const power = cell.powerUw(trace.glucose[i], oxygenFrac, dtS);
    harvestedUj += power * dtS;
    store.charge(power, dtS);

    const level = store.level;
    const rate = policy.rateScale(level);
    const r = net.step(inputCurrent * trace.demand[i], dtS, store, rate);

    totalSpikes += r.spikes;
    suppressed += r.attempted - r.spikes;
    if (level < BROWNOUT_LEVEL) brownoutSteps++;
    if (level < minReserve) minReserve = level;

    while (wi < trace.windows.length && i >= trace.windows[wi][1]) wi++;
    if (wi < trace.windows.length && i >= trace.windows[wi][0]) {
      eventSpikes[wi] += r.spikes;
    }

    if (i % sampleEvery === 0) {
      series.t.push(i * dtS);
      series.glucose.push(trace.glucose[i]);
      series.power.push(power);
      series.level.push(level);
      series.rate.push(rate);
      series.spikes.push(r.spikes);
    }
  }

  const responsiveness = eventSpikes.length
    ? eventSpikes.reduce((a, b) => a + b, 0) / eventSpikes.length : 0;

  return {
    responsiveness,
    brownoutFrac: brownoutSteps / n,
    minReserve,
    efficiency: harvestedUj > 0 ? totalSpikes / harvestedUj : 0,
    totalSpikes,
    suppressed,
    series,
  };
}

// ---------------------------------------------------------------- statistics

function mean(a) { return a.reduce((x, y) => x + y, 0) / a.length; }

function bootstrapCI(x, nBoot = 2000, alpha = 0.05, rng = new RNG(99)) {
  const m = mean(x);
  if (x.length < 2 || x.every((v) => v === x[0])) return [m, m, m];
  const means = new Float64Array(nBoot);
  for (let b = 0; b < nBoot; b++) {
    let s = 0;
    for (let i = 0; i < x.length; i++) s += x[rng.int(0, x.length)];
    means[b] = s / x.length;
  }
  means.sort();
  const lo = means[Math.floor((alpha / 2) * nBoot)];
  const hi = means[Math.floor((1 - alpha / 2) * nBoot)];
  return [m, lo, hi];
}
