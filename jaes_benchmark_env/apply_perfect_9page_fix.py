import os, zipfile

workspace_dir = '/Users/mymac/Desktop/Ai 2026 Work/Antigravity Works/ Real-Time Circuit-Based-Exrtended/jaes_benchmark_env'
tex_path = os.path.join(workspace_dir, 'OVERLEAF_COPY_PASTE.tex')

with open(tex_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Ensure begin{document} is 100% clean
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

# 3. Clean Author Biography on Page 9 Column 2 (Strict 9-Page Paper, ZERO Blank Space)
idx_bib = content.find(r'\end{thebibliography}')
if idx_bib != -1:
    content_before = content[:idx_bib + len(r'\end{thebibliography}')]
    clean_author_block = r'''

% =========================================================================
% THE AUTHOR - Official JAES Template Layout (Fits Page 9, Exactly 9 Pages)
% =========================================================================
\vfill\columnbreak

\noindent\rule{\columnwidth}{0.8pt}\par\vspace{5pt}
\centerline{\large\bfseries THE AUTHOR}\par\vspace{5pt}
\noindent\rule{\columnwidth}{0.8pt}\par\vspace{10pt}

\begin{center}
\IfFileExists{headshot1.jpg}{%
  \includegraphics[width=32mm,height=40mm,keepaspectratio]{headshot1.jpg}\par\vspace{6pt}%
}{%
  \IfFileExists{figures/headshot1.jpg}{%
    \includegraphics[width=32mm,height=40mm,keepaspectratio]{figures/headshot1.jpg}\par\vspace{6pt}%
  }{%
    \IfFileExists{boobalan.jpg}{%
      \includegraphics[width=32mm,height=40mm,keepaspectratio]{boobalan.jpg}\par\vspace{6pt}%
    }{%
      \fbox{\parbox[c][40mm][c]{32mm}{\centering \textbf{Author Photo}}}\par\vspace{6pt}%
    }%
  }%
}
{\bfseries Boobalan Arjunan}
\end{center}
\vspace{6pt}

\noindent\textbf{Boobalan Arjunan} is the Founder and Lead AI/ML Architect at ComposerMind Labs LLP, Chennai, India, and a music technologist with over 18 years of experience in software engineering and emerging technologies. He spent 14 years at IBM as a Software Developer and Technical Lead, developing enterprise mainframe applications across banking, transportation, telecommunications, logistics, energy, utilities, and automotive industries. He subsequently specialized in Azure Data Engineering, cloud computing, and AI/ML technologies. His current research focuses on Audio AI, Music Information Retrieval, Digital Signal Processing, Generative AI, Deep Learning, Neural Audio Synthesis, and Circuit-Based Physical Modeling. At ComposerMind Labs, he leads research and development of intelligent audio systems, music synthesis technologies, and machine learning datasets.

\par\vspace{14pt}
\noindent\rule{\columnwidth}{0.8pt}

\end{document}
'''
    content = content_before + clean_author_block

# Write to all 3 tex files
for fname in ['OVERLEAF_COPY_PASTE.tex', 'jaes_manuscript.tex', 'jaes_manuscript_official.tex']:
    p = os.path.join(workspace_dir, fname)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully updated:", p)

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

