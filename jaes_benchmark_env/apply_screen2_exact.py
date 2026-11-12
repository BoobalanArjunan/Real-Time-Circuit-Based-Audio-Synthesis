import os, zipfile

workspace_dir = '/Users/mymac/Desktop/Ai 2026 Work/Antigravity Works/ Real-Time Circuit-Based-Exrtended/jaes_benchmark_env'
tex_path = os.path.join(workspace_dir, 'OVERLEAF_COPY_PASTE.tex')

with open(tex_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Clean begin{document}
content = content.replace('\x08egin{document}', r'\begin{document}')
content = content.replace(' egin{document}', r'\begin{document}')

# 2. Preamble author macro neutralization: completely silence any template \theauthors or \biography
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

# 3. Exact Screen 2 Author Presentation (100% Visual Clone of Screen 2)
idx_bib = content.find(r'\end{thebibliography}')
if idx_bib != -1:
    content_before = content[:idx_bib + len(r'\end{thebibliography}')]
    screen2_author_block = r'''

\clearpage

% =========================================================================
% THE AUTHOR - Official JAES Template Layout (Exact Match to Screen 2)
% =========================================================================
\vspace*{10pt}
\noindent\rule{\linewidth}{0.8pt}

\vspace{12pt}
\begin{center}
{\bfseries THE AUTHOR}\\[12pt]
\IfFileExists{headshot1.jpg}{%
  \includegraphics[width=36mm,height=45mm,keepaspectratio]{headshot1.jpg}\\[6pt]%
}{%
  \IfFileExists{figures/headshot1.jpg}{%
    \includegraphics[width=36mm,height=45mm,keepaspectratio]{figures/headshot1.jpg}\\[6pt]%
  }{%
    \IfFileExists{boobalan.jpg}{%
      \includegraphics[width=36mm,height=45mm,keepaspectratio]{boobalan.jpg}\\[6pt]%
    }{%
      \fbox{\parbox[c][45mm][c]{36mm}{\centering \textbf{Author Photo}}}\\[6pt]%
    }%
  }%
}
{\bfseries Boobalan Arjunan}
\end{center}

\vspace{12pt}

\noindent
\begin{minipage}[t]{0.48\linewidth}
\setlength{\parindent}{14pt}
\noindent\textbf{Boobalan Arjunan} is the Founder and Lead AI/ML Architect at ComposerMind Labs LLP, Chennai, India, and a music technologist with over 18 years of experience in software engineering and emerging technologies. He spent 14 years at IBM as a Software Developer and Technical Lead, developing enterprise mainframe applications across banking, transportation, telecommunications, logistics, energy, utilities, and automotive industries. He subsequently
\end{minipage}\hfill
\begin{minipage}[t]{0.48\linewidth}
\noindent specialized in Azure Data Engineering, cloud computing, and AI/ML technologies. His current research focuses on Audio AI, Music Information Retrieval, Digital Signal Processing, Generative AI, Deep Learning, Neural Audio Synthesis, and Circuit-Based Physical Modeling. At ComposerMind Labs, he leads research and development of intelligent audio systems, music synthesis technologies, and machine learning datasets.
\end{minipage}

\vspace{24pt}
\noindent\rule{\linewidth}{0.8pt}

\end{document}
'''
    content = content_before + screen2_author_block

# Write to all 3 tex files
for fname in ['OVERLEAF_COPY_PASTE.tex', 'jaes_manuscript.tex', 'jaes_manuscript_official.tex']:
    p = os.path.join(workspace_dir, fname)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully updated with exact Screen 2 format:", p)

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
            if f not in ['figure2_polyphony.pdf', 'figure2_polyphony.png']:
                zipf.write(fp, arcname=f'figures/{f}')

print("Package zip re-bundled successfully!")

