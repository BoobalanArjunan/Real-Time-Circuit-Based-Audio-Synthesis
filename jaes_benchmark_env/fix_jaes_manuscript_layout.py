import os, zipfile, shutil

workspace_dir = '/Users/mymac/Desktop/Ai 2026 Work/Antigravity Works/ Real-Time Circuit-Based-Exrtended/jaes_benchmark_env'
tex_path = os.path.join(workspace_dir, 'OVERLEAF_COPY_PASTE.tex')
with open(tex_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update preamble: ensure graphicx[final], remove cuted, add graphicspath
preamble_old = r'''\usepackage[final]{graphicx}
\usepackage{cuted}'''

preamble_new = r'''\usepackage[final]{graphicx}
\graphicspath{{./}{figures/}}'''

if preamble_old in content:
    content = content.replace(preamble_old, preamble_new)
elif r'\usepackage{graphicx}' in content:
    content = content.replace(r'\usepackage{graphicx}', r'\usepackage[final]{graphicx}' + '\n' + r'\graphicspath{{./}{figures/}}')

# 2. Fix biography fallback definition in preamble
old_bio_marker = r'\@ifundefined{biography}'
if old_bio_marker in content:
    start_idx = content.find(r'% Official JAES biography fallback')
    if start_idx == -1:
        start_idx = content.find(old_bio_marker)
    end_idx = content.find(r'\makeatother', start_idx)
    
    new_bio_def = r'''% Definitive JAES Author Presentation (Zero Float, Zero Page Split)
\makeatletter
\providecommand{\@LN@col}[1]{}
\providecommand{\@LN}[2]{}

% Robust Biography definition matching official JAES template styling
\renewcommand{\biography}[3]{%
  \clearpage
  \vspace*{12pt}%
  \noindent\rule{\textwidth}{0.8pt}\vspace{14pt}%
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
  \begin{minipage}{0.88\textwidth}%
  \setlength{\parindent}{14pt}%
  \noindent #3%
  \end{minipage}%
  \end{center}%
  \vspace{24pt}%
  \noindent\rule{\textwidth}{0.8pt}%
}'''
    content = content[:start_idx] + new_bio_def + '\n' + content[end_idx:]

# 3. Fix Abstract & JAES Thematic Section
old_abstract_block = r'''\begin{abstract}
{}Interactive spatial audio engines must meet fixed audio-processing deadlines, maintain minimal memory footprints, and deliver responsive modulation under continuous parameter sweeps. Conventional multi-sample playback demands substantial storage for multi-zone parameter coverage and can introduce phase cancellation during crossfading. This paper evaluates discrete-time Modified Nodal Analysis (MNA) with iterative Newton--Raphson non-linear solving in Web Audio \texttt{AudioWorkletProcessor} architectures. High-resolution profiling on an ARM64 Apple M1 Max host demonstrated that steady-state 4-voice MNA consumes an average of 10.31\% to 22.98\% (612.7~$\mu$s) of the 2,666.67~$\mu$s block deadline across an 18,000-block factorial benchmark, with zero deadline violations observed during testing (peak transient duration: 1,704.7~$\mu$s, 36.07\% headroom). In a dedicated 20-trial evaluation, preallocated cold-start blocks completed within 873.4~$\mu$s. Under a 60~Hz parameter sweep across 20 trials, in-place reactive state preservation produced significantly fewer first-derivative outlier spikes than a matched 3-zone sample-crossfade baseline ($t = -6.64, p = 2.37 \times 10^{-6}$). The verified 61-preset netlist library occupies 81,130 bytes of persistent source assets, representing a $12,992\times$ to $76,223\times$ storage reduction compared to modeled uncompressed PCM sample banks (1.05 to 6.18~GB) and $860\times$ to $1,170\times$ versus lossy compressed audio (70 to 95~MB), balanced against an approximately $8\times$ higher computational cost during active modulation ($152.7\,\mu\text{s}$ vs. $19.0\,\mu\text{s}$ in 1-voice testing; polyphonic ratios in steady-state range from $4.9\times$ to $11.1\times$).
\end{abstract}'''

new_abstract_block = r'''\abstract{%
Interactive spatial audio engines must meet fixed audio-processing deadlines, maintain minimal memory footprints, and deliver responsive modulation under continuous parameter sweeps. Conventional multi-sample playback demands substantial storage for multi-zone parameter coverage and can introduce phase cancellation during crossfading. This paper evaluates discrete-time Modified Nodal Analysis (MNA) with iterative Newton--Raphson non-linear solving in Web Audio \texttt{AudioWorkletProcessor} architectures. High-resolution profiling on an ARM64 Apple M1 Max host demonstrated that steady-state 4-voice MNA consumes an average of 10.31\% to 22.98\% (612.7~$\mu$s) of the 2,666.67~$\mu$s block deadline across an 18,000-block factorial benchmark, with zero deadline violations observed during testing (peak transient duration: 1,704.7~$\mu$s, 36.07\% headroom). In a dedicated 20-trial evaluation, preallocated cold-start blocks completed within 873.4~$\mu$s. Under a 60~Hz parameter sweep across 20 trials, in-place reactive state preservation produced significantly fewer first-derivative outlier spikes than a matched 3-zone sample-crossfade baseline ($t = -6.64, p = 2.37 \times 10^{-6}$). The verified 61-preset netlist library occupies 81,130 bytes of persistent source assets, representing a $12,992\times$ to $76,223\times$ storage reduction compared to modeled uncompressed PCM sample banks (1.05 to 6.18~GB) and $860\times$ to $1,170\times$ versus lossy compressed audio (70 to 95~MB), balanced against an approximately $8\times$ higher computational cost during active modulation ($152.7\,\mu\text{s}$ vs. $19.0\,\mu\text{s}$ in 1-voice testing; polyphonic ratios in steady-state range from $4.9\times$ to $11.1\times$).
}'''

if old_abstract_block in content:
    content = content.replace(old_abstract_block, new_abstract_block)

# 4. Fix end of document (biography presentation on Page 9)
bio_start = content.find(r'\end{thebibliography}')
if bio_start != -1:
    content_before_bio = content[:bio_start + len(r'\end{thebibliography}')]
    new_final_page = r'''

\clearpage

% =========================================================================
% THE AUTHOR - Official JAES Template Presentation (Page 9 - Complete)
% =========================================================================
\vspace*{12pt}
\noindent\rule{\textwidth}{0.8pt}\vspace{14pt}

\begin{center}
{\large\bfseries THE AUTHOR}\\[18pt]
\IfFileExists{headshot1.jpg}{%
  \includegraphics[width=32mm,height=40mm,keepaspectratio]{headshot1.jpg}\\[10pt]%
}{%
  \IfFileExists{figures/headshot1.jpg}{%
    \includegraphics[width=32mm,height=40mm,keepaspectratio]{figures/headshot1.jpg}\\[10pt]%
  }{%
    \fbox{\parbox[c][40mm][c]{32mm}{\centering \textbf{Author Photo}}}\\[10pt]%
  }%
}
{\large\bfseries Boobalan Arjunan}\\[20pt]
\end{center}

\begin{center}
\begin{minipage}{0.88\textwidth}
\setlength{\parindent}{14pt}
\noindent\textbf{Boobalan Arjunan} is the Founder and Lead AI/ML Architect at ComposerMind Labs LLP, Chennai, India, and a music technologist with over 18 years of experience in software engineering and emerging technologies. He spent 14 years at IBM as a Software Developer and Technical Lead, developing enterprise mainframe applications across banking, transportation, telecommunications, logistics, energy, utilities, and automotive industries. He subsequently specialized in Azure Data Engineering, cloud computing, and AI/ML technologies. His current research focuses on Audio AI, Music Information Retrieval, Digital Signal Processing, Generative AI, Deep Learning, Neural Audio Synthesis, and Circuit-Based Physical Modeling. At ComposerMind Labs, he leads research and development of intelligent audio systems, music synthesis technologies, and machine learning datasets.
\end{minipage}
\end{center}

\vspace{24pt}
\noindent\rule{\textwidth}{0.8pt}

\end{document}
'''
    content = content_before_bio + new_final_page

# Save to OVERLEAF_COPY_PASTE.tex, jaes_manuscript.tex, and jaes_manuscript_official.tex
for filename in ['OVERLEAF_COPY_PASTE.tex', 'jaes_manuscript.tex', 'jaes_manuscript_official.tex']:
    p = os.path.join(workspace_dir, filename)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated:', p)

# Re-bundle jaes_submission_package.zip
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

print('Successfully re-bundled jaes_submission_package.zip')

