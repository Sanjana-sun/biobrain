/* UI layer: wires the controls to the engine and draws everything on canvas.
 * No dependencies. */

const COLORS = {
  'fixed-rate': '#8d93a0',
  'power-gating': '#2f6f8f',
  'static-dvfs': '#4a4f57',
  'adaptive-metabolic': '#b3341f',
};
const ORDER = ['fixed-rate', 'power-gating', 'static-dvfs', 'adaptive-metabolic'];
const $ = (id) => document.getElementById(id);
const dpr = () => window.devicePixelRatio || 1;

let current = 'adaptive-metabolic';

// ---------------------------------------------------------------- canvas utils

function prep(canvas) {
  const r = dpr();
  const h = parseInt(canvas.dataset.h || canvas.getAttribute('height'), 10);
  canvas.dataset.h = h;                 // remember the logical height
  canvas.style.height = h + 'px';       // CSS size, else the backing store sets layout
  const w = canvas.clientWidth;
  canvas.width = Math.round(w * r);
  canvas.height = Math.round(h * r);
  const c = canvas.getContext('2d');
  c.setTransform(r, 0, 0, r, 0, 0);
  c.clearRect(0, 0, w, h);
  return { c, w, h, ok: w > 0 };
}

function axes(c, x, y, w, h, { xlab, ylab, y0, y1, x1, ticks = 4 }) {
  c.strokeStyle = '#e4e7ec'; c.lineWidth = 1;
  c.fillStyle = '#9aa1aa'; c.font = '10px ui-monospace, Menlo, monospace';
  for (let i = 0; i <= ticks; i++) {
    const yy = Math.round(y + (h * i) / ticks) + 0.5;
    c.beginPath(); c.moveTo(x, yy); c.lineTo(x + w, yy); c.stroke();
    const v = y1 - ((y1 - y0) * i) / ticks;
    c.textAlign = 'right'; c.textBaseline = 'middle';
    c.fillText(fmtTick(v), x - 7, yy);
  }
  c.fillStyle = '#6b727b';
  c.font = '500 10px ui-monospace, Menlo, monospace';
  c.textAlign = 'left'; c.textBaseline = 'top';
  c.fillText(ylab, x + 3, y + 3);
  if (xlab) {
    c.textAlign = 'right'; c.textBaseline = 'bottom';
    c.fillStyle = '#9aa1aa';
    c.fillText(xlab, x + w, y + h + 15);
  }
}

function fmtTick(v) {
  const a = Math.abs(v);
  if (a >= 1000) return v.toFixed(0);
  if (a >= 10) return v.toFixed(0);
  if (a >= 1) return v.toFixed(1);
  return v.toFixed(2);
}

function line(c, xs, ys, x, y, w, h, y0, y1, color, lw = 1.4) {
  c.strokeStyle = color; c.lineWidth = lw; c.beginPath();
  const n = xs.length, span = (y1 - y0) || 1;
  for (let i = 0; i < n; i++) {
    const px = x + (w * i) / (n - 1);
    const py = y + h - (h * (ys[i] - y0)) / span;
    i ? c.lineTo(px, py) : c.moveTo(px, py);
  }
  c.stroke();
}

function band(c, x, y, w, h, frac0, frac1, fill) {
  c.fillStyle = fill;
  c.fillRect(x + w * frac0, y, w * (frac1 - frac0), h);
}

// ---------------------------------------------------------------- live trace

function opts() {
  return {
    seed: +$('s-seed').value,
    pMaxUw: +$('s-pmax').value,
    capacityUj: +$('s-cap').value,
    famineDepthMM: +$('s-famine').value,
    gain: +$('s-gain').value,
    setpoint: +$('s-set').value,
    scale: +$('s-scale').value,
    low: +$('s-low').value,
  };
}

function policyFor(name, o) {
  if (name === 'adaptive-metabolic') return POLICIES[name].make({ setpoint: o.setpoint, gain: o.gain });
  if (name === 'static-dvfs') return POLICIES[name].make({ scale: o.scale });
  if (name === 'power-gating') return POLICIES[name].make({ low: o.low, high: Math.min(0.95, o.low + 0.30) });
  return POLICIES[name].make({});
}

function drawTrace() {
  const o = opts();
  const trace = makeTrace(o.seed, { famineDepthMM: o.famineDepthMM });
  const res = runPolicy(trace, policyFor(current, o), o.seed, {
    capacityUj: o.capacityUj, pMaxUw: o.pMaxUw, sampleEvery: 20,
  });
  const s = res.series;

  // metrics
  const bo = res.brownoutFrac;
  const cls = (v, good) => (good ? 'good' : v ? 'bad' : '');
  $('live-metrics').innerHTML = [
    ['responsiveness', res.responsiveness.toFixed(0), 'spikes per event', ''],
    ['brownout', (bo * 100).toFixed(1) + '%', 'time below 5% reserve', bo < 0.005 ? 'good' : bo > 0.1 ? 'bad' : 'warn'],
    ['min reserve', res.minReserve.toFixed(3), 'safety margin', res.minReserve > 0.15 ? 'good' : res.minReserve < 0.02 ? 'bad' : 'warn'],
    ['spikes lost', res.suppressed.toLocaleString(), 'could not be paid for', res.suppressed > 5000 ? 'bad' : res.suppressed < 100 ? 'good' : 'warn'],
  ].map(([k, v, sub, c]) =>
    `<div class="metric"><div class="k">${k}</div><div class="v ${c}">${v}</div>
     <div class="k" style="text-transform:none;letter-spacing:0;margin-top:2px">${sub}</div></div>`).join('');

  // canvas
  const { c, w, h, ok } = prep($('trace'));
  if (!ok) return;                       // hidden container; ResizeObserver will retry
  const L = 52, R = 14, T = 12, gap = 26;
  const pw = w - L - R;
  const ph = (h - T - gap * 3 - 22) / 4;
  const xs = s.t;

  const panels = [
    { ys: s.glucose, lab: 'glucose (mM)', col: '#2f6f8f', y0: 0, y1: 7 },
    { ys: s.power, lab: 'cell power (µW)', col: '#1f7a4d', y0: 0, y1: Math.max(10, o.pMaxUw) },
    { ys: s.level, lab: 'reserve (0–1)', col: COLORS[current], y0: 0, y1: 1 },
    { ys: s.rate, lab: 'rate scale (0–1)', col: COLORS[current], y0: 0, y1: 1 },
  ];

  panels.forEach((p, i) => {
    const y = T + i * (ph + gap);
    // event windows
    trace.windows.forEach(([a, b]) => {
      band(c, L, y, pw, ph, a / trace.glucose.length, b / trace.glucose.length, 'rgba(179,52,31,.07)');
    });
    if (p.lab.startsWith('reserve')) {
      // brownout threshold
      const yy = y + ph - ph * 0.05;
      c.strokeStyle = 'rgba(179,52,31,.45)'; c.lineWidth = 1;
      c.setLineDash([3, 3]); c.beginPath(); c.moveTo(L, yy); c.lineTo(L + pw, yy); c.stroke();
      c.setLineDash([]);
      c.fillStyle = 'rgba(179,52,31,.7)'; c.font = '9.5px ui-monospace, monospace';
      c.textAlign = 'left'; c.textBaseline = 'bottom';
      c.fillText('brownout', L + 4, yy - 2);
    }
    axes(c, L, y, pw, ph, {
      ylab: p.lab, y0: p.y0, y1: p.y1,
      xlab: i === 3 ? 'time (s) →  60' : null, ticks: 2,
    });
    line(c, xs, p.ys, L, y, pw, ph, p.y0, p.y1, p.col, 1.3);
  });

  $('trace-note').textContent =
    `Seed ${o.seed}. Shaded bands are the six urgent events. `
    + `The dashed line in the reserve panel is the 5% brownout threshold. `
    + (bo > 0.5 ? 'This policy is in brownout for most of the run.'
      : bo > 0.02 ? 'This policy dips into brownout during the famines.'
      : 'The reserve is defended throughout.');
}

// ---------------------------------------------------------------- comparison

function yieldFrame() { return new Promise((r) => setTimeout(r, 0)); }

async function runComparison() {
  const btn = $('run-compare');
  btn.disabled = true;
  const N = +document.querySelector('input[name=nseeds]:checked').value;
  const o = opts();
  const acc = {};
  ORDER.forEach((k) => (acc[k] = { responsiveness: [], brownoutFrac: [], minReserve: [], efficiency: [] }));

  let done = 0;
  const total = N * ORDER.length;
  for (let s = 0; s < N; s++) {
    const trace = makeTrace(s, { famineDepthMM: o.famineDepthMM });
    for (const name of ORDER) {
      const r = runPolicy(trace, policyFor(name, o), s, {
        capacityUj: o.capacityUj, pMaxUw: o.pMaxUw, sampleEvery: 1e9,
      });
      acc[name].responsiveness.push(r.responsiveness);
      acc[name].brownoutFrac.push(r.brownoutFrac);
      acc[name].minReserve.push(r.minReserve);
      acc[name].efficiency.push(r.efficiency);
      done++;
      $('cmp-progress').textContent = `${Math.round((100 * done) / total)}%`;
    }
    await yieldFrame();
  }
  $('cmp-progress').textContent = '';
  btn.disabled = false;
  renderComparison(acc, N, o);
}

function renderComparison(acc, N, o) {
  const cell = (arr, dp) => {
    const [m, lo, hi] = bootstrapCI(arr);
    const w = hi - lo;
    return `${m.toFixed(dp)}<br><span class="ci">${w < 1e-9 ? '—' : `[${lo.toFixed(dp)}, ${hi.toFixed(dp)}]`}</span>`;
  };
  const rows = ORDER.map((k) => {
    const a = acc[k];
    const ours = k === 'adaptive-metabolic';
    return `<tr class="${ours ? 'ours' : ''}">
      <td>${POLICIES[k].label}</td>
      <td>${cell(a.responsiveness, 1)}</td>
      <td>${cell(a.brownoutFrac, 3)}</td>
      <td>${cell(a.minReserve, 3)}</td>
      <td>${cell(a.efficiency, 3)}</td></tr>`;
  }).join('');

  const ours = acc['adaptive-metabolic'];
  const oR = mean(ours.responsiveness), oB = mean(ours.brownoutFrac), oM = mean(ours.minReserve);
  const dv = acc['static-dvfs'], pg = acc['power-gating'];
  const dvR = mean(dv.responsiveness), dvB = mean(dv.brownoutFrac);
  const pgR = mean(pg.responsiveness);
  const beatsDvfs = oR > dvR;

  $('cmp-out').innerHTML = `
  <table>
    <thead><tr><th>policy</th><th>responsiveness</th><th>brownout</th>
      <th>min reserve</th><th>efficiency</th></tr></thead>
    <tbody>${rows}</tbody>
  </table>
  <p class="note">${N} paired seeds · percentile bootstrap, 2000 resamples ·
    cell ${o.pMaxUw} µW · store ${o.capacityUj} µJ · famine floor ${o.famineDepthMM} mM.
    A dash means the metric was identical across every seed, so the interval has zero width.</p>
  <div class="verdict">
    <strong>Read this honestly.</strong>
    ${beatsDvfs
      ? `Under these settings the regulator leads on responsiveness (${oR.toFixed(0)} vs ${dvR.toFixed(0)}) <em>and</em> holds a ${oM.toFixed(3)} reserve at ${(oB * 100).toFixed(1)}% brownout.`
      : `Static DVFS is <em>more</em> responsive than the regulator here (${dvR.toFixed(0)} vs ${oR.toFixed(0)}). It gets there by browning out ${(dvB * 100).toFixed(1)}% of the time and keeping essentially no reserve, while the regulator holds ${oM.toFixed(3)} at ${(oB * 100).toFixed(1)}%.`}
    Against power gating — the only other policy that avoids brownout — the regulator is
    ${(oR / Math.max(pgR, 1e-9)).toFixed(1)}× more responsive at equal safety.
    <strong>The claim is ownership of the tradeoff, not an outright win.</strong>
  </div>`;
}

// ---------------------------------------------------------------- cliff

async function runCliff() {
  const btn = $('run-cliff');
  btn.disabled = true;
  const o = opts();
  const N = 8;
  const scales = [];
  for (let s = 0.10; s <= 0.901; s += 0.05) scales.push(+s.toFixed(2));

  const rows = [];
  let done = 0;
  for (const sc of scales) {
    const r = { responsiveness: [], brownoutFrac: [], minReserve: [] };
    for (let s = 0; s < N; s++) {
      const t = makeTrace(s, { famineDepthMM: o.famineDepthMM });
      const x = runPolicy(t, POLICIES['static-dvfs'].make({ scale: sc }), s, {
        capacityUj: o.capacityUj, pMaxUw: o.pMaxUw, sampleEvery: 1e9,
      });
      r.responsiveness.push(x.responsiveness);
      r.brownoutFrac.push(x.brownoutFrac);
      r.minReserve.push(x.minReserve);
    }
    rows.push({ scale: sc, resp: mean(r.responsiveness), bo: mean(r.brownoutFrac), mr: mean(r.minReserve) });
    done++;
    $('cliff-progress').textContent = `${Math.round((100 * done) / scales.length)}%`;
    await yieldFrame();
  }

  const our = { responsiveness: [], brownoutFrac: [], minReserve: [] };
  for (let s = 0; s < N; s++) {
    const t = makeTrace(s, { famineDepthMM: o.famineDepthMM });
    const x = runPolicy(t, policyFor('adaptive-metabolic', o), s, {
      capacityUj: o.capacityUj, pMaxUw: o.pMaxUw, sampleEvery: 1e9,
    });
    our.responsiveness.push(x.responsiveness);
    our.brownoutFrac.push(x.brownoutFrac);
    our.minReserve.push(x.minReserve);
  }
  $('cliff-progress').textContent = '';
  btn.disabled = false;
  drawCliff(rows, {
    resp: mean(our.responsiveness), bo: mean(our.brownoutFrac), mr: mean(our.minReserve),
  }, N);
}

function drawCliff(rows, ours, N) {
  const working = rows.filter((r) => r.resp > 1);
  const idle = rows.filter((r) => r.resp <= 1);
  const first = working[0];
  const lastIdle = idle.length ? idle[idle.length - 1] : null;

  $('cliff-out').innerHTML = lastIdle && first ? `
    <div class="verdict">
      <strong>The cliff sits between scale ${lastIdle.scale.toFixed(2)} and
      ${first.scale.toFixed(2)}.</strong><br>
      At ${lastIdle.scale.toFixed(2)}: ${lastIdle.resp.toFixed(0)} spikes per event,
      ${(lastIdle.bo * 100).toFixed(1)}% brownout, reserve ${lastIdle.mr.toFixed(3)} —
      perfectly safe, because it computes nothing.<br>
      At ${first.scale.toFixed(2)}: ${first.resp.toFixed(0)} spikes per event,
      ${(first.bo * 100).toFixed(1)}% brownout, reserve ${first.mr.toFixed(3)} —
      it computes, and the margin is gone.<br><br>
      There is no static setting in between, because a fixed knob cannot express
      “compute and keep a margin”: it cannot see the reserve.
      The regulator reaches ${ours.resp.toFixed(0)} spikes per event at
      ${(ours.bo * 100).toFixed(1)}% brownout while holding ${ours.mr.toFixed(3)}.
    </div>` : `<p class="note">No cliff detected at these settings.</p>`;

  const { c, w, h, ok } = prep($('cliff'));
  if (!ok) return;
  const L = 54, R = 16, T = 18, B = 34, mid = 30;
  const pw = (w - L - R - mid) / 2, ph = h - T - B;

  // left: responsiveness vs scale
  const maxR = Math.max(ours.resp, ...rows.map((r) => r.resp)) * 1.12;
  axes(c, L, T, pw, ph, { ylab: 'spikes per event', y0: 0, y1: maxR, xlab: 'static duty scale →', ticks: 4 });
  c.strokeStyle = COLORS['static-dvfs']; c.lineWidth = 1.6; c.beginPath();
  rows.forEach((r, i) => {
    const x = L + (pw * i) / (rows.length - 1);
    const y = T + ph - (ph * r.resp) / maxR;
    i ? c.lineTo(x, y) : c.moveTo(x, y);
  });
  c.stroke();
  rows.forEach((r, i) => {
    const x = L + (pw * i) / (rows.length - 1);
    const y = T + ph - (ph * r.resp) / maxR;
    c.beginPath(); c.arc(x, y, 3, 0, 7);
    if (r.resp <= 1) { c.strokeStyle = '#9aa1aa'; c.fillStyle = '#fff'; c.fill(); c.lineWidth = 1.4; c.stroke(); }
    else { c.fillStyle = COLORS['static-dvfs']; c.fill(); }
  });
  const yo = T + ph - (ph * ours.resp) / maxR;
  c.strokeStyle = COLORS['adaptive-metabolic']; c.lineWidth = 1.5;
  c.setLineDash([5, 4]); c.beginPath(); c.moveTo(L, yo); c.lineTo(L + pw, yo); c.stroke(); c.setLineDash([]);
  c.fillStyle = COLORS['adaptive-metabolic']; c.font = '500 10px ui-monospace, monospace';
  c.textAlign = 'right'; c.textBaseline = 'bottom';
  c.fillText('adaptive regulator', L + pw - 2, yo - 3);

  // right: safety plane
  const x2 = L + pw + mid + 6;
  axes(c, x2, T, pw, ph, { ylab: 'min reserve (higher better)', y0: 0, y1: 0.55, xlab: 'brownout fraction →', ticks: 4 });
  const px = (bo) => x2 + pw * Math.min(1, bo / 1.0);
  const py = (mr) => T + ph - (ph * mr) / 0.55;
  c.strokeStyle = '#c9ced6'; c.lineWidth = 1.2; c.beginPath();
  rows.forEach((r, i) => (i ? c.lineTo(px(r.bo), py(r.mr)) : c.moveTo(px(r.bo), py(r.mr))));
  c.stroke();
  rows.forEach((r) => {
    c.beginPath(); c.arc(px(r.bo), py(r.mr), 3.4, 0, 7);
    if (r.resp <= 1) { c.strokeStyle = '#9aa1aa'; c.fillStyle = '#fff'; c.fill(); c.lineWidth = 1.4; c.stroke(); }
    else { c.fillStyle = COLORS['static-dvfs']; c.fill(); }
  });
  // ours as a star
  c.fillStyle = COLORS['adaptive-metabolic'];
  star(c, px(ours.bo), py(ours.mr), 7.5);
  if (lastIdle) {
    c.strokeStyle = '#b6bcc4'; c.lineWidth = 1;
    const ix = px(lastIdle.bo), iy = py(lastIdle.mr);
    c.beginPath(); c.moveTo(ix + 8, iy + 6); c.lineTo(ix + 46, iy + 26); c.stroke();
    c.fillStyle = '#7b828c'; c.font = '9.5px ui-monospace, monospace';
    c.textAlign = 'left'; c.textBaseline = 'top';
    c.fillText('idle: safe because', ix + 48, iy + 18);
    c.fillText('it computes nothing', ix + 48, iy + 29);
  }
  c.fillStyle = COLORS['adaptive-metabolic']; c.font = '500 10px ui-monospace, monospace';
  c.textAlign = 'left'; c.textBaseline = 'middle';
  c.fillText(`adaptive (${ours.resp.toFixed(0)} spikes/event)`, px(ours.bo) + 12, py(ours.mr));

  c.fillStyle = '#9aa1aa'; c.font = '10px ui-monospace, monospace';
  c.textAlign = 'left'; c.textBaseline = 'top';
  c.fillText(`${N} seeds per point · hollow markers do no work`, L, h - 13);
}

function star(c, x, y, r) {
  c.beginPath();
  for (let i = 0; i < 10; i++) {
    const rr = i % 2 ? r * 0.45 : r;
    const a = (Math.PI / 5) * i - Math.PI / 2;
    const px = x + rr * Math.cos(a), py = y + rr * Math.sin(a);
    i ? c.lineTo(px, py) : c.moveTo(px, py);
  }
  c.closePath(); c.fill();
}

// ---------------------------------------------------------------- wiring

function syncVisibility() {
  document.querySelectorAll('.ctrl[data-only]').forEach((el) => {
    el.hidden = el.dataset.only !== current;
  });
}

function initSegmented() {
  const seg = $('policy-seg');
  seg.innerHTML = ORDER.map((k) =>
    `<button class="seg-btn" data-k="${k}" aria-pressed="${k === current}">${POLICIES[k].label}</button>`).join('');
  seg.addEventListener('click', (e) => {
    const b = e.target.closest('.seg-btn');
    if (!b) return;
    current = b.dataset.k;
    seg.querySelectorAll('.seg-btn').forEach((x) => x.setAttribute('aria-pressed', x.dataset.k === current));
    $('policy-blurb').textContent = POLICIES[current].blurb;
    syncVisibility();
    drawTrace();
  });
  $('policy-blurb').textContent = POLICIES[current].blurb;
}

const LABELS = {
  's-seed': (v) => v,
  's-pmax': (v) => `${v} µW`,
  's-cap': (v) => `${v} µJ`,
  's-famine': (v) => `${(+v).toFixed(1)} mM`,
  's-gain': (v) => (+v).toFixed(1),
  's-set': (v) => (+v).toFixed(2),
  's-scale': (v) => (+v).toFixed(2),
  's-low': (v) => (+v).toFixed(2),
};

function initSliders() {
  Object.keys(LABELS).forEach((id) => {
    const el = $(id);
    const out = $('o-' + id.slice(2));
    const upd = () => { out.textContent = LABELS[id](el.value); };
    upd();
    let raf = null;
    el.addEventListener('input', () => {
      upd();
      if (raf) cancelAnimationFrame(raf);
      raf = requestAnimationFrame(drawTrace);
    });
  });
}

window.addEventListener('load', () => {
  initSegmented();
  initSliders();
  syncVisibility();
  drawTrace();
  $('run-compare').addEventListener('click', runComparison);
  $('run-cliff').addEventListener('click', runCliff);

  // #run-all computes both experiments on load. Useful for sharing a fully
  // populated page, and for automated screenshot checks.
  if (location.hash === '#run-all') {
    runComparison().then(runCliff);
  }
});

let rz = null;
window.addEventListener('resize', () => {
  if (rz) clearTimeout(rz);
  rz = setTimeout(drawTrace, 150);
});

/* A canvas inside a hidden or zero-width container measures 0 and draws nothing,
 * and a plain load handler never retries. Redraw as soon as it actually has a
 * width, which also covers being loaded in a background tab or collapsed pane. */
if (typeof ResizeObserver !== 'undefined') {
  let lastW = 0;
  const ro = new ResizeObserver((entries) => {
    for (const e of entries) {
      const w = Math.round(e.contentRect.width);
      if (w > 0 && w !== lastW) { lastW = w; drawTrace(); }
    }
  });
  window.addEventListener('load', () => ro.observe($('trace')));
}
