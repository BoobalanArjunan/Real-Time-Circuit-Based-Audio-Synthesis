# Real-Time Circuit-Based Audio Synthesis Using Modified Nodal Analysis

**Feasibility, Signal Continuity, and Storage Trade-Offs**

**Author:** Boobalan Arjunan  
**Affiliation:** ComposerMind Labs, Chennai, India  
**Research manuscript:** Submitted to *Journal of the Audio Engineering Society* (JAES), November 12, 2026 — **Under Peer Review**  
**Editorial Manager Tracking ID:** `JAES-S-26-00299` | **Confirmation ID:** `EMID:4c1c93d9e0c91bba`  
**Repository:** [https://github.com/BoobalanArjunan/Real-Time-Circuit-Based-Audio-Synthesis](https://github.com/BoobalanArjunan/Real-Time-Circuit-Based-Audio-Synthesis)  
**Contact:** boobalan_arjunan@composermind.com

> **Research repository, not the NodalSynth Pro commercial product.** This repository provides the scientific MNA research benchmark implementation, evaluated circuit netlists, measurement datasets, and interactive reproducibility test harnesses. It does **not** include the full proprietary NodalSynth Pro application, GUI, preset-management system, or commercial packaging.

---

## Overview

Can a circuit-based audio synthesizer compute sound in real time, respond continuously to changing controls, and use substantially less stored audio data than a multi-sample playback engine?

This study evaluates a **discrete-time Modified Nodal Analysis (MNA)** implementation with **Newton–Raphson nonlinear solving**, running in a **Web Audio `AudioWorkletProcessor`** architecture. It compares live circuit synthesis with a defined three-zone, parameter-smoothed sample-crossfade baseline. The evaluation examines:

- **Real-time feasibility:** processing time per 128-sample audio block against the $2,666.67\ \mu\text{s}$ deadline.
- **Polyphony:** one, two, and four simultaneous voices.
- **Parameter continuity:** signal behavior during a 60 Hz control sweep.
- **Asset storage:** measured circuit-netlist bytes versus *modeled* sample-bank requirements.
- **Trade-offs and limitations:** higher synthesis computation, peak timing, and hardware scope.

**Research question:** Can state-preserving, circuit-based procedural synthesis support rapid interactive parameter changes while offering a practical compute–storage trade-off against multi-sample playback?

---

## System Architecture

```text
128-sample audio block at 48 kHz
              │
              ▼
In-place parameter updates (60 Hz)
Preserve capacitor/inductor history states (S1, S2)
              │
              ▼
Discrete-time MNA circuit solver
Newton–Raphson iterations for nonlinear components
2× oversampling: 96 kHz internal rate
              │
              ▼
23-tap half-band FIR decimation
              │
              ▼
128-sample output at 48 kHz
```

The solver uses trapezoidal companion models for reactive components. Nonlinear diode behavior is modeled using the Shockley equation and solved iteratively with bounded updates. The manuscript specifies a **$1 \times 10^{-6}\text{ V}$ convergence tolerance** and a **24-iteration cap**.

---

## Evaluated Circuits

| Circuit | Type | Main characteristics |
|---|---|---|
| **RC high-pass filter** | Linear | 2 nodes; 10 nF capacitor; 10 kΩ resistor |
| **Half-wave rectifier** | Weakly nonlinear | 3 nodes; 1N4148 diode model, resistor, capacitor |
| **Fuzz distortion stage** | Strongly nonlinear | 5 nodes; antiparallel clipping diodes, reactive capacitors, variable drive resistance (940 Ω–23.5 kΩ) |

Each circuit was evaluated at **1, 2, and 4 voices**, against a matched WAV playback baseline.

---

## Experimental Environment

The reported results were collected on the following host:

| Item | Manuscript configuration |
|---|---|
| **Processor** | Apple M1 Max, ARM64 (10 CPU cores: 8 performance, 2 efficiency) |
| **Memory** | 32 GB unified memory (LPDDR5, 400 GB/s) |
| **Operating system** | macOS 15.6 Darwin kernel |
| **Headless runtime** | Node.js 24.5.0 / V8 |
| **Browser verification** | Chromium 157 / `AudioWorkletProcessor` |
| **Output sample rate** | 48,000 Hz |
| **Audio block size** | 128 samples |
| **Deadline per block** | **2,666.67 µs** ($2.667\text{ ms}$) |
| **Internal solver rate** | 96,000 Hz (2× oversampling) |

The paper uses `process.hrtime.bigint()` for headless timing and reports separate browser-level verification. **Headless timing measurements are not equivalent to measuring the complete end-to-end XR audio pipeline.**

---

## Benchmark Design & Measured Results

### 1. Steady-State Block Timing

- 3 circuit presets × 3 voice counts × 2 engines = **18 conditions**.
- **1,000 blocks per condition**, for **18,000 measured blocks**.
- Measurements include mean, median (P50), P95, maximum processing duration, deadline load, and violations.

Selected results from the manuscript (4-voice live MNA vs. $2,666.67\ \mu\text{s}$ deadline):

| Circuit | Mean per block | P95 | Observed maximum | Mean deadline load | Violations |
|---|---:|---:|---:|---:|---:|
| **RC high-pass** | 274.9 µs | 293.7 µs | 915.5 µs | 10.31% | 0 / 1,000 |
| **Half-wave rectifier** | 530.9 µs | 576.0 µs | 704.5 µs | 19.91% | 0 / 1,000 |
| **Fuzz distortion** | **612.7 µs** | **686.6 µs** | **1,704.7 µs** | **22.98%** | **0 / 1,000** |

The fuzz peak used **63.93%** of the 2,666.67 µs deadline, leaving **36.07% headroom** in that observed block. **No deadline violations were observed in the 18,000 tested steady-state blocks on this host.**

### 2. Cold-Start Repeatability

For the 4-voice fuzz circuit, the study evaluated **20 independent engine instantiations** with preallocated buffers:

| Regime | Blocks | Mean | Observed maximum | Deadline violations |
|---|---:|---:|---:|---:|
| **Initial block (Block 0)** | 20 | 784.5 µs | 873.4 µs | 0 / 20 |
| **Warmed blocks (1–1,000 per trial)** | 20,000 | 612.7 µs | 1,704.7 µs | 0 / 20,000 |

An earlier **17.7 ms spike** observed in unbuffered pilot scripts was eliminated when state memory was preallocated during initialization.

### 3. Parameter-Continuity Comparison

A resistor was swept from **940 Ω to 23,500 Ω** over **2 seconds**, with **60 Hz** control updates and **20 trials**. Live MNA was compared against a **three-zone equal-power sample crossfade** using single-pole parameter smoothing ($\alpha = 1 - e^{-2\pi f_c / f_s}$) and cubic-Hermite interpolation:

| Metric | Live MNA mean | Sample-crossfade mean | Reported inference |
|---|---:|---:|---|
| **4σ first-derivative outliers** | **483.30** | **503.65** | Fewer for MNA; $t = -6.64$, $p = 2.37 \times 10^{-6}$ |
| **Mean spectral flux** | 42.93 | 40.39 | Different; $t = 12.01$, $p = 5.99 \times 10^{-13}$ |
| **Quasi-static reference distance** | 0.2989 | 0.2613 | No statistically significant difference detected; $p = 0.2827$ |
| **Median block duration during modulation** | 152.7 µs | 19.0 µs | MNA ≈ **8×** more computationally intensive |

### 4. Storage Audit and Modeled Comparisons

The **61 circuit netlists were measured at exactly 81,130 bytes** of persistent source assets. The comparison sample-bank sizes below are **modeled projections**:

| Representation | Assets | Storage | Evidence type |
|---|---:|---:|---|
| **MNA circuit netlists** | 61 presets | **81,130 bytes (81.13 KB)** | Verified netlist asset audit |
| **Minimal 16-bit PCM coverage** | 2,745 WAV files | 1.054 GB | Modeled |
| **Standard 16-bit PCM coverage** | 4,392 WAV files | 1.687 GB | Modeled |
| **Full chromatic 16-bit PCM coverage** | 16,104 WAV files | 6.184 GB | Modeled |
| **Minimal coverage, lossy encoded** | 2,745 audio files | Approximately 70–95 MB | Modeled |

The manuscript reports roughly **12,992×–76,223× less netlist asset storage** than modeled uncompressed banks, and **860×–1,170× less** than lossy audio, balanced against an $\approx 8\times$ higher computational cost.

---

## Repository Structure & Verified Manifest

```
Real-Time-Circuit-Based-Audio-Synthesis/
├── README.md                               # This master documentation and reproduction guide
├── LICENSE                                 # Open-source MIT License
├── headless_benchmark.js                   # Node.js runner: 18-condition steady-state & polyphony benchmark
├── parameter_continuity_test.js            # Node.js runner: 60 Hz gesture parameter sweep & continuity test
├── memory_scalability_test.js              # Node.js runner: 61-preset netlist storage audit & modeled bank projections
├── benchmark.html                          # Interactive browser AudioWorklet harness with real-time HUD
├── original_nodalsynth.html                # Reference standalone synthesis engine
│
├── jaes_phase1_1_validated_results.csv     # Raw steady-state factorial timing dataset (18,000 blocks)
├── jaes_phase1_1_validated_results.json    # JSON structured timing data
├── jaes_phase2_parameter_continuity.csv    # Raw parameter continuity & derivative outlier measurements
├── jaes_phase2_parameter_continuity.json   # JSON structured continuity data
├── jaes_phase3_memory_scalability.csv      # Raw storage footprint audit and modeled sample calculations
├── jaes_phase3_memory_scalability.json     # JSON structured storage data
│
├── jaes_manuscript.tex                     # JAES candidate manuscript LaTeX source
├── references.bib                          # BibTeX bibliography
└── figures/                                # High-resolution publication figures (Vector SVG & PDF)
```

---

## Reproducing the Experiments

### Prerequisites

- **Node.js**: Version 20+ (tested on Node.js 24.5.0). **Zero npm dependencies required** (pure standard library).
- **Web Browser**: Any modern browser supporting Web Audio `AudioWorklet` (tested in Chromium 157, Safari, and Firefox).

### 1. Clone the Repository

```bash
git clone https://github.com/BoobalanArjunan/Real-Time-Circuit-Based-Audio-Synthesis.git
cd Real-Time-Circuit-Based-Audio-Synthesis
```

### 2. Execute Headless Timing Benchmark

Runs the 18-condition steady-state factorial benchmark (3 circuits × 3 polyphony tiers × 2 engines = 18,000 blocks):

```bash
node headless_benchmark.js
```

*Expected output:* A formatted ASCII summary table of Mean, P50, P95, P99, and Max processing times per block, plus automated export of `jaes_benchmark_pilot_results.csv` and `.json`.

### 3. Execute Parameter Continuity Test

Sweeps the fuzz drive resistor from 940 Ω to 23,500 Ω over 2 seconds at 60 Hz across 20 randomized trials:

```bash
node parameter_continuity_test.js
```

*Expected output:* Quantitative distributions of $4\sigma$ derivative jumps, spectral flux, and compute latency between Live MNA and sample crossfading.

### 4. Execute Memory & Storage Audit

Audits the exact binary footprint of the 61 circuit presets and calculates modeled sample bank requirements:

```bash
node memory_scalability_test.js
```

*Expected output:* Table verifying the 81,130-byte netlist asset size and modeled compression ratios ($1,444\times$ to $25,408\times$).

### 5. Launch Interactive Browser AudioWorklet Harness

To run real-time audio interactive tests in your browser:

```bash
# Start a local static HTTP server (Python 3)
python3 -m http.server 8000
```

Open `http://localhost:8000/benchmark.html` in your browser. Click **Start AudioWorklet Benchmark** to audition the synthesis engine, inspect live oscilloscope output, and view real-time per-block execution HUDs.

---

## Scientific Scope and Limitations

This study **demonstrates**, within the tested conditions:
- Real-time deadline compliance for the evaluated circuits up to 4 voices on the specified Apple M1 Max host.
- Quantified continuity metrics during one standardized 60 Hz modulation trajectory.
- The measured size of 61 circuit-netlist assets (81,130 bytes).
- Explicit compute-versus-storage comparisons against a defined sample baseline.

This study **does not demonstrate**:
- Real-time performance on Meta Quest, Apple Vision Pro, or standalone mobile XR headsets.
- Performance at 16+ voices or arbitrary runtime circuit-topology changes.
- End-to-end 3D spatialization, binaural rendering, or room-acoustic simulation.
- Subjectively audible improvement, as no MUSHRA/ABX listening test was conducted.
- Equivalent full-product storage comparisons, because sample banks were modeled and netlist sizes exclude the application shell.

---

## Manuscript and Citation

**Boobalan Arjunan**, “Real-Time Circuit-Based Audio Synthesis Using Modified Nodal Analysis: Feasibility, Signal Continuity, and Storage Trade-Offs,” manuscript prepared for the *Journal of the Audio Engineering Society* (JAES), November 2026.

```bibtex
@article{arjunan2026realtimemna,
  author    = {Arjunan, Boobalan},
  title     = {Real-Time Circuit-Based Audio Synthesis Using Modified Nodal Analysis: Feasibility, Signal Continuity, and Storage Trade-Offs},
  journal   = {Journal of the Audio Engineering Society},
  year      = {2026},
  month     = {November},
  note      = {Submitted for peer review; candidate draft}
}
```

---

## License

This research codebase and datasets are released under the [MIT License](LICENSE).

**Author:** Boobalan Arjunan  
**Affiliation:** ComposerMind Labs, Chennai, India  
**Contact:** boobalan_arjunan@composermind.com
