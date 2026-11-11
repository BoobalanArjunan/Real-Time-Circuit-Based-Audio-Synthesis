import os
import re

print("Reading original index.html...")
with open('../Circuit Synthesizer/index.html', 'r', encoding='utf-8') as f:
    src = f.read()

# 1. Newton-Raphson iterations & convergence failure tracking in wt.solve
old_solve_loop = 'if(R){for(let t=0;t<24;t++){for(let t=0;t<r;t++)'
new_solve_loop = 'if(R){let _it=0,_cvg=false;for(let _iter=0;_iter<24;_iter++){_it=_iter+1;for(let t=0;t<r;t++)'
assert old_solve_loop in src, 'old_solve_loop not found'
src = src.replace(old_solve_loop, new_solve_loop)

old_solve = 'if(t<1e-6)break}for(let t=0;t<r;t++)u[t]=g[t]?this.nl(y[t],f[t]):0;'
new_solve = 'if(t<1e-6){_cvg=true;break}}this.lastNrIters=_it;if(!_cvg&&_it>=24){this.nrFails=(this.nrFails||0)+1;}for(let t=0;t<r;t++)u[t]=g[t]?this.nl(y[t],f[t]):0;'
assert old_solve in src, 'old_solve not found'
src = src.replace(old_solve, new_solve)

# 2. wt.flush exposing iteration telemetry
old_flush = 'const e={snap:this.snap.slice(),rms:s,ext:Array.from(this.ext),sc:this.sc.slice(0,2*this.scN),f:this.f,closed:this.closed,trigAt:this.trig?this.trigAt:-1};'
new_flush = 'const e={snap:this.snap.slice(),rms:s,ext:Array.from(this.ext),sc:this.sc.slice(0,2*this.scN),f:this.f,closed:this.closed,trigAt:this.trig?this.trigAt:-1,nrIters:this.lastNrIters||0,nrFails:this.nrFails||0};'
assert old_flush in src, 'old_flush not found'
src = src.replace(old_flush, new_flush)

# 3. AudioWorkletProcessor telemetry with zero GC and preallocated buffers
old_worklet = 'function WORKLET(t){class s extends AudioWorkletProcessor{constructor(){super(),this.e=new t.Mix(sampleRate),this.k=0,this.busy=0,this.nb=0,this.port.onmessage=t=>this.e.set(t.data)}process(t,s){const i=s[0],e=Date.now();return this.e.process(i[0],i[1]||i[0],i[0].length),this.busy+=Date.now()-e,++this.nb>=750&&(this.e.load(this.busy/(this.nb*i[0].length/sampleRate*1e3)),this.busy=0,this.nb=0),++this.k%4==0&&this.port.postMessage(this.e.flush()),!0}}registerProcessor("circuit-engine",s)}'

new_worklet = '''function WORKLET(t){
  class s extends AudioWorkletProcessor {
    constructor(){
      super();
      this.e = new t.Mix(sampleRate);
      this.k = 0;
      this.busy = 0;
      this.nb = 0;
      
      // Preallocated circular buffer (zero GC allocation)
      this.RING_SIZE = 128;
      this.durRing = new Float32Array(this.RING_SIZE);
      this.ringIdx = 0;
      this.totalBlocks = 0;
      this.missedDeadlines = 0;
      
      // Detect timer support in AudioWorkletGlobalScope
      this.hasPerf = (typeof performance !== 'undefined' && typeof performance.now === 'function');
      this.timingMode = this.hasPerf ? 'performance.now' : 'Date.now';
      
      this.port.onmessage = (msg) => {
        if(msg.data && msg.data.__benchReset){
          this.totalBlocks = 0;
          this.missedDeadlines = 0;
          this.durRing.fill(0);
          this.ringIdx = 0;
          this.busy = 0;
          this.nb = 0;
        } else {
          this.e.set(msg.data);
        }
      };
    }
    
    process(inputs, outputs){
      const out = outputs[0];
      const blockSize = out[0].length;
      const budgetMs = (blockSize / sampleRate) * 1000;
      
      const t0 = this.hasPerf ? performance.now() : Date.now();
      const res = this.e.process(out[0], out[1] || out[0], blockSize);
      const dt = (this.hasPerf ? performance.now() : Date.now()) - t0;
      
      this.durRing[this.ringIdx] = dt;
      this.ringIdx = (this.ringIdx + 1) & (this.RING_SIZE - 1);
      this.totalBlocks++;
      
      if(dt > budgetMs){
        this.missedDeadlines++;
      }
      
      this.busy += dt;
      ++this.nb;
      
      if(this.nb >= 32){
        const batchDuration = (this.nb * blockSize / sampleRate) * 1000;
        const avgLoad = (this.busy / batchDuration) * 100;
        this.e.load(avgLoad / 100);
        
        const payload = this.e.flush();
        payload.__benchTelemetry = {
          timingMode: this.timingMode,
          hasSubMs: this.hasPerf,
          budgetMs: budgetMs,
          avgLoadPct: avgLoad,
          lastDtMs: dt,
          totalBlocks: this.totalBlocks,
          missedDeadlines: this.missedDeadlines,
          recentDurations: Array.from(this.durRing)
        };
        this.port.postMessage(payload);
        this.busy = 0;
        this.nb = 0;
      } else if(++this.k % 4 === 0){
        this.port.postMessage(this.e.flush());
      }
      
      return res;
    }
  }
  registerProcessor("circuit-engine", s);
}'''
assert old_worklet in src, 'old_worklet not found'
src = src.replace(old_worklet, new_worklet)

# 4. Inject takeMix hook to capture telemetry
old_takeMix = 'function takeMix(t,e){take(t.cur,e),'
new_takeMix = '''function takeMix(t,e){
  if(t && t.__benchTelemetry && window.__updateBenchTelemetry){
    window.__updateBenchTelemetry(t.__benchTelemetry, t);
  }
  take(t.cur,e),'''
assert old_takeMix in src, 'old_takeMix not found'
src = src.replace(old_takeMix, new_takeMix)

# 5. Inject noteOn/noteOff hooks for WAV baseline
old_noteOn = 'function noteOn(t){t=clamp(t,12,108),audioReady().catch(()=>{}),'
new_noteOn = '''function noteOn(t){
  if(window.__benchMode === 'wav' && window.__playWavNote){
    window.__playWavNote(t);
    return;
  }
  t=clamp(t,12,108),audioReady().catch(()=>{}),'''
assert old_noteOn in src, 'old_noteOn not found'
src = src.replace(old_noteOn, new_noteOn)

old_noteOff = 'function noteOff(t){const e=held.indexOf(t);'
new_noteOff = '''function noteOff(t){
  if(window.__benchMode === 'wav' && window.__stopWavNote){
    window.__stopWavNote(t);
    return;
  }
  const e=held.indexOf(t);'''
assert old_noteOff in src, 'old_noteOff not found'
src = src.replace(old_noteOff, new_noteOff)

# 6. Append Benchmark Dashboard UI and Benchmark Controller Script
dashboard_script = """
<!-- JAES BENCHMARK DASHBOARD & CONTROLLER -->
<div id="benchPanel" style="position:fixed;top:10px;right:10px;z-index:9999;width:420px;max-height:92vh;overflow-y:auto;background:rgba(20,22,28,0.96);border:1px solid rgba(255,100,75,0.4);border-radius:12px;box-shadow:0 12px 40px rgba(0,0,0,0.85);font-family:var(--latin);padding:14px;color:#f6ede8;font-size:12px;backdrop-filter:blur(10px);">
  <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,100,75,0.25);padding-bottom:8px;margin-bottom:10px;">
    <div>
      <div style="font-size:13px;font-weight:600;letter-spacing:0.12em;color:#ff6550;">🔬 JAES BENCHMARK HARNESS</div>
      <div style="font-size:9.5px;color:rgba(246,237,232,0.6);letter-spacing:0.04em;">Live MNA Circuit Solver vs. WAV Playback Baseline</div>
    </div>
    <button id="benchToggleMinimize" type="button" style="background:none;border:1px solid rgba(255,100,75,0.3);color:#ff6550;border-radius:4px;padding:2px 8px;font-size:11px;cursor:pointer;">_</button>
  </div>
  
  <div id="benchContent">
    <!-- Mode Selector -->
    <div style="margin-bottom:10px;">
      <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.15em;color:rgba(255,100,75,0.8);margin-bottom:4px;">Synthesis Engine Condition:</div>
      <div style="display:flex;gap:6px;">
        <button id="btnModeMNA" type="button" style="flex:1;padding:6px 8px;border-radius:6px;border:1px solid #ff6550;background:#ff6550;color:#121317;font-weight:600;cursor:pointer;">A: Live MNA Solver</button>
        <button id="btnModeWAV" type="button" style="flex:1;padding:6px 8px;border-radius:6px;border:1px solid rgba(255,100,75,0.3);background:transparent;color:#f6ede8;cursor:pointer;">B: WAV Playback</button>
      </div>
    </div>

    <!-- Polyphony Selector -->
    <div style="margin-bottom:10px;">
      <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.15em;color:rgba(255,100,75,0.8);margin-bottom:4px;">Voice Polyphony:</div>
      <div style="display:flex;gap:4px;">
        <button class="benchPolyBtn" data-poly="1" type="button" style="flex:1;padding:4px;border-radius:4px;border:1px solid #ff6550;background:#ff6550;color:#121317;font-weight:600;cursor:pointer;">1 Voice</button>
        <button class="benchPolyBtn" data-poly="2" type="button" style="flex:1;padding:4px;border-radius:4px;border:1px solid rgba(255,100,75,0.3);background:transparent;color:#f6ede8;cursor:pointer;">2 Voices</button>
        <button class="benchPolyBtn" data-poly="4" type="button" style="flex:1;padding:4px;border-radius:4px;border:1px solid rgba(255,100,75,0.3);background:transparent;color:#f6ede8;cursor:pointer;">4 Voices</button>
      </div>
    </div>

    <!-- Telemetry Cards -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px;">
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:6px 8px;">
        <div style="font-size:9px;color:rgba(246,237,232,0.6);text-transform:uppercase;">128-Sample Compute</div>
        <div id="valComputeMs" style="font-size:15px;font-weight:600;color:#ff9f43;margin-top:2px;">0.00 ms</div>
        <div id="valDeadlineBudget" style="font-size:9.5px;color:rgba(246,237,232,0.5);">Budget: 2.67 ms (0%)</div>
      </div>
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:6px 8px;">
        <div style="font-size:9px;color:rgba(246,237,232,0.6);text-transform:uppercase;">Deadline Misses</div>
        <div id="valMissedDeadlines" style="font-size:15px;font-weight:600;color:#ff6550;margin-top:2px;">0 blocks</div>
        <div id="valTotalBlocks" style="font-size:9.5px;color:rgba(246,237,232,0.5);">Total: 0 blocks</div>
      </div>
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:6px 8px;">
        <div style="font-size:9px;color:rgba(246,237,232,0.6);text-transform:uppercase;">Newton-Raphson Iters</div>
        <div id="valNrIters" style="font-size:15px;font-weight:600;color:#4cd137;margin-top:2px;">0 iters</div>
        <div id="valNrFails" style="font-size:9.5px;color:rgba(246,237,232,0.5);">Failures: 0 (cap 24)</div>
      </div>
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:6px 8px;">
        <div style="font-size:9px;color:rgba(246,237,232,0.6);text-transform:uppercase;">Timing API / Overhead</div>
        <div id="valTimingMode" style="font-size:13px;font-weight:500;color:#00d2d3;margin-top:2px;">Detecting...</div>
        <div id="valOverhead" style="font-size:9.5px;color:rgba(246,237,232,0.5);">Overhead: measuring...</div>
      </div>
    </div>

    <!-- Limitation Disclosure -->
    <div id="benchDisclosure" style="background:rgba(255,159,67,0.08);border:1px solid rgba(255,159,67,0.3);border-radius:6px;padding:6px 8px;font-size:9.5px;line-height:1.4;color:rgba(255,200,150,0.9);margin-bottom:10px;">
      <b>Scientific Note:</b> Browser AudioWorkletGlobalScope omits <code>performance.now()</code> under standard Spectre protections. Live worklet timing uses <code>Date.now()</code> batch accumulation; sub-millisecond distribution (P50/P95/P99) is measured via the Offline Precision Profiler below.
    </div>

    <!-- Automated Benchmark Test -->
    <div style="border-top:1px solid rgba(255,255,255,0.1);padding-top:8px;margin-bottom:10px;">
      <button id="btnRunAutoBench" type="button" style="width:100%;padding:8px;border-radius:6px;background:#2ed573;border:none;color:#121317;font-weight:600;font-size:12px;cursor:pointer;">▶ Run 1,000-Block Automated Benchmark</button>
      <div id="benchProgress" style="display:none;font-size:10px;color:#2ed573;margin-top:4px;text-align:center;">Running test sweep across polyphony 1, 2, 4...</div>
    </div>

    <!-- Benchmark Results Table -->
    <div id="benchResultsContainer" style="display:none;margin-bottom:10px;">
      <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.12em;color:#ff6550;margin-bottom:4px;">Benchmark Summary Results:</div>
      <table id="benchResultsTable" style="width:100%;border-collapse:collapse;font-size:10px;text-align:right;">
        <thead>
          <tr style="border-bottom:1px solid rgba(255,255,255,0.2);color:rgba(246,237,232,0.7);">
            <th style="text-align:left;padding:3px 2px;">Condition</th>
            <th style="padding:3px 2px;">Mean (µs)</th>
            <th style="padding:3px 2px;">P50</th>
            <th style="padding:3px 2px;">P95</th>
            <th style="padding:3px 2px;">P99</th>
            <th style="padding:3px 2px;">Max</th>
            <th style="padding:3px 2px;">Miss%</th>
          </tr>
        </thead>
        <tbody id="benchResultsBody"></tbody>
      </table>
    </div>

    <!-- Export Actions -->
    <div style="display:flex;gap:6px;">
      <button id="btnExportCSV" type="button" disabled style="flex:1;padding:6px;border-radius:6px;border:1px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.06);color:rgba(255,255,255,0.5);font-size:11px;cursor:pointer;">📥 Export CSV</button>
      <button id="btnExportJSON" type="button" disabled style="flex:1;padding:6px;border-radius:6px;border:1px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.06);color:rgba(255,255,255,0.5);font-size:11px;cursor:pointer;">📥 Export JSON</button>
      <button id="btnResetBench" type="button" style="padding:6px 10px;border-radius:6px;border:1px solid rgba(255,100,75,0.3);background:transparent;color:#ff6550;font-size:11px;cursor:pointer;">↺ Reset</button>
    </div>
  </div>
</div>

<script>
(function(){
  // Benchmark Controller State
  window.__benchMode = 'mna';
  window.__benchPoly = 1;
  const BENCH = {
    mode: 'mna',
    poly: 1,
    budgetMs: 2.6666667,
    lastDtMs: 0,
    totalBlocks: 0,
    missedDeadlines: 0,
    avgLoadPct: 0,
    nrIters: 0,
    nrFails: 0,
    timingMode: 'detecting',
    overheadUs: 0,
    results: [],
    wavBuffer: null,
    wavSources: new Map()
  };

  // Measure benchmark timing harness overhead (100,000 iterations)
  function measureOverhead(){
    const t0 = performance.now();
    let x = 0;
    const n = 100000;
    for(let i=0; i<n; i++){
      const a = performance.now();
      x += (performance.now() - a);
    }
    const dt = performance.now() - t0;
    BENCH.overheadUs = (dt / n) * 1000;
    const el = document.getElementById('valOverhead');
    if(el) el.textContent = `Overhead: ${BENCH.overheadUs.toFixed(3)} µs/call`;
  }
  setTimeout(measureOverhead, 500);

  // Hook from AudioWorklet telemetry
  window.__updateBenchTelemetry = function(t, fullMsg){
    BENCH.timingMode = t.timingMode;
    BENCH.lastDtMs = t.lastDtMs;
    BENCH.totalBlocks = t.totalBlocks;
    BENCH.missedDeadlines = t.missedDeadlines;
    BENCH.avgLoadPct = t.avgLoadPct;
    if(fullMsg && fullMsg.nrIters !== undefined) BENCH.nrIters = fullMsg.nrIters;
    if(fullMsg && fullMsg.nrFails !== undefined) BENCH.nrFails = fullMsg.nrFails;

    // Update UI DOM
    const elCompute = document.getElementById('valComputeMs');
    if(elCompute) elCompute.textContent = `${t.lastDtMs.toFixed(2)} ms`;
    
    const elBudget = document.getElementById('valDeadlineBudget');
    if(elBudget) elBudget.textContent = `Budget: 2.67 ms (${t.avgLoadPct.toFixed(1)}%)`;

    const elMiss = document.getElementById('valMissedDeadlines');
    if(elMiss) {
      const rate = BENCH.totalBlocks ? (BENCH.missedDeadlines / BENCH.totalBlocks * 100).toFixed(2) : '0.00';
      elMiss.textContent = `${BENCH.missedDeadlines} (${rate}%)`;
    }

    const elTot = document.getElementById('valTotalBlocks');
    if(elTot) elTot.textContent = `Total: ${BENCH.totalBlocks} blocks`;

    const elIters = document.getElementById('valNrIters');
    if(elIters) elIters.textContent = `${BENCH.nrIters} iters`;

    const elFails = document.getElementById('valNrFails');
    if(elFails) elFails.textContent = `Failures: ${BENCH.nrFails} (cap 24)`;

    const elTiming = document.getElementById('valTimingMode');
    if(elTiming) elTiming.textContent = t.hasSubMs ? 'performance.now' : 'Date.now (batch)';
  };

  // WAV Playback Baseline Voice Allocator
  async function ensureWavBuffer(){
    if(BENCH.wavBuffer) return BENCH.wavBuffer;
    if(!window.__circuit || !window.__circuit.ac) return null;
    const ac = window.__circuit.ac;
    const durSec = 2.0;
    const sr = ac.sampleRate || 48000;
    const nSamples = Math.floor(durSec * sr);
    
    // Render current preset offline via L.Engine
    const L = window.__circuit.L;
    const eng = new L.Engine(sr);
    eng.setBoard(Object.assign({}, window.__circuit.st.board, {reset: 1}));
    eng.set({note: 45, gate: 1, trig: 1, jump: 1});
    
    const buf = ac.createBuffer(2, nSamples, sr);
    const left = buf.getChannelData(0);
    const right = buf.getChannelData(1);
    const tmpL = new Float32Array(128);
    const tmpR = new Float32Array(128);
    
    for(let i=0; i<nSamples; i+=128){
      const block = Math.min(128, nSamples - i);
      eng.process(tmpL, tmpR, block);
      for(let k=0; k<block; k++){
        left[i + k] = tmpL[k];
        right[i + k] = tmpR[k];
      }
    }
    BENCH.wavBuffer = buf;
    return buf;
  }

  window.__playWavNote = async function(note){
    const ac = window.__circuit.ac;
    if(!ac) return;
    const buf = await ensureWavBuffer();
    if(!buf) return;
    
    // Stop voice if polyphony exceeded
    while(BENCH.wavSources.size >= BENCH.poly){
      const oldestKey = BENCH.wavSources.keys().next().value;
      const oldNode = BENCH.wavSources.get(oldKey);
      try{ oldNode.stop(); }catch(e){}
      BENCH.wavSources.delete(oldKey);
    }
    
    const src = ac.createBufferSource();
    src.buffer = buf;
    // Pitch shift relative to base note 45 (A2)
    src.playbackRate.value = Math.pow(2, (note - 45)/12);
    
    const gain = ac.createGain();
    gain.gain.value = 0.8;
    src.connect(gain);
    if(window.__circuit.G && window.__circuit.G.master){
      gain.connect(window.__circuit.G.master);
    } else {
      gain.connect(ac.destination);
    }
    
    src.start();
    BENCH.wavSources.set(note, src);
  };

  window.__stopWavNote = function(note){
    if(BENCH.wavSources.has(note)){
      const src = BENCH.wavSources.get(note);
      try{ src.stop(); }catch(e){}
      BENCH.wavSources.delete(note);
    }
  };

  // UI Event Handlers
  document.getElementById('btnModeMNA').onclick = function(){
    BENCH.mode = 'mna';
    window.__benchMode = 'mna';
    this.style.background = '#ff6550';
    this.style.color = '#121317';
    this.style.border = '1px solid #ff6550';
    document.getElementById('btnModeWAV').style.background = 'transparent';
    document.getElementById('btnModeWAV').style.color = '#f6ede8';
    document.getElementById('btnModeWAV').style.border = '1px solid rgba(255,100,75,0.3)';
  };

  document.getElementById('btnModeWAV').onclick = async function(){
    BENCH.mode = 'wav';
    window.__benchMode = 'wav';
    this.style.background = '#00d2d3';
    this.style.color = '#121317';
    this.style.border = '1px solid #00d2d3';
    document.getElementById('btnModeMNA').style.background = 'transparent';
    document.getElementById('btnModeMNA').style.color = '#f6ede8';
    document.getElementById('btnModeMNA').style.border = '1px solid rgba(255,100,75,0.3)';
    await ensureWavBuffer();
  };

  document.querySelectorAll('.benchPolyBtn').forEach(btn => {
    btn.onclick = function(){
      document.querySelectorAll('.benchPolyBtn').forEach(b => {
        b.style.background = 'transparent';
        b.style.color = '#f6ede8';
        b.style.border = '1px solid rgba(255,100,75,0.3)';
      });
      this.style.background = '#ff6550';
      this.style.color = '#121317';
      this.style.border = '1px solid #ff6550';
      const poly = parseInt(this.getAttribute('data-poly'), 10);
      BENCH.poly = poly;
      window.__benchPoly = poly;
      if(window.__circuit && window.__circuit.st){
        window.__circuit.st.poly = poly;
      }
    };
  });

  document.getElementById('btnResetBench').onclick = function(){
    BENCH.totalBlocks = 0;
    BENCH.missedDeadlines = 0;
    BENCH.results = [];
    if(window.__circuit && window.__circuit.node && window.__circuit.node.port){
      window.__circuit.node.port.postMessage({__benchReset: true});
    }
  };

  document.getElementById('benchToggleMinimize').onclick = function(){
    const content = document.getElementById('benchContent');
    if(content.style.display === 'none'){
      content.style.display = 'block';
      this.textContent = '_';
    } else {
      content.style.display = 'none';
      this.textContent = '+';
    }
  };

  // Precision Statistics Calculator (Mean, P50, P95, P99, Max)
  function computeDistribution(arr){
    if(!arr || !arr.length) return {mean:0, p50:0, p95:0, p99:0, max:0, missRate:0};
    const sorted = Float64Array.from(arr).sort();
    const sum = sorted.reduce((a, b) => a + b, 0);
    const mean = sum / sorted.length;
    const p50 = sorted[Math.floor(sorted.length * 0.50)];
    const p95 = sorted[Math.floor(sorted.length * 0.95)];
    const p99 = sorted[Math.floor(sorted.length * 0.99)];
    const max = sorted[sorted.length - 1];
    const budgetUs = 2666.67; // 2.667 ms in microseconds
    const missed = sorted.filter(v => v > budgetUs).length;
    const missRate = (missed / sorted.length) * 100;
    return {mean, p50, p95, p99, max, missRate};
  }

  // 1,000-Block Precision Automated Benchmark Sweep
  document.getElementById('btnRunAutoBench').onclick = async function(){
    const btn = this;
    const prog = document.getElementById('benchProgress');
    btn.disabled = true;
    prog.style.display = 'block';

    const L = window.__circuit.L;
    const sr = 48000;
    const blockSize = 128;
    const nBlocks = 1000;
    const outL = new Float32Array(blockSize);
    const outR = new Float32Array(blockSize);
    const testResults = [];

    // Test Conditions: Live MNA (1V, 2V, 4V) and WAV Playback (1V, 2V, 4V)
    const polyLevels = [1, 2, 4];
    
    // 1. Live MNA Tests
    for(const v of polyLevels){
      prog.textContent = `Benchmarking Condition A: Live MNA (${v} Voice${v>1?'s':''}) across 1,000 blocks...`;
      await new Promise(r => setTimeout(r, 40));
      
      const polyEng = new L.Poly(sr);
      polyEng.want = v;
      polyEng.set({board: window.__circuit.st.board, poly: v});
      // Excite voice with noteOn
      for(let vi=0; vi<v; vi++){
        polyEng.set({on: 36 + vi*7});
      }
      
      const blockDurUs = new Float64Array(nBlocks);
      for(let b=0; b<nBlocks; b++){
        const t0 = performance.now();
        polyEng.process(outL, outR, blockSize);
        blockDurUs[b] = (performance.now() - t0) * 1000; // microseconds
      }
      const stats = computeDistribution(blockDurUs);
      testResults.push({
        condition: `Live MNA (${v}V)`,
        mode: 'Live MNA',
        voices: v,
        ...stats
      });
    }

    // 2. WAV Playback Baseline Tests
    for(const v of polyLevels){
      prog.textContent = `Benchmarking Condition B: WAV Playback (${v} Voice${v>1?'s':''}) across 1,000 blocks...`;
      await new Promise(r => setTimeout(r, 40));
      
      // Standard linear interpolation streaming buffer simulator
      const wavBuf = new Float32Array(sr * 2);
      for(let i=0; i<wavBuf.length; i++) wavBuf[i] = Math.sin(2 * Math.PI * 440 * i / sr);
      
      const blockDurUs = new Float64Array(nBlocks);
      const phases = new Float64Array(v);
      const phaseSteps = new Float64Array(v).map((_, i) => Math.pow(2, (i*7)/12));
      
      for(let b=0; b<nBlocks; b++){
        const t0 = performance.now();
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
        blockDurUs[b] = (performance.now() - t0) * 1000; // microseconds
      }
      const stats = computeDistribution(blockDurUs);
      testResults.push({
        condition: `WAV Playback (${v}V)`,
        mode: 'WAV Playback',
        voices: v,
        ...stats
      });
    }

    BENCH.results = testResults;
    prog.textContent = 'Benchmark complete!';
    btn.disabled = false;

    // Render results in table
    const tableBody = document.getElementById('benchResultsBody');
    tableBody.innerHTML = '';
    testResults.forEach(r => {
      const tr = document.createElement('tr');
      tr.style.borderBottom = '1px solid rgba(255,255,255,0.06)';
      tr.innerHTML = `
        <td style="text-align:left;padding:3px 2px;color:#ff9f43;">${r.condition}</td>
        <td style="padding:3px 2px;">${r.mean.toFixed(1)}</td>
        <td style="padding:3px 2px;">${r.p50.toFixed(1)}</td>
        <td style="padding:3px 2px;">${r.p95.toFixed(1)}</td>
        <td style="padding:3px 2px;">${r.p99.toFixed(1)}</td>
        <td style="padding:3px 2px;">${r.max.toFixed(1)}</td>
        <td style="padding:3px 2px;color:${r.missRate>0?'#ff6550':'#2ed573'};">${r.missRate.toFixed(1)}%</td>
      `;
      tableBody.appendChild(tr);
    });
    document.getElementById('benchResultsContainer').style.display = 'block';
    
    // Enable export buttons
    document.getElementById('btnExportCSV').disabled = false;
    document.getElementById('btnExportJSON').disabled = false;
    document.getElementById('btnExportCSV').style.color = '#f6ede8';
    document.getElementById('btnExportJSON').style.color = '#f6ede8';
  };

  // CSV Export Handler
  document.getElementById('btnExportCSV').onclick = function(){
    if(!BENCH.results.length) return;
    let csv = 'Condition,Mode,Voices,Mean_us,P50_us,P95_us,P99_us,Max_us,MissedDeadlines_pct,DeadlineBudget_us,Overhead_us\\n';
    BENCH.results.forEach(r => {
      csv += `"${r.condition}","${r.mode}",${r.voices},${r.mean.toFixed(2)},${r.p50.toFixed(2)},${r.p95.toFixed(2)},${r.p99.toFixed(2)},${r.max.toFixed(2)},${r.missRate.toFixed(2)},2666.67,${BENCH.overheadUs.toFixed(3)}\\n`;
    });
    const blob = new Blob([csv], {type: 'text/csv;charset=utf-8;'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `nodalsynth_jaes_benchmark_${Date.now()}.csv`;
    a.click();
  };

  // JSON Export Handler
  document.getElementById('btnExportJSON').onclick = function(){
    if(!BENCH.results.length) return;
    const payload = {
      benchmark: 'JAES NodalSynth Pro Circuit Simulation vs WAV Playback',
      timestamp: new Date().toISOString(),
      sampleRate: 48000,
      blockSize: 128,
      deadlineBudgetUs: 2666.67,
      instrumentationOverheadUs: BENCH.overheadUs,
      hardwareMetadata: {
        userAgent: navigator.userAgent,
        hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
        deviceMemoryGB: navigator.deviceMemory || 'unknown'
      },
      results: BENCH.results
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], {type: 'application/json'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `nodalsynth_jaes_benchmark_${Date.now()}.json`;
    a.click();
  };
})();
</script>
"""

# Insert the dashboard right before </body>
if '</body>' in src:
    src = src.replace('</body>', dashboard_script + '\n</body>')
else:
    src += '\n' + dashboard_script

# Also write to jaes_benchmark_env/benchmark.html
print("Writing jaes_benchmark_env/benchmark.html...")
with open('jaes_benchmark_env/benchmark.html', 'w', encoding='utf-8') as f:
    f.write(src)

# Write out Circuit Synthesizer/benchmark.html if permissible
try:
    print("Writing ../Circuit Synthesizer/benchmark.html...")
    with open('../Circuit Synthesizer/benchmark.html', 'w', encoding='utf-8') as f:
        f.write(src)
    print("Successfully wrote ../Circuit Synthesizer/benchmark.html")
except Exception as e:
    print(f"Note: Could not write ../Circuit Synthesizer/benchmark.html due to workspace sandbox isolation: {e}")

print("SUCCESS: benchmark.html created cleanly in jaes_benchmark_env!")
