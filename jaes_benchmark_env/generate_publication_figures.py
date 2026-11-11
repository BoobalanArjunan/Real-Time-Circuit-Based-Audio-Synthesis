import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

os.environ['MPLCONFIGDIR'] = '/tmp/mpl_cache'
os.makedirs('jaes_benchmark_env/figures', exist_ok=True)

# Set clean publication style
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['xtick.labelsize'] = 8.5
plt.rcParams['ytick.labelsize'] = 8.5
plt.rcParams['legend.fontsize'] = 8.5
plt.rcParams['figure.titlesize'] = 12

# ==========================================
# Figure 1: MNA AudioWorklet Pipeline Diagram
# ==========================================
fig, ax = plt.subplots(figsize=(7, 2.5), dpi=300)
ax.axis('off')

# Boxes
bbox_props = dict(boxstyle="round,pad=0.5", fc="#f0f4f8", ec="#004488", lw=1.5)
bbox_hl = dict(boxstyle="round,pad=0.5", fc="#e1effe", ec="#0066cc", lw=2)

ax.text(0.12, 0.6, "Audio Block In\n(128 samples\n@ 48 kHz)", ha="center", va="center", bbox=bbox_props)
ax.text(0.42, 0.6, "2x Discrete-Time MNA\nNewton–Raphson Solver\n(96 kHz Internal Rate)", ha="center", va="center", bbox=bbox_hl)
ax.text(0.75, 0.6, "Half-Band Decimation\nFIR Filter (23-tap)\n(Downsample to 48 kHz)", ha="center", va="center", bbox=bbox_props)
ax.text(0.95, 0.6, "Audio Out\n(128 samples\n@ 48 kHz)", ha="center", va="center", bbox=bbox_props)

# In-place state box
bbox_state = dict(boxstyle="square,pad=0.4", fc="#fef3c7", ec="#d97706", lw=1.5)
ax.text(0.42, 0.15, "In-Place Parameter Updates (60 Hz)\nPreserves Reactive States S1 (v) & S2 (i)", ha="center", va="center", bbox=bbox_state)

# Arrows
ax.annotate("", xy=(0.26, 0.6), xytext=(0.19, 0.6), arrowprops=dict(arrowstyle="->", lw=1.5, color="#333"))
ax.annotate("", xy=(0.60, 0.6), xytext=(0.58, 0.6), arrowprops=dict(arrowstyle="->", lw=1.5, color="#333"))
ax.annotate("", xy=(0.89, 0.6), xytext=(0.87, 0.6), arrowprops=dict(arrowstyle="->", lw=1.5, color="#333"))
ax.annotate("", xy=(0.42, 0.44), xytext=(0.42, 0.28), arrowprops=dict(arrowstyle="->", lw=1.5, color="#d97706"))

plt.title("Figure 1: High-Performance Discrete-Time MNA AudioWorklet Pipeline", fontsize=11, fontweight="bold", pad=10)
plt.tight_layout()
plt.savefig("jaes_benchmark_env/figures/figure1_pipeline.png")
plt.savefig("jaes_benchmark_env/figures/figure1_pipeline.pdf")
plt.close()
print("Figure 1 generated.")

# ==========================================
# Figure 2: Compute Duration vs Budget
# ==========================================
fig, ax = plt.subplots(figsize=(6.5, 3.5), dpi=300)

circuits = ['RC High-Pass', 'Half-Wave Rectifier', 'Fuzz Distortion']
poly_1 = [99.6, 160.5, 180.8]
poly_2 = [158.7, 283.0, 322.0]
poly_4 = [274.9, 530.9, 612.7]
poly_4_max = [915.5, 704.5, 1704.7]
baseline_4 = [55.9, 55.1, 55.2]

x = np.arange(len(circuits))
width = 0.18

rects1 = ax.bar(x - 1.5*width, poly_1, width, label='MNA 1 Voice (Mean)', color='#93c5fd')
rects2 = ax.bar(x - 0.5*width, poly_2, width, label='MNA 2 Voices (Mean)', color='#3b82f6')
rects3 = ax.bar(x + 0.5*width, poly_4, width, label='MNA 4 Voices (Mean)', color='#1d4ed8')
rects4 = ax.bar(x + 1.5*width, baseline_4, width, label='Matched Baseline 4V', color='#9ca3af')

# Peak transient markers for 4V
ax.scatter(x + 0.5*width, poly_4_max, color='#b91c1c', marker='D', s=45, label='MNA 4V Worst-Case Peak', zorder=5)

# 2.67 ms Audio Block Budget Line
ax.axhline(2666.67, color='#dc2626', linestyle='--', lw=1.5, label='Audio Block Deadline (2,666.7 µs)')
ax.text(1.0, 2730, 'Real-Time Audio Deadline Budget (128 samples @ 48 kHz)', color='#dc2626', fontweight='bold', fontsize=8.5, ha='center')

ax.set_ylabel('Execution Duration per Block (µs)')
ax.set_title('Figure 2: Steady-State Execution Latency Across Circuits and Polyphony (Apple M1 Max)', fontweight='bold', pad=12)
ax.set_xticks(x)
ax.set_xticklabels(circuits, fontweight='bold')
ax.set_ylim(0, 3000)
ax.grid(True, linestyle=':', alpha=0.6, axis='y')
ax.legend(loc='upper left', framealpha=0.95, ncol=2)

plt.tight_layout()
plt.savefig("jaes_benchmark_env/figures/figure2_polyphony.png")
plt.savefig("jaes_benchmark_env/figures/figure2_polyphony.pdf")
plt.close()
print("Figure 2 generated.")

# ==========================================
# Figure 3: Storage Scaling (Logarithmic)
# ==========================================
fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=300)

categories = [
    'NodalSynth Pro\n61 Netlists',
    'Compressed Audio\n(96–128 kbps)',
    'Modeled Minimal\nPCM (15 notes x 3z)',
    'Modeled Standard\nPCM (24 notes x 3z)',
    'Modeled Chromatic\nPCM (88 notes x 3z)'
]
sizes_mb = [0.07737, 82.5, 1054.08, 1686.53, 6183.94]
colors = ['#059669', '#d97706', '#2563eb', '#1d4ed8', '#1e3a8a']

bars = ax.bar(categories, sizes_mb, color=colors, width=0.55, edgecolor='#1f2937', lw=1)
ax.set_yscale('log')
ax.set_ylabel('Storage Footprint (MB, Log Scale)')
ax.set_title('Figure 3: Persistent Asset Storage Footprint: Physical Netlists vs. Multi-Sample Banks', fontweight='bold', pad=12)
ax.set_ylim(0.01, 20000)
ax.grid(True, which='both', linestyle=':', alpha=0.5, axis='y')

# Labels on top of bars
labels = ['81.1 KB\n(1.0x)', '70–95 MB\n(~1,000x)', '1.05 GB\n(12,992x)', '1.69 GB\n(20,788x)', '6.18 GB\n(76,223x)']
for bar, label in zip(bars, labels):
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval * 1.5, label, ha='center', va='bottom', fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig("jaes_benchmark_env/figures/figure3_storage.png")
plt.savefig("jaes_benchmark_env/figures/figure3_storage.pdf")
plt.close()
print("Figure 3 generated.")
