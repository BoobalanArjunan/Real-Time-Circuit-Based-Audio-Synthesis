import os, zipfile

workspace_dir = '/Users/mymac/Desktop/Ai 2026 Work/Antigravity Works/ Real-Time Circuit-Based-Exrtended/jaes_benchmark_env'
tex_path = os.path.join(workspace_dir, 'OVERLEAF_COPY_PASTE.tex')

with open(tex_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Preamble author macro neutralization
preamble_guard = r'''% Safeguard against template-level author macros or trailing hooks
\makeatletter
\providecommand{\@LN@col}[1]{}
\providecommand{\@LN}[2]{}
\def\theauthors{}
\def\THEAUTHORS{}
\let\theauthors\relax
\let\THEAUTHORS\relax
\makeatother
'''

if r'\def\theauthors{}' not in content:
    content = content.replace(r'\begin{document}', preamble_guard + '\n\\begin{document}')

# 2. Section 4 block tightening (Page 4)
idx_s4_start = content.find(r'The audio rendering deadline was configured')
if idx_s4_start == -1:
    idx_s4_start = content.find(r'The audio block budget corresponds to')

idx_s5_start = content.find(r'\section{MEASURED EXPERIMENTAL RESULTS}')

if idx_s4_start != -1 and idx_s5_start != -1:
    s4_clean_block = r'''The audio block budget corresponds to standard real-time interactive audio constraints ($f_s = 48\text{ kHz}$, $B = 128\text{ samples}$):
\begin{equation}
T_{\text{budget}} = \frac{B}{f_s} = \frac{128}{48,000\text{ s}^{-1}} \approx 2.66667\text{ ms} = 2,666.67\,\mu\text{s}
\end{equation}

\subsection{Circuit Topologies Evaluated}
Three circuit presets spanning linear, weakly non-linear, and strongly non-linear categories were benchmarked:
\begin{enumerate}\setlength{\itemsep}{1.2pt}\setlength{\parsep}{0pt}
\item \textbf{RC High-Pass Filter (Linear):} 2 nodes, 1 capacitor ($10\text{ nF}$), 1 resistor ($10\text{ k}\Omega$). Solved directly via linear matrix solution without Newton--Raphson iteration.
\item \textbf{Half-Wave Rectifier (Weakly Non-linear):} 3 nodes, 1 signal diode (1N4148 model), 1 resistor, 1 capacitor. Requires iterative non-linear solving during forward conduction cycles.
\item \textbf{Fuzz Distortion Stage (Strongly Non-linear):} 5 nodes, anti-parallel clipping diode pair, reactive capacitors, variable drive resistance ($940\,\Omega \le R \le 23.5\text{ k}\Omega$). Exercises frequent Jacobian updates and Newton--Raphson iterations per step.
\end{enumerate}

\subsection{Matched Multi-Zone Sample-Crossfade Baseline}
To establish a realistic baseline, the MNA solver was benchmarked against a defined \textbf{3-Zone Parameter-Smoothed Sample-Crossfade Baseline Engine}:
\begin{itemize}\setlength{\itemsep}{1.2pt}\setlength{\parsep}{0pt}
\item \textbf{Reference Audio:} 24-bit/48~kHz audio rendered directly from the MNA circuit at three anchor states: Zone 1 ($R = 940\,\Omega$), Zone 2 ($R = 11,750\,\Omega$), and Zone 3 ($R = 23,500\,\Omega$). 24-bit depth was chosen to maximize dynamic range and eliminate quantization noise in the reference material.
\item \textbf{Crossfade Curve:} Equal-power piecewise crossfading across adjacent zones:
\begin{equation}
y_{\text{sample}}[n] = \cos(\theta) \, s_A[n] + \sin(\theta) \, s_B[n], \quad \theta = \frac{\pi}{2} \cdot \frac{p - p_A}{p_B - p_A}
\end{equation}
\item \textbf{Control Smoothing:} A continuous single-pole low-pass filter ($f_c = 30\text{ Hz}$) applied to incoming parameter transitions:
\begin{equation}
R_{\text{smooth}}[n] = (1 - \alpha) R_{\text{smooth}}[n-1] + \alpha R_{\text{target}}[n]
\end{equation}
where $\alpha = 1 - \exp\left(-\frac{2\pi f_c}{f_s}\right) \approx 0.00392$.
\item \textbf{Interpolation:} Cubic-Hermite polynomial interpolation.
\end{itemize}

'''
    content = content[:idx_s4_start] + s4_clean_block + content[idx_s5_start:]
    print("Section 4 successfully updated.")

# 3. Clean Author Biography (Final Page)
idx_bib = content.find(r'\end{thebibliography}')
if idx_bib != -1:
    content_before = content[:idx_bib + len(r'\end{thebibliography}')]
    clean_author_block = r'''

\clearpage

% =========================================================================
% THE AUTHOR - Official JAES Template Layout (Single Author)
% =========================================================================
\vspace*{14pt}
\noindent\rule{\linewidth}{0.8pt}
\vspace{6pt}

\begin{center}
{\large\bfseries THE AUTHOR}
\end{center}

\vspace{6pt}
\noindent\rule{\linewidth}{0.8pt}
\vspace{18pt}

\noindent
\begin{minipage}[t]{0.30\linewidth}
\centering
\IfFileExists{headshot1.jpg}{%
  \includegraphics[width=34mm,height=42mm,keepaspectratio]{headshot1.jpg}\par\vspace{8pt}%
}{%
  \IfFileExists{figures/headshot1.jpg}{%
    \includegraphics[width=34mm,height=42mm,keepaspectratio]{figures/headshot1.jpg}\par\vspace{8pt}%
  }{%
    \IfFileExists{boobalan.jpg}{%
      \includegraphics[width=34mm,height=42mm,keepaspectratio]{boobalan.jpg}\par\vspace{8pt}%
    }{%
      \fbox{\parbox[c][42mm][c]{34mm}{\centering \textbf{Author Photo}}}\par\vspace{8pt}%
    }%
  }%
}
{\bfseries Boobalan Arjunan}
\end{minipage}\hfill
\begin{minipage}[t]{0.67\linewidth}
\setlength{\parindent}{14pt}
\noindent\textbf{Boobalan Arjunan} is the Founder and Lead AI/ML Architect at ComposerMind Labs LLP, Chennai, India, and a music technologist with over 18 years of experience in software engineering and emerging technologies. He spent 14 years at IBM as a Software Developer and Technical Lead, developing enterprise mainframe applications across banking, transportation, telecommunications, logistics, energy, utilities, and automotive industries. He subsequently specialized in Azure Data Engineering, cloud computing, and AI/ML technologies. His current research focuses on Audio AI, Music Information Retrieval, Digital Signal Processing, Generative AI, Deep Learning, Neural Audio Synthesis, and Circuit-Based Physical Modeling. At ComposerMind Labs, he leads research and development of intelligent audio systems, music synthesis technologies, and machine learning datasets.
\end{minipage}

\vspace{24pt}
\noindent\rule{\linewidth}{0.8pt}

\end{document}
'''
    content = content_before + clean_author_block
    print("Clean author section successfully updated.")

# Write to all 3 tex files
for fname in ['OVERLEAF_COPY_PASTE.tex', 'jaes_manuscript.tex', 'jaes_manuscript_official.tex']:
    p = os.path.join(workspace_dir, fname)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Saved:", p)

# Re-bundle zip
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
            zipf.write(fp, arcname=f'figures/{f}')
            zipf.write(fp, arcname=f)

print("Successfully generated and re-bundled submission package zip!")

