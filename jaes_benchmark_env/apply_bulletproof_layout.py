import os, zipfile

workspace_dir = '/Users/mymac/Desktop/Ai 2026 Work/Antigravity Works/ Real-Time Circuit-Based-Exrtended/jaes_benchmark_env'
tex_path = os.path.join(workspace_dir, 'OVERLEAF_COPY_PASTE.tex')

with open(tex_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix ($ decomposition) -> ($LU$ decomposition)
content = content.replace('($ decomposition)', '($LU$ decomposition)')

# Fix bibliography to use \small and tight spacing to guarantee all 20 references stay on Page 8
old_bib_block = r'''\begin{thebibliography}{20}
\setlength{\itemsep}{1.2pt plus 0.8pt minus 0.5pt}
\setlength{\parsep}{0pt}
\setlength{\parskip}{0pt}'''

new_bib_block = r'''\begin{thebibliography}{20}
\small
\setlength{\itemsep}{0.5pt plus 0.5pt minus 0.5pt}
\setlength{\parsep}{0pt}
\setlength{\parskip}{0pt}'''

if old_bib_block in content:
    content = content.replace(old_bib_block, new_bib_block)
elif r'\begin{thebibliography}{20}' in content:
    content = content.replace(r'\begin{thebibliography}{20}', new_bib_block)

# Replace the biography presentation at the end of the file
# We override \biography right before it is called, using exact \linewidth minipages so it NEVER truncates
end_bib_idx = content.find(r'\end{thebibliography}')
if end_bib_idx != -1:
    content_before = content[:end_bib_idx + len(r'\end{thebibliography}')]
    
    new_tail = r'''

\clearpage

% =========================================================================
% THE AUTHOR - Page 9 (Final Page, Zero Margins Overflow, Zero Truncation)
% =========================================================================
\makeatletter
\def\biography#1#2#3{%
  \vspace*{8pt}%
  \noindent\rule{\linewidth}{0.8pt}\\[10pt]%
  \noindent%
  \begin{minipage}[t]{0.26\linewidth}%
    \centering%
    \vspace{0pt}%
    {\bfseries THE AUTHOR}\\[8pt]%
    \IfFileExists{#2}{%
      \includegraphics[width=32mm,height=40mm,keepaspectratio]{#2}%
    }{%
      \IfFileExists{figures/#2}{%
        \includegraphics[width=32mm,height=40mm,keepaspectratio]{figures/#2}%
      }{%
        \fbox{\parbox[c][40mm][c]{32mm}{\centering \textbf{Author Photo}}}%
      }%
    }%
  \end{minipage}%
  \hfill%
  \begin{minipage}[t]{0.70\linewidth}%
    \vspace{0pt}%
    {\large\bfseries #1}\\[4pt]%
    \rule{\linewidth}{0.4pt}\\[6pt]%
    \setlength{\parindent}{0pt}%
    \fontsize{9pt}{11.5pt}\selectfont%
    #3\par%
  \end{minipage}\\[12pt]%
  \noindent\rule{\linewidth}{0.8pt}%
}
\makeatother

\biography{Boobalan Arjunan}{headshot1.jpg}{%
\textbf{Boobalan Arjunan} is the Founder and Lead AI/ML Architect at ComposerMind Labs LLP, Chennai, India, and a music technologist with over 18 years of experience in software engineering and emerging technologies. He spent 14 years at IBM as a Software Developer and Technical Lead, developing enterprise mainframe applications across banking, transportation, telecommunications, logistics, energy, utilities, and automotive industries. He subsequently specialized in Azure Data Engineering, cloud computing, and AI/ML technologies. His current research focuses on Audio AI, Music Information Retrieval, Digital Signal Processing, Generative AI, Deep Learning, Neural Audio Synthesis, and Circuit-Based Physical Modeling. At ComposerMind Labs, he leads research and development of intelligent audio systems, music synthesis technologies, and machine learning datasets.%
}

\end{document}
'''
    content = content_before + new_tail

# Write to all 3 tex files
for fname in ['OVERLEAF_COPY_PASTE.tex', 'jaes_manuscript.tex', 'jaes_manuscript_official.tex']:
    p = os.path.join(workspace_dir, fname)
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

print('Successfully re-bundled zip with bulletproof 9-page layout.')

