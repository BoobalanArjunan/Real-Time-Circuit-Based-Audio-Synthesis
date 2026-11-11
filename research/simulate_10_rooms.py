#!/usr/bin/env python3
"""
SpatialMind-RoomShift: Phase 0 10-Room Simulation and Acoustic Verification
Implements:
1. Image Source Method (Allen & Berkley 1979) for shoebox rooms in pure NumPy/SciPy.
2. Schroeder energy decay backward integration (Schroeder 1965).
3. T20 (-5 to -25 dB) and T30 (-5 to -35 dB) RT60 regression with R^2 fit quality.
4. Direct-to-Reverberant Ratio (DRR) with documented 2.5 ms direct-path window.
5. Analytical Sabine and Eyring RT60 cross-checks.
6. Verification quality gates and export to research/room_verification.csv.
"""

import os
os.environ['MPLCONFIGDIR'] = '/tmp/mpl_cache'
import json
import numpy as np
import scipy.signal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def compute_sabine(dimensions, absorption_coeffs):
    # dimensions: [L, W, H]
    # absorption_coeffs: [alpha_x1, alpha_x2, alpha_y1, alpha_y2, alpha_z1, alpha_z2]
    L, W, H = dimensions
    surfaces = [W*H, W*H, L*H, L*H, L*W, L*W]
    V = L * W * H
    A = sum(s * a for s, a in zip(surfaces, absorption_coeffs))
    c = 343.0
    # Sabine: T60 = 24 * ln(10) * V / (c * A) = 0.1611 * V / A
    t60_sabine = 0.1611 * V / A
    return t60_sabine, A, V

def compute_eyring(dimensions, absorption_coeffs):
    L, W, H = dimensions
    surfaces = [W*H, W*H, L*H, L*H, L*W, L*W]
    S = sum(surfaces)
    V = L * W * H
    A = sum(s * a for s, a in zip(surfaces, absorption_coeffs))
    mean_alpha = A / S
    if mean_alpha >= 1.0:
        return 0.0, mean_alpha
    t60_eyring = 0.1611 * V / (-S * np.log(1.0 - mean_alpha))
    return t60_eyring, mean_alpha

def generate_shoebox_rir(dimensions, source_pos, mic_pos, absorption_coeffs, max_order=15, fs=16000, max_duration=2.5):
    """
    Image Source Method for a 3D shoebox room.
    dimensions: [Lx, Ly, Lz]
    source_pos: [x, y, z]
    mic_pos: [x, y, z]
    absorption_coeffs: 6 walls [x1, x2, y1, y2, z1, z2]
    """
    c = 343.0
    Lx, Ly, Lz = dimensions
    num_samples = int(max_duration * fs)
    rir = np.zeros(num_samples, dtype=np.float64)
    
    # Reflection coefficients beta = sqrt(1 - alpha)
    betas = [np.sqrt(np.maximum(0.0, 1.0 - a)) for a in absorption_coeffs]
    beta_x1, beta_x2, beta_y1, beta_y2, beta_z1, beta_z2 = betas
    
    xs, ys, zs = source_pos
    xm, ym, zm = mic_pos
    
    for nx in range(-max_order, max_order + 1):
        for ny in range(-max_order, max_order + 1):
            for nz in range(-max_order, max_order + 1):
                # 8 image sources per cell
                for qx in (0, 1):
                    for qy in (0, 1):
                        for qz in (0, 1):
                            # Image coordinates
                            xi = 2 * nx * Lx + (-1)**qx * xs
                            yi = 2 * ny * Ly + (-1)**qy * ys
                            zi = 2 * nz * Lz + (-1)**qz * zs
                            
                            dist = np.sqrt((xi - xm)**2 + (yi - ym)**2 + (zi - zm)**2)
                            if dist < 1e-4:
                                continue
                            
                            arrival_time = dist / c
                            idx = int(np.round(arrival_time * fs))
                            if idx >= num_samples:
                                continue
                            
                            # Wall reflection counts
                            # x-reflections:
                            rx1 = abs(nx) if nx <= 0 else nx
                            rx2 = abs(nx) if nx >= 0 else -nx
                            if qx == 1:
                                rx1 += 1
                                
                            ry1 = abs(ny) if ny <= 0 else ny
                            ry2 = abs(ny) if ny >= 0 else -ny
                            if qy == 1:
                                ry1 += 1
                                
                            rz1 = abs(nz) if nz <= 0 else nz
                            rz2 = abs(nz) if nz >= 0 else -nz
                            if qz == 1:
                                rz1 += 1
                                
                            amp = (beta_x1**rx1 * beta_x2**rx2 *
                                   beta_y1**ry1 * beta_y2**ry2 *
                                   beta_z1**rz1 * beta_z2**rz2) / (4.0 * np.pi * dist)
                            
                            rir[idx] += amp
                            
    # Normalize direct arrival
    direct_dist = np.sqrt(sum((s - m)**2 for s, m in zip(source_pos, mic_pos)))
    return rir, direct_dist

def analyze_rir(rir, fs, direct_dist):
    c = 343.0
    direct_idx = int(np.round((direct_dist / c) * fs))
    direct_window_samples = int(0.0025 * fs) # 2.5 ms direct path window
    
    # 1. Direct-to-Reverberant Ratio (DRR)
    t_split = min(len(rir), direct_idx + direct_window_samples)
    energy_direct = np.sum(rir[:t_split]**2)
    energy_reverb = np.sum(rir[t_split:]**2)
    drr_db = 10.0 * np.log10(max(1e-12, energy_direct) / max(1e-12, energy_reverb))
    
    # 2. Schroeder backward energy integration
    energy = rir**2
    schroeder = np.cumsum(energy[::-1])[::-1]
    schroeder_db = 10.0 * np.log10(np.maximum(1e-12, schroeder) / np.max(schroeder))
    
    # Usable decay range
    noise_floor_db = schroeder_db[-1]
    usable_decay_db = -noise_floor_db
    
    time_axis = np.arange(len(rir)) / fs
    
    # Helper linear fit for T_eval
    def fit_segment(db_start, db_end):
        indices = np.where((schroeder_db <= db_start) & (schroeder_db >= db_end))[0]
        if len(indices) < 20:
            return None, 0.0
        t_seg = time_axis[indices]
        y_seg = schroeder_db[indices]
        # Linear regression: y = slope * t + intercept
        slope, intercept = np.polyfit(t_seg, y_seg, 1)
        # R^2 calculation
        y_pred = slope * t_seg + intercept
        ss_tot = np.sum((y_seg - np.mean(y_seg))**2)
        ss_res = np.sum((y_seg - y_pred)**2)
        r2 = 1.0 - (ss_res / (ss_tot + 1e-12))
        t60 = -60.0 / slope if slope < 0 else None
        return t60, r2
    
    t20_rt60, r2_t20 = fit_segment(-5.0, -25.0)
    t30_rt60, r2_t30 = fit_segment(-5.0, -35.0)
    
    return {
        "drr_db": drr_db,
        "usable_decay_db": usable_decay_db,
        "t20_rt60": t20_rt60,
        "r2_t20": r2_t20,
        "t30_rt60": t30_rt60,
        "r2_t30": r2_t30,
        "schroeder_db": schroeder_db,
        "time_axis": time_axis
    }

def main():
    np.random.seed(42)
    os.makedirs("research/figures", exist_ok=True)
    os.makedirs("research/rirs", exist_ok=True)
    
    # 10 Diverse Test Rooms spanning small, medium, and large volumes and varying absorption
    rooms_config = [
        {"id": "ROOM_01_SMALL_DRY", "dim": [3.2, 4.0, 2.6], "alpha": 0.55, "target_rt60": 0.25,
         "src": [1.0, 1.2, 1.4], "mic": [2.0, 2.5, 1.4]},
        {"id": "ROOM_02_STUDIO_MED", "dim": [5.0, 4.2, 2.8], "alpha": 0.40, "target_rt60": 0.38,
         "src": [1.5, 1.5, 1.2], "mic": [3.5, 2.8, 1.2]},
        {"id": "ROOM_03_OFFICE", "dim": [6.0, 5.0, 3.0], "alpha": 0.30, "target_rt60": 0.55,
         "src": [1.8, 1.8, 1.3], "mic": [4.2, 3.5, 1.3]},
        {"id": "ROOM_04_CLASSROOM", "dim": [7.5, 6.0, 3.2], "alpha": 0.25, "target_rt60": 0.72,
         "src": [2.0, 2.0, 1.5], "mic": [5.5, 4.5, 1.5]},
        {"id": "ROOM_05_MED_HALL", "dim": [9.0, 7.0, 3.8], "alpha": 0.22, "target_rt60": 0.95,
         "src": [2.5, 2.0, 1.6], "mic": [6.5, 5.0, 1.6]},
        {"id": "ROOM_06_RECITAL", "dim": [11.0, 8.5, 4.5], "alpha": 0.20, "target_rt60": 1.20,
         "src": [3.0, 2.5, 1.6], "mic": [8.0, 6.0, 1.6]},
        {"id": "ROOM_07_CHURCH_SMALL", "dim": [14.0, 10.0, 6.0], "alpha": 0.18, "target_rt60": 1.55,
         "src": [3.5, 3.0, 1.8], "mic": [10.5, 7.0, 1.8]},
        {"id": "ROOM_08_AUDITORIUM", "dim": [16.0, 12.0, 7.0], "alpha": 0.16, "target_rt60": 1.85,
         "src": [4.0, 3.5, 1.8], "mic": [12.0, 8.5, 1.8]},
        {"id": "ROOM_09_CAVERN_DRY", "dim": [18.0, 14.0, 8.0], "alpha": 0.35, "target_rt60": 1.40,
         "src": [4.5, 4.0, 2.0], "mic": [13.5, 10.0, 2.0]},
        {"id": "ROOM_10_CATHEDRAL", "dim": [20.0, 15.0, 9.0], "alpha": 0.14, "target_rt60": 2.30,
         "src": [5.0, 4.0, 2.0], "mic": [15.0, 11.0, 2.0]},
    ]
    
    fs = 16000 # 16 kHz as specified in master plan
    csv_rows = ["room_id,target_rt60,measured_t20_rt60,measured_t30_rt60,sabine_rt60,eyring_rt60,drr_db,fit_r2,usable_decay_db,rir_length_s,verification_status,reason"]
    
    results = []
    
    fig, axes = plt.subplots(5, 2, figsize=(14, 18))
    axes = axes.flatten()
    
    print("Executing Phase 0 10-Room Simulation and Quality Gate Audit...")
    print("-" * 80)
    
    for idx, cfg in enumerate(rooms_config):
        rid = cfg["id"]
        dim = cfg["dim"]
        alpha = cfg["alpha"]
        abs_coeffs = [alpha] * 6
        target_rt60 = cfg["target_rt60"]
        
        # Analytical Sabine & Eyring
        t60_sab, A, V = compute_sabine(dim, abs_coeffs)
        t60_eyr, mean_a = compute_eyring(dim, abs_coeffs)
        
        # Simulation duration: at least 1.5 * max(target, eyring)
        duration = max(1.5, min(3.5, 1.4 * t60_eyr))
        order = 12 if V < 200 else (15 if V < 1000 else 18)
        
        rir, d_dist = generate_shoebox_rir(dim, cfg["src"], cfg["mic"], abs_coeffs,
                                          max_order=order, fs=fs, max_duration=duration)
        
        analysis = analyze_rir(rir, fs, d_dist)
        t20 = analysis["t20_rt60"]
        t30 = analysis["t30_rt60"]
        r2 = analysis["r2_t30"] if analysis["r2_t30"] > 0 else analysis["r2_t20"]
        drr = analysis["drr_db"]
        usable_db = analysis["usable_decay_db"]
        
        # Quality Gate Check
        status = "PASSED"
        reasons = []
        if r2 < 0.95:
            status = "FAILED"
            reasons.append(f"Low R^2 fit ({r2:.3f} < 0.95)")
        if usable_db < 35.0:
            status = "WARNING"
            reasons.append(f"Decay dynamic range below 35 dB ({usable_db:.1f} dB)")
        if t30 is None:
            status = "FAILED"
            reasons.append("T30 decay segment could not be fitted")
            
        reason_str = "; ".join(reasons) if reasons else "Meets Schroeder fit & dynamic range thresholds"
        
        t20_str = f"{t20:.3f}" if t20 is not None else "N/A"
        t30_str = f"{t30:.3f}" if t30 is not None else "N/A"
        
        csv_rows.append(f"{rid},{target_rt60:.2f},{t20_str},{t30_str},{t60_sab:.3f},{t60_eyr:.3f},{drr:.2f},{r2:.4f},{usable_db:.1f},{duration:.2f},{status},{reason_str}")
        
        # Plot Schroeder decay curve
        ax = axes[idx]
        t_axis = analysis["time_axis"]
        sch_db = analysis["schroeder_db"]
        ax.plot(t_axis, sch_db, label="Schroeder Decay (dB)", color="#0066cc", lw=1.5)
        ax.axhline(-5, color="gray", linestyle="--", alpha=0.6)
        ax.axhline(-35, color="gray", linestyle="--", alpha=0.6)
        ax.set_title(f"{rid} (Vol: {V:.0f}m³, T30: {t30_str}s, Eyring: {t60_eyr:.2f}s)", fontsize=10, fontweight="bold")
        ax.set_xlabel("Time (s)", fontsize=8)
        ax.set_ylabel("Energy (dB)", fontsize=8)
        ax.set_ylim(-65, 5)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7, loc="upper right")
        
        print(f"[{status}] {rid:<20} | Target: {target_rt60:.2f}s | T30: {t30_str}s | Eyring: {t60_eyr:.2f}s | DRR: {drr:>5.1f} dB | R²: {r2:.4f}")
        
    plt.tight_layout()
    plot_path = "research/figures/room_decay_curves.png"
    plt.savefig(plot_path, dpi=200)
    plt.close()
    
    csv_path = "research/room_verification.csv"
    with open(csv_path, "w") as f:
        f.write("\n".join(csv_rows) + "\n")
        
    print("-" * 80)
    print(f"Saved room verification report to: {csv_path}")
    print(f"Saved 10-room decay plots to: {plot_path}")

if __name__ == "__main__":
    main()

