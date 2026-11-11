/**
 * JAES Phase 2 Experiment: Parameter Continuity and Modulation Responsiveness
 * 
 * Compares Live Discrete-Time MNA Circuit Simulation against a Professionally
 * Smoothed Sample-Playback Baseline under 60 Hz XR Gesture-Tracking Modulation.
 * 
 * Strict Methodological Controls:
 * - Rigorous buffer clearing (outL.fill(0), outR.fill(0)) before every block.
 * - Exact matched MNA pre-rendered audio for the sample-playback baseline.
 * - One-pole parameter smoothing filter (fc = 30 Hz) on the sample-playback baseline.
 * - Static unmodulated reference recording to normalize high-frequency baseline energy.
 * - Fast Radix-2 512-point FFT with Hann windowing for spectral flux calculation.
 * - 20 repeated randomized trials reporting full distributions (Mean, P50, P95, Max).
 * - Exports results to CSV and JSON.
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
const testDurationSec = 2.0;
const totalSamples = Math.floor(testDurationSec * sr);
const controlRateHz = 60;
const controlPeriodSamples = Math.floor(sr / controlRateHz); // 800 samples per control tick (16.67 ms)
const totalControlSteps = Math.floor(totalSamples / controlPeriodSamples); // 120 steps
const budgetUs = (blockSize / sr) * 1e6; // 2666.67 µs

// Fast 512-point Radix-2 Cooley-Tukey FFT implementation
function makeFFT(N) {
  const sinTab = new Float64Array(N);
  const cosTab = new Float64Array(N);
  for (let i = 0; i < N; i++) {
    sinTab[i] = Math.sin(-2 * Math.PI * i / N);
    cosTab[i] = Math.cos(-2 * Math.PI * i / N);
  }
  return function fft(real, imag) {
    let j = 0;
    for (let i = 0; i < N - 1; i++) {
      if (i < j) {
        let tr = real[i]; real[i] = real[j]; real[j] = tr;
        let ti = imag[i]; imag[i] = imag[j]; imag[j] = ti;
      }
      let k = N >> 1;
      while (k <= j) { j -= k; k >>= 1; }
      j += k;
    }
    for (let len = 2; len <= N; len <<= 1) {
      const half = len >> 1;
      const step = N / len;
      for (let i = 0; i < N; i += len) {
        for (let k = 0; k < half; k++) {
          const tabIdx = k * step;
          const u_r = cosTab[tabIdx];
          const u_i = sinTab[tabIdx];
          const tr = real[i + k + half] * u_r - imag[i + k + half] * u_i;
          const ti = real[i + k + half] * u_i + imag[i + k + half] * u_r;
          real[i + k + half] = real[i + k] - tr;
          imag[i + k + half] = imag[i + k] - ti;
          real[i + k] += tr;
          imag[i + k] += ti;
        }
      }
    }
  };
}

const N_FFT = 512;
const HOP_SIZE = 128;
const fft512 = makeFFT(N_FFT);
const hannWin = new Float64Array(N_FFT);
for (let n = 0; n < N_FFT; n++) {
  hannWin[n] = 0.5 * (1 - Math.cos(2 * Math.PI * n / N_FFT));
}

// Select representative non-linear circuit: Fuzz
const preset = L.LIBRARY.find(p => p.id === 'fuzz') || L.LIBRARY[2];
const pa = L.point(preset.probes[0][0], preset.probes[0][1]);
const pb = L.point(preset.probes[1][0], preset.probes[1][1]);

const baseBoard = preset.make();
let sweepSlot = -1;
let nominalVal = 1000;
for (let i = 0; i < baseBoard.t.length; i++) {
  if (baseBoard.t[i] === 2) { // Resistor
    sweepSlot = i;
    nominalVal = baseBoard.v[i];
    break;
  }
}

// Sweep trajectory: 60 Hz cosine trajectory from nominalVal*0.2 to nominalVal*5.0
const sweepTrajectory = new Float64Array(totalControlSteps);
const minVal = Math.max(100, nominalVal * 0.2);
const maxVal = nominalVal * 5.0;
for (let step = 0; step < totalControlSteps; step++) {
  const norm = step / (totalControlSteps - 1);
  const shape = 0.5 * (1 - Math.cos(Math.PI * norm));
  sweepTrajectory[step] = minVal * Math.pow(maxVal / minVal, shape);
}

// Pre-render exact matched reference sample from MNA preset
function renderReferenceSample() {
  const eng = new L.Engine(sr);
  const board = preset.make();
  eng.setBoard(Object.assign({}, board, { reset: 1 }));
  eng.set({ probes: [pa, pb], note: 45, gate: 1, trig: 1, jump: 1 });
  
  const buf = new Float32Array(sr * 3);
  const tmpL = new Float32Array(blockSize);
  const tmpR = new Float32Array(blockSize);
  for (let i = 0; i < buf.length; i += blockSize) {
    tmpL.fill(0);
    tmpR.fill(0);
    const chunk = Math.min(blockSize, buf.length - i);
    eng.process(tmpL, tmpR, chunk);
    for (let k = 0; k < chunk; k++) buf[i + k] = tmpL[k];
  }
  return buf;
}

const referenceSampleBuffer = renderReferenceSample();

// 1. Static Reference Recording (Nominal unmodulated parameter)
function recordStaticReference() {
  const eng = new L.Engine(sr);
  const board = preset.make();
  eng.setBoard(Object.assign({}, board, { reset: 1 }));
  eng.set({ probes: [pa, pb], note: 45, gate: 1, trig: 1, jump: 1 });
  
  const out = new Float32Array(totalSamples);
  const tmpL = new Float32Array(blockSize);
  const tmpR = new Float32Array(blockSize);
  for (let i = 0; i < totalSamples; i += blockSize) {
    tmpL.fill(0);
    tmpR.fill(0);
    const chunk = Math.min(blockSize, totalSamples - i);
    eng.process(tmpL, tmpR, chunk);
    for (let k = 0; k < chunk; k++) out[i + k] = tmpL[k];
  }
  return out;
}

const staticReferenceAudio = recordStaticReference();

// Baseline high-frequency derivative energy of the static circuit
function computeBaselineHfEnergy(signal) {
  let hfSum = 0;
  for (let i = 2; i < signal.length; i++) {
    const d2 = signal[i] - 2 * signal[i - 1] + signal[i - 2];
    hfSum += d2 * d2;
  }
  return hfSum / (signal.length - 2);
}

const staticBaselineHf = computeBaselineHfEnergy(staticReferenceAudio);

// 2. Condition A: Live MNA Dynamic Conductance Modulation
function runTrialLiveMNA(trialSeed) {
  const eng = new L.Engine(sr);
  const board = preset.make();
  eng.setBoard(Object.assign({}, board, { reset: 1 }));
  eng.set({ probes: [pa, pb], note: 45 + (trialSeed % 3) * 0.01, gate: 1, trig: 1, jump: 1 });
  
  const audioOut = new Float32Array(totalSamples);
  const tmpL = new Float32Array(blockSize);
  const tmpR = new Float32Array(blockSize);
  
  let currentControlStep = 0;
  let sampleCount = 0;
  const blockComputeTimes = [];

  for (let i = 0; i < totalSamples; i += blockSize) {
    // 60 Hz control update check
    const targetStep = Math.min(totalControlSteps - 1, Math.floor(sampleCount / controlPeriodSamples));
    if (targetStep !== currentControlStep) {
      currentControlStep = targetStep;
      const newR = sweepTrajectory[currentControlStep];
      eng.set({ val: [sweepSlot, newR] });
    }

    // REQUIREMENT: Clear buffers before every block
    tmpL.fill(0);
    tmpR.fill(0);

    const t0 = process.hrtime.bigint();
    eng.process(tmpL, tmpR, blockSize);
    const dtUs = Number(process.hrtime.bigint() - t0) / 1000;
    blockComputeTimes.push(dtUs);

    for (let k = 0; k < blockSize; k++) {
      if (i + k < totalSamples) audioOut[i + k] = tmpL[k];
    }
    sampleCount += blockSize;
  }

  return { audio: audioOut, computeTimes: blockComputeTimes };
}

// 3. Condition B: Professionally Smoothed Sample-Playback Baseline
function runTrialSmoothedSample(trialSeed) {
  const audioOut = new Float32Array(totalSamples);
  const blockComputeTimes = [];
  
  // 1-pole parameter smoothing filter (fc = 30 Hz)
  const fc = 30;
  const alpha = 1 - Math.exp(-2 * Math.PI * fc / sr);
  let smoothedParam = sweepTrajectory[0];

  let currentControlStep = 0;
  let sampleCount = 0;
  let phase = (trialSeed * 137) % referenceSampleBuffer.length;
  const baseStep = Math.pow(2, ((trialSeed % 3) * 0.01) / 12);

  for (let i = 0; i < totalSamples; i += blockSize) {
    const targetStep = Math.min(totalControlSteps - 1, Math.floor(sampleCount / controlPeriodSamples));
    if (targetStep !== currentControlStep) {
      currentControlStep = targetStep;
    }
    const rawTarget = sweepTrajectory[currentControlStep];

    const t0 = process.hrtime.bigint();
    
    for (let k = 0; k < blockSize; k++) {
      smoothedParam += alpha * (rawTarget - smoothedParam);
      
      // Resample with cubic interpolation
      const idx = Math.floor(phase);
      const frac = phase - idx;
      const len = referenceSampleBuffer.length;
      const s0 = referenceSampleBuffer[(idx - 1 + len) % len];
      const s1 = referenceSampleBuffer[idx % len];
      const s2 = referenceSampleBuffer[(idx + 1) % len];
      const s3 = referenceSampleBuffer[(idx + 2) % len];
      
      const c0 = s1;
      const c1 = 0.5 * (s2 - s0);
      const c2 = s0 - 2.5 * s1 + 2 * s2 - 0.5 * s3;
      const c3 = 0.5 * (s3 - s0) + 1.5 * (s1 - s2);
      let sampleVal = ((c3 * frac + c2) * frac + c1) * frac + c0;
      
      // Matched physical transfer function approximation
      const gainMod = nominalVal / (nominalVal + smoothedParam);
      sampleVal *= gainMod;

      if (i + k < totalSamples) audioOut[i + k] = sampleVal;
      phase = (phase + baseStep) % len;
    }

    const dtUs = Number(process.hrtime.bigint() - t0) / 1000;
    blockComputeTimes.push(dtUs);
    sampleCount += blockSize;
  }

  return { audio: audioOut, computeTimes: blockComputeTimes };
}

// 4. Metrics Evaluator with Fast Radix-2 STFT
function evaluateMetrics(audioSignal, computeTimes) {
  // A. Discontinuity Metric
  let maxD2 = 0;
  let totalD2 = 0;
  for (let i = 2; i < audioSignal.length; i++) {
    const d2 = Math.abs(audioSignal[i] - 2 * audioSignal[i - 1] + audioSignal[i - 2]);
    if (d2 > maxD2) maxD2 = d2;
    totalD2 += d2 * d2;
  }
  const meanD2 = totalD2 / (audioSignal.length - 2);
  const excessArtifactRatio = meanD2 / (staticBaselineHf + 1e-12);

  // B. Fast Spectral Flux using 512-point Radix-2 FFT
  const nFrames = Math.floor((audioSignal.length - N_FFT) / HOP_SIZE);
  let totalFlux = 0;
  let maxFlux = 0;
  const prevMag = new Float64Array(N_FFT / 2);
  const real = new Float64Array(N_FFT);
  const imag = new Float64Array(N_FFT);

  for (let f = 0; f < nFrames; f++) {
    const start = f * HOP_SIZE;
    for (let n = 0; n < N_FFT; n++) {
      real[n] = audioSignal[start + n] * hannWin[n];
      imag[n] = 0;
    }
    fft512(real, imag);

    let frameFlux = 0;
    for (let k = 0; k < N_FFT / 2; k++) {
      const mag = Math.sqrt(real[k] * real[k] + imag[k] * imag[k]);
      if (f > 0) {
        const diff = mag - prevMag[k];
        if (diff > 0) frameFlux += diff;
      }
      prevMag[k] = mag;
    }

    if (f > 0) {
      totalFlux += frameFlux;
      if (frameFlux > maxFlux) maxFlux = frameFlux;
    }
  }
  const meanFlux = totalFlux / Math.max(1, nFrames - 1);

  // C. Compute Times
  const sortedTimes = Float64Array.from(computeTimes).sort();
  const meanCompute = sortedTimes.reduce((a, b) => a + b, 0) / sortedTimes.length;
  const p50Compute = sortedTimes[Math.floor(sortedTimes.length * 0.50)];
  const p95Compute = sortedTimes[Math.floor(sortedTimes.length * 0.95)];
  const maxCompute = sortedTimes[sortedTimes.length - 1];

  return {
    maxDiscontinuity: maxD2,
    excessArtifactRatio: excessArtifactRatio,
    meanSpectralFlux: meanFlux,
    maxSpectralFlux: maxFlux,
    meanComputeUs: meanCompute,
    p50ComputeUs: p50Compute,
    p95ComputeUs: p95Compute,
    maxComputeUs: maxCompute
  };
}

// 5. Run 20 Repeated Randomized Trials
console.log('========================================================================');
console.log('  JAES PHASE 2: PARAMETER CONTINUITY & MODULATION RESPONSIVENESS');
console.log('========================================================================');
console.log(`Test Circuit: "${preset.name}" | Swept Slot: Resistor ${sweepSlot}`);
console.log(`Control Rate: ${controlRateHz} Hz (${controlPeriodSamples} samples / 16.67 ms per update)`);
console.log(`Modulation Range: ${minVal.toFixed(1)} Ω -> ${maxVal.toFixed(1)} Ω over ${testDurationSec}s`);
console.log(`Static Reference High-Frequency Baseline: ${staticBaselineHf.toExponential(3)}`);
console.log('Running 20 repeated trials per condition with randomized trial order...\n');

const nTrials = 20;
const mnaTrials = [];
const sampleTrials = [];

for (let trial = 0; trial < nTrials; trial++) {
  // Randomize order of trial execution
  if (Math.random() > 0.5) {
    const resMna = runTrialLiveMNA(trial);
    mnaTrials.push(evaluateMetrics(resMna.audio, resMna.computeTimes));

    const resSample = runTrialSmoothedSample(trial);
    sampleTrials.push(evaluateMetrics(resSample.audio, resSample.computeTimes));
  } else {
    const resSample = runTrialSmoothedSample(trial);
    sampleTrials.push(evaluateMetrics(resSample.audio, resSample.computeTimes));

    const resMna = runTrialLiveMNA(trial);
    mnaTrials.push(evaluateMetrics(resMna.audio, resMna.computeTimes));
  }
}

function summarizeTrials(trials, conditionName) {
  const stat = key => {
    const arr = Float64Array.from(trials.map(t => t[key])).sort();
    const sum = arr.reduce((a, b) => a + b, 0);
    return {
      mean: sum / arr.length,
      p50: arr[Math.floor(arr.length * 0.50)],
      p95: arr[Math.floor(arr.length * 0.95)],
      max: arr[arr.length - 1]
    };
  };

  return {
    condition: conditionName,
    discontinuity: stat('maxDiscontinuity'),
    artifactRatio: stat('excessArtifactRatio'),
    spectralFlux: stat('meanSpectralFlux'),
    computeP50: stat('p50ComputeUs'),
    computeP95: stat('p95ComputeUs'),
    computeMax: stat('maxComputeUs')
  };
}

const summaryMna = summarizeTrials(mnaTrials, 'Live MNA (Physical Circuit Solver)');
const summarySample = summarizeTrials(sampleTrials, 'Smoothed Sample Playback (30 Hz LPF)');

console.log('========================================================================');
console.log('PHASE 2 SUMMARY RESULTS: 20-RUN DISTRIBUTIONS (Values in Microseconds)');
console.log('========================================================================');
console.table([
  {
    Condition: summaryMna.condition,
    'Max Jump (P50)': summaryMna.discontinuity.p50.toFixed(4),
    'Artifact Ratio (P50)': summaryMna.artifactRatio.p50.toFixed(2) + 'x',
    'Mean Spectral Flux': summaryMna.spectralFlux.p50.toFixed(3),
    'Compute P50 (µs)': summaryMna.computeP50.p50.toFixed(1),
    'Compute P95 (µs)': summaryMna.computeP95.p95.toFixed(1),
    'Compute Max (µs)': summaryMna.computeMax.max.toFixed(1)
  },
  {
    Condition: summarySample.condition,
    'Max Jump (P50)': summarySample.discontinuity.p50.toFixed(4),
    'Artifact Ratio (P50)': summarySample.artifactRatio.p50.toFixed(2) + 'x',
    'Mean Spectral Flux': summarySample.spectralFlux.p50.toFixed(3),
    'Compute P50 (µs)': summarySample.computeP50.p50.toFixed(1),
    'Compute P95 (µs)': summarySample.computeP95.p95.toFixed(1),
    'Compute Max (µs)': summarySample.computeMax.max.toFixed(1)
  }
]);

// Export JSON & CSV
const exportPayload = {
  experiment: 'JAES Phase 2: Parameter Continuity and Modulation Responsiveness',
  timestamp: new Date().toISOString(),
  environment: {
    cpuModel: os.cpus()[0].model,
    cpuCores: os.cpus().length,
    nodeVersion: process.version,
    sampleRate: sr,
    blockSize: blockSize
  },
  settings: {
    preset: preset.name,
    controlRateHz: controlRateHz,
    sweepRange: [minVal, maxVal],
    staticReferenceBaselineHf: staticBaselineHf,
    trialsCount: nTrials
  },
  summaries: [summaryMna, summarySample],
  rawTrials: {
    liveMNA: mnaTrials,
    smoothedSample: sampleTrials
  }
};

fs.writeFileSync(path.join(__dirname, 'jaes_phase2_parameter_continuity.json'), JSON.stringify(exportPayload, null, 2));

let csv = 'Condition,Trial,MaxDiscontinuity,ArtifactRatio,MeanSpectralFlux,ComputeP50_us,ComputeP95_us,ComputeMax_us\n';
mnaTrials.forEach((t, i) => {
  csv += `"Live MNA",${i+1},${t.maxDiscontinuity.toFixed(5)},${t.excessArtifactRatio.toFixed(3)},${t.meanSpectralFlux.toFixed(4)},${t.p50ComputeUs.toFixed(1)},${t.p95ComputeUs.toFixed(1)},${t.maxComputeUs.toFixed(1)}\n`;
});
sampleTrials.forEach((t, i) => {
  csv += `"Smoothed Sample",${i+1},${t.maxDiscontinuity.toFixed(5)},${t.excessArtifactRatio.toFixed(3)},${t.meanSpectralFlux.toFixed(4)},${t.p50ComputeUs.toFixed(1)},${t.p95ComputeUs.toFixed(1)},${t.maxComputeUs.toFixed(1)}\n`;
});
fs.writeFileSync(path.join(__dirname, 'jaes_phase2_parameter_continuity.csv'), csv);

console.log('\n[Phase 2 Export Complete]');
console.log(' - jaes_phase2_parameter_continuity.json');
console.log(' - jaes_phase2_parameter_continuity.csv\n');
