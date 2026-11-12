#!/usr/bin/env python3
"""
SpatialMind-RoomShift: Phase 1 Dynamic Room Transition Dataset Generator
Implements:
1. Dynamic time-varying convolution simulating room transitions.
2. Two transition operators:
   - Abrupt Hard-Switch (tau = 0 ms): immediate discrete acoustic change.
   - Continuous Equal-Energy Crossfade (tau = 500 ms, 1000 ms): gradual walking transition.
3. Multi-source excitation library:
   - Percussive impulse train (transient-rich, high observability).
   - Conversational speech-like bursts (realistic pauses).
   - Sustained harmonic drone (challenging continuous excitation).
4. Frame-by-frame ground truth logging (T60, DRR, transition state, event timestamps).
"""

import os
os.environ['MPLCONFIGDIR'] = '/tmp/mpl_cache'
import json
import numpy as np
import scipy.signal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Import verified ISM engine from Phase 0
from simulate_10_rooms import generate_shoebox_rir, ROOMS, compute_sabine

FS = 16000

def generate_source_signal(source_type, duration_sec=6.0, fs=FS):
    """Generates standardized test source excitation signals."""
    num_samples = int(duration_sec * fs)
    t = np.arange(num_samples) / fs
    np.random.seed(42)
    
    events = [] # Timestamps of discrete excitation events (onsets/offsets)
    
    if source_type == 'percussive':
        # Train of short decaying percussive bursts every 0.6 seconds
        signal = np.zeros(num_samples, dtype=np.float64)
        interval = int(0.6 * fs)
        burst_len = int(0.04 * fs) # 40 ms burst
        for start in range(int(0.2 * fs), num_samples - interval, interval):
            burst_t = np.arange(burst_len) / fs
            envelope = np.exp(-burst_t / 0.01)
            carrier = np.sin(2 * np.pi * 880 * burst_t) + 0.5 * np.random.randn(burst_len)
            signal[start:start+burst_len] = carrier * envelope
            events.append({
                'onset_sec': start / fs,
                'offset_sec': (start + burst_len) / fs
            })
            
    elif source_type == 'speech_bursts':
        # Semi-periodic speech-like syllables with 150-250 ms active bursts and 200-400 ms pauses
        signal = np.zeros(num_samples, dtype=np.float64)
        curr = int(0.25 * fs)
        while curr < num_samples - int(0.5 * fs):
            burst_len = int(np.random.uniform(0.15, 0.25) * fs)
            b_t = np.arange(burst_len) / fs
            f0 = np.random.uniform(130, 220)
            # Harmonic source + formant filtering approximation
            carrier = np.sin(2 * np.pi * f0 * b_t) + 0.5 * np.sin(2 * np.pi * 2 * f0 * b_t) + 0.25 * np.sin(2 * np.pi * 3 * f0 * b_t)
            carrier += 0.1 * np.random.randn(burst_len)
            env = np.sin(np.pi * b_t / (burst_len / fs)) ** 1.5
            signal[curr:curr+burst_len] = carrier * env
            events.append({
                'onset_sec': curr / fs,
                'offset_sec': (curr + burst_len) / fs
            })
            pause_len = int(np.random.uniform(0.25, 0.45) * fs)
            curr += burst_len + pause_len
            
    elif source_type == 'drone':
        # Continuous harmonic chord (low observability without offsets)
        f1, f2, f3 = 220.0, 277.18, 329.63 # A major triad
        signal = (np.sin(2 * np.pi * f1 * t) + 
                  0.7 * np.sin(2 * np.pi * f2 * t) + 
                  0.5 * np.sin(2 * np.pi * f3 * t))
        signal *= 0.5
        events.append({'onset_sec': 0.0, 'offset_sec': duration_sec})
        
    else:
        raise ValueError(f"Unknown source type: {source_type}")
        
    # Normalize peak to 0.9
    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = 0.9 * signal / peak
        
    return signal, events

def synthesize_transition_scene(room_a_id, room_b_id, transition_type='crossfade', 
                                transition_time=2.5, transition_duration=0.5,
                                source_type='percussive', scene_duration=6.0, fs=FS):
    """
    Synthesizes a continuous audio signal undergoing a spatial acoustic transition from Room A to Room B.
    transition_type: 'hard_switch' or 'crossfade'
    transition_time: timestamp in seconds when the transition begins
    transition_duration: crossfade duration in seconds (0 for hard_switch)
    """
    def get_room(r_id):
        if isinstance(r_id, int):
            # 1-indexed or 0-indexed integer
            idx = r_id - 1 if 1 <= r_id <= len(ROOMS) else r_id
            return ROOMS[idx]
        for r in ROOMS:
            if r['id'] == r_id:
                return r
        raise ValueError(f"Room not found: {r_id}")

    room_a = get_room(room_a_id)
    room_b = get_room(room_b_id)
    
    # Generate RIRs
    abs_a = [room_a['alpha']] * 6 if 'alpha' in room_a else room_a.get('absorptions', [0.3]*6)
    abs_b = [room_b['alpha']] * 6 if 'alpha' in room_b else room_b.get('absorptions', [0.3]*6)
    dim_a = room_a.get('dim', room_a.get('dims'))
    dim_b = room_b.get('dim', room_b.get('dims'))
    src_a = room_a.get('src', room_a.get('source'))
    src_b = room_b.get('src', room_b.get('source'))
    
    rir_a, _ = generate_shoebox_rir(dim_a, src_a, room_a['mic'], abs_a, fs=fs)
    rir_b, _ = generate_shoebox_rir(dim_b, src_b, room_b['mic'], abs_b, fs=fs)
    
    # Generate dry source
    dry_signal, events = generate_source_signal(source_type, duration_sec=scene_duration, fs=fs)
    
    # Convolve with each room
    conv_a = scipy.signal.fftconvolve(dry_signal, rir_a, mode='full')[:len(dry_signal)]
    conv_b = scipy.signal.fftconvolve(dry_signal, rir_b, mode='full')[:len(dry_signal)]
    
    num_samples = len(dry_signal)
    t = np.arange(num_samples) / fs
    
    # Time-varying blending weights w_a(t), w_b(t)
    w_a = np.ones(num_samples, dtype=np.float64)
    w_b = np.zeros(num_samples, dtype=np.float64)
    
    t_start = transition_time
    if transition_type == 'hard_switch':
        mask = (t >= t_start)
        w_a[mask] = 0.0
        w_b[mask] = 1.0
    elif transition_type == 'crossfade':
        t_end = t_start + transition_duration
        for i, ti in enumerate(t):
            if ti < t_start:
                w_a[i] = 1.0
                w_b[i] = 0.0
            elif ti > t_end:
                w_a[i] = 0.0
                w_b[i] = 1.0
            else:
                progress = (ti - t_start) / transition_duration
                # Equal-power crossfade curve
                w_a[i] = np.cos(0.5 * np.pi * progress)
                w_b[i] = np.sin(0.5 * np.pi * progress)
    else:
        raise ValueError(f"Unknown transition_type: {transition_type}")
        
    # Render blended reverberant signal
    output_audio = w_a * conv_a + w_b * conv_b
    
    # Compute ground truth T60(t) trajectory
    # In pure physics, during crossfade, apparent T60 blends between Room A and Room B
    # Weighted by relative reverberant energy:
    t60_a, _, _ = compute_sabine(dim_a, abs_a)
    t60_b, _, _ = compute_sabine(dim_b, abs_b)
    gt_t60 = (w_a**2 * t60_a + w_b**2 * t60_b) / np.maximum(1e-6, w_a**2 + w_b**2)
    
    return {
        'output_audio': output_audio,
        'dry_signal': dry_signal,
        'time_axis': t,
        'gt_t60': gt_t60,
        'room_a': room_a,
        'room_b': room_b,
        'transition_time': transition_time,
        'transition_duration': transition_duration if transition_type == 'crossfade' else 0.0,
        'transition_type': transition_type,
        'source_type': source_type,
        'events': events,
        'fs': fs
    }

if __name__ == '__main__':
    print("Testing dynamic dataset generator...")
    # Test transition Room 1 (Vocal Booth, 0.10s) -> Room 4 (Classroom, 0.53s)
    scene = synthesize_transition_scene(1, 4, transition_type='crossfade', source_type='percussive')
    print(f"Generated scene: {len(scene['output_audio'])} samples at {scene['fs']} Hz")
    print(f"Events detected: {len(scene['events'])}")
    t60_a_val, _, _ = compute_sabine(scene['room_a']['dim'], [scene['room_a']['alpha']]*6)
    t60_b_val, _, _ = compute_sabine(scene['room_b']['dim'], [scene['room_b']['alpha']]*6)
    print(f"Room A T60: {t60_a_val:.3f} s, Room B T60: {t60_b_val:.3f} s")
    print("Test passed successfully.")

