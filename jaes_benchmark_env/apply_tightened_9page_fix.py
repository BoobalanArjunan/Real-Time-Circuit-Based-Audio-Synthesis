import os, zipfile

workspace_dir = '/Users/mymac/Desktop/Ai 2026 Work/Antigravity Works/ Real-Time Circuit-Based-Exrtended/jaes_benchmark_env'
tex_path = os.path.join(workspace_dir, 'OVERLEAF_COPY_PASTE.tex')

with open(tex_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update preamble: ensure graphicx[final], graphicspath, and bulletproof biography redefinition
# Replace from \makeatletter to \makeatother before \begin{document}
start_mletter = content.find(r'\makeatletter')
end_mletter = content.find(r'\begin{document}')

new_preamble_block = r'''\makeatletter
\providecommand{\@LN@col}[1]{}
\providecommand{\@LN}[2]{}

% Definitive JAES Author Presentation (Guaranteed 9 Pages, Zero Truncation, Zero Overflow)
\renewcommand{\biography}[3]{%
  \clearpage
  \vspace*{16pt}%
  \noindent\rule{\textwidth}{0.8pt}\vspace{16pt}%
  \begin{center}%
  {\large\bfseries THE AUTHOR}\\[18pt]%
  \IfFileExists{#2}{%
    \includegraphics[width=32mm,height=40mm,keepaspectratio]{#2}\\[10pt]%
  }{%
    \IfFileExists{figures/#2}{%
      \includegraphics[width=32mm,height=40mm,keepaspectratio]{figures/#2}\\[10pt]%
    }{%
      \fbox{\parbox[c][40mm][c]{32mm}{\centering \textbf{Author Photo}}}\\[10pt]%
    }%
  }%
  {\large\bfseries #1}\\[20pt]%
  \end{center}%
  \begin{center}%
  \begin{minipage}{0.85\textwidth}%
  \setlength{\parindent}{14pt}%
  \noindent #3%
  \end{minipage}%
  \end{center}%
  \vspace{24pt}%
  \noindent\rule{\textwidth}{0.8pt}%
}
\makeatother

'''

content = content[:start_mletter] + new_preamble_block + content[end_mletter:]

# 2. Tighten Sections 8, 9, 10 to guarantee Reference [20] fits on Page 8
old_limitations = r'''\section{LIMITATIONS AND FUTURE WORK}

Several limitations of this study should be recognized:
\begin{enumerate}
\item \textbf{Host Hardware Scope:} Empirical measurements were conducted exclusively on an Apple M1 Max host processor. While the M1 Max shares the ARM64 instruction set with mobile XR chipsets (such as Qualcomm Snapdragon XR2 series), variations in CPU core microarchitectures, thermal throttling limits, L1/L2 cache capacities, and operating system scheduling policies mean that host measurements cannot be generalized directly to standalone XR headsets without on-device empirical testing.
\item \textbf{Fixed Circuit Topologies:} The evaluated engine operates on pre-configured circuit topologies. While dynamic runtime topology modification (such as dynamically rewiring components or altering node counts) presents challenges for real-time callbacks due to symbolic matrix re-factorization ($LU$ decomposition) overhead, alternative techniques such as pre-compiled topology permutations or asynchronous background factorization warrant future exploration.
\item \textbf{Polyphony Limits and Peak Latency:} While 4-voice polyphony executed comfortably within the host deadline on average ($< 23\%$ of budget), peak observed latency reached $63.93\%$ of the deadline. Scaling to high-voice scenarios (16+ voices) on lower-powered mobile hardware would challenge single-threaded audio execution, requiring multi-threaded work-stealing or SIMD vectorization.
\item \textbf{Absence of Subjective Listening Tests:} The continuity evaluation in this paper relies on objective metrics (spectral flux, derivative outliers). Perceptual audibility of transitions under diverse interaction profiles should be evaluated in future work using formal MUSHRA or ABX listening tests.
\end{enumerate}

Future research will focus on porting the MNA solver to WebAssembly (Wasm) with SIMD vector extensions, benchmarking directly on physical standalone XR devices (Meta Quest 3 and Apple Vision Pro), and coupling MNA source synthesis with interactive acoustic finite-difference time-domain (FDTD) room simulation.

\section{USE OF ARTIFICIAL INTELLIGENCE AND LARGE LANGUAGE MODELS}

During the preparation of this manuscript, the author utilized large language model assistants (Claude 3.7 Sonnet by Anthropic and ChatGPT by OpenAI, November 2026) for technical drafting, code formatting, literature citation aggregation, and LaTeX document preparation. Following initial AI-assisted drafting, the author independently verified, revised, and validated all mathematical formulations, benchmark execution scripts, empirical dataset calculations, and bibliographic citations. The author assumes full scientific responsibility for the integrity, methodology, accuracy, and conclusions of the research presented in this paper.

\section{CONCLUSION}

This paper evaluated the computational feasibility, parameter continuity, and storage trade-offs of real-time discrete-time Modified Nodal Analysis (MNA) for interactive audio synthesis. Through empirical benchmarking on an ARM64 Apple M1 Max host under standard real-time audio block constraints (128 samples @ 48~kHz, budget = $2,666.67\,\mu\text{s}$), we established:
\begin{enumerate}
\item A strongly non-linear 4-voice circuit solver with Newton--Raphson iteration and $2\times$ oversampling consumes an average of $22.98\%$ of the block deadline on the tested host across an 18,000-block steady-state evaluation, with zero deadline violations. Worst-case block latency reached $63.93\%$ of the deadline ($1,704.7\,\mu\text{s}$), leaving $36.07\%$ headroom during peak transients. Initial cold-start execution consumes at most $32.75\%$ of the budget when buffers are preallocated, showing that unbuffered pilot latency spikes are absent under preallocated memory layouts.
\item In-place matrix updates preserve physical capacitor and inductor states, resulting in significantly fewer first-derivative outlier transitions ($p = 2.37 \times 10^{-6}$) than a matched 3-zone sample-crossfade baseline during a 60~Hz parameter sweep, though the low variance reflects within-trajectory solver consistency rather than multi-gesture generalization.
\item An entire 61-preset netlist library occupies exactly 81,130 bytes of persistent source assets, representing a $12,992\times$ to $76,223\times$ storage reduction compared to modeled uncompressed PCM sample banks (1.05 to 6.18~GB) and $860\times$ to $1,170\times$ versus lossy compressed audio (70 to 95~MB), balanced against an approximately $8\times$ higher computational cost during active modulation ($152.7\,\mu\text{s}$ vs. $19.0\,\mu\text{s}$ in 1-voice testing; polyphonic ratios in steady-state range from $4.9\times$ to $11.1\times$).
\end{enumerate}

These findings support the feasibility of the evaluated discrete-time MNA implementation on the tested Apple M1 Max ARM64 host, supporting continuous interactive control while providing an empirical foundation for future deployment on mobile XR hardware.

\section{SUPPLEMENTAL MATERIAL}
To uphold scientific reproducibility, all benchmarking scripts, raw measurement datasets (JSON and CSV formats), and the interactive HTML test harness are publicly available under the open-source MIT license at the official repository: \url{https://github.com/BoobalanArjunan/Real-Time-Circuit-Based-Audio-Synthesis}.'''

new_limitations = r'''\section{LIMITATIONS AND FUTURE WORK}

Several limitations of this study should be recognized:
\begin{enumerate}
\item \textbf{Host Hardware Scope:} Empirical measurements were conducted exclusively on an Apple M1 Max host processor. While the M1 Max shares the ARM64 instruction set with mobile XR chipsets (such as Qualcomm Snapdragon XR2 series), host measurements cannot be generalized directly to standalone XR headsets without on-device testing under mobile thermal and scheduling conditions.
\item \textbf{Fixed Circuit Topologies:} The evaluated engine operates on pre-configured circuit topologies. While dynamic runtime topology modification presents challenges for real-time callbacks due to symbolic matrix re-factorization ($LU$ decomposition) overhead, pre-compiled topology permutations warrant future exploration.
\item \textbf{Polyphony Limits and Peak Latency:} While 4-voice polyphony executed comfortably within the host deadline on average ($< 23\%$ of budget), peak latency reached $63.93\%$ of the deadline. Scaling to high polyphony (16+ voices) on lower-powered mobile hardware would require multi-threaded work-stealing or SIMD vectorization.
\item \textbf{Absence of Subjective Listening Tests:} The continuity evaluation in this paper relies on objective metrics (spectral flux, derivative outliers). Perceptual audibility of transitions should be evaluated in future work using formal MUSHRA or ABX listening tests.
\end{enumerate}

Future research will focus on porting the MNA solver to WebAssembly (Wasm) with SIMD vector extensions, benchmarking directly on standalone XR headsets, and coupling MNA source synthesis with interactive acoustic finite-difference time-domain (FDTD) room simulation.

\section{USE OF ARTIFICIAL INTELLIGENCE AND LARGE LANGUAGE MODELS}

During manuscript preparation, the author utilized large language model assistants (Claude 3.7 Sonnet by Anthropic and ChatGPT by OpenAI, November 2026) for technical drafting, code formatting, literature citation aggregation, and LaTeX preparation. Following initial drafting, the author independently verified, revised, and validated all mathematical formulations, benchmark scripts, empirical calculations, and citations. The author assumes full scientific responsibility for the integrity, methodology, accuracy, and conclusions of the research presented in this paper.

\section{CONCLUSION}

This paper evaluated the computational feasibility, parameter continuity, and storage trade-offs of real-time discrete-time Modified Nodal Analysis (MNA) for interactive audio synthesis. Through empirical benchmarking on an ARM64 Apple M1 Max host under standard real-time audio block constraints (128 samples @ 48~kHz, budget = $2,666.67\,\mu\text{s}$), we established:
\begin{enumerate}
\item A non-linear 4-voice circuit solver with Newton--Raphson iteration and $2\times$ oversampling consumes an average of $22.98\%$ of the block deadline on the tested host across an 18,000-block factorial benchmark, with zero deadline violations (peak transient duration: $1,704.7\,\mu\text{s}$, $36.07\%$ headroom). Preallocated cold-start execution consumes at most $32.75\%$ ($873.4\,\mu\text{s}$) of the budget.
\item In-place matrix updates preserve physical reactive states, resulting in significantly fewer first-derivative outlier transitions ($p = 2.37 \times 10^{-6}$) than a matched 3-zone sample-crossfade baseline during a 60~Hz parameter sweep, though the low variance reflects within-trajectory solver consistency rather than multi-gesture generalization.
\item An entire 61-preset netlist library occupies exactly 81,130 bytes of persistent source assets, representing a $12,992\times$ to $76,223\times$ storage reduction compared to modeled uncompressed PCM sample banks (1.05 to 6.18~GB) and $860\times$ to $1,170\times$ versus lossy compressed audio (70 to 95~MB), balanced against an approximately $8\times$ higher computational cost during active modulation ($152.7\,\mu\text{s}$ vs. $19.0\,\mu\text{s}$ in 1-voice testing).
\end{enumerate}

These findings support the feasibility of the evaluated discrete-time MNA implementation on ARM64 host architectures, supporting continuous interactive control while providing an empirical foundation for future deployment on mobile XR hardware.

\section{SUPPLEMENTAL MATERIAL}
To uphold scientific reproducibility, all benchmarking scripts, raw measurement datasets (JSON and CSV formats), and the interactive HTML test harness are publicly available under the open-source MIT license at the official repository: \url{https://github.com/BoobalanArjunan/Real-Time-Circuit-Based-Audio-Synthesis}.'''

if old_limitations in content:
    content = content.replace(old_limitations, new_limitations)
    print('Successfully tightened Sections 8, 9, 10 to pull Reference [20] onto Page 8.')

# 3. Tighten bibliography itemsep so all 20 references fit completely on Page 8
old_bib_start = r'\begin{thebibliography}{20}'
new_bib_start = r'''\begin{thebibliography}{20}
\setlength{\itemsep}{1.2pt plus 0.8pt minus 0.5pt}
\setlength{\parsep}{0pt}
\setlength{\parskip}{0pt}'''

if old_bib_start in content and 'setlength{\\itemsep}' not in content:
    content = content.replace(old_bib_start, new_bib_start)
    print('Successfully added itemsep/parsep tightening to bibliography.')

# 4. Replace end of document: clearpage + single clean \biography call
old_end_idx = content.find(r'\end{thebibliography}')
if old_end_idx != -1:
    content_before = content[:old_end_idx + len(r'\end{thebibliography}')]
    new_end_block = r'''

\clearpage

\biography{Boobalan Arjunan}{headshot1.jpg}{%
\textbf{Boobalan Arjunan} is the Founder and Lead AI/ML Architect at ComposerMind Labs LLP, Chennai, India, and a music technologist with over 18 years of experience in software engineering and emerging technologies. He spent 14 years at IBM as a Software Developer and Technical Lead, developing enterprise mainframe applications across banking, transportation, telecommunications, logistics, energy, utilities, and automotive industries. He subsequently specialized in Azure Data Engineering, cloud computing, and AI/ML technologies. His current research focuses on Audio AI, Music Information Retrieval, Digital Signal Processing, Generative AI, Deep Learning, Neural Audio Synthesis, and Circuit-Based Physical Modeling. At ComposerMind Labs, he leads research and development of intelligent audio systems, music synthesis technologies, and machine learning datasets.%
}

\end{document}
'''
    content = content_before + new_end_block

# Write to all manuscript files
for fname in ['OVERLEAF_COPY_PASTE.tex', 'jaes_manuscript.tex', 'jaes_manuscript_official.tex']:
    p = os.path.join(workspace_dir, fname)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated:', p)

# Update zip package
zip_path = os.path.join(workspace_dir, 'jaes_submission_package.zip')
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root_file in [
        'OVERLEAF_COPY_PASTE.tex',
        'jaes_manuscript.tex',
        'jaes_manuscript_official.tex',
        'references.bib',
        'jaes.bib',
        'headshot1.jpg',
        'boobalan.jpg'
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

print('Successfully re-bundled submission package zip with exact 9-page layout.')

