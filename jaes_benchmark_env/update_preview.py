import json

with open('jaes_benchmark_env/JAES_MANUSCRIPT_DRAFT.md') as f:
    md_content = f.read()

json_md = json.dumps(md_content)

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>JAES Manuscript Draft - Standalone Preview & PDF Export</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      line-height: 1.6;
      color: #1a1a1a;
      max-width: 900px;
      margin: 0 auto;
      padding: 40px 24px;
      background: #fdfdfd;
    }
    @media print {
      body { max-width: 100%; padding: 0; background: #fff; }
      .no-print { display: none !important; }
      h1, h2, h3 { page-break-after: avoid; }
      table, pre, blockquote { page-break-inside: avoid; }
    }
    h1, h2, h3, h4 { color: #111; margin-top: 1.5em; }
    h1 { border-bottom: 2px solid #eaeaea; padding-bottom: 0.3em; font-size: 2.1rem; }
    h2 { border-bottom: 1px solid #eaeaea; padding-bottom: 0.2em; font-size: 1.5rem; }
    table { border-collapse: collapse; width: 100%; margin: 1.5em 0; font-size: 0.95rem; }
    th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
    th { background: #f4f6f8; font-weight: 600; }
    tr:nth-child(even) { background: #fafbfc; }
    blockquote { border-left: 4px solid #0066cc; margin: 1em 0; padding: 0.5em 1em; background: #f0f7ff; color: #333; }
    code { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; background: #f3f4f6; padding: 0.2em 0.4em; border-radius: 3px; font-size: 85%; }
    pre code { display: block; padding: 1em; overflow-x: auto; }
    .print-bar { background: #e8f4fd; border: 1px solid #b6d4fe; padding: 12px 20px; border-radius: 6px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }
    .btn { background: #0066cc; color: #fff; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: 600; }
    .btn:hover { background: #0052a3; }
  </style>
</head>
<body>
  <div class="print-bar no-print">
    <span>📄 <strong>JAES Manuscript Offline Preview</strong> (LaTeX math & tables rendered)</span>
    <button class="btn" onclick="window.print()">🖨️ Print / Save as PDF</button>
  </div>
  <div id="content">Rendering manuscript...</div>

  <script>
    let rawText = """ + json_md + """;
    
    // Protect LaTeX math blocks from markdown processing
    const mathBlocks = [];
    rawText = rawText.replace(/\\$\\$([\\s\\S]*?)\\$\\$/g, function(match, p1) {
      mathBlocks.push({ type: 'display', math: p1 });
      return '%%MATH_BLOCK_' + (mathBlocks.length - 1) + '%%';
    });
    rawText = rawText.replace(/\\$([^$\\n]+?)\\$/g, function(match, p1) {
      mathBlocks.push({ type: 'inline', math: p1 });
      return '%%MATH_BLOCK_' + (mathBlocks.length - 1) + '%%';
    });

    // Render Markdown
    let html = marked.parse(rawText);

    // Restore Math blocks
    html = html.replace(/%%MATH_BLOCK_(\\d+)%%/g, function(match, id) {
      const item = mathBlocks[parseInt(id)];
      if (item.type === 'display') {
        return '$$' + item.math + '$$';
      } else {
        return '$' + item.math + '$';
      }
    });

    document.getElementById('content').innerHTML = html;

    // Trigger KaTeX rendering
    renderMathInElement(document.getElementById('content'), {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false},
        {left: '\\\\[', right: '\\\\]', display: true},
        {left: '\\\\(', right: '\\\\)', display: false}
      ],
      throwOnError: false
    });
  </script>
</body>
</html>"""

with open('jaes_benchmark_env/preview_manuscript.html', 'w') as f:
    f.write(html_content)
print('Successfully generated clean preview_manuscript.html!')

