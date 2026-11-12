# Candidate Novelty & Contribution Statement: SpatialMind-RoomShift
## Causal Tracking of Dynamic Room Acoustics Under Controlled Acoustic Transitions

**Author:** Boobalan Arjunan  
**Date:** November 2026  
**Status:** Working Hypothesis & Scope Boundary  

---

## 1. Candidate Research Contribution

This research investigates the **causal estimation of room-acoustic decay properties ($T_{60}$ and DRR) under time-varying acoustic conditions**. 

Prior research in blind room acoustic parameter estimation (e.g., Eaton et al. [ACE Challenge 2016], Gamper & Tashev [2018], Bryan [2020], Götz & Välimäki [2022]) has predominantly evaluated **static acoustic spaces**, where a single unchanging room impulse response (RIR) characterizes the entire audio excerpt. Where dynamic adaptation has been studied (e.g., Löllmann et al. [2010], Kothari et al. [2021], Genovese et al. [2023]), evaluations have lacked standardized, source-event-conditioned lag metrics that account for excitation observability gaps.

Our candidate contributions are:
1. **Source-Event-Conditioned Adaptation Protocol:** We formalize adaptation latency not merely from the instantaneous time of a room transition, but relative to the *first observable acoustic event* following the transition, preventing artificial penalization during silence.
2. **Transition-Operator Generalization:** We evaluate whether causal estimators trained on smooth parametric crossfades generalize to abrupt acoustic hard-switches, quantifying transition-induced tracking error.
3. **Disjoint Source & Room Benchmark:** We enforce strict separation between training and test sets across both room geometries/absorptions and musical/circuit source sound families.

---

## 2. Distinction from Prior Art

| Property | ACE Challenge (2016) | Bryan (2020) | Götz & Välimäki (2022) | SpatialMind-RoomShift (Ours) |
| :--- | :---: | :---: | :---: | :---: |
| **Acoustic State** | Static | Static | Static (Frame-by-frame) | **Dynamic (Time-varying)** |
| **Causality** | Non-causal (Full-utterance) | Non-causal (Spectrogram CNN) | Causal (Conv1D / TCN) | **Strictly Causal** |
| **Transition Operators** | None | None | None | **Crossfade & Hard-Switch** |
| **Adaptation Lag Metric** | None | None | None | **Event-Conditioned Settling** |
| **Domain Scope** | Speech & Ambient Noise | Speech & Music | Speech & Instruments | **Circuit Sources & Percussive** |

