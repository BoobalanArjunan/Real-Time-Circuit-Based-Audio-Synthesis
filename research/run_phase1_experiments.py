#!/usr/bin/env python3
"""
SpatialMind-RoomShift: Phase 1 Full Factorial Dynamic Tracking Benchmark
Executes a 4-Room-Pair x 3-Transition x 3-Source factorial benchmark (36 conditions).
Measures:
- MAE, RMSE, RelError (%)
- Instantaneous Settling Lag (t_settle)
- Event-Conditioned Adaptation Lag (Delta t_adapt)
- Observability Latency Gap (Delta t_gap = t_event - t_trans)
- Generates publication figures:
  1. research/figures/dynamic_tracking_trajectories.png
  2. research/figures/lag_vs_observability.png
  3. research/figures/directional_asymmetry_analysis.png
- Exports raw measurement data to research/phase1_dynamic_tracking_results.csv
"""

import os
os.environ['MPLCONFIGDIR'] = '/tmp/mpl_cache'
import json
import csv
import numpy as np
import scipy.signal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from generate_dynamic_dataset import synthesize_transition_scene, FS
from simulate_10_rooms import ROOMS, compute_sabine
from causal_room_estimator import CausalRoomEstimator, evaluate_transition_tracking

def main():
    os.makedirs("research/figures", exist_ok=True)
    
    # 4 Representative Room Transition Pairs
    # 1: Small -> Medium (Dry to Moderate)
    # 2: Small -> Large (Dry to Reverberant)
    # 3: Large -> Small (Reverberant to Dry - tests acoustic hysteresis)
    # 4: Medium -> Very Large (Moderate to Cathedral)
    room_pairs = [
        {"name": "Small -> Medium", "from": 1, "to": 3, "desc": "Room 1 (0.16s) -> Room 3 (0.42s)"},
        {"name": "Small -> Large", "from": 1, "to": 8, "desc": "Room 1 (0.16s) -> Room 8 (1.54s)"},
        {"name": "Large -> Small", "from": 8, "to": 2, "desc": "Room 8 (1.54s) -> Room 2 (0.29s)"},
        {"name": "Medium -> Cathedral", "from": 4, "to": 10, "desc": "Room 4 (0.53s) -> Room 10 (2.15s)"}
    ]
    
    # 3 Transition Operators
    transitions = [
        {"type": "hard_switch", "duration": 0.0, "label": "Hard-Switch (tau=0ms)"},
        {"type": "crossfade", "duration": 0.5, "label": "Fast Crossfade (tau=500ms)"},
        {"type": "crossfade", "duration": 1.0, "label": "Slow Crossfade (tau=1000ms)"}
    ]
    
    # 3 Excitation Source Sound Families
    sources = [
        {"type": "percussive", "label": "Percussive (High Observability)"},
        {"type": "speech_bursts", "label": "Speech Bursts (Realistic Pauses)"},
        {"type": "drone", "label": "Harmonic Drone (Low Observability)"}
    ]
    
    csv_headers = [
        "condition_id", "room_pair", "room_from", "room_to", "t60_initial_s", "t60_target_s",
        "transition_type", "transition_tau_s", "source_type",
        "mae_s", "rmse_s", "rel_error_pct",
        "t_trans_s", "t_first_event_s", "t_settle_instant_s", "delta_t_adapt_s", "observability_gap_s"
    ]
    
    results = []
    trajectories_to_plot = []
    
    cond_id = 1
    print("=" * 80)
    print("Executing SpatialMind-RoomShift: Phase 1 Dynamic Tracking Factorial Benchmark")
    print(f"Total Conditions: {len(room_pairs)} pairs x {len(transitions)} transitions x {len(sources)} sources = {len(room_pairs)*len(transitions)*len(sources)} runs")
    print("=" * 80)
    
    for rp in room_pairs:
        for tr in transitions:
            for src in sources:
                print(f"[{cond_id:02d}/36] Testing: {rp['name']} | {tr['label']} | {src['type']}...")
                
                # Synthesize scene
                scene = synthesize_transition_scene(
                    room_a_id=rp['from'],
                    room_b_id=rp['to'],
                    transition_type=tr['type'],
                    transition_time=2.5,
                    transition_duration=tr['duration'],
                    source_type=src['type'],
                    scene_duration=6.5,
                    fs=FS
                )
                
                # Run causal estimator
                eval_res = evaluate_transition_tracking(scene)
                
                t_trans = eval_res['trans_time']
                t_event = eval_res['first_event_time']
                gap = t_event - t_trans
                
                row = {
                    "condition_id": cond_id,
                    "room_pair": rp['name'],
                    "room_from": rp['from'],
                    "room_to": rp['to'],
                    "t60_initial_s": round(eval_res['init_t60'], 4),
                    "t60_target_s": round(eval_res['target_t60'], 4),
                    "transition_type": tr['type'],
                    "transition_tau_s": tr['duration'],
                    "source_type": src['type'],
                    "mae_s": round(eval_res['mae'], 4),
                    "rmse_s": round(eval_res['rmse'], 4),
                    "rel_error_pct": round(eval_res['rel_error_pct'], 2),
                    "t_trans_s": round(t_trans, 4),
                    "t_first_event_s": round(t_event, 4),
                    "t_settle_instant_s": round(eval_res['t_settle_instant'], 4),
                    "delta_t_adapt_s": round(eval_res['delta_t_adapt'], 4),
                    "observability_gap_s": round(gap, 4)
                }
                results.append(row)
                
                # Collect representative trajectories for visualization
                if rp['name'] == "Small -> Large":
                    trajectories_to_plot.append({
                        "condition": f"{tr['label']} ({src['type']})",
                        "trans_type": tr['type'],
                        "source": src['type'],
                        "tau": tr['duration'],
                        "eval_res": eval_res
                    })
                    
                cond_id += 1
                
    # Save CSV
    csv_path = "research/phase1_dynamic_tracking_results.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nAll 36 experimental runs exported to: {csv_path}")
    
    # -------------------------------------------------------------------------
    # FIGURE 1: Dynamic Tracking Trajectories (4 panels)
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("SpatialMind-RoomShift: Causal T60(t) Dynamic Tracking Trajectories\n(Room 1 [0.16s] -> Room 8 [1.54s] Transition at t = 2.5s)", fontsize=14, fontweight='bold')
    
    plot_cases = [
        {"title": "(a) Hard-Switch (tau = 0ms) | Percussive Source", "tr": "hard_switch", "tau": 0.0, "src": "percussive", "ax": axes[0, 0]},
        {"title": "(b) Fast Crossfade (tau = 500ms) | Percussive Source", "tr": "crossfade", "tau": 0.5, "src": "percussive", "ax": axes[0, 1]},
        {"title": "(c) Slow Crossfade (tau = 1000ms) | Speech Bursts", "tr": "crossfade", "tau": 1.0, "src": "speech_bursts", "ax": axes[1, 0]},
        {"title": "(d) Hard-Switch (tau = 0ms) | Harmonic Drone", "tr": "hard_switch", "tau": 0.0, "src": "drone", "ax": axes[1, 1]}
    ]
    
    for case in plot_cases:
        ax = case['ax']
        # Find matching item
        match = next(t for t in trajectories_to_plot if t['trans_type'] == case['tr'] and t['tau'] == case['tau'] and t['source'] == case['src'])
        er = match['eval_res']
        
        t = er['frame_times']
        est = er['estimated_t60']
        gt = er['gt_t60']
        
        ax.plot(t, gt, 'k--', label='Ground Truth T60(t)', linewidth=2.0)
        ax.plot(t, est, 'b-', label='Causal Estimator (Ours)', linewidth=1.8)
        
        # Mark transition onset
        ax.axvline(x=2.5, color='r', linestyle=':', label='Transition Onset (t=2.5s)')
        if er['first_event_time'] > 2.5:
            ax.axvline(x=er['first_event_time'], color='g', linestyle='-.', alpha=0.8, 
                       label=f"1st Event (t={er['first_event_time']:.2f}s, Gap={er['first_event_time']-2.5:.2f}s)")
            
        # Target tolerance band (+/-15%)
        target = er['target_t60']
        ax.axhspan(target * 0.85, target * 1.15, color='gray', alpha=0.15, label='+/-15% Settling Band')
        
        ax.set_title(case['title'], fontsize=11, fontweight='bold')
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Reverberation Time T60 (s)")
        ax.set_ylim([0.0, 2.0])
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left', fontsize=8)
        
    plt.tight_layout()
    fig1_path = "research/figures/dynamic_tracking_trajectories.png"
    plt.savefig(fig1_path, dpi=300)
    plt.close()
    print(f"Generated Figure 1: {fig1_path}")
    
    # -------------------------------------------------------------------------
    # FIGURE 2: Instantaneous vs Event-Conditioned Lag (Observability Gap)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Aggregate across sources
    percussive_rows = [r for r in results if r['source_type'] == 'percussive']
    speech_rows = [r for r in results if r['source_type'] == 'speech_bursts']
    drone_rows = [r for r in results if r['source_type'] == 'drone']
    
    categories = ['Percussive\n(High Observability)', 'Speech Bursts\n(Periodic Pauses)', 'Harmonic Drone\n(Continuous/Low)']
    
    instant_means = [np.mean([r['t_settle_instant_s'] for r in percussive_rows]),
                     np.mean([r['t_settle_instant_s'] for r in speech_rows]),
                     np.mean([r['t_settle_instant_s'] for r in drone_rows])]
                     
    adapt_means = [np.mean([r['delta_t_adapt_s'] for r in percussive_rows]),
                   np.mean([r['delta_t_adapt_s'] for r in speech_rows]),
                   np.mean([r['delta_t_adapt_s'] for r in drone_rows])]
                   
    gap_means = [np.mean([r['observability_gap_s'] for r in percussive_rows]),
                 np.mean([r['observability_gap_s'] for r in speech_rows]),
                 np.mean([r['observability_gap_s'] for r in drone_rows])]
                 
    x = np.arange(len(categories))
    width = 0.28
    
    ax.bar(x - width, instant_means, width, label='Instantaneous Settling Lag (t_settle)', color='#e74c3c')
    ax.bar(x, adapt_means, width, label='Event-Conditioned Lag (Delta t_adapt)', color='#2ecc71')
    ax.bar(x + width, gap_means, width, label='Observability Latency Gap (Delta t_gap)', color='#3498db')
    
    ax.set_ylabel("Latency / Lag Duration (seconds)", fontsize=11)
    ax.set_title("Impact of Acoustic Observability on Causal Adaptation Latency\n(Instantaneous vs Event-Conditioned Formulation)", fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(fontsize=10)
    
    for i in range(len(categories)):
        ax.text(x[i] - width, instant_means[i] + 0.05, f"{instant_means[i]:.2f}s", ha='center', fontsize=9)
        ax.text(x[i], adapt_means[i] + 0.05, f"{adapt_means[i]:.2f}s", ha='center', fontsize=9, fontweight='bold')
        ax.text(x[i] + width, gap_means[i] + 0.05, f"{gap_means[i]:.2f}s", ha='center', fontsize=9)
        
    ax.set_ylim([0, 4.5])
    plt.tight_layout()
    fig2_path = "research/figures/lag_vs_observability.png"
    plt.savefig(fig2_path, dpi=300)
    plt.close()
    print(f"Generated Figure 2: {fig2_path}")
    
    # -------------------------------------------------------------------------
    # FIGURE 3: Directional Transition Asymmetry (Dry->Wet vs Wet->Dry)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    
    dry_to_wet = [r for r in results if r['room_pair'] == "Small -> Large"]
    wet_to_dry = [r for r in results if r['room_pair'] == "Large -> Small"]
    
    d2w_adapt = [r['delta_t_adapt_s'] for r in dry_to_wet]
    w2d_adapt = [r['delta_t_adapt_s'] for r in wet_to_dry]
    
    labels = ['Dry -> Wet\n(Room 1 [0.16s] -> Room 8 [1.54s])', 'Wet -> Dry (Acoustic Memory)\n(Room 8 [1.54s] -> Room 2 [0.29s])']
    means = [np.mean(d2w_adapt), np.mean(w2d_adapt)]
    stds = [np.std(d2w_adapt), np.std(w2d_adapt)]
    
    bars = ax.bar(labels, means, yerr=stds, capsize=8, color=['#3498db', '#e67e22'], width=0.5)
    ax.set_ylabel("Adaptation Lag Delta t_adapt (seconds)", fontsize=11)
    ax.set_title("Directional Acoustic Asymmetry: Lingering Energy Hysteresis\n(Wet->Dry transitions experience lingering reverberant tails)", fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.08, f"{yval:.2f} s", ha='center', va='bottom', fontweight='bold')
        
    ax.set_ylim([0, max(means) * 1.5])
    plt.tight_layout()
    fig3_path = "research/figures/directional_asymmetry_analysis.png"
    plt.savefig(fig3_path, dpi=300)
    plt.close()
    print(f"Generated Figure 3: {fig3_path}")
    
    # Print Summary Table
    print("\n" + "=" * 80)
    print("PHASE 1 SUMMARY STATISTICS BY TRANSITION TYPE")
    print("=" * 80)
    for tr in transitions:
        sub = [r for r in results if r['transition_type'] == tr['type'] and r['transition_tau_s'] == tr['duration']]
        mae_m = np.mean([r['mae_s'] for r in sub])
        rmse_m = np.mean([r['rmse_s'] for r in sub])
        rel_m = np.mean([r['rel_error_pct'] for r in sub])
        adapt_m = np.mean([r['delta_t_adapt_s'] for r in sub])
        print(f"{tr['label']:<32} | MAE: {mae_m:.3f}s | RMSE: {rmse_m:.3f}s | RelErr: {rel_m:.1f}% | Adapt Lag: {adapt_m:.2f}s")
        
    print("\n" + "=" * 80)
    print("PHASE 1 SUMMARY STATISTICS BY SOURCE FAMILY")
    print("=" * 80)
    for src in sources:
        sub = [r for r in results if r['source_type'] == src['type']]
        mae_m = np.mean([r['mae_s'] for r in sub])
        rmse_m = np.mean([r['rmse_s'] for r in sub])
        rel_m = np.mean([r['rel_error_pct'] for r in sub])
        adapt_m = np.mean([r['delta_t_adapt_s'] for r in sub])
        gap_m = np.mean([r['observability_gap_s'] for r in sub])
        print(f"{src['label']:<36} | MAE: {mae_m:.3f}s | RelErr: {rel_m:.1f}% | Adapt Lag: {adapt_m:.2f}s | Obs Gap: {gap_m:.2f}s")
    print("=" * 80)

if __name__ == '__main__':
    main()

