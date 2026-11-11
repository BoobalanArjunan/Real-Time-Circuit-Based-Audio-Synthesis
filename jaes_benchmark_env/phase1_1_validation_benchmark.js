/**
 * JAES Phase 1.1: Benchmark Correction and Validation Suite
 * 
 * Implements strict methodological controls:
 * 1. Clears WAV output buffers (outL, outR) before every processing block.
 * 2. Generates WAV reference audio directly from the physical MNA preset and exact MIDI notes.
 * 3. Records individual block timings with block indices for outlier analysis.
 * 4. Strictly separates genuine Cold-Start tests from Warmed Steady-State tests.
 * 5. Captures raw runtime environment metadata (CPU, OS, Node, memory).
 * 6. Executes independent trials in randomized condition order.
 * 7. Records direct Newton-Raphson iteration counts and convergence telemetry.
 * 8. Exports revised CSV and JSON datasets.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const htmlPath = path.join(__dirname, 'benchmark.html');
const html = fs.readFileSync(htmlPath, 'utf8');

const idx1 = html.indexOf('function LIB()');
const idx2 = html.indexOf('</script>', idx1);
eval(html.slice(idx1, idx2));
const L = LIB();

const sr = 48000;
const blockSize = 128;
const nBlocksSteadyState = 1000;
const nWarmupBlocks = 100;
const budgetUs = (blockSize / sr) * 1e6; // 2666.67 µs @ 48kHz / 128 samples

// Runtime environment metadata
const cpus = os.cpus();
const envMetadata = {
  cpuModel: cpus[0].model,
  cpuSpeedMhz: cpus[0].speed,
  cpuLogicalCores: cpus.length,
  osPlatform: os.platform(),
  osType: os.type(),
  osRelease: os.release(),
  osArch: os.arch(),
  totalMemoryBytes: os.totalmem(),
  freeMemoryBytes: os.freemem(),
  nodeVersion: process.version,
  sampleRate: sr,
  blockSize: blockSize,
  audioDeadlineBudgetUs: budgetUs
};

// Calibrate timing harness overhead
const t0_oh = process.hrtime.bigint();
let dummy = 0;
const n_oh = 100000;
for (let i = 0; i < n_oh; i++) {
  const a = process.hrtime.bigint();
  dummy += Number(process.hrtime.bigint() - a);
}
const timingHarnessOverheadUs = Number(process.hrtime.bigint() - t0_oh) / (n_oh * 1000);

function computeStats(arr) {
  const sorted = Float64Array.from(arr).sort();
  const sum = sorted.reduce((a, b) => a + b, 0);
  const mean = sum / sorted.length;
  const p50 = sorted[Math.floor(sorted.length * 0.50)];
  const p95 = sorted[Math.floor(sorted.length * 0.95)];
  const p99 = sorted[Math.floor(sorted.length * 0.99)];
  const max = sorted[sorted.length - 1];
  const min = sorted[0];
  const missed = sorted.filter(v => v > budgetUs).length;
  const missRate = (missed / sorted.length) * 100;
  return { mean, p50, p95, p99, min, max, missRate };
}

// Select representative presets across complexity spectrum
const testPresets = [
  L.LIBRARY.find(p => p.id === 'hp') || L.LIBRARY.find(p => p.name === 'RC high-pass') || L.LIBRARY[0],
  L.LIBRARY.find(p => p.id === 'rect') || L.LIBRARY.find(p => p.name === 'Half-wave rectifier') || L.LIBRARY[1],
  L.LIBRARY.find(p => p.id === 'fuzz') || L.LIBRARY[2]
];

console.log('========================================================================');
console.log('     JAES PHASE 1.1: BENCHMARK CORRECTION & VALIDATION SUITE');
console.log('========================================================================');
console.log(`CPU: ${envMetadata.cpuModel} (${envMetadata.cpuLogicalCores} cores)`);
console.log(`OS: ${envMetadata.osType} ${envMetadata.osRelease} (${envMetadata.osArch})`);
console.log(`Node.js: ${envMetadata.nodeVersion} | Sample Rate: ${sr} Hz | Block Size: ${blockSize}`);
console.log(`Deadline Budget: ${budgetUs.toFixed(2)} µs (${(budgetUs/1000).toFixed(3)} ms)`);
console.log(`Timing Harness Overhead: ${timingHarnessOverheadUs.toFixed(4)} µs/call`);
console.log('========================================================================\n');

// Helper to pre-render exact MNA reference audio for each preset and note
function renderMnaReferenceAudio(preset, note, durationSec = 2.0) {
  const pa = L.point(preset.probes[0][0], preset.probes[0][1]);
  const pb = L.point(preset.probes[1][0], preset.probes[1][1]);
  const eng = new L.Engine(sr);
  const board = preset.make();
  eng.setBoard(Object.assign({}, board, { reset: 1 }));
  eng.set({ probes: [pa, pb], note: note, gate: 1, trig: 1, jump: 1 });

  const totalLen = Math.floor(durationSec * sr);
  const bufL = new Float32Array(totalLen);
  const bufR = new Float32Array(totalLen);
  const tmpL = new Float32Array(blockSize);
  const tmpR = new Float32Array(blockSize);

  for (let i = 0; i < totalLen; i += blockSize) {
    const chunk = Math.min(blockSize, totalLen - i);
    eng.process(tmpL, tmpR, chunk);
    for (let k = 0; k < chunk; k++) {
      bufL[i + k] = tmpL[k];
      bufR[i + k] = tmpR[k];
    }
  }
  return { left: bufL, right: bufR, length: totalLen };
}

const outL = new Float32Array(blockSize);
const outR = new Float32Array(blockSize);

const steadyStateResults = [];
const coldStartResults = [];
const outlierLog = [];

const voiceLevels = [1, 2, 4];

for (const p of testPresets) {
  const pa = L.point(p.probes[0][0], p.probes[0][1]);
  const pb = L.point(p.probes[1][0], p.probes[1][1]);
  console.log(`\n>>> Evaluating Preset: "${p.name}" (ID: ${p.id || 'N/A'})`);

  // Pre-render exact matched reference buffers for notes used
  const noteList = [36, 43, 50, 57];
  const refBuffers = noteList.map(n => renderMnaReferenceAudio(p, n, 2.5));

  for (const v of voiceLevels) {
    // -------------------------------------------------------------
    // TEST 1: GENUINE COLD-START TEST (Block 0 without warm-up)
    // Repeat across 20 independent cold allocations
    // -------------------------------------------------------------
    const coldMnaTimes = [];
    const coldWavTimes = [];
    const nColdTrials = 20;

    for (let trial = 0; trial < nColdTrials; trial++) {
      // Cold MNA
      const polyCold = new L.Poly(sr);
      polyCold.want = v;
      polyCold.set({ probes: [pa, pb], board: p.make(), poly: v });
      for (let vi = 0; vi < v; vi++) polyCold.set({ on: noteList[vi] });

      outL.fill(0);
      outR.fill(0);
      const t0_mna = process.hrtime.bigint();
      polyCold.process(outL, outR, blockSize);
      coldMnaTimes.push(Number(process.hrtime.bigint() - t0_mna) / 1000);

      // Cold WAV Baseline
      outL.fill(0);
      outR.fill(0);
      const t0_wav = process.hrtime.bigint();
      // Read block 0 from matched preset buffer
      for (let vi = 0; vi < v; vi++) {
        const bL = refBuffers[vi].left;
        const bR = refBuffers[vi].right;
        for (let s = 0; s < blockSize; s++) {
          outL[s] += bL[s];
          outR[s] += bR[s];
        }
      }
      coldWavTimes.push(Number(process.hrtime.bigint() - t0_wav) / 1000);
    }

    const sColdMna = computeStats(coldMnaTimes);
    const sColdWav = computeStats(coldWavTimes);

    coldStartResults.push({
      Preset: p.name,
      Condition: `Live MNA (${v}V)`,
      Voices: v,
      Type: 'Cold-Start (Block 0)',
      ...sColdMna
    });
    coldStartResults.push({
      Preset: p.name,
      Condition: `WAV Baseline (${v}V)`,
      Voices: v,
      Type: 'Cold-Start (Block 0)',
      ...sColdWav
    });

    // -------------------------------------------------------------
    // TEST 2: WARMED STEADY-STATE TEST (1,000 blocks after warm-up)
    // With randomized condition order per run
    // -------------------------------------------------------------
    const conditions = ['MNA', 'WAV'];
    // Randomize order
    if (Math.random() > 0.5) conditions.reverse();

    for (const cond of conditions) {
      if (cond === 'MNA') {
        const polyWarm = new L.Poly(sr);
        polyWarm.want = v;
        polyWarm.set({ probes: [pa, pb], board: p.make(), poly: v });
        for (let vi = 0; vi < v; vi++) polyWarm.set({ on: noteList[vi] });

        // Warm up strictly for 100 blocks
        for (let i = 0; i < nWarmupBlocks; i++) {
          outL.fill(0);
          outR.fill(0);
          polyWarm.process(outL, outR, blockSize);
        }

        const mnaBlockTimes = new Float64Array(nBlocksSteadyState);
        let nrItersTotal = 0;
        let nrFailsTotal = 0;

        for (let b = 0; b < nBlocksSteadyState; b++) {
          outL.fill(0);
          outR.fill(0);
          const t0 = process.hrtime.bigint();
          polyWarm.process(outL, outR, blockSize);
          const dt = Number(process.hrtime.bigint() - t0) / 1000;
          mnaBlockTimes[b] = dt;

          const fl = polyWarm.flush();
          if (fl.nrIters) nrItersTotal += fl.nrIters;
          if (fl.nrFails) nrFailsTotal += fl.nrFails;

          // Outlier logging
          if (dt > budgetUs) {
            outlierLog.push({
              preset: p.name,
              condition: `Live MNA (${v}V)`,
              blockIndex: b,
              durationUs: dt,
              budgetUs: budgetUs,
              nrIters: fl.nrIters || 0,
              type: 'Deadline Exceeded (> 2666.67 µs)'
            });
          }
        }

        const sMna = computeStats(Array.from(mnaBlockTimes));
        steadyStateResults.push({
          Preset: p.name,
          Condition: `Live MNA (${v}V)`,
          Voices: v,
          Type: 'Steady-State (Warm)',
          meanNrIters: (nrItersTotal / nBlocksSteadyState).toFixed(2),
          totalNrFails: nrFailsTotal,
          ...sMna
        });
      } else {
        // Matched WAV playback baseline with buffer clearing & stereo staging
        const wavBlockTimes = new Float64Array(nBlocksSteadyState);
        const phases = new Float64Array(v);
        const phaseSteps = new Float64Array(v).fill(1.0); // Exact 1x playback rate since buffers are note-matched

        // Warm up for 100 blocks
        for (let i = 0; i < nWarmupBlocks; i++) {
          outL.fill(0);
          outR.fill(0);
          for (let vi = 0; vi < v; vi++) {
            phases[vi] = (phases[vi] + blockSize) % refBuffers[vi].length;
          }
        }

        for (let b = 0; b < nBlocksSteadyState; b++) {
          // REQUIREMENT 1: Rigorously clear buffers before every block
          outL.fill(0);
          outR.fill(0);

          const t0 = process.hrtime.bigint();
          for (let vi = 0; vi < v; vi++) {
            const bL = refBuffers[vi].left;
            const bR = refBuffers[vi].right;
            const bLen = refBuffers[vi].length;
            let ph = phases[vi];

            for (let s = 0; s < blockSize; s++) {
              const idx = Math.floor(ph);
              const frac = ph - idx;
              const nextIdx = (idx + 1) % bLen;
              
              // Linear interpolation on matched preset audio
              const sL0 = bL[idx];
              const sL1 = bL[nextIdx];
              const sR0 = bR[idx];
              const sR1 = bR[nextIdx];

              outL[s] += sL0 + frac * (sL1 - sL0);
              outR[s] += sR0 + frac * (sR1 - sR0);

              ph += 1.0;
              if (ph >= bLen) ph -= bLen;
            }
            phases[vi] = ph;
          }
          const dt = Number(process.hrtime.bigint() - t0) / 1000;
          wavBlockTimes[b] = dt;

          if (dt > budgetUs) {
            outlierLog.push({
              preset: p.name,
              condition: `WAV Baseline (${v}V)`,
              blockIndex: b,
              durationUs: dt,
              budgetUs: budgetUs,
              type: 'Deadline Exceeded (> 2666.67 µs)'
            });
          }
        }

        const sWav = computeStats(Array.from(wavBlockTimes));
        steadyStateResults.push({
          Preset: p.name,
          Condition: `WAV Baseline (${v}V)`,
          Voices: v,
          Type: 'Steady-State (Warm)',
          meanNrIters: 'N/A',
          totalNrFails: 'N/A',
          ...sWav
        });
      }
    }
  }
}

// -------------------------------------------------------------
// PRINT RESULTS TABLES
// -------------------------------------------------------------
console.log('\n========================================================================');
console.log('TABLE 1: STEADY-STATE (WARM-START) RESULTS (1,000 BLOCKS @ 48 kHz)');
console.log('========================================================================');
console.table(steadyStateResults.map(r => ({
  Preset: r.Preset,
  Condition: r.Condition,
  'Mean (µs)': r.mean.toFixed(1),
  'P50 (µs)': r.p50.toFixed(1),
  'P95 (µs)': r.p95.toFixed(1),
  'P99 (µs)': r.p99.toFixed(1),
  'Max (µs)': r.max.toFixed(1),
  'Budget %': ((r.p50 / budgetUs) * 100).toFixed(1) + '%',
  'Miss %': r.missRate.toFixed(1) + '%',
  'NR Iters': r.meanNrIters
})));

console.log('\n========================================================================');
console.log('TABLE 2: GENUINE COLD-START ALLOCATION RESULTS (BLOCK 0, 20 TRIALS)');
console.log('========================================================================');
console.table(coldStartResults.map(r => ({
  Preset: r.Preset,
  Condition: r.Condition,
  'Cold Mean (µs)': r.mean.toFixed(1),
  'Cold P50 (µs)': r.p50.toFixed(1),
  'Cold P95 (µs)': r.p95.toFixed(1),
  'Cold Max (µs)': r.max.toFixed(1),
  'Cold Budget %': ((r.p50 / budgetUs) * 100).toFixed(1) + '%'
})));

console.log('\n========================================================================');
console.log(`TABLE 3: OUTLIER TIMING LOG (Total Deadline Violations: ${outlierLog.length})`);
console.log('========================================================================');
if (outlierLog.length === 0) {
  console.log('Zero steady-state deadline violations observed across all tested blocks.');
} else {
  console.table(outlierLog);
}

// -------------------------------------------------------------
// EXPORT COMPREHENSIVE DATASETS (CSV & JSON)
// -------------------------------------------------------------
const csvHeader = 'Preset,Condition,Voices,Type,Mean_us,P50_us,P95_us,P99_us,Min_us,Max_us,MissRate_pct,DeadlineBudget_us,MeanNrIters\n';
const csvRowsSteady = steadyStateResults.map(r => 
  `"${r.Preset}","${r.Condition}",${r.Voices},"${r.Type}",${r.mean.toFixed(2)},${r.p50.toFixed(2)},${r.p95.toFixed(2)},${r.p99.toFixed(2)},${r.min.toFixed(2)},${r.max.toFixed(2)},${r.missRate.toFixed(2)},${budgetUs.toFixed(2)},"${r.meanNrIters}"`
).join('\n');
const csvRowsCold = coldStartResults.map(r => 
  `"${r.Preset}","${r.Condition}",${r.Voices},"${r.Type}",${r.mean.toFixed(2)},${r.p50.toFixed(2)},${r.p95.toFixed(2)},${r.p99.toFixed(2)},${r.min.toFixed(2)},${r.max.toFixed(2)},${r.missRate.toFixed(2)},${budgetUs.toFixed(2)},"N/A"`
).join('\n');

fs.writeFileSync(path.join(__dirname, 'jaes_phase1_1_validated_results.csv'), csvHeader + csvRowsSteady + '\n' + csvRowsCold);

const exportPayload = {
  experiment: 'JAES Phase 1.1: Benchmark Correction and Validation Report',
  timestamp: new Date().toISOString(),
  environment: envMetadata,
  timingOverheadUs: timingHarnessOverheadUs,
  outlierLog: outlierLog,
  steadyStateResults: steadyStateResults,
  coldStartResults: coldStartResults
};

fs.writeFileSync(path.join(__dirname, 'jaes_phase1_1_validated_results.json'), JSON.stringify(exportPayload, null, 2));

console.log('\n[Phase 1.1 Validation Export Complete]');
console.log(' - jaes_phase1_1_validated_results.csv');
console.log(' - jaes_phase1_1_validated_results.json\n');

