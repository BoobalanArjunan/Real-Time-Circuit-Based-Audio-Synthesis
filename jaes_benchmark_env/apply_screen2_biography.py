import os, zipfile

workspace_dir = '/Users/mymac/Desktop/Ai 2026 Work/Antigravity Works/ Real-Time Circuit-Based-Exrtended/jaes_benchmark_env'
tex_path = os.path.join(workspace_dir, 'OVERLEAF_COPY_PASTE.tex')

with open(tex_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Ensure Abstract is present with \begin{abstract}\noindent Interactive ... \end{abstract}
# and ensure Section 8 text is exact clean text
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
\item \textbf{Absence of Subjective Listening Tests:} The continuity evaluation in this paper relies on objective metrics (spectral flux, derivative outliers). Perceptual audibility of transitions should be evaluated in future work using formal MUSHRA or ABX listening tests.
\end{enumerate}

Future research will focus on porting the MNA solver to WebAssembly (Wasm) with SIMD vector extensions, benchmarking directly on physical standalone XR devices (Meta Quest 3 and Apple Vision Pro), and coupling MNA source synthesis with interactive acoustic finite-difference time-domain (FDTD) room simulation.

'''
    content = content[:idx_s8] + s8_clean + content[idx_s9:]

# 2. Perfect JAES Official Template Biography Layout (Screen 2 Matching)
# Zero \biography macro calls, Zero line collision, Zero overlapping THE AUTHORS
end_bib_idx = content.find(r'\end{thebibliography}')
if end_bib_idx != -1:
    content_before = content[:end_bib_idx + len(r'\end{thebibliography}')]
    
    perfect_author_block = r'''

\clearpage

% =========================================================================
% THE AUTHOR - Official JAES Template Layout (Exact Match to Screen 2)
% =========================================================================
\vspace*{10pt}
\noindent\rule{\linewidth}{0.8pt}\vspace{14pt}

\begin{center}
{\large\bfseries THE AUTHOR}\\[16pt]
\IfFileExists{headshot1.jpg}{%
  \includegraphics[width=32mm,height=40mm,keepaspectratio]{headshot1.jpg}\\[8pt]%
}{%
  \IfFileExists{figures/headshot1.jpg}{%
    \includegraphics[width=32mm,height=40mm,keepaspectratio]{figures/headshot1.jpg}\\[8pt]%
  }{%
    \fbox{\parbox[c][40mm][c]{32mm}{\centering \textbf{Author Photo}}}\\[8pt]%
  }%
}
{\large\bfseries Boobalan Arjunan}\\[18pt]
\end{center}

\begin{center}
\begin{minipage}{0.88\linewidth}
\setlength{\parindent}{14pt}
\noindent\textbf{Boobalan Arjunan} is the Founder and Lead AI/ML Architect at ComposerMind Labs LLP, Chennai, India, and a music technologist with over 18 years of experience in software engineering and emerging technologies. He spent 14 years at IBM as a Software Developer and Technical Lead, developing enterprise mainframe applications across banking, transportation, telecommunications, logistics, energy, utilities, and automotive industries. He subsequently specialized in Azure Data Engineering, cloud computing, and AI/ML technologies. His current research focuses on Audio AI, Music Information Retrieval, Digital Signal Processing, Generative AI, Deep Learning, Neural Audio Synthesis, and Circuit-Based Physical Modeling. At ComposerMind Labs, he leads research and development of intelligent audio systems, music synthesis technologies, and machine learning datasets.
\end{minipage}
\end{center}

\vspace{24pt}
\noindent\rule{\linewidth}{0.8pt}

\end{document}
'''
    content = content_before + perfect_author_block

# Save to all 3 tex files
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

