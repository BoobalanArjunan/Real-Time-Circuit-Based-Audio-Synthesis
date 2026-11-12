import os, zipfile

workspace_dir = '/Users/mymac/Desktop/Ai 2026 Work/Antigravity Works/ Real-Time Circuit-Based-Exrtended/jaes_benchmark_env'
tex_path = os.path.join(workspace_dir, 'OVERLEAF_COPY_PASTE.tex')

with open(tex_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Combine FIR equations in Section 3.4 to save 3 vertical lines on Page 4
old_fir_eqs = r'''The decimation filter is a 23-tap (order 22) linear-phase Type-I half-band FIR filter centered at index $k=11$ ($h[11] = 0.5$). The impulse response satisfies the half-band zero condition at non-central even offsets:
\begin{equation}
h[11 + 2m] = 0 \quad (1 \le |m| \le 5, \, m \in \mathbb{Z})
\end{equation}
The non-zero odd-offset coefficients $h[11 \pm (2m+1)]$ for $m \in \{0, 1, 2, 3, 4, 5\}$ are computed from windowed sinc prototypes:
\begin{equation}
h[11 \pm (2m+1)] = \frac{(-1)^m}{\pi (2m+1)} \cdot w[m]
\end{equation}'''

new_fir_eqs = r'''The decimation filter is a 23-tap (order 22) linear-phase Type-I half-band FIR filter centered at index $k=11$ ($h[11] = 0.5$). The impulse response satisfies the half-band zero condition at non-central even offsets, with non-zero odd-offset coefficients ($m \in \{0, 1, 2, 3, 4, 5\}$) computed from windowed sinc prototypes:
\begin{equation}
h[11 + 2m] = 0 \quad (1 \le |m| \le 5), \qquad h[11 \pm (2m+1)] = \frac{(-1)^m}{\pi (2m+1)} \cdot w[m]
\end{equation}'''

if old_fir_eqs in content:
    content = content.replace(old_fir_eqs, new_fir_eqs)
    print("FIR equations consolidated on single line (saved 3 lines on Page 4).")

# 2. Compact Section 4.1 and Section 4.3 so that Section 4.3 finishes completely on Page 4
old_s41_item = r'''\begin{itemize}
\item \textbf{Headless V8 Profiling:} To eliminate browser timer quantization (where Spectre/Meltdown security mitigations round \texttt{performance.now()} to 5--20~$\mu$s intervals), quantitative latency distributions were measured using \texttt{process.hrtime.bigint()} in a headless Node.js v24.5.0 environment executing the identical V8 JIT compilation pipeline.
\item \textbf{Browser AudioWorklet Verification:} In parallel, browser execution was verified in Chromium 157 using an interactive harness (\texttt{benchmark.html}) executing within an active \texttt{AudioWorkletProcessor} thread. This confirmed engine instantiation, thread-safety, and matching median block processing loads within timer quantization limits.
\end{itemize}'''

new_s41_item = r'''\begin{itemize}\setlength{\itemsep}{1.2pt}\setlength{\parsep}{0pt}
\item \textbf{Headless V8 Profiling:} To eliminate timer quantization (5--20~$\mu$s jitter in browser \texttt{performance.now()}), quantitative latency distributions were profiled via \texttt{process.hrtime.bigint()} in headless Node.js v24.5.0 executing the identical V8 JIT compilation pipeline.
\item \textbf{Browser AudioWorklet Verification:} In parallel, browser execution was verified in Chromium 157 via an interactive harness (\texttt{benchmark.html}) executing within an active \texttt{AudioWorkletProcessor} thread, confirming thread-safety and matching median loads.
\end{itemize}'''

if old_s41_item in content:
    content = content.replace(old_s41_item, new_s41_item)
    print("Section 4.1 profiling items compacted (saved 2 lines).")

# 3. Clean, indivisible Section 4.3 (Equations aligned, ZERO separation of tag and formula)
old_s43_block = r'''\subsection{Matched Multi-Zone Sample-Crossfade Baseline}
To establish a realistic baseline, the MNA solver was benchmarked against a defined \textbf{3-Zone Parameter-Smoothed Sample-Crossfade Baseline Engine}:

\noindent\textbf{1. Reference Audio:} 24-bit/48~kHz audio rendered directly from the MNA circuit at three anchor states: Zone 1 ($R = 940\,\Omega$), Zone 2 ($R = 11,750\,\Omega$), and Zone 3 ($R = 23,500\,\Omega$). 24-bit depth was chosen to maximize dynamic range and eliminate quantization noise in the reference material.

\noindent\textbf{2. Equal-Power Crossfade Curve:} Piecewise crossfading across adjacent parameter zones:
\begin{equation}
y_{\text{sample}}[n] = \cos(\theta) \, s_A[n] + \sin(\theta) \, s_B[n], \quad \theta = \frac{\pi}{2} \cdot \frac{p - p_A}{p_B - p_A}
\end{equation}

\noindent\textbf{3. Continuous Parameter Smoothing:} A single-pole low-pass filter ($f_c = 30\text{ Hz}$) applied to incoming parameter transitions:
\begin{equation}
R_{\text{smooth}}[n] = (1 - \alpha) \, R_{\text{smooth}}[n-1] + \alpha \, R_{\text{target}}[n]
\end{equation}
where $\alpha = 1 - \exp(-2\pi f_c / f_s) \approx 0.00392$.

\noindent\textbf{4. Interpolation:} Cubic-Hermite polynomial interpolation.'''

new_s43_block = r'''\subsection{Matched Multi-Zone Sample-Crossfade Baseline}
To establish a realistic baseline, the MNA solver was benchmarked against a defined \textbf{3-Zone Parameter-Smoothed Sample-Crossfade Baseline Engine}:

\noindent\textbf{1. Reference Audio:} 24-bit/48~kHz audio rendered directly from the MNA circuit at three anchor states: Zone 1 ($R = 940\,\Omega$), Zone 2 ($R = 11,750\,\Omega$), and Zone 3 ($R = 23,500\,\Omega$). 24-bit depth maximizes dynamic range and eliminates quantization noise.

\noindent\textbf{2. Equal-Power Crossfade Curve:} Piecewise crossfade across adjacent parameter zones:
\begin{equation}
y_{\text{sample}}[n] = \cos(\theta) \, s_A[n] + \sin(\theta) \, s_B[n], \quad \theta = \frac{\pi}{2} \cdot \frac{p - p_A}{p_B - p_A}
\end{equation}

\noindent\textbf{3. Continuous Parameter Smoothing:} Single-pole filter ($f_c = 30\text{ Hz}$, $\alpha = 1 - e^{-2\pi f_c / f_s} \approx 0.00392$):
\begin{equation}
R_{\text{smooth}}[n] = (1 - \alpha) \, R_{\text{smooth}}[n-1] + \alpha \, R_{\text{target}}[n]
\end{equation}

\noindent\textbf{4. Interpolation:} Cubic-Hermite polynomial interpolation.'''

if old_s43_block in content:
    content = content.replace(old_s43_block, new_s43_block)
    print("Section 4.3 smoothed and streamlined (formula and number guaranteed on single line).")

# Save to all 3 tex files
for fname in ['OVERLEAF_COPY_PASTE.tex', 'jaes_manuscript.tex', 'jaes_manuscript_official.tex']:
    p = os.path.join(workspace_dir, fname)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Saved:", p)

# Re-bundle submission zip
zip_path = os.path.join(workspace_dir, 'jaes_submission_package.zip')
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root_file in [
        'OVERLEAF_COPY_PASTE.tex',
        'jaes_manuscript.tex',
        'jaes_manuscript_official.tex',
        'references.bib',
        'jaes.bib',
        'headshot1.jpg',
        'boobalan.jpg',
        'figure1_pipeline.pdf',
        'figure1_pipeline.png',
        'figure2_polyphony.pdf',
        'figure2_polyphony.png',
        'figure3_storage.pdf',
        'figure3_storage.png'
    ]:
        p = os.path.join(workspace_dir, root_file)
        if os.path.exists(p):
            zipf.write(p, arcname=root_file)
            
    fig_dir = os.path.join(workspace_dir, 'figures')
    for f in os.listdir(fig_dir):
        fp = os.path.join(fig_dir, f)
        if os.path.isfile(fp):
            if f not in ['figure2_polyphony.pdf', 'figure2_polyphony.png']:
                zipf.write(fp, arcname=f'figures/{f}')

print("Package zip re-bundled successfully!")

