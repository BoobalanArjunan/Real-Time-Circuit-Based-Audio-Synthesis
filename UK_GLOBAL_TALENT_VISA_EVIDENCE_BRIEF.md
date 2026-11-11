# UK Global Talent Visa — Evidence Portfolio Document
## Significant Technical Innovation & Research Contribution: Real-Time Circuit-Based Procedural Audio for Spatial Computing (Extended Reality)

**Applicant:** Boobalan Arjunan  
**Organization / Laboratory:** ComposerMind Labs LLP  
**Evidence Category:** Mandatory Criterion 1 (Innovation & Technical Leadership) / Optional Criterion 3 (Significant Technical/Commercial Contribution to Digital Technology)  
**Field of Specialism:** Advanced Agentic Audio Engineering, Real-Time Audio DSP, Spatial Computing (XR), Procedural Audio Synthesis  
**Date of Document:** November 2026  
**Primary Research Artifact:** *Journal of the Audio Engineering Society (JAES)* Manuscript Draft & GitHub Benchmark Repository  

---

## 1. Executive Summary & Statement of Contribution

This evidence document demonstrates **original technical innovation and advanced engineering leadership** by Boobalan Arjunan in the development of **NodalSynth Pro**: a state-preserving, discrete-time Modified Nodal Analysis (MNA) physical modeling audio synthesis engine optimized for deterministic real-time execution in Extended Reality (XR) and spatial computing environments.

### The Engineering Challenge Solved:
Interactive spatial computing (e.g., Apple Vision Pro, Meta Quest) demands audio engines that respond continuously to 60–120 Hz hand-tracking gestures within strict sub-buffer audio deadlines (typically 2.67 ms for 128-sample blocks at 48 kHz). Conventional industry architectures rely on pre-recorded multi-sample playback, which:
1. Strains embedded flash storage and unified memory (requiring gigabytes of sample data across pitch and parameter axes);
2. Introduces phase-cancellation comb filtering and audible stepping when crossfading between discrete audio recordings.

### The Technical Breakthrough:
Boobalan Arjunan formulated, architected, and profiled a real-time discrete-time circuit solver in JavaScript / Web Audio `AudioWorkletProcessor` that solves continuous electrical circuits (including non-linear diode clipping and multi-stage fuzz topologies) sample-by-sample via **bilinear trapezoidal integration and iterative Newton–Raphson dynamic conductance matrices**.

---

## 2. Key Quantitative Evidence & Benchmarks

The applicant conducted an exhaustive, multi-phase empirical evaluation comprising **18,000 steady-state audio blocks** and a **20-trial 60 Hz dynamic modulation experiment** on an ARM64 host (Apple M1 Max) with headless V8 nanosecond profiling and browser-level Chromium verification:

| Metric / Dimension | Industry Standard (Multi-Sample Playback) | Applicant's Innovation (NodalSynth Pro MNA) | Measured Impact |
| :--- | :---: | :---: | :---: |
| **Persistent Asset Storage (61 Presets)** | 1.054 GB (Minimal) to 6.184 GB (Full Chromatic) | **81,130 bytes (79.23 KiB)** total (1,330 bytes/preset) | **12,992.5× to 76,222.6× reduction** in disk/memory storage footprint |
| **Lossy Compressed Audio Asset Footprint** | 70–95 MB (Opus/AAC @ 96–128 kbps) | **81,130 bytes** | **860× to 1,170× reduction** vs. compressed audio banks |
| **Execution Latency per 128-sample Block** | 55.2 µs (2.07% of 2.67 ms deadline) | **612.7 µs (22.98% of deadline)** for 4-voice non-linear fuzz | Real-time budget preserved with **36.07% headroom** even during worst-case transient spikes (1,704.7 µs) |
| **Cold-Start Buffer Latency** | Pre-buffering required (or 17.7 ms pilot spike) | **784.5 µs (29.42% budget)** (max 873.4 µs) | Zero audio dropouts; pilot latency spikes completely eliminated via preallocated typed arrays |
| **Dynamic Parameter Modulation (60 Hz Sweep)** | Severe first-derivative outlier spikes ($503.65 \pm 13.97$) | **$483.30 \pm 0.47$ outlier spikes** ($t = -6.64, p = 2.37 \times 10^{-6}$) | Statistically smoother transitions under continuous gesture control ($p < 0.001$) |

---

## 3. Academic Peer-Review & Publication Venue

The research paper produced from this work is prepared for formal submission to the **Journal of the Audio Engineering Society (JAES)**, the world's leading archival peer-reviewed journal dedicated exclusively to audio technology:

* **Manuscript Title:** *Real-Time Discrete-Time Modified Nodal Analysis for Interactive Audio: Computational Feasibility, Parameter Continuity, and Modeled Storage Trade-Offs*
* **Journal:** *Journal of the Audio Engineering Society* (JAES)
* **Category:** Research Paper
* **Scholarly Foundation:** 20 verified peer-reviewed publications cited (IEEE, AES, MIT Press, Wiley), establishing rigorous mathematical continuity from foundational circuit modeling literature (Ho et al. 1975, Fettweis 1986, Yeh et al. 2007/2009, Holters & Zölzer 2011/2015, Choi 2018).
* **Open Science & Reproducibility:** The submission includes full LaTeX source (`jaes_manuscript.tex`), BibTeX database (`references.bib`), vector publication figures, full CSV benchmark raw data, and a browser-executable audio test harness.

---

## 4. Open-Source Leadership & Codebase Transparency

To adhere to the highest standards of scientific reproducibility and open-source contribution required by the UK Global Talent Visa endorsement bodies (Tech Nation / Royal Academy of Engineering):

* **Public Repository:** [https://github.com/BoobalanArjunan/SpatialMind-RoomShift-Research](https://github.com/BoobalanArjunan/SpatialMind-RoomShift-Research)
* **Commit Discipline:** The research progression is structured into 10 clean, transparent, chronological commits documenting:
  1. Research master plan and problem formalization (`bfe35c2`)
  2. Standalone circuit engine and assets (`cf45a64`)
  3. Automated benchmark harness generator (`f7f3cf2`)
  4. Headless V8 nanosecond profiling suite (`c35ecef`)
  5. 18,000-block factorial benchmark dataset (`cc229bb`)
  6. 60 Hz parameter sweep continuity test and statistical validation (`d5dfdce`)
  7. 61-preset netlist storage audit and multi-sample scaling analysis (`e8ef2cc`)
  8. Technical verification proofs and publication vector figures (`ecbd2c2`)
  9. Two-column JAES LaTeX manuscript and verified BibTeX bibliography (`b41b9a1`)
  10. Peer-review response package and submission archive (`de1f0e7`)

---

## 5. Mapping to UK Global Talent Visa Endorsement Criteria

| Tech Nation / RAE Endorsement Criteria | Evidence Demonstrated by the Applicant |
| :--- | :--- |
| **Mandatory Criterion: Innovation / Technical Leadership** | • Created an original real-time implementation of discrete-time MNA in Web Audio/AudioWorklet.<br>• Derived and proved exact bilinear companion models ($S_1, S_2$) ensuring mathematical state retention.<br>• Achieved unprecedented memory efficiency ($12,992\times$ reduction) for embedded spatial computing engines. |
| **Optional Criterion: Academic / Industry Contributions** | • Authored a full-length, archival research paper candidate for the *Journal of the Audio Engineering Society* (JAES).<br>• Published complete reproducible datasets, benchmarking harness, and open-source codebase on GitHub.<br>• Benchmarked real-time compute-storage trade-offs directly addressing resource bottlenecks in mobile XR chipsets (ARM64 architecture). |
| **Commercial & Applied Relevance** | • Directly applicable to high-growth spatial audio, immersive gaming, and virtual reality industries (e.g., Apple VisionOS, Meta Horizon, WebXR audio engines).<br>• Enables complex interactive synthesizers to run entirely in lightweight browser environments with zero multi-gigabyte asset downloads. |

---

## 6. Verification & Contact Details

* **Lead Researcher / Engineer:** Boobalan Arjunan
* **Laboratory:** ComposerMind Labs LLP
* **GitHub Repository:** `https://github.com/BoobalanArjunan/SpatialMind-RoomShift-Research`
* **Artifact Archive:** `jaes_submission_package.zip` (SHA-256 verified)
