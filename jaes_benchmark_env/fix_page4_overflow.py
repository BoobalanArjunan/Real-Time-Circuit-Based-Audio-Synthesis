import os, zipfile

workspace_dir = '/Users/mymac/Desktop/Ai 2026 Work/Antigravity Works/ Real-Time Circuit-Based-Exrtended/jaes_benchmark_env'
tex_path = os.path.join(workspace_dir, 'OVERLEAF_COPY_PASTE.tex')

with open(tex_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Clean Section 3.4 to permanently eliminate left-column overflow into the right column
old_s34 = r'''\subsection{Oversampling and Anti-Aliasing Filtering}
To attenuate non-linear aliasing harmonics, the MNA solver executes with internal $2\times$ oversampling ($f_{\text{internal}} = 96\text{ kHz}$ for a $48\text{ kHz}$ audio output). Each audio step solves two internal sub-samples, which are filtered and downsampled using a 23-tap (22nd-order) Blackman-windowed half-band polyphase FIR decimation filter:
\begin{equation}
H(z) = \sum_{k=0}^{22} h[k] \, z^{-k}
\end{equation}
The decimation filter is a 23-tap (order 22) linear-phase Type-I half-band FIR filter centered at index $k=11$ ($h[11] = 0.5$). The impulse response satisfies the half-band zero condition at non-central even offsets, with non-zero odd-offset coefficients ($m \in \{0, 1, 2, 3, 4, 5\}$) computed from windowed sinc prototypes:
\begin{equation}
h[11 + 2m] = 0 \quad (1 \le |m| \le 5), \qquad h[11 \pm (2m+1)] = \frac{(-1)^m}{\pi (2m+1)} \cdot w[m]
\end{equation}
where $w[m]$ denotes the 12-point symmetric Blackman window:
\begin{equation}
w[m] = 0.42 + 0.5 \cos\left(\frac{\pi(2m+1)}{12}\right) + 0.08 \cos\left(\frac{2\pi(2m+1)}{12}\right)
\end{equation}
normalized such that $\sum_{k=0}^{22} h[k] = 1$. This half-band structure identically eliminates half of the multiplication operations during polyphase decimation.'''

new_s34 = r'''\subsection{Oversampling and Anti-Aliasing Filtering}
To attenuate non-linear aliasing harmonics, the MNA solver executes with internal $2\times$ oversampling ($f_{\text{internal}} = 96\text{ kHz}$ for a $48\text{ kHz}$ audio output). Each audio step solves two internal sub-samples, which are filtered and downsampled using a 23-tap (22nd-order) Blackman-windowed half-band polyphase FIR decimation filter:
\begin{equation}
H(z) = \sum_{k=0}^{22} h[k] \, z^{-k}
\end{equation}
The filter is a linear-phase Type-I half-band FIR filter centered at $k=11$ ($h[11] = 0.5$). The impulse response satisfies the half-band zero condition $h[11 + 2m] = 0$ for $1 \le |m| \le 5$. The non-zero odd-offset coefficients ($m \in \{0, 1, 2, 3, 4, 5\}$) are evaluated from windowed sinc prototypes:
\begin{equation}
h[11 \pm (2m+1)] = \frac{(-1)^m}{\pi (2m+1)} \cdot w[m]
\end{equation}
where $w[m]$ is the 12-point symmetric Blackman window:
\begin{equation}
\begin{aligned}
w[m] &= 0.42 + 0.5 \cos\left(\frac{\pi(2m+1)}{12}\right) \\
&\quad + 0.08 \cos\left(\frac{2\pi(2m+1)}{12}\right)
\end{aligned}
\end{equation}
normalized such that $\sum_{k=0}^{22} h[k] = 1$. This half-band structure identically eliminates half of the multiplication operations during polyphase decimation.'''

if old_s34 in content:
    content = content.replace(old_s34, new_s34)
    print("Section 3.4 replaced with overflow-free aligned equations.")
else:
    print("WARNING: old_s34 block not matched exactly, finding via range...")
    idx_s34_start = content.find(r'\subsection{Oversampling and Anti-Aliasing Filtering}')
    idx_fig1 = content.find(r'\begin{figure}[t]', idx_s34_start)
    content = content[:idx_s34_start] + new_s34 + '\n\n' + content[idx_fig1:]
    print("Section 3.4 replaced via range.")

# 2. Clean Section 4.3 in the right column
old_s43 = r'''\subsection{Matched Multi-Zone Sample-Crossfade Baseline}
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

new_s43 = r'''\subsection{Matched Multi-Zone Sample-Crossfade Baseline}
To establish a realistic baseline, the MNA solver was benchmarked against a defined \textbf{3-Zone Parameter-Smoothed Sample-Crossfade Baseline Engine}:

\noindent\textbf{1. Reference Audio:} 24-bit/48~kHz audio rendered from the MNA circuit at three anchor states: Zone 1 ($940\,\Omega$), Zone 2 ($11,750\,\Omega$), and Zone 3 ($23,500\,\Omega$). 24-bit depth maximizes dynamic range and eliminates quantization noise.

\noindent\textbf{2. Equal-Power Crossfade Curve:} Piecewise crossfade across adjacent parameter zones:
\begin{equation}
\begin{aligned}
y_{\text{sample}}[n] &= \cos(\theta) \, s_A[n] + \sin(\theta) \, s_B[n] \\
\theta &= \frac{\pi}{2} \cdot \frac{p - p_A}{p_B - p_A}
\end{aligned}
\end{equation}

\noindent\textbf{3. Continuous Parameter Smoothing:} Single-pole filter ($f_c = 30\text{ Hz}$, $\alpha = 1 - e^{-2\pi f_c / f_s} \approx 0.00392$):
\begin{equation}
R_{\text{smooth}}[n] = (1 - \alpha) \, R_{\text{smooth}}[n-1] + \alpha \, R_{\text{target}}[n]
\end{equation}

\noindent\textbf{4. Interpolation:} Cubic-Hermite polynomial interpolation.'''

if old_s43 in content:
    content = content.replace(old_s43, new_s43)
    print("Section 4.3 aligned with two-line crossfade equation.")

# Write to all 3 tex files
for fname in ['OVERLEAF_COPY_PASTE.tex', 'jaes_manuscript.tex', 'jaes_manuscript_official.tex']:
    p = os.path.join(workspace_dir, fname)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Saved:", p)

# Re-bundle zip package
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

print("Package zip successfully re-bundled!")

