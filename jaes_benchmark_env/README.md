# JAES Research Submission Package: Real-Time Discrete-Time MNA for Interactive Audio

**Target Journal:** *Journal of the Audio Engineering Society (JAES)*  
**Manuscript Title:** Real-Time Discrete-Time Modified Nodal Analysis for Interactive Audio: Computational Feasibility, Parameter Continuity, and Modeled Storage Trade-Offs  
**Submission Target:** November 30, 2026  
**Status:** Validated Submission Candidate  

---

## 1. Directory Structure & File Manifest

```
jaes_benchmark_env/
├── README.md                               # This master index and replication guide
├── JAES_MANUSCRIPT_DRAFT.md                # Full revised manuscript draft (Markdown)
├── jaes_manuscript.tex                     # Compilation-ready LaTeX document (IEEE/AES format)
├── references.bib                          # Complete BibTeX database (all 20 verified citations)
├── TECHNICAL_VERIFICATION_REPORT.md        # Mathematical proofs, code-to-math audit, reproducibility details
├── REVIEWER_RESPONSE_PACKET.md             # Detailed point-by-point response to initial peer review
│
├── figures/                                # Publication-quality vector figures
│   ├── figure1_mna_pipeline.svg            # Architecture of MNA solver in AudioWorklet (2x oversampling)
│   ├── figure2_budget_polyphony.svg        # Processing time vs. 2,666.67 µs budget across polyphony tiers
│   └── figure3_storage_scaling.svg         # Logarithmic asset footprint scaling (81 KB vs. 1.05 GB - 6.18 GB)
│
├── benchmark.html                          # Interactive browser AudioWorklet test harness with real-time HUD
├── original_nodalsynth.html                # Baseline pristine reference copy of synthesis engine
│
├── phase1_1_validation_benchmark.js        # Node.js runner: Steady-state factorial & cold-start repeatability
├── phase2_1_scientific_validation.js       # Node.js runner: 60 Hz gesture modulation continuity & t-tests
├── memory_scalability_test.js              # Node.js runner: Full 61-preset binary netlist audit
│
└── datasets/ (archived in root)
    ├── jaes_phase1_1_validated_results.json # 18,000 steady blocks + 20 cold-start trials (raw timings)
    ├── jaes_phase1_1_validated_results.csv  # CSV export for steady-state & cold-start benchmarks
    ├── jaes_phase2_1_validated.json         # Raw 60 Hz sweep spectral flux, derivative outliers, t-stats
    ├── jaes_phase2_parameter_continuity.csv # CSV export for parameter continuity metrics
    ├── jaes_phase3_memory_scalability.json  # Full 61-preset netlist byte counts & modeled sample banks
    └── jaes_phase3_memory_scalability.csv   # CSV export for storage scalability analysis
```

---

## 2. Core Empirical Findings Summary

```
=========================================================================================================
                                     KEY RESEARCH METRICS
=========================================================================================================
1. Audio Block Budget: 128 samples @ 48 kHz = 2,666.67 µs
   - 4-Voice RC High-Pass (Linear):        Mean = 274.9 µs (10.31%), P95 = 293.7 µs, Max = 915.5 µs
   - 4-Voice Rectifier (Weakly Nonlinear): Mean = 530.9 µs (19.91%), P95 = 576.0 µs, Max = 704.5 µs
   - 4-Voice Fuzz Stage (Strong Nonlinear): Mean = 612.7 µs (22.98%), P95 = 686.6 µs, Max = 1,704.7 µs (63.93%)
   - 4-Voice Matched Sample Baseline:      Mean =  55.4 µs ( 2.08%), P95 =  57.4 µs, Max = 284.5 µs
   - Deadline Violation Rate:              0.00% across all 18,000 evaluated steady-state blocks

2. Cold-Start (Block 0) Execution (20 Independent Trials, 4-Voice Fuzz):
   - Mean Cold Block = 784.5 µs (29.42%), P50 = 771.4 µs, Worst-Case Max = 873.4 µs (32.75% budget)
   - Zero missed deadlines; confirms that unbuffered pilot latency spikes are absent under preallocated memory.

3. Parameter Modulation Continuity (60 Hz Sweep over 2.0s, N=20 Paired Trials, df=19, alpha=0.05):
   - First-Derivative Outliers (> 4σ): MNA = 483.30 ± 0.47 vs. Sample = 503.65 ± 13.97 (t = -6.64, p = 2.37e-6)
     -> Statistically significant reduction in micro-transient spikes due to in-place reactive state preservation.
   - Distance to Quasi-Static Physical Reference: MNA = 0.2989 ± 0.0588 vs. Sample = 0.2613 ± 0.1137
     -> Fail to reject H0 (t = 1.11, p = 0.2827), confirming matched baseline macroscopic tuning.

4. Persistent Storage vs. Compute Trade-Off (All 61 Presets):
   - MNA Netlist Library (Verified):       81,130 bytes (79.23 KiB; 1,330.0 bytes/preset)
   - Modeled Sample Bank (Minimal):        2,745 WAVs  -> 1.054 GB (12,992.5x larger than netlists)
   - Modeled Sample Bank (Standard):       4,392 WAVs  -> 1.687 GB (20,788.1x larger than netlists)
   - Modeled Sample Bank (Full Chromatic): 16,104 WAVs -> 6.184 GB (76,222.6x larger than netlists)
   - Lossy Compressed Sample Bank (Opus):  70 to 95 MB -> ~860x to 1,170x larger than netlists
=========================================================================================================
```

---

## 3. How to Reproduce All Benchmarks

### 3.1 Requirements
* Node.js v18.0.0 or later (v24.5.0 recommended).
* Modern Chromium-based browser (Chromium 120+ / Chrome) for browser `AudioWorklet` verification.

### 3.2 Running the Steady-State and Cold-Start Profiling
```bash
cd jaes_benchmark_env
node phase1_1_validation_benchmark.js
```
*Outputs:* Generates updated `jaes_phase1_1_validated_results.json` and `.csv`.

### 3.3 Running the Parameter Modulation & Continuity Test
```bash
node phase2_1_scientific_validation.js
```
*Outputs:* Computes FFT spectral flux, derivative outliers, distance to quasi-static ground truth, and paired $t$-test statistics across 20 trials. Generates `jaes_phase2_1_validated.json`.

### 3.4 Running the Storage & Netlist Audit
```bash
node memory_scalability_test.js
```
*Outputs:* Audits all 61 synthesizer presets and outputs `jaes_phase3_memory_scalability.json` and `.csv`.

### 3.5 Browser AudioWorklet Real-Time Verification
Open `benchmark.html` directly in Google Chrome / Chromium:
```bash
open jaes_benchmark_env/benchmark.html
```
Click **"Start Benchmark"** to observe real-time AudioWorklet block profiling, polyphony scaling HUD, and export fresh CSV data.

---

## 4. Codebase Preservation Notice
The primary application file (`../Circuit Synthesizer/index.html`) is completely isolated and has **0 modifications** (`git status` is clean). All benchmarking harnesses and research artifacts are maintained strictly within this environment.

