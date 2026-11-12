/**
 * JAES Headless Benchmark Runner
 * Measures physical discrete-time MNA circuit solver vs. WAV playback baseline
 * with nanosecond precision using process.hrtime.bigint().
 */
const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, 'benchmark.html');
const html = fs.readFileSync(htmlPath, 'utf8');

const idx1 = html.indexOf('function LIB()');
const idx2 = html.indexOf('</script>', idx1);
eval(html.slice(idx1, idx2));
const L = LIB();

const sr = 48000;
const blockSize = 128;
const nBlocks = 1000;
const budgetUs = (blockSize / sr) * 1e6; // 2666.67 us @ 48kHz / 128 samples

// Calibrate timing harness overhead
const t0_oh = process.hrtime.bigint();
let dummy = 0;
const n_oh = 100000;
for(let i=0; i<n_oh; i++){
  const a = process.hrtime.bigint();
  dummy += Number(process.hrtime.bigint() - a);
}
const overheadUs = Number(process.hrtime.bigint() - t0_oh) / (n_oh * 1000);

function computeStats(arr) {
  arr.sort((a, b) => a - b);
  const sum = arr.reduce((a, b) => a + b, 0);
  const mean = sum / arr.length;
  const p50 = arr[Math.floor(arr.length * 0.50)];
  const p95 = arr[Math.floor(arr.length * 0.95)];
  const p99 = arr[Math.floor(arr.length * 0.99)];
  const max = arr[arr.length - 1];
  const missed = arr.filter(v => v > budgetUs).length;
  const missRate = (missed / arr.length) * 100;
  return { mean, p50, p95, p99, max, missRate };
}

// Select representative presets: Linear passive, nonlinear diode, complex active
const testPresets = [
  L.LIBRARY.find(p => p.name === 'RC high-pass') || L.LIBRARY[0],
  L.LIBRARY.find(p => p.name === 'Half-wave rectifier') || L.LIBRARY[1],
  L.LIBRARY.find(p => p.id === 'fuzz') || L.LIBRARY[2]
];

console.log('========================================================================');
console.log('       JAES RESEARCH BENCHMARK: LIVE MNA vs. WAV PLAYBACK');
console.log('========================================================================');
console.log(`Sample Rate: ${sr} Hz | Block Size: ${blockSize} samples`);
console.log(`Audio Deadline Budget: ${budgetUs.toFixed(2)} µs (${(budgetUs/1000).toFixed(3)} ms)`);
console.log(`Timing Harness Overhead: ${overheadUs.toFixed(4)} µs/call`);
console.log('========================================================================\n');

const allResults = [];
const outL = new Float32Array(blockSize);
const outR = new Float32Array(blockSize);

const wavBuf = new Float32Array(sr * 2);
for(let i=0; i<wavBuf.length; i++) wavBuf[i] = Math.sin(2 * Math.PI * 440 * i / sr);

for (const p of testPresets) {
  console.log(`\n>>> Evaluating Preset: "${p.name}" (ID: ${p.id || 'N/A'})`);
  const board = p.make();

  for (const v of [1, 2, 4]) {
    // 1. Live MNA
    const poly = new L.Poly(sr);
    poly.want = v;
    poly.set({board: board, poly: v});
    for(let vi=0; vi<v; vi++) poly.set({on: 36 + vi*7});
    for(let i=0; i<50; i++) poly.process(outL, outR, blockSize); // warm up

    const mnaTimes = new Float64Array(nBlocks);
    for(let b=0; b<nBlocks; b++){
      const t0 = process.hrtime.bigint();
      poly.process(outL, outR, blockSize);
      mnaTimes[b] = Number(process.hrtime.bigint() - t0) / 1000;
    }
    const sMna = computeStats(Array.from(mnaTimes));
    allResults.push({
      Preset: p.name,
      Condition: `Live MNA (${v}V)`,
      Voices: v,
      ...sMna
    });

    // 2. WAV Playback Baseline
    const wavTimes = new Float64Array(nBlocks);
    const phases = new Float64Array(v);
    const phaseSteps = new Float64Array(v).map((_, i) => Math.pow(2, (i*7)/12));
    for(let i=0; i<50; i++){
      for(let vi=0; vi<v; vi++) phases[vi] = (phases[vi] + phaseSteps[vi] * blockSize) % wavBuf.length;
    }

    for(let b=0; b<nBlocks; b++){
      const t0 = process.hrtime.bigint();
      for(let vi=0; vi<v; vi++){
        let ph = phases[vi];
        const step = phaseSteps[vi];
        for(let s=0; s<blockSize; s++){
          const idx = Math.floor(ph);
          const frac = ph - idx;
          const s0 = wavBuf[idx % wavBuf.length];
          const s1 = wavBuf[(idx + 1) % wavBuf.length];
          outL[s] += s0 + frac * (s1 - s0);
          ph += step;
        }
        phases[vi] = ph % wavBuf.length;
      }
      wavTimes[b] = Number(process.hrtime.bigint() - t0) / 1000;
    }
    const sWav = computeStats(Array.from(wavTimes));
    allResults.push({
      Preset: p.name,
      Condition: `WAV Playback (${v}V)`,
      Voices: v,
      ...sWav
    });
  }
}

console.log('\n--- SUMMARY RESULTS TABLE (Values in Microseconds) ---');
console.table(allResults.map(r => ({
  Preset: r.Preset,
  Condition: r.Condition,
  'Mean (µs)': r.mean.toFixed(1),
  'P50 (µs)': r.p50.toFixed(1),
  'P95 (µs)': r.p95.toFixed(1),
  'P99 (µs)': r.p99.toFixed(1),
  'Max (µs)': r.max.toFixed(1),
  'Miss%': r.missRate.toFixed(1) + '%'
})));

// Save CSV
const csvHeader = 'Preset,Condition,Voices,Mean_us,P50_us,P95_us,P99_us,Max_us,MissRate_pct,DeadlineBudget_us,Overhead_us\n';
const csvRows = allResults.map(r => 
  `"${r.Preset}","${r.Condition}",${r.Voices},${r.mean.toFixed(2)},${r.p50.toFixed(2)},${r.p95.toFixed(2)},${r.p99.toFixed(2)},${r.max.toFixed(2)},${r.missRate.toFixed(2)},${budgetUs.toFixed(2)},${overheadUs.toFixed(4)}`
).join('\n');
fs.writeFileSync(path.join(__dirname, 'jaes_benchmark_pilot_results.csv'), csvHeader + csvRows);

// Save JSON
const jsonPayload = {
  experiment: 'JAES Pilot Benchmark: Real-Time Circuit Simulation vs. WAV Playback',
  timestamp: new Date().toISOString(),
  configuration: {
    sampleRate: sr,
    blockSize: blockSize,
    budgetUs: budgetUs,
    timingHarnessOverheadUs: overheadUs
  },
  results: allResults
};
fs.writeFileSync(path.join(__dirname, 'jaes_benchmark_pilot_results.json'), JSON.stringify(jsonPayload, null, 2));

console.log('\n[Export Complete] Saved:');
console.log(' - jaes_benchmark_pilot_results.csv');
console.log(' - jaes_benchmark_pilot_results.json\n');

