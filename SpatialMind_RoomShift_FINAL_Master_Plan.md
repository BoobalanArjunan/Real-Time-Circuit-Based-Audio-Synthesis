# ComposerMind Labs — SpatialMind-RoomShift
## End-to-End AI/ML/DL Research, Dataset, Engineering and Publication Specification

**Author:** Boobalan Arjunan  
**Organization:** ComposerMind Labs LLP  
**Date:** 11 November 2026  
**Version:** 1.1 — final master specification with JAES MVP execution controls  
**Status:** PROPOSED; no experimental results, benchmark novelty, journal acceptance, or real-time deployment capability are claimed.

> **Core objective:** Develop and rigorously evaluate causal machine-learning estimators of room-acoustic properties (reverberation decay time and direct-to-reverberant ratio) under controlled changes in acoustic conditions. The contribution must be established through literature review, rigorous labels, held-out tests, and measurable improvements or new findings. The project is **not** an Audio2Circuit inverse-prediction paper.

---


# FINAL EXECUTION ADDENDUM — 11 NOV 2026 (OVERRIDES OPTIONAL MASTER SCOPE)

**Authority:** This is the single implementation master file. The following MVP and gates take precedence over optional experiments, integrations, model heads, panels, and figures elsewhere in the document. Status remains **PLAN ONLY**; no measured results or acceptance claims exist.

## Mandatory minimum viable paper

1. Verified 10-room RIR/RT60/DRR report, 100-scene pilot and source-event observability test.
2. Predict-training-mean, blind classical DSP, gradient-boosting ML, and small causal TCN baselines. Blind baselines must not access clean sources or RIRs at inference.
3. Experiment A: event-aligned adaptation detection and settling; Experiment C: static-only vs transition-aware TCN under **equal training budget** (at least 3 seeds per condition).
4. Held-out rooms and source families, and crossfade-to-hard-switch transfer. Report the **independent room count and source-family count**, not just scene count.
5. Room-clustered bootstrap confidence intervals, streaming analysis-window + hop + inference latency, and measured CPU real-time factor.
6. Publish only measured, script-generated numbers; include negative findings and failure rates.

**Deferred unless time permits:** confidence/observability prediction head, pretrained embeddings or encoders, DAW/VST demos, click-suppressed controls, extra generalization panels, large model searches, full-band XR claims, measured rooms and coupled-room simulation. No pretrained model is required for the MVP.

## Data and acoustic validity

- Preserve rights-cleared original 48 kHz WAV masters; generate deterministic, anti-aliased **16 kHz research copies** for fast RIR simulation and model training. Disclose the limited frequency band and avoid full-band performance claims.
- Use the owner's rights-cleared dry circuit sounds as the default source pool, split by circuit family **before** rendering; include percussive/gated sources with known note-on/off events. Optional natural sounds are **unseen-domain evaluation only** after license verification. Do not claim Audio2Circuit inverse-model results.
- Test 10 rooms first, including challenging room sizes/RT60s; record wall-clock simulation time and effective decay range. Favor **300–400 distinct rooms if affordable** over many correlated scenes, but do not increase scale at the expense of the deadline. If test-room count is small, report wide uncertainty or consider room-grouped cross-validation without leaking test data.
- RIR label source: documented Schroeder decay fit (T20/T30 with stated usable decay range, minimum dynamic range and fit-quality threshold); compute DRR from a documented direct-path window. Independently compare T20/T30 against analytical Sabine/Eyring predictions, report discrepancies per room, and acknowledge that these are approximate cross-checks rather than exact truth.
- Freeze the **informative-event eligibility rule before the 100-scene pilot** using known source onset/offset and decay metadata. Pre-register adaptation detection delay, first valid post-event estimate, settling tolerance, continuous hold time, overshoot and censored/failure handling. Set tolerance candidates using pilot/validation data only; freeze before test evaluation. Report time relative to both room transition and first informative event.
- Crossfaded and hard-switched RIR outputs are controlled non-physical rendering transitions, **not actual movement through coupled rooms**. Crossfade regions are excluded from ordinary single-room RT60/DRR regression scoring; transition-tracking metrics use declared schedule and validity rules.
- Ensure no dry source recording, source family or room/RIR leaks between train/validation/test as applicable to the specified split. Distinguish room-only and joint room-plus-source-family evaluations if their sample sizes differ.

## Time-critical gates and deliverables

| Date | Required work | Stop condition |
|---|---|---|
| **Nov 11–12** | **Phase 0 only:** literature novelty matrix; verify official JAES XR call scope, benchmark/dataset paper eligibility, article type, limits and submission rules (ask guest editors if unclear); environment; 10-room RT60/DRR verification and percussive observability | **STOP for human review. No 100-scene pilot without authorization.** If JAES scope is unsuitable, redirect venue, do not force XR framing. |
| Nov 13–15 | After approval: 100-scene pilot, event timestamps, reproducible splits, mean and classical baseline | Stop if labels/observability fail |
| Nov 16 | Formal novelty + label + observability + baseline go/no-go | Stop JAES submission if any critical gate fails |
| Nov 17–19 | Generate scalable data; **early TCN smoke test:** overfit tiny subset, future-perturbation causality test, one timed 16 kHz training epoch; project runtime for 6 runs | Reduce model size/data before reducing 3 seeds per condition |
| Nov 20–25 | Gradient boosting, 6 equal-budget TCN runs, Experiments A/C, hard-switch transfer, grouped CIs; draft related work, methods and dataset card in parallel | Stop if results cannot support claim |
| Nov 26–29 | Error analysis, script-generated figures/tables, limitations, formatting, rights/anonymity review, submission rehearsal | Do not fabricate or rush results |
| Nov 30 | Conditional submission only if scientific novelty, venue fit and evidence pass | Otherwise retain work for later venue |

**Phase 0 handoff package:** `room_verification.csv` with room ID, target RT60, T20, T30, Sabine, Eyring, DRR, fit quality, dynamic range, acceptance/rejection and reasons; per-room RIR/decay plots; percussive observability test with source-event timestamps; simulator/config/seed/hash manifest; literature matrix; venue scope record; commands and test logs. Antigravity must **stop and request explicit review** after producing this package.

**Training fairness:** 3 or more independently seeded runs per TCN condition (minimum six); same architecture, train/validation data budget, optimizer/search policy, training steps or compute budget, and validation-only selection. The static-only vs transition-aware data allocation and evaluation must be documented explicitly. Never tune on the test set.

---

# 1. Executive decision and scientific boundaries

## 1.1 Research questions

- **RQ1 — adaptation:** How does event-conditioned adaptation delay vary across classical blind estimators, feature-based ML, and causal deep models after a controlled room-response change?
- **RQ2 — generalization:** How well do estimates generalize to previously unseen room geometries, absorption conditions, and independent sound-source families?
- **RQ3 — transition robustness:** Does transition-aware training improve accuracy/settling time without degrading static-room accuracy, and does that improvement persist for an unseen transition operator (hard switch versus crossfade)?
- **RQ4 — observability:** Under which source-event patterns and SNRs are RT60/DRR estimable from audio, and when should a model abstain or report low confidence?

**Candidate contribution, NOT yet a novelty claim:** A source-event-conditioned, reproducible evaluation protocol for *causal* room-property tracking, with transition-operator generalization, event-aligned lag metrics, room/source-disjoint testing, and a confidence/observability analysis. Prior-art verification may require narrowing or abandoning this claim.

## 1.2 Scope

**In:** synthetic single-channel shoebox-room responses, dry source audio, labeled RIRs, scripted acoustic changes, causal estimation, DSP/ML/DL baselines, reproducibility, streaming-latency measurement, optional DAW demonstrations.

**Out of scope for the deadline:** physically simulated doorway traversal, coupled rooms, head-tracked HRTFs, binaural perception, actual listener movement, Unity/Unreal integration, real-world XR deployment, multisource separation, source localization, Audio2Circuit inverse model, perceptual listening-study claims.

**Important terminology:** The benchmark studies *changes in rendered acoustic conditions*, not physically accurate motion through coupled spaces. A crossfade between two RIR-convolved signals does not represent a measured room trajectory. The term “XR-relevant” describes the application motivation, not proven XR deployment.

## 1.3 Go/no-go gates

- **12 Nov:** literature matrix and venue scope verified; 10 rooms simulated; RIR/label pipeline functioning.
- **15 Nov:** 100-scene pilot, independent physics cross-check, source-event observability report, mean and classical baselines, and one trajectory plot.
- **16 Nov:** proceed only if novelty is defensible, labels pass quality gates, the source conditions permit estimation, and classical baseline meaningfully outperforms mean on held-out rooms.
- **22 Nov:** if results, validation or novelty remain thin, do not rush a JAES submission.
- **30 Nov:** conditional target for the XR special issue; confirm current official call, article categories, length, formatting, review process, charges, licensing and submission procedure directly before committing.

Acceptance is never guaranteed. A valid research outcome may be a negative result or a later conference/journal submission.

---

# 2. Literature, novelty, and venue verification

## 2.1 Literature search matrix (must be completed with verified citations)

Search primary publications and publisher/DBLP records for: ACE Challenge (RT60/DRR), blind reverberation estimation, causal/online RT60 estimation, DRR estimation, dynamic room-acoustic tracking, time-varying RIR estimation, transition-aware acoustic models, source-independent room acoustics, cross-dataset evaluation, pyroomacoustics-based datasets, uncertainty/observability in acoustic estimation, and XR room-adaptive rendering.

Create `research/literature_matrix.csv` with fields:
`paper_id,title,authors,year,venue,doi_or_publisher_url,task,static_or_dynamic,causal,source_event_control,room_split,source_split,transition_operator,metrics,dataset,code_available,novelty_overlap,notes`.

**Decision:** Write a one-paragraph *falsifiable* novelty statement and a table contrasting at least the closest 5–10 relevant works. Do not claim first-ever, state of the art, or a new benchmark category without documentary support.

## 2.2 Venue compliance

Record the official AES/JAES call URL, deadline with timezone, permitted paper types (research article/engineering report/dataset paper), length and figures, anonymization, supplementary materials, code/data availability, APC/overlength charges, copyright and reuse policies. Store a dated PDF/screenshot of the official call in `research/venue/`. **All details are unverified until checked against the official publisher page.**

---

# 3. Architecture and data flow

```text
Rights-cleared DRY WAV pool ── QC / fingerprint / family grouping ─┐
                                                                ├── scene manifest + split assignment
Room geometry / material parameters ── RIR simulator ── RIR QC ──┘
                                           │
                           RIR labels: T20/T30-derived RT60, DRR
                           analytical check: Sabine / Eyring
                                           │
                  source ⊛ RIR_A, source ⊛ RIR_B (convolution)
                                           │
                  controlled static / hard switch / crossfade
                                           │
                   WAV + transition envelope + event annotations
                                           │
            DSP baseline | feature ML | causal TCN | optional pretrained
                                           │
                  causal streaming inference and evaluation
                                           │
              result files → statistical analysis → figures → paper
```

**Separation of concerns:** The simulator creates references; the estimator receives only audio (plus explicitly permitted features) and must not access room IDs, RIRs, target RT60, source IDs or transition schedules at inference time.

---

# 4. Repository layout and deliverables

```text
spatialmind-roomshift/
├── README.md
├── LICENSE                     # decide before release
├── pyproject.toml
├── requirements-lock.txt
├── configs/
│   ├── pilot.yaml
│   ├── dataset_full.yaml
│   ├── dsp_baseline.yaml
│   ├── features_ml.yaml
│   └── tcn.yaml
├── research/
│   ├── literature_matrix.csv
│   ├── novelty_statement.md
│   └── venue/
├── data/
│   ├── raw_sources/            # restricted / not committed
│   ├── source_manifest.csv
│   ├── rirs/
│   ├── scenes/
│   ├── labels/
│   ├── splits/
│   └── manifests/
├── src/roomshift/
│   ├── ingest.py
│   ├── audio_qc.py
│   ├── source_events.py
│   ├── simulate_rooms.py
│   ├── rir_labels.py
│   ├── physics_checks.py
│   ├── render_scenes.py
│   ├── split_data.py
│   ├── features.py
│   ├── models/tcn.py
│   ├── models/ml_baselines.py
│   ├── dsp_baseline.py
│   ├── streaming.py
│   ├── evaluate.py
│   ├── bootstrap.py
│   └── figures.py
├── scripts/
│   ├── 00_environment_check.py
│   ├── 01_ingest_qc.py
│   ├── 02_generate_10_rooms.py
│   ├── 03_verify_rirs.py
│   ├── 04_render_pilot.py
│   ├── 05_baselines.py
│   ├── 06_freeze_splits.py
│   ├── 07_render_full.py
│   ├── 08_train_ml.py
│   ├── 09_train_tcn.py
│   ├── 10_evaluate.py
│   ├── 11_bootstrap_and_plots.py
│   └── 12_reproduce_paper.py
├── tests/
├── results/
│   ├── pilot/
│   ├── full/
│   └── publication/
├── demos/
│   ├── daw_optional/
│   └── streaming_optional/
└── manuscript/
    ├── draft.md
    ├── tables/
    └── figures/
```

Every stage produces a machine-readable manifest, QC report, checksums and a log. Scripts fail closed on missing input, bad metadata, leakage or label-quality violations.

---

# 5. Hardware, OS, environment, dependencies

## 5.1 Primary machine

MacBook Pro Apple Silicon M1 Max (64 GB RAM reported), macOS; CPU-first simulation and pilot; PyTorch MPS may accelerate training but must be validated for supported operations and determinism. Do not assume MPS and CPU produce bitwise-identical training results.

Optional remote NVIDIA GPU is justified only if profiling shows training time blocks the schedule. Record device, OS, chip, CPU cores, RAM, GPU, library versions and elapsed time for all benchmarks.

## 5.2 Python stack

Python 3.11 or 3.12 (verify package compatibility), NumPy, SciPy, soundfile/libsndfile, librosa (optional analysis), pyroomacoustics, scikit-learn, PyTorch, torchaudio (only if compatible), pandas, matplotlib, pytest, pydantic, PyYAML, tqdm, psutil, packaging, and a deterministic audio hashing/fingerprinting utility. Optional: MLflow or TensorBoard for experiment tracking; no cloud account required.

**Installation principle:** Pin versions after a successful compatibility check; pyroomacoustics may require compilation and toolchain support on Apple Silicon. Install from official package documentation and validate a minimal RIR simulation before building other modules. Do not claim that a specific version is compatible until tested.

Example environment workflow:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install numpy scipy soundfile pandas scikit-learn matplotlib pyyaml pydantic pytest psutil tqdm
python -m pip install pyroomacoustics torch
python -m pip freeze > requirements-lock.txt
python -c "import numpy, scipy, soundfile, pyroomacoustics, torch; print('ENVIRONMENT_OK', torch.__version__)"
```

This is a starting command, **not** a verified lockfile or a guarantee of a successful build. Capture errors and resolve one by one.

## 5.3 Reproducibility

Pin source code commit, Python and dependencies, room generator seeds, source selection seeds, transition seeds, train/val/test split IDs, model initialization seeds, and data hashes. Prefer content-addressed manifests. Record nondeterministic operations; report differences across reruns rather than promising bitwise identity across hardware.

---

# 6. Source audio dataset: rights, WAV quality, diversity

## 6.1 Primary pool and legal controls

Default: owner-created, rights-cleared ComposerMind circuit-generated dry WAVs. These are **audio source inputs only**, not Audio2Circuit labels, and the inverse model is neither used nor trained. Ownership and redistribution rights must still be documented; ownership alone does not prove that any third-party plugin samples or libraries embedded in a render are redistributable.

**Source-manifest required fields:** `source_id,sha256,source_family,circuit_family,source_preset,original_path,rights_holder,creation_method,license,redistribution_allowed,commercial_allowed,third_party_content,provenance_note,original_sr,original_channels,duration_s,peak_dbfs,true_peak_dbfs,integrated_lufs,dc_offset,clipped_samples,noise_floor_dbfs,onset_count,source_type,split_id`.

Optional out-of-domain set: a small set of natural sound or speech clips only after explicit license review; track attribution, derivative rights and whether processed WAVs may be published. No uncontrolled scraping or unlicensed commercial songs.

## 6.2 WAV format specification

- Master: **48,000 Hz**, mono, **24-bit PCM WAV or 32-bit float WAV** (choose one and record encoding); preserve original masters separately.
- Model input: 48 kHz or explicitly documented resampling to 16/24 kHz; anti-aliasing resampler, measured resampling consistency; do not silently relabel sample rates.
- Prefer genuinely dry, isolated sources: no built-in reverb, room tail, stereo widening, chorus, spatializer or mastered ambience. If sources are not dry, tag and exclude them from primary tests.
- Duration: sufficient to cover 10–12 s scenes; longer source clips may be deterministically cropped. Avoid looping short sounds without documenting repetitions.
- Avoid unintended clipping; target headroom (for example ≤ -3 dBFS sample peak before convolution), record true peak and gain. These are **engineering targets**, not scientifically necessary universal thresholds.
- DC offset: flag material offsets and correct only with logged transformations. Flag silence, near silence, corrupted headers, NaN/Inf, repeated or near-duplicate files.
- Loudness: measure rather than blindly normalize all clips; if gain normalization is used, apply a frozen protocol and retain gain metadata. Prevent loudness from leaking the room label.
- Bandwidth: include broadband transient sources, gated bursts, alarms and sustained tones as separately labeled groups; do not assume narrowband tones can reveal broadband RT60.
- Source events: detect and validate onset/offset times; store event type, time, strength and confidence. Where possible use generated event metadata as reference and independently check with DSP.

## 6.3 Quality assurance pipeline

1. Decode and verify file format, sample rate, channel count, length, finite samples.
2. Measure sample/true peaks, RMS, LUFS where applicable, DC offset, silence ratio, clipping count, spectral bandwidth and estimated noise floor.
3. Compute SHA-256 and near-duplicate fingerprints; deduplicate **before splitting**.
4. Check for pre-existing reverb using decay/late-energy heuristics and manual review of a sample; heuristics are not proof of dryness.
5. Classify source families and event structure; require enough independent source families to support held-out testing.
6. Produce `source_qc.csv`, `source_qc_summary.json`, rejected-file log and a curated immutable source manifest.

## 6.4 Observability gate

Generate a set of isolated impulses/bursts and percussive/gated sources with known event times, and a sustained-tone negative control. Estimate whether a blind decay method can recover RIR decay under each condition. Report failures and error versus onset/offset spacing, spectral bandwidth and source SNR. A source event alone does not guarantee recoverability: overlap, excitation spectrum, and source decay confound the room decay. If no useful events occur after a room change, mark that period **unobservable** for event-conditioned lag scoring rather than pretending an estimator should infer the new room instantly.

---

# 7. Room simulation and RIR dataset

## 7.1 Initial geometry and acoustics

Pilot: 10 rooms, varied geometries and absorption. Full target: at least 200 **independent** shoebox rooms; dimensions approximately 3–20 m per axis, with physically plausible volumes and heights; avoid unrealistic extreme combinations. Target RT60 range about 0.2–2.0 s **where the simulator can reliably realize and measure it**. Source-receiver distance 1–6 m, constrained by room geometry and wall clearances. Randomize positions and material/absorption profiles independently of source families and split assignments.

Use pyroomacoustics image-source modeling (and supported options if verified). Record sound speed, temperature assumption, sample rate, room dimensions, wall coefficients, reflection order, simulation method and implementation version. Verify that generated RIR length and reflection order are sufficient to measure the target decay, especially for long RT60.

**Caution:** Frequency-independent shoebox absorption and Sabine/Eyring assumptions simplify actual room physics. If frequency-dependent materials are implemented, specify how broadband and band-limited T20/T30 labels are computed.

## 7.2 Labels

- **RT60 reference:** estimate from the *simulated RIR*, using backward Schroeder energy integration and regression on an explicitly defined T20 (-5 to -25 dB) or T30 (-5 to -35 dB) decay segment; extrapolate to 60 dB. State noise-floor estimation, dynamic-range criterion, fitting error, and any discarded RIRs. Do not label all scenes using the requested target RT60 alone.
- **DRR reference:** determine direct-arrival sample using source-receiver geometry and sound speed, with peak/timing validation; integrate a preregistered direct-path window around arrival and compare to remaining reverberant energy. Specify window width, whether early reflections fall inside it, and sensitivity to window choice.
- **Analytical cross-check:** compute Sabine and/or Eyring predicted RT60 from geometry and absorption. This is a *physics-based sanity check*, not a gold-standard measurement or a fully independent empirical experiment. Report discrepancy distributions and explain known model mismatch.
- **Quality gates:** finite RIR, adequate dynamic range, physically plausible direct arrival, measurable decay, no silent channels, and documented failure/rejection reasons.

## 7.3 Independent verification strategy

Implement the RIR decay estimator and a separate analytical Sabine/Eyring calculation in different modules with unit tests and independently checked formula conventions. Include synthetic reference cases (known exponential decays), direct impulse tests, and manual inspection of 10 plots. Optionally use a second established implementation of RIR decay estimation to cross-check numeric behavior; two Schroeder implementations are algorithmic replication, not physically independent validation.

Report `room_id,target_rt60,measured_t20_rt60,measured_t30_rt60,sabine_rt60,eyring_rt60,drr_db,fit_r2,usable_decay_db,rir_length_s,verification_status,reason`.

---

# 8. Scene synthesis and acoustic transitions

## 8.1 Scene classes

- **Static control:** single RIR throughout.
- **Hard switch:** change between two independently convolved responses at a known time (may cause discontinuity; report and QC it).
- **Crossfade:** smoothly blend convolved signals using a preregistered envelope over 0.5, 1 or 2 s.
- **Two transitions:** A→B→C with adequate separation to observe settling.
- **Optional negative controls:** unchanged acoustic parameters but equivalent gain/crossfade operations, to test artifact shortcuts.

Render convolution consistently: compute source ⊛ RIR_A and source ⊛ RIR_B with aligned direct arrivals and equal documented gain conventions, then switch or crossfade outputs. If direct arrivals differ, align or explicitly preserve and document timing; accidental alignment changes must not become the dominant transition cue. Avoid peak normalization independently per room because it can leak the label.

## 8.2 Transition labels and masking

Store start/end times, transition operator, envelope shape, room A/B IDs, RIR labels, source-event timestamps, and a valid-label mask. For static periods, the active RIR reference RT60/DRR is meaningful. During crossfades, do **not** invent a physically meaningful single RT60/DRR; mask them from ordinary regression scoring. For adaptation metrics, define the new-room target as applicable after the end of the transition and report both onset-referenced and completion-referenced delays.

## 8.3 Audio quality checks for rendered scenes

Check output duration/sample count, finite values, clipping/true peak, unintended silence, abrupt discontinuities, RMS changes, direct-path timing, scene hash and repeatability. Listen to a stratified sample for broken audio, but do not claim perceptual validity without a formal listening test. Record hard-switch clicks as a potential shortcut and consider a click-suppressed abrupt-transition control.

---

# 9. Event-conditioned adaptation metrics — preregistration

Define all metrics **before** looking at test results.

- `t_change_start`: programmed start of acoustic transition.
- `t_change_end`: completion of transition (same as start for hard switch).
- `t_event`: first *informative* source onset or offset at/after `t_change_end`, validated by event metadata and an audio event detector. An event is informative only if its excitation and decay support the relevant metric; use a stated eligibility rule.
- `t_first_valid`: first output timestamp with enough causal context and valid audio evidence, whether or not prediction is correct.
- `t_first_correct`: first eligible prediction inside tolerance after the transition/event.
- `t_settled`: first time prediction remains within tolerance continuously for hold duration, without peeking into future samples for the prediction itself.

**Provisional preregistered tolerances:** RT60 within ±15% of the new-room reference; DRR within ±2 dB; continuous hold time 1.0 s. These must be frozen before the held-out evaluation; sensitivity analysis may report alternatives without replacing the primary definition.

**Metrics:**

1. Event-conditioned first-valid latency = `t_first_valid - t_event` (nonnegative or explicitly censored).
2. Event-conditioned first-correct delay = `t_first_correct - t_event`.
3. Event-conditioned settling delay = `t_settled - t_event`.
4. Transition-completion-to-settling delay = `t_settled - t_change_end` (includes waiting for acoustic information).
5. Overshoot = maximum absolute signed deviation beyond the new target over a preregistered observation window, reported separately for RT60 and DRR.
6. Failure/censoring rate = proportion not reaching accuracy/hold criteria before next transition or scene end.

Report event spacing, event category, source decay, and source type alongside delays. Do not discard non-settling cases when computing summary statistics; report censoring or use appropriate time-to-event analysis. Predictions remain causal; using future samples to *evaluate* a hold interval is permissible, but not to construct predictions.

---

# 10. Data splitting and leakage prevention

## 10.1 Splits before scene rendering

Assign **room IDs** and **source-family IDs** to train/validation/test partitions before combining them into scenes. All source recordings, near-duplicates, source preset variants and RIR variants from the same underlying family/room remain in one partition. No dry recording, source family, room geometry instance, RIR or derivative may cross splits. Verify with hashes and group keys.

Suggested split ratios 70/15/15 by independent rooms and source families, adjusted to maintain sufficient category diversity. Explicitly document how rooms and sources are crossed within each split; do not create train scenes from a test room or test source.

## 10.2 Generalization panels

- **Primary IID-within-domain:** held-out rooms **and** source families, transition types represented in training.
- **Room shift:** held-out room geometries/materials with known source families; separate panel, no leakage.
- **Source shift:** unseen source families in known acoustic parameter ranges.
- **Transition shift:** train on crossfades, test hard switch/click-controlled switch and vice versa.
- **Speed shift:** hold out a crossfade duration from training.
- **Optional:** unseen RT60 ranges, natural sounds and SNRs.

Use distinct manifests and explicitly label each panel. Validation is used for tuning; the final test is accessed only for preregistered evaluation.

---

# 11. AI/ML/DL methodology

## 11.1 Learning task and inputs

Streaming mono audio waveform `x[t]` is converted to causal frame features. Model outputs every ~250 ms (4 Hz): `log(RT60_seconds)`, `DRR_dB`, and optionally `observability_confidence` or `valid_estimate_probability`. No RIR, source ID, room ID, transition schedule, ground truth or future audio is provided at inference.

Use log-RT60 regression to reduce scale imbalance. Record target normalization statistics from training only. DRR clipping and output ranges must be preregistered. For masked transition intervals, exclude ambiguous RT60/DRR targets from supervised regression; do not label them with an arbitrary interpolation. An auxiliary transition-detection head is optional and must be ablated.

## 11.2 Baseline 0 — trivial floor

Predict training-set mean (or median) RT60 and DRR. Also consider last-value carry-forward as a dynamic baseline. Never compute baseline constants from test labels.

## 11.3 Baseline 1 — classical blind estimator

Select a documented, cited, implementable decay-based blind estimator suitable for event-conditioned input. Avoid presenting direct RIR Schroeder integration as a *blind* estimator: the estimator does not have the RIR. A simple first prototype may use gated source-offset detection and fit the post-offset decay envelope, with the explicit assumption that source release is sufficiently short. Report the source-decay confound and invalidity on sustained signals. DRR estimation requires a separately justified blind method; do not silently use true source/room impulse responses. If reliable blind DRR cannot be estimated, retain a mean/feature baseline and document the limitation.

## 11.4 Baseline 2 — classical ML

Causal STFT/log-mel and spectral/temporal features: decay slopes after detected events, subband energy, modulation statistics, spectral centroid/flatness, short-term energy and optional onset timing. Train gradient-boosted trees (e.g. HistGradientBoostingRegressor) separately for log RT60 and DRR, or a supported multi-output wrapper. Fit preprocessing and model using training split only; tune on validation; report model size and CPU inference latency.

## 11.5 Baseline 3 — causal TCN (primary DL model)

Suggested starting architecture (hyperparameters are experimental, not final):

- Input: causal log-mel/STFT frames (e.g. 25 ms window, 10 ms hop) plus optional causal energy/onset features.
- Stem: 1-D temporal convolution or linear projection, 64 channels.
- Temporal blocks: 4–6 residual depthwise/separable or ordinary 1-D causal convolution blocks, kernel size 3, dilations 1/2/4/8/16/32; verify receptive field and total lookback.
- Normalization: channel-wise/feature-wise scheme that does not use future frames or test-batch statistics. Avoid noncausal temporal batch normalization at inference.
- Heads: two regression outputs (log RT60, DRR); optional confidence/observability and transition detection heads.
- Output rate: 4 Hz with causal pooling/downsampling; explicitly timestamp predictions at the latest input sample consumed.
- Loss: masked Huber or MAE for regression, optionally confidence calibration and transition auxiliary loss; select weights using validation only.
- Optimization: AdamW, early stopping, gradient clipping, deterministic seed logging, 3+ initialization seeds, same data and compute budgets across comparative conditions.

**Pretraining:** No pretrained model is required. Train the compact TCN from scratch for the primary controlled comparison. Optional external pretrained audio embeddings (e.g. PANNs, BEATs, wav2vec2) may be exploratory only after checking license, domain fit, compute, causality and input rate. Most standard encoders use bidirectional context and are **not automatically valid causal baselines**; do not present them as streaming models unless re-engineered and benchmarked causally. Freeze versus fine-tune protocols must be specified and compared fairly. A pretrained room-acoustics estimator may be included only if published code/checkpoints and licensing are verified, and input/target definitions are compatible.

## 11.6 Experiment A — adaptation

Compare mean/hold, classical blind estimator, feature ML and causal TCN on fixed unseen-room transitions. Stratify by event delay after transition, source class, transition operator and RT60/DRR contrast. Report error curves aligned both to transition completion and to first informative source event, settling/failure statistics, confidence intervals and CPU latency.

## 11.7 Experiment B — unseen rooms

Freeze the model and test on held-out room geometries/materials and source families. Report static and dynamic MAE/bias, per-room error distributions, long-decay versus short-decay performance and domain-shift gap. Separate in-range new rooms from out-of-range RT60 extrapolation.

## 11.8 Experiment C — transition-aware learning

Train two models with identical architecture, parameter count, optimizer, initialization seed set, total gradient updates, total audio seconds, batch sizes and comparable source/room distributions:

- **Static-only:** scenes with fixed RIRs.
- **Transition-aware:** matched scenes including transitions.

Use equal training budgets and a common static + dynamic held-out test. Compare static accuracy, dynamic accuracy, event-conditioned lag, failure rate and transition-operator transfer. Repeat for 3+ seeds. If transitions add scene diversity, explicitly balance or quantify it rather than claiming the difference is purely due to transition learning.

## 11.9 Ablations

Minimum: causal context length; static-only vs transition training; unseen source families; hard switch vs crossfade; event availability; with/without noise. Optional: confidence head, spectrogram versus waveform, loss weighting, transition auxiliary head, DRR-window sensitivity.

---

# 12. Training protocol and model management

1. Validate immutable manifests and split audit.
2. Compute feature statistics from train only; cache with source/split/version hashes.
3. Fit mean and DSP baselines before DL.
4. Train feature ML with fixed search space and validation budget.
5. Train causal TCN with at least seeds 11, 23, 37 (illustrative), fixed training budget, checkpoint best validation epoch, no test-based model selection.
6. Save optimizer config, architecture, parameter count, feature schema, receptive field, checkpoints, seed, device, training logs and dataset hash.
7. Evaluate each seed on the same frozen test; report per-seed values and mean/spread. Do **not** mislabel a three-seed range as a statistical confidence interval.
8. If pretrained models are tested, document provenance, version, license, receptive field, frozen/fine-tuned status and inference constraints.

**Training sanity tests:** overfit a tiny train subset, check gradients finite, verify causal masking by changing future audio and ensuring earlier predictions do not change, verify no test data enters normalization, and check reproducibility within expected hardware tolerance.

---

# 13. Metrics, statistics and evaluation

## 13.1 Regression metrics

RT60: MAE (s), median absolute error, relative absolute error (%), signed bias, and per-range breakdown. DRR: MAE (dB), median absolute error and signed bias. Calculate static-period metrics only where valid labels exist; show coverage percentage.

## 13.2 Tracking metrics

Event-conditioned first-valid/correct delay, settling delay, completion-to-settling delay, overshoot, recovery time, and non-settling fraction. Define timestamp resolution (e.g. 250 ms output hop) and maximum observable horizon. Use failure-aware summaries; do not report a deceptively low mean based only on successful transitions.

## 13.3 Statistics

Bootstrap **at the independent room level** (e.g. 2,000 replicates) and preserve within-room correlations; if room and source-family effects both matter, consider a crossed/clustered or hierarchical resampling sensitivity analysis. Report 95% CIs for main effects and paired differences where applicable. Three or more DL seeds show optimization variability; report seed-specific values separately from room-bootstrap CIs. Predefine primary metrics and comparisons; avoid uncorrected fishing across dozens of tests.

## 13.4 Runtime / real-time

Measure preprocessing + feature computation + inference on the target CPU, with warmup, repeated trials and p50/p95/p99 timings. Report actual streaming analysis window, hop, algorithmic lookback, buffering and wall-clock computation separately. Real-time factor `audio_duration / processing_duration` is a throughput statistic, **not** proof of meeting callback deadlines. A 4 Hz output imposes at least an output-cadence limit on reported tracking. Measure peak memory and model size.

## 13.5 Visualizations

Generate only from result files: (1) room/RIR validation scatter, (2) RIR decay curves, (3) event/transition/audio/ground-truth/prediction timeline, (4) event-aligned tracking curves, (5) MAE by source family and room range, (6) operator-generalization matrix, (7) paired seed/room uncertainty plot, (8) latency-accuracy tradeoff, (9) failure/censoring chart.

---

# 14. VST, DAW and plugin policy

**Primary research pipeline: Python only.** DAWs/VSTs are **not needed** for ground-truth generation, training or reproducible numerical evaluation. This protects label integrity, automation repeatability, licensing and schedule.

## 14.1 Optional tools and appropriate roles

| Tool / category | Potential use | Research restriction |
|---|---|---|
| REAPER or another DAW | Audition and visualize transitions; automate parameters for demo | Do not use DAW automation as ground-truth timing without sample-accurate export checks |
| Sound Particles Air / Doppler / Space Controller / Energy Panner / Density / Brightness Panner | Future spatial-rendering demonstrations and subjective comparisons | Not required for mono RIR labels; spatial effects may invalidate RT60/DRR assumptions |
| NovoNotes 3DX | Optional spatial mixing demonstration | Not a physical reference RIR generator |
| SoundMorph DUST / granular plugins | Optional sound-design sources | Granular tails can confound decay estimates; require dryness/QC and license check |
| AIR Music Technology synths / own MNA synth | Produce original dry transients, alarms and controlled source events | Disable reverbs, delays, chorus and spatial effects; document preset and render chain |
| Generic reverb plugins | External-domain stress test only | Not used for core simulator-ground-truth labels unless independently measured and separately tagged |
| Voxengo PHA-979 / MAutoAlign | Optional timing diagnostics | Do not assume phase tools produce verified direct-path timing |

## 14.2 Optional DAW integration workflow

1. Import the **same** dry source WAV used in the benchmark.
2. Import Python-rendered Room A, Room B and transition outputs on separate tracks.
3. Set DAW session to 48 kHz; disable automatic time stretch, normalization and FX.
4. Verify sample alignment and export sample counts; render offline in float format.
5. Compare exported samples against Python reference and document any gain, dither or latency changes.
6. Use only for demonstration/qualitative checks; preserve Python files as authoritative research outputs.

**Do not require commercial plugins for reproducing the paper.** Any plugin-generated source audio must be legally redistributable under the relevant license if included in a public dataset. Plugin ownership does not automatically grant redistribution rights for factory samples/presets.

---

# 15. Testing and acceptance criteria

## 15.1 Unit tests

- WAV decoding, sample-rate conversion, channel conversion and corruption handling.
- DC/peak/silence/NaN/clipping checks.
- Onset/event timestamps on synthetic impulse/gated test cases.
- Schroeder T20/T30 against known exponential-decay references.
- Sabine/Eyring formula and unit conventions against hand-calculated cases.
- DRR direct-arrival window and direct/reverberant energy on controlled RIRs.
- Transition envelope boundary and time/sample indexing.
- Causal-model invariance to future-audio perturbation.
- No leakage across source families, near-duplicates, rooms or RIR derivatives.
- Deterministic manifests/hashes for repeat render with same seed.
- Masked labels do not contribute to regression loss or ordinary MAE.
- Event-conditioned metrics handle absent events and censored transitions.

## 15.2 Integration tests

- Ten rooms → validated RIRs → labels → 100 scenes → split audit → mean/DSP baseline → reports.
- Test generated audio against manifest, sample counts, clipping and labels.
- Test one scene with no post-transition event; verify it is flagged unobservable rather than scored as an instant estimator failure.
- Test click-only transition control and source-gain control for shortcut detection.
- Test CPU streaming with known chunk sizes and timing logs.

## 15.3 Acceptance gates (thresholds to preregister, not fabricated results)

- 100% of accepted scenes have valid manifests, checksum and split provenance.
- All reported RIR labels pass stated dynamic-range/fit/direct-arrival QC; report rejection rate.
- Pilot includes demonstrably recoverable percussive examples and documented negative controls.
- Classical baseline beats mean baseline on held-out rooms by a **predefined practically meaningful margin**, not just noise; determine margin before testing.
- At least one contribution survives source-family and transition-operator robustness tests, or paper honestly reports failure.
- Manuscript tables/figures generated directly from immutable result files.

---

# 16. Detailed implementation phases and command-line contracts

Each command below is a **planned interface** for Antigravity to implement, not an assertion that these scripts already exist.

## Phase 0 — project and environment (11 Nov)

```bash
python scripts/00_environment_check.py --out results/pilot/environment.json
pytest -q tests/test_environment.py
```

Output: hardware/version report and minimal pyroomacoustics smoke test.

## Phase 1 — source audit and 10-room reference (11–12 Nov)

```bash
python scripts/01_ingest_qc.py --config configs/pilot.yaml --out results/pilot/source_qc/
python scripts/02_generate_10_rooms.py --config configs/pilot.yaml --out data/rirs/pilot/
python scripts/03_verify_rirs.py --rir-dir data/rirs/pilot --out results/pilot/rir_verification/
pytest -q tests/test_rir_labels.py tests/test_source_events.py
```

Outputs: source manifest, 10 RIRs, RT60/DRR CSV, Sabine/Eyring discrepancies, plots, rejected cases and event-observability check.

## Phase 2 — 100-scene pilot (13–15 Nov)

```bash
python scripts/04_render_pilot.py --config configs/pilot.yaml --out data/scenes/pilot/
python scripts/05_baselines.py --manifest data/manifests/pilot.csv --out results/pilot/baselines/
python scripts/10_evaluate.py --config configs/pilot.yaml --out results/pilot/evaluation/
```

Outputs: reproducible scene audio, metadata, event labels, held-out split audit, mean and DSP metrics, tracking plot, timing/censoring report.

## Phase 3 — formal decision (16 Nov)

Create `research/go_no_go_2026-11-16.md` documenting novelty citations, room-label QC, observability, baseline-vs-mean, limitations, compute estimate, and explicit GO/NO-GO decision. If NO-GO, stop deadline-driven expansion.

## Phase 4 — full dataset (17–21 Nov, conditional)

```bash
python scripts/06_freeze_splits.py --config configs/dataset_full.yaml --out data/splits/
python scripts/07_render_full.py --config configs/dataset_full.yaml --out data/scenes/full/
pytest -q tests/test_splits.py tests/test_rendering.py
```

Output: target 2,000+ scenes, 200+ rooms where feasible, independent source counts, dataset card and QC report. Targets may be reduced transparently if runtime/validation requires it.

## Phase 5 — model experiments (20–25 Nov, conditional)

```bash
python scripts/08_train_ml.py --config configs/features_ml.yaml --out results/full/ml/
python scripts/09_train_tcn.py --config configs/tcn.yaml --seed 11 --out results/full/tcn_seed11/
python scripts/09_train_tcn.py --config configs/tcn.yaml --seed 23 --out results/full/tcn_seed23/
python scripts/09_train_tcn.py --config configs/tcn.yaml --seed 37 --out results/full/tcn_seed37/
python scripts/10_evaluate.py --config configs/dataset_full.yaml --out results/full/evaluation/
python scripts/11_bootstrap_and_plots.py --results results/full/evaluation --out results/publication/
```

Output: checkpoints, train/validation curves, per-scene predictions, metrics, uncertainty and ablations. Equal-budget Experiment C must be separately logged.

## Phase 6 — manuscript (25–30 Nov, conditional)

```bash
python scripts/12_reproduce_paper.py --results results/full --out manuscript/
pytest -q
```

Output: reproducible figures/tables, evidence audit, manuscript, reference validation, code/data statement and submission checklist. Do not submit if the results or novelty are insufficient.

---

# 17. Manuscript structure

1. **Abstract:** problem, exact evaluation design, measured findings only, limitations.
2. **Introduction:** XR acoustic adaptation motivation; scope of synthetic acoustic-condition changes.
3. **Related work:** blind RT60/DRR, online estimation, time-varying acoustics, existing benchmarks.
4. **Benchmark methodology:** rooms, source rights/QC, RIR labels, physics checks, transitions, splits, observability.
5. **Models:** trivial, blind DSP, classical ML, causal TCN; pretraining status and compute.
6. **Evaluation:** metrics, event-conditioned lag, censoring, statistical plan and runtime.
7. **Experiments A/B/C:** preregistered primary results, operator transfer and ablations.
8. **Discussion:** what is learned, shortcuts, generalization, failure cases, limitations.
9. **Reproducibility and data availability:** code, config, seed, hashes, dataset rights.
10. **Conclusion:** bounded claims, no untested physical XR/perceptual assertions.

All tables must be generated from raw logged metrics. No fabricated references, effect sizes or confidence intervals.

---

# 18. Risks, mitigations and fallbacks

| Risk | Detection | Mitigation / decision |
|---|---|---|
| Novelty already covered | Literature matrix overlaps closely | Narrow research question or stop submission |
| Source event not informative | Observability pilot fails | Use controlled percussive/gated sources; report unobservable cases |
| Electronic-source domain bias | Held-out family/natural-sound performance collapses | Publish domain limitations; add licensed OOD test only if feasible |
| Bad RIR decay | T20/T30 fit/dynamic-range failure | Increase RIR length/order, correct simulator, reject invalid rooms |
| DRR label ambiguity | Direct window sensitivity large | Preregister window; report sensitivity and uncertainty |
| Crossfade shortcut | Fails hard-switch/negative control | Add operator-shift evaluation; remove unsupported generalization claim |
| Room/source leakage | Group/hash audit flags overlap | Regenerate split before any training |
| Training takes too long | Pilot profile exceeds budget | Reduce model/dataset, keep classical results, defer deadline |
| Causal leakage | Future perturbation changes past output | Fix padding/normalization/feature buffering |
| Paper category not allowed | Official call disallows benchmark form | Change framing only if justified; choose another venue |
| Deadline evidence weak | 22 Nov evidence audit fails | Do not submit; retain reproducible research assets |

---

# 19. Dataset card and release strategy

Dataset card must disclose creation date, ownership, provenance, license, source selection, synthetic nature, sample rate, mono format, room simulation assumptions, transition operators, label algorithms, split design, source-event observability, exclusions, failure modes, intended research use and prohibited interpretations.

Keep raw audio and proprietary presets out of the public repository unless redistributable. Consider releasing scripts, manifests, room parameters and synthetic impulse responses separately from restricted dry audio; confirm the licenses of generated derivatives and dependencies. Maintain private repository until venue anonymization and licensing rules are verified. Author credit: **Created by Boobalan Arjunan**; publisher: **ComposerMind Labs LLP**.

---

# 20. Antigravity / coding-agent execution contract

The implementation agent MUST:

1. Treat this specification as a design, not a claim that code/data/results exist.
2. Work sequentially and stop after each phase for user review; do not silently jump to 2,000 scenes or neural training.
3. Read actual local files and inspect package APIs; never invent source files, versions, licenses, test results or scientific citations.
4. Implement minimal working code with tests and type-checked configs; avoid unnecessary frameworks.
5. Save every result with seed, configuration, dataset hash, git commit and runtime metadata.
6. Show actual commands, stdout/stderr and file paths; never say a stage passed without executable evidence.
7. Fail closed on leakage, missing licenses, corrupted audio, invalid labels or noncausal model operations.
8. Use actual RIR-derived RT60/DRR as labels and analytical physics as a cross-check; do not confuse these with blind estimator inputs.
9. Keep all pretrained models optional and provenance-checked; do not download weights without approval and license review.
10. Keep DAW/VST branches optional and outside the authoritative label-generation path.
11. Run no paid GPU/cloud jobs without explicit approval and budget cap.
12. Prepare `PHASE_REPORT.md` with completed work, artifacts, measured results, failures, next command and go/no-go recommendation.
13. Never manufacture novelty, performance, statistical significance, acceptance probability or citations.
14. If a key scientific assumption fails, stop and recommend a revised experiment rather than patching the narrative.

## First agent task — start here, and stop

**Objective:** Complete only Phase 0 and the initial ten-room label-verification scaffold. First check source availability, toolchain and existing repo structure. Create reproducible code to simulate 10 RIRs and calculate T20/T30-derived RT60, DRR, Sabine/Eyring checks and plots; write unit tests; report any library/API incompatibility. Do not generate the full dataset, train models, claim novelty or draft results.

**Required first outputs:**

- `results/pilot/environment.json`
- `results/pilot/rir_verification/room_metrics.csv`
- `results/pilot/rir_verification/verification_summary.json`
- `results/pilot/rir_verification/plots/`
- `results/pilot/source_qc/` (only if sources were actually supplied)
- `PHASE_REPORT.md`

**Stop and request review** after the ten-room verification report. If no source audio is available, use explicitly marked synthetic impulse test signals for RIR validation only; do not pretend the source pool has passed rights or quality checks.

---

# 21. Final definition of success

**Engineering success:** verified, reproducible room simulation, labeled audio, quality checks, causal streaming inference, source/room leakage controls and executable baseline tests.

**Scientific success:** a well-supported, literature-distinct finding about event-conditioned adaptation, robustness to unseen acoustic conditions or transition-operator shortcuts, with transparent uncertainty and limitations.

**Publication success:** a compliant submission supported by real logged experiments. **Acceptance is a separate external decision and cannot be guaranteed.**

**Commercial/research asset:** a rights-compliant ComposerMind dataset and reusable evaluation toolkit, whether or not the November 30 submission is made.
