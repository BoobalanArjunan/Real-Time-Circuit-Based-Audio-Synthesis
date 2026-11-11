/**
 * JAES Phase 3 Experiment: Memory Footprint and Storage Scalability
 * 
 * Quantifies the storage footprint and runtime memory allocation across
 * all 61 circuit families comparing:
 * 1. Physical Netlist Representation (MNA Procedural Synthesis)
 * 2. Multi-Sampled Audio Buffers (Sample-Based Playback Baseline)
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

const nPresets = L.LIBRARY.length;
const sr = 48000;
const bytesPerSample = 2; // 16-bit PCM
const nChannels = 2; // Stereo
const noteDurationSec = 2.0;

console.log('========================================================================');
console.log('      JAES PHASE 3: MEMORY FOOTPRINT & STORAGE SCALABILITY');
console.log('========================================================================');
console.log(`Total Circuit Families / Presets: ${nPresets}`);
console.log(`Target Audio Specifications: ${sr} Hz, 16-bit PCM, Stereo, ${noteDurationSec}s per note`);
console.log('========================================================================\n');

// 1. Physical MNA Asset Footprint
let totalNetlistBytes = 0;
const presetDetails = [];

L.LIBRARY.forEach((p, idx) => {
  const board = p.make();
  // Compact binary representation: 133 component types (uint8) + 133 component values (float64)
  const binaryNetlistBytes = board.t.length * 1 + board.v.length * 8 + board.rev.length * 1;
  const jsonDescriptorBytes = Buffer.byteLength(JSON.stringify(p), 'utf8');
  totalNetlistBytes += binaryNetlistBytes;

  presetDetails.push({
    id: p.id || `preset_${idx}`,
    name: p.name,
    componentsCount: Array.from(board.t).filter(t => t > 1).length,
    binaryBytes: binaryNetlistBytes,
    jsonBytes: jsonDescriptorBytes
  });
});

const avgNetlistBytes = totalNetlistBytes / nPresets;

// 2. Sample-Based Playback Asset Footprint
// Scenario A: Minimalist representation (1 zone per octave, 5 octaves = 5 samples per preset)
const samplesPerPresetMin = 5;
const bytesPerSampleFile = sr * noteDurationSec * nChannels * bytesPerSample; // 384,000 bytes (~375 KB) per sample note
const totalSampleBytesMin = nPresets * samplesPerPresetMin * bytesPerSampleFile;

// Scenario B: Standard production sample bank (1 sample per minor third, 24 samples per preset)
const samplesPerPresetStd = 24;
const totalSampleBytesStd = nPresets * samplesPerPresetStd * bytesPerSampleFile;

// Scenario C: Full chromatic multi-sampling (88 keys, 1 velocity layer)
const samplesPerPresetFull = 88;
const totalSampleBytesFull = nPresets * samplesPerPresetFull * bytesPerSampleFile;

// 3. Runtime State Memory per Active Voice
// In L.Engine (wt), examine all typed array allocations per voice instance
const sampleEngine = new L.Engine(sr);
const engineProperties = Object.keys(sampleEngine);
let engineStateBytes = 0;

for (const prop of engineProperties) {
  const val = sampleEngine[prop];
  if (val && val.buffer && val.byteLength) {
    engineStateBytes += val.byteLength;
  }
}

// Polyphonic voice state scaling: 1, 4, 8, 16, 32 voices
const voiceScaling = [1, 4, 8, 16, 32];
const runtimeMemoryTable = voiceScaling.map(v => {
  const mnaRamBytes = engineStateBytes * v;
  // For sample playback, active voices hold playback pointer + streaming ring buffer (e.g. 4096 samples stereo)
  const streamingBufferBytes = 4096 * nChannels * 4; // 32-bit float streaming buffer per voice
  const sampleVoiceRamBytes = streamingBufferBytes * v;
  return {
    voices: v,
    mnaVoiceRamKb: (mnaRamBytes / 1024).toFixed(2),
    sampleVoiceRamKb: (sampleVoiceRamBytes / 1024).toFixed(2)
  };
});

// 4. Output Summary Tables
console.log('--- STORAGE FOOTPRINT COMPARISON (ALL 61 PRESETS) ---');
console.table([
  {
    'Representation Method': 'Physical MNA Netlists (Binary Format)',
    'Storage Footprint (MB)': (totalNetlistBytes / (1024 * 1024)).toFixed(4) + ' MB',
    'Storage Footprint (KB)': (totalNetlistBytes / 1024).toFixed(1) + ' KB',
    'Avg per Preset': avgNetlistBytes.toFixed(0) + ' bytes',
    'Relative Compression': '1.0x (Baseline)'
  },
  {
    'Representation Method': 'Sample Bank: Minimal (5 notes/preset)',
    'Storage Footprint (MB)': (totalSampleBytesMin / (1024 * 1024)).toFixed(2) + ' MB',
    'Storage Footprint (KB)': (totalSampleBytesMin / 1024).toFixed(0) + ' KB',
    'Avg per Preset': (samplesPerPresetMin * bytesPerSampleFile / 1024).toFixed(0) + ' KB',
    'Relative Compression': (totalSampleBytesMin / totalNetlistBytes).toFixed(0) + 'x larger'
  },
  {
    'Representation Method': 'Sample Bank: Standard (24 notes/preset)',
    'Storage Footprint (MB)': (totalSampleBytesStd / (1024 * 1024)).toFixed(2) + ' MB',
    'Storage Footprint (KB)': (totalSampleBytesStd / 1024).toFixed(0) + ' KB',
    'Avg per Preset': (samplesPerPresetStd * bytesPerSampleFile / 1024).toFixed(0) + ' KB',
    'Relative Compression': (totalSampleBytesStd / totalNetlistBytes).toFixed(0) + 'x larger'
  },
  {
    'Representation Method': 'Sample Bank: Chromatic (88 notes/preset)',
    'Storage Footprint (MB)': (totalSampleBytesFull / (1024 * 1024)).toFixed(2) + ' MB',
    'Storage Footprint (KB)': (totalSampleBytesFull / 1024).toFixed(0) + ' KB',
    'Avg per Preset': (samplesPerPresetFull * bytesPerSampleFile / 1024).toFixed(0) + ' KB',
    'Relative Compression': (totalSampleBytesFull / totalNetlistBytes).toFixed(0) + 'x larger'
  }
]);

console.log('\n--- RUNTIME STATE MEMORY SCALING ACROSS ACTIVE VOICES ---');
console.table(runtimeMemoryTable.map(r => ({
  'Active Voices': r.voices,
  'Live MNA State RAM (KB)': r.mnaVoiceRamKb + ' KB',
  'Sample Voice RAM (KB)': r.sampleVoiceRamKb + ' KB'
})));

// 5. Export JSON & CSV
const exportPayload = {
  experiment: 'JAES Phase 3: Memory Footprint and Storage Scalability',
  timestamp: new Date().toISOString(),
  configuration: {
    presetsCount: nPresets,
    sampleRate: sr,
    noteDurationSec: noteDurationSec,
    bytesPerSampleFile: bytesPerSampleFile
  },
  storageComparison: {
    mnaNetlistTotalBytes: totalNetlistBytes,
    mnaNetlistAvgBytes: avgNetlistBytes,
    sampleBankMinBytes: totalSampleBytesMin,
    sampleBankStdBytes: totalSampleBytesStd,
    sampleBankFullBytes: totalSampleBytesFull
  },
  runtimeStateScaling: runtimeMemoryTable,
  presetDetails: presetDetails
};

fs.writeFileSync(path.join(__dirname, 'jaes_phase3_memory_scalability.json'), JSON.stringify(exportPayload, null, 2));

let csv = 'Preset,ComponentsCount,BinaryNetlistBytes,JsonDescriptorBytes,MinSampleBytes,StdSampleBytes,FullSampleBytes\n';
presetDetails.forEach(p => {
  const minBytes = samplesPerPresetMin * bytesPerSampleFile;
  const stdBytes = samplesPerPresetStd * bytesPerSampleFile;
  const fullBytes = samplesPerPresetFull * bytesPerSampleFile;
  csv += `"${p.name}",${p.componentsCount},${p.binaryBytes},${p.jsonBytes},${minBytes},${stdBytes},${fullBytes}\n`;
});
fs.writeFileSync(path.join(__dirname, 'jaes_phase3_memory_scalability.csv'), csv);

console.log('\n[Phase 3 Export Complete]');
console.log(' - jaes_phase3_memory_scalability.json');
console.log(' - jaes_phase3_memory_scalability.csv\n');

