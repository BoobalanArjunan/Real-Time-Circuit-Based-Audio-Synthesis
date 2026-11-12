import os, zipfile

workspace_dir = '/Users/mymac/Desktop/Ai 2026 Work/Antigravity Works/ Real-Time Circuit-Based-Exrtended/jaes_benchmark_env'
tex_path = os.path.join(workspace_dir, 'OVERLEAF_COPY_PASTE.tex')

with open(tex_path, 'r', encoding='utf-8') as f:
    content = f.read()

# -------------------------------------------------------------------------
# Fix 4: Page 1 - Abstract Placement & Capital "I" Protection
# -------------------------------------------------------------------------
# Replace \abstract{% ... } with \begin{abstract}\noindent Interactive ... \end{abstract}
abs_old_start = r'\abstract{%'
abs_old_end = r'polyphonic ratios in steady-state range from $4.9\times$ to $11.1\times$).' + '\n' + '}'

abs_new = r'''\begin{abstract}
\noindent Interactive spatial audio engines must meet fixed audio-processing deadlines, maintain minimal memory footprints, and deliver responsive modulation under continuous parameter sweeps. Conventional multi-sample playback demands substantial storage for multi-zone parameter coverage and can introduce phase cancellation during crossfading. This paper evaluates discrete-time Modified Nodal Analysis (MNA) with iterative Newton--Raphson non-linear solving in Web Audio \texttt{AudioWorkletProcessor} architectures. High-resolution profiling on an ARM64 Apple M1 Max host demonstrated that steady-state 4-voice MNA consumes an average of 10.31\% to 22.98\% (612.7~$\mu$s) of the 2,666.67~$\mu$s block deadline across an 18,000-block factorial benchmark, with zero deadline violations observed during testing (peak transient duration: 1,704.7~$\mu$s, 36.07\% headroom). In a dedicated 20-trial evaluation, preallocated cold-start blocks completed within 873.4~$\mu$s. Under a 60~Hz parameter sweep across 20 trials, in-place reactive state preservation produced significantly fewer first-derivative outlier spikes than a matched 3-zone sample-crossfade baseline ($t = -6.64, p = 2.37 \times 10^{-6}$). The verified 61-preset netlist library occupies 81,130 bytes of persistent source assets, representing a $12,992\times$ to $76,223\times$ storage reduction compared to modeled uncompressed PCM sample banks (1.05 to 6.18~GB) and $860\times$ to $1,170\times$ versus lossy compressed audio (70 to 95~MB), balanced against an approximately $8\times$ higher computational cost during active modulation ($152.7\,\mu\text{s}$ vs. $19.0\,\mu\text{s}$ in 1-voice testing; polyphonic ratios in steady-state range from $4.9\times$ to $11.1\times$).
\end{abstract}'''

if abs_old_start in content:
    idx_start = content.find(abs_old_start)
    idx_end = content.find(r'\end{abstract}', idx_start)
    if idx_end == -1:
        # find matching closing brace
        idx_end = content.find('}\n\n\\begin{keywords}', idx_start)
        if idx_end != -1:
            content = content[:idx_start] + abs_new + content[idx_end + 1:]
            print('Fixed Abstract to \\begin{abstract}\\noindent ... \\end{abstract}')
else:
    print('Abstract already using environment or modified format.')

# -------------------------------------------------------------------------
# Fix 1: Page 7 - Repair corrupted text in Section 8 (Exact GPT wording)
# -------------------------------------------------------------------------
s8_marker = r'\section{LIMITATIONS AND FUTURE WORK}'
s9_marker = r'\section{USE OF ARTIFICIAL INTELLIGENCE AND LARGE LANGUAGE MODELS}'

idx_s8 = content.find(s8_marker)
idx_s9 = content.find(s9_marker)

if idx_s8 != -1 and idx_s9 != -1:
    s8_clean = r'''\section{LIMITATIONS AND FUTURE WORK}

Several limitations of this study should be recognized:
\begin{enumerate}
\item \textbf{Host Hardware Scope:} Empirical measurements were conducted exclusively on an Apple M1 Max host processor. While the M1 Max shares the ARM64 instruction set with mobile XR chipsets (such as Qualcomm Snapdragon XR2 series), host measurements cannot be generalized directly to standalone XR headsets without on-device empirical testing under mobile thermal constraints.
\item \textbf{Fixed Circuit Topologies:} Dynamic runtime topology modification presents challenges for real-time callbacks due to symbolic matrix re-factorization overhead; precompiled topology permutations warrant future exploration.
\item \textbf{Polyphony Limits and Peak Latency:} While 4-voice polyphony executed within the host deadline on average, peak latency reached 63.93\% of the deadline. Scaling to high polyphony (16 or more voices) on mobile hardware would require further optimization and empirical validation.
\item \textbf{Absence of Subjective Listening Tests:} The continuity evaluation in this paper relies on objective metrics (spectral flux, derivative outliers). Perceptual audibility of transitions under diverse interaction profiles should be evaluated in future work using formal MUSHRA or ABX listening tests.
\end{enumerate}

Future research will focus on porting the MNA solver to WebAssembly (Wasm) with SIMD vector extensions, benchmarking directly on physical standalone XR devices (Meta Quest 3 and Apple Vision Pro), and coupling MNA source synthesis with interactive acoustic finite-difference time-domain (FDTD) room simulation.

'''
    content = content[:idx_s8] + s8_clean + content[idx_s9:]
    print('Fixed Section 8 corrupted text with exact requested text.')

# -------------------------------------------------------------------------
# Fix 3: Author Biography - Zero Truncation, Zero Overflow, Remove Empty THE AUTHORS
# -------------------------------------------------------------------------
end_bib_idx = content.find(r'\end{thebibliography}')
if end_bib_idx != -1:
    content_before = content[:end_bib_idx + len(r'\end{thebibliography}')]
    
    clean_author_block = r'''

\clearpage

% =========================================================================
% THE AUTHOR - Clean Publication Presentation (Page 9 of 9)
% =========================================================================
\vspace*{8pt}
\noindent\rule{\linewidth}{0.8pt}\\[12pt]
\noindent
\begin{minipage}[t]{0.26\linewidth}
  \centering
  \vspace{0pt}
  {\bfseries THE AUTHOR}\\[8pt]
  \IfFileExists{headshot1.jpg}{%
    \includegraphics[width=32mm,height=40mm,keepaspectratio]{headshot1.jpg}%
  }{%
    \IfFileExists{figures/headshot1.jpg}{%
      \includegraphics[width=32mm,height=40mm,keepaspectratio]{figures/headshot1.jpg}%
    }{%
      \fbox{\parbox[c][40mm][c]{32mm}{\centering \textbf{Author Photo}}}%
    }%
  }
\end{minipage}%
\hfill%
\begin{minipage}[t]{0.70\linewidth}
  \vspace{0pt}
  {\large\bfseries Boobalan Arjunan}\\[4pt]
  \rule{\linewidth}{0.4pt}\\[6pt]
  \setlength{\parindent}{0pt}
  \fontsize{9pt}{11.5pt}\selectfont
  \textbf{Boobalan Arjunan} is the Founder and Lead AI/ML Architect at ComposerMind Labs LLP, Chennai, India, and a music technologist with over 18 years of experience in software engineering and emerging technologies. He spent 14 years at IBM as a Software Developer and Technical Lead, developing enterprise mainframe applications across banking, transportation, telecommunications, logistics, energy, utilities, and automotive industries. He subsequently specialized in Azure Data Engineering, cloud computing, and AI/ML technologies. His current research focuses on Audio AI, Music Information Retrieval, Digital Signal Processing, Generative AI, Deep Learning, Neural Audio Synthesis, and Circuit-Based Physical Modeling. At ComposerMind Labs, he leads research and development of intelligent audio systems, music synthesis technologies, and machine learning datasets.\par
\end{minipage}\\[14pt]
\noindent\rule{\linewidth}{0.8pt}

\end{document}
'''
    content = content_before + clean_author_block
    print('Replaced Biography with clean responsive non-overflow layout.')

# Clean preamble: remove \renewcommand{\biography} from preamble so it doesn't conflict
bio_preamble_marker = r'% Definitive JAES Author Presentation (Guaranteed 9 Pages'
if bio_preamble_marker in content:
    idx_p1 = content.find(bio_preamble_marker)
    idx_p2 = content.find(r'\makeatother', idx_p1)
    if idx_p1 != -1 and idx_p2 != -1:
        content = content[:idx_p1] + content[idx_p2:]
        print('Cleaned biography macro from preamble.')

# Save to all manuscript files
for fname in ['OVERLEAF_COPY_PASTE.tex', 'jaes_manuscript.tex', 'jaes_manuscript_official.tex']:
    p = os.path.join(workspace_dir, fname)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated:', p)

# Re-bundle jaes_submission_package.zip with all updated files and figures
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

print('Successfully re-bundled jaes_submission_package.zip!')

