import os
os.environ['MPLCONFIGDIR'] = '/tmp/mpl_cache'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

os.makedirs('jaes_benchmark_env/figures', exist_ok=True)

# Publication typography standards for JAES (AES / IEEE transactions style)
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 8.5
plt.rcParams['axes.labelsize'] = 8.5
plt.rcParams['axes.titlesize'] = 9.0
plt.rcParams['xtick.labelsize'] = 7.5
plt.rcParams['ytick.labelsize'] = 8.0
plt.rcParams['legend.fontsize'] = 7.0
plt.rcParams['figure.titlesize'] = 9.5

# ==========================================
# Figure 1: MNA AudioWorklet Pipeline Diagram
# ==========================================
fig, ax = plt.subplots(figsize=(7.0, 2.2), dpi=300)
ax.axis('off')

bbox_props = dict(boxstyle="round,pad=0.4", fc="#f8fafc", ec="#334155", lw=1.1)
bbox_hl = dict(boxstyle="round,pad=0.4", fc="#eff6ff", ec="#1d4ed8", lw=1.6)
bbox_state = dict(boxstyle="square,pad=0.35", fc="#fffbeb", ec="#b45309", lw=1.2)

ax.text(0.11, 0.64, "Audio Block In\n(128 samples\n@ 48 kHz)", ha="center", va="center", bbox=bbox_props)
ax.text(0.41, 0.64, "2x Discrete-Time MNA\nNewton–Raphson Solver\n(96 kHz Internal Rate)", ha="center", va="center", bbox=bbox_hl)
ax.text(0.73, 0.64, "Polyphase Decimation\n23-Tap FIR (Order 22)\n(Downsample to 48 kHz)", ha="center", va="center", bbox=bbox_props)
ax.text(0.95, 0.64, "Audio Out\n(128 samples\n@ 48 kHz)", ha="center", va="center", bbox=bbox_props)

# In-place state box
ax.text(0.41, 0.16, "In-Place Parameter Updates (60 Hz)\nPreserves Reactive States S1 (v) & S2 (i)", ha="center", va="center", bbox=bbox_state)

# Signal flow arrows
ax.annotate("", xy=(0.25, 0.64), xytext=(0.18, 0.64), arrowprops=dict(arrowstyle="->", lw=1.3, color="#1e293b"))
ax.annotate("", xy=(0.59, 0.64), xytext=(0.57, 0.64), arrowprops=dict(arrowstyle="->", lw=1.3, color="#1e293b"))
ax.annotate("", xy=(0.87, 0.64), xytext=(0.85, 0.64), arrowprops=dict(arrowstyle="->", lw=1.3, color="#1e293b"))
ax.annotate("", xy=(0.41, 0.48), xytext=(0.41, 0.30), arrowprops=dict(arrowstyle="->", lw=1.3, color="#b45309"))

plt.tight_layout()
plt.savefig("jaes_benchmark_env/figures/figure1_pipeline.pdf", bbox_inches='tight')
plt.savefig("jaes_benchmark_env/figures/figure1_pipeline.png", bbox_inches='tight')
plt.close()
print("Figure 1 generated.")

# ==========================================
# Figure 2: Compute Duration vs Budget (Horizontal Layout - DAWBench Style)
# Dedicated legend outside plot area to eliminate ANY overlap
# ==========================================
fig, ax = plt.subplots(figsize=(6.8, 3.2), dpi=300)

circuits = ['RC High-Pass', 'Half-Wave Rectifier', 'Fuzz Distortion']
y = np.arange(len(circuits))
height = 0.18

poly_1 = [99.6, 160.5, 180.8]
poly_2 = [158.7, 283.0, 322.0]
poly_4 = [274.9, 530.9, 612.7]
baseline_4 = [55.9, 55.1, 55.2]
poly_4_max = [915.5, 704.5, 1704.7]

rects1 = ax.barh(y + 1.5*height, poly_1, height, label='Live MNA 1V', color='#93c5fd', edgecolor='#1e40af', lw=0.6)
rects2 = ax.barh(y + 0.5*height, poly_2, height, label='Live MNA 2V', color='#3b82f6', edgecolor='#1e40af', lw=0.6)
rects3 = ax.barh(y - 0.5*height, poly_4, height, label='Live MNA 4V', color='#1d4ed8', edgecolor='#1e40af', lw=0.6)
rects4 = ax.barh(y - 1.5*height, baseline_4, height, label='Sample Baseline 4V', color='#9ca3af', edgecolor='#374151', lw=0.6)

# Peak transient markers for 4V
ax.scatter(poly_4_max, y - 0.5*height, color='#b91c1c', marker='D', s=32, label='MNA 4V Worst-Case Peak', zorder=5)

# Single clean annotation for the maximum peak to highlight remaining headroom
ax.annotate('Worst-Case Transient Peak: 1,704.7 µs\n(36.07% Headroom Remaining)',
            xy=(1704.7, 2 - 0.5*height), xytext=(1780, 2 - 0.1),
            arrowprops=dict(arrowstyle="->", lw=0.8, color="#b91c1c"),
            fontsize=6.8, color="#b91c1c", fontweight='bold', va='center')

# Real-time Audio Block Deadline line (Vertical)
ax.axvline(2666.67, color='#dc2626', linestyle='--', lw=1.2)
ax.text(2680, -0.4, 'Block Deadline: 2,666.7 µs\n(128 samples @ 48 kHz)', color='#dc2626', fontsize=6.8, fontweight='bold', va='bottom')

ax.set_xlabel('Block Processing Duration (µs) on Apple M1 Max Host')
ax.set_yticks(y)
ax.set_yticklabels(circuits, fontweight='bold')
ax.set_xlim(0, 3100)
ax.set_ylim(-0.5, 2.7)
ax.invert_yaxis()
ax.grid(True, linestyle=':', alpha=0.5, axis='x')

# Clean legend positioned strictly at the top outside the chart area
ax.legend(loc='lower left', bbox_to_anchor=(0.0, 1.02, 1.0, 0.2), mode="expand",
          ncol=5, frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', framealpha=0.95,
          handletextpad=0.3, columnspacing=0.6, fontsize=6.8)

plt.tight_layout()
plt.savefig("jaes_benchmark_env/figures/figure2_polyphony.pdf", bbox_inches='tight')
plt.savefig("jaes_benchmark_env/figures/figure2_polyphony.png", bbox_inches='tight')
plt.close()
print("Figure 2 regenerated cleanly with external legend.")

# ==========================================
# Figure 3: Storage Scaling (Logarithmic)
# ==========================================
fig, ax = plt.subplots(figsize=(6.8, 3.2), dpi=300)

categories = [
    'MNA Netlists\n(61 Presets)',
    'Lossy Audio\n(Opus/AAC)',
    'Minimal PCM\n(15 notes × 3z)',
    'Standard PCM\n(24 notes × 3z)',
    'Chromatic PCM\n(88 notes × 3z)'
]
sizes_mb = [0.07737, 82.5, 1054.08, 1686.53, 6183.94]
colors = ['#059669', '#d97706', '#2563eb', '#1d4ed8', '#1e3a8a']

bars = ax.bar(categories, sizes_mb, color=colors, width=0.48, edgecolor='#1f2937', lw=0.8)
ax.set_yscale('log')
ax.set_ylabel('Persistent Storage Footprint (MB, Log Scale)')
ax.set_ylim(0.005, 120000)
ax.grid(True, which='both', linestyle=':', alpha=0.4, axis='y')

labels = [
    '81.1 KB\n(1.0× Ref)',
    '70–95 MB\n(~1,000×)',
    '1.05 GB\n(12,992×)',
    '1.69 GB\n(20,788×)',
    '6.18 GB\n(76,223×)'
]
for bar, label in zip(bars, labels):
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval * 1.5, label, ha='center', va='bottom', fontsize=7.2, fontweight='bold')

plt.tight_layout()
plt.savefig("jaes_benchmark_env/figures/figure3_storage.pdf", bbox_inches='tight')
plt.savefig("jaes_benchmark_env/figures/figure3_storage.png", bbox_inches='tight')
plt.close()
print("Figure 3 regenerated cleanly.")
