import os, zipfile

workspace_dir = '/Users/mymac/Desktop/Ai 2026 Work/Antigravity Works/ Real-Time Circuit-Based-Exrtended/jaes_benchmark_env'
tex_path = os.path.join(workspace_dir, 'OVERLEAF_COPY_PASTE.tex')

with open(tex_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix Equation 16: eliminate unusually long formula
old_eq16 = r'''\begin{equation}
V_T = \frac{k_B T_K}{q} \approx 25.85\text{ mV} \quad (\text{at } T_K = 300\text{ K},\, 25.26\text{ mV at } 293.15\text{ K})
\end{equation}
where $k_B = 1.380649 \times 10^{-23}\text{ J/K}$ is Boltzmann's constant, $T_K$ is absolute temperature, and $q = 1.60217663 \times 10^{-19}\text{ C}$ is elementary charge.'''

new_eq16 = r'''\begin{equation}
V_T = \frac{k_B T_K}{q} \approx 25.85\text{ mV}
\end{equation}
where $k_B = 1.380649 \times 10^{-23}\text{ J/K}$ is Boltzmann's constant, $T_K = 300\text{ K}$ is the operating temperature ($V_T \approx 25.26\text{ mV}$ at standard room temperature $293.15\text{ K}$), and $q = 1.60217663 \times 10^{-19}\text{ C}$ is elementary charge.'''

if old_eq16 in content:
    content = content.replace(old_eq16, new_eq16)
    print("Equation 16 successfully tightened and formatted cleanly.")
else:
    # Try alternate replacement
    idx_eq16 = content.find(r'V_T = \frac{k_B T_K}{q}')
    if idx_eq16 != -1:
        start_eq = content.rfind(r'\begin{equation}', 0, idx_eq16)
        end_eq = content.find(r'elementary charge.', idx_eq16) + len('elementary charge.')
        content = content[:start_eq] + new_eq16 + content[end_eq:]
        print("Equation 16 replaced via range matching.")

# 2. Fix Section 4.3 and Equation alignment (eliminate split equation number on Page 5)
idx_s43 = content.find(r'\subsection{Matched Multi-Zone Sample-Crossfade Baseline}')
idx_s50 = content.find(r'\section{MEASURED EXPERIMENTAL RESULTS}')

new_s43 = r'''\subsection{Matched Multi-Zone Sample-Crossfade Baseline}
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

\noindent\textbf{4. Interpolation:} Cubic-Hermite polynomial interpolation.

'''

if idx_s43 != -1 and idx_s50 != -1:
    content = content[:idx_s43] + new_s43 + content[idx_s50:]
    print("Section 4.3 equations successfully un-nested from itemize and aligned on single lines.")

# 3. Save to all 3 tex files
for fname in ['OVERLEAF_COPY_PASTE.tex', 'jaes_manuscript.tex', 'jaes_manuscript_official.tex']:
    p = os.path.join(workspace_dir, fname)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated:", p)

# 4. Re-bundle submission zip
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

