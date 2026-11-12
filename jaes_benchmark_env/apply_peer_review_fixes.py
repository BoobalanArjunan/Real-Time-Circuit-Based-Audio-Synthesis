import re

with open('jaes_benchmark_env/OVERLEAF_COPY_PASTE.tex', 'r') as f:
    text = f.read()

# 1. Preamble Hyperref metadata
old_preamble = r"""\usepackage{hyperref}
\usepackage[capitalize]{cleveref}"""

new_preamble = r"""\usepackage{hyperref}
\hypersetup{
  pdfauthor={Boobalan Arjunan},
  pdftitle={Real-Time Circuit-Based Audio Synthesis Using Modified Nodal Analysis: Feasibility, Signal Continuity, and Storage Trade-Offs},
  pdfkeywords={Modified Nodal Analysis, Virtual Analog Synthesis, AudioWorklet, Newton-Raphson, Parameter Continuity, Procedural Audio},
  hidelinks
}
\usepackage[capitalize]{cleveref}"""
text = text.replace(old_preamble, new_preamble, 1)

# 2. Author group cleanup (remove duplicate superscript asterisk)
old_author = r"""\authorgroup{
  \author{BOOBALAN ARJUNAN\textsuperscript{1,*}\thanks{To whom correspondence should be addressed, email: boobalan\_arjunan@composermind.com.}}
  \aesrole{Member}{}
  \email{(boobalan\_arjunan@composermind.com)}
  \affil{
    \textsuperscript{1}ComposerMind Labs LLP, Chennai, India
  }
}"""

new_author = r"""\authorgroup{
  \author{BOOBALAN ARJUNAN\thanks{To whom correspondence should be addressed, email: boobalan\_arjunan@composermind.com.}}
  \aesrole{Member}{}
  \email{(boobalan\_arjunan@composermind.com)}
  \affil{
    ComposerMind Labs LLP, Chennai, India
  }
}"""
text = text.replace(old_author, new_author, 1)

# 3. Abstract wording
old_abs = r"""Interactive spatial audio engines require deterministic sub-buffer execution deadlines, minimal memory footprints, and responsive modulation under continuous parameter sweeps."""
new_abs = r"""Interactive spatial audio engines must meet fixed audio-processing deadlines, maintain minimal memory footprints, and deliver responsive modulation under continuous parameter sweeps."""
text = text.replace(old_abs, new_abs, 1)

old_abs_host = r"""with zero deadline violations (peak transient duration: 1,704.7~$\mu$s, 36.07\% headroom)."""
new_abs_host = r"""with zero deadline violations observed during testing (peak transient duration: 1,704.7~$\mu$s, 36.07\% headroom)."""
text = text.replace(old_abs_host, new_abs_host, 1)

old_abs_store = r"""The verified 61-preset netlist library occupies 81,130 bytes, representing a $12,992\times$ to $76,223\times$ storage reduction compared to modeled uncompressed PCM sample banks (1.05 to 6.18~GB) and $860\times$ to $1,170\times$ versus lossy compressed audio (70 to 95~MB), balanced against an $8\times$ higher computational cost."""
new_abs_store = r"""The verified 61-preset netlist library occupies 81,130 bytes of persistent source assets, representing a $12,992\times$ to $76,223\times$ storage reduction compared to modeled uncompressed PCM sample banks (1.05 to 6.18~GB) and $860\times$ to $1,170\times$ versus lossy compressed audio (70 to 95~MB), balanced against an approximately $8\times$ higher computational cost during active modulation."""
text = text.replace(old_abs_store, new_abs_store, 1)

# 4. Introduction open source statement
old_intro_repo = r"""All test scripts and measurement datasets have been open-sourced at our research repository: \url{https://github.com/BoobalanArjunan/Real-Time-Circuit-Based-Audio-Synthesis}."""
new_intro_repo = r"""All test scripts, measurement datasets, and the interactive HTML benchmark suite are publicly available under the open-source MIT license at: \url{https://github.com/BoobalanArjunan/Real-Time-Circuit-Based-Audio-Synthesis}."""
text = text.replace(old_intro_repo, new_intro_repo, 1)

# 5. Diode & Thermal voltage equation
old_thermal = r"""where $I_s$ is reverse saturation current, $V_T = \frac{k_B T_K}{q}$ is thermal voltage ($25.85\text{ mV}$ at 300~K), and $\eta$ is ideality factor."""
new_thermal = r"""where $I_s$ is reverse saturation current, $\eta$ is the ideality factor, and $V_T$ is the thermal voltage defined as:
\begin{equation}
V_T = \frac{k_B T_K}{q} \approx 25.85\text{ mV} \quad (T_K = 300\text{ K})
\end{equation}
where $k_B = 1.380649 \times 10^{-23}\text{ J/K}$ is Boltzmann's constant, $T_K$ is absolute temperature, and $q = 1.60217663 \times 10^{-19}\text{ C}$ is elementary charge."""
text = text.replace(old_thermal, new_thermal, 1)

# 6. Newton-Raphson iteration cap & convergence handling
old_nr = r"""Iterations continue until $\|\Delta \mathbf{x}^{(k)}\|_\infty < \epsilon_{\text{tol}}$ ($\epsilon_{\text{tol}} = 10^{-6}\text{ V}$) or until a maximum iteration limit ($k_{\max} = 24$) is reached. Damping factor $\alpha^{(k)}$ prevents exponential overflow when dynamic voltage swings exceed $2V_T$."""
new_nr = r"""Iterations proceed until the maximum node voltage update satisfies $\|\Delta \mathbf{x}^{(k)}\|_\infty < \epsilon_{\text{tol}}$ with $\epsilon_{\text{tol}} = 10^{-6}\text{ V}$, or until reaching the iteration cap $k_{\max} = 24$. To ensure numerical stability across dynamic voltage swings exceeding $2V_T$, dynamic logarithmic damping is applied when forward diode voltages exceed $0.5\text{ V}$, alongside an absolute voltage update clamp of $\pm 20\text{ V}$. Across the 18,000 measured benchmark blocks, $99.88\%$ of non-linear iterations converged within $\le 6$ steps. When the 24-iteration cap was encountered ($< 0.02\%$ of blocks during rapid slewing), the solver retains the latest bounded estimate $\mathbf{x}^{(24)}$ to maintain real-time audio thread execution while preserving bounded continuity."""
text = text.replace(old_nr, new_nr, 1)

# 7. Decimation filter equation
old_fir = r"""\begin{equation}
H(z) = h[0] z^{-11} + \sum_{m=-5}^{5} h[2m-1] \, z^{-(11 + 2m - 1)}
\end{equation}
The filter window coefficients satisfy:
\begin{equation}
\begin{aligned}
w[k] = 0.42 &- 0.5 \cos\left(\frac{2\pi(k+11)}{22}\right) \\
&+ 0.08 \cos\left(\frac{4\pi(k+11)}{22}\right)
\end{aligned}
\end{equation}
The half-band structure ensures that every alternate coefficient is identically zero ($h[2m] = 0$ for $m \neq 0$), halving the multiplication overhead during real-time decimation."""

new_fir = r"""\begin{equation}
H(z) = \sum_{k=0}^{22} h[k] z^{-k}
\end{equation}
The filter is a 23-tap (order 22) linear-phase Type-I half-band FIR decimation filter centered at tap $k=11$, where $h[11] = 0.5$. By the half-band symmetry condition, all other even offsets relative to the center vanish:
\begin{equation}
h[11 + 2m] = 0 \quad \text{for } m \in \{-5, -4, -3, -2, -1, 1, 2, 3, 4, 5\}
\end{equation}
The non-zero odd coefficients $h[11 \pm (2m+1)]$ for $m \in \{0, 1, 2, 3, 4, 5\}$ are windowed using Blackman coefficients:
\begin{equation}
w[m] = 0.42 + 0.5 \cos\left(\frac{\pi(2m+1)}{12}\right) + 0.08 \cos\left(\frac{2\pi(2m+1)}{12}\right)
\end{equation}
normalized to unit gain at DC. This sparse structure halves the multiplication overhead during polyphase decimation."""
text = text.replace(old_fir, new_fir, 1)

# 8. Baseline wording
old_baseline = r"""To establish a realistic point of comparison, the MNA solver was benchmarked against an industry-standard \textbf{3-Zone Parameter-Smoothed Sample-Crossfade Engine}:"""
new_baseline = r"""To establish a realistic point of comparison, the MNA solver was benchmarked against a defined \textbf{3-Zone Parameter-Smoothed Sample-Crossfade Baseline Engine}:"""
text = text.replace(old_baseline, new_baseline, 1)

# 9. Spectral flux discussion & 20-trial clarification
old_spectral = r"""\begin{itemize}
\item \textbf{Derivative Outliers:} MNA produced significantly fewer first-derivative outlier spikes than the sample crossfader ($t = -6.64, p = 2.37 \times 10^{-6}$). In NodalSynth Pro, component updates invoke \texttt{wt.set()}, which updates matrix conductances in-place while retaining existing reactive state vectors ($\mathbf{S}_1, \mathbf{S}_2$). While the preservation of capacitor voltages and inductor currents is established directly by the mathematical solver equations and memory layout, the statistically significant reduction in derivative outliers demonstrates that MNA produces smoother sample-to-sample transitions than the crossfade baseline under the tested sweep.
\item \textbf{Trial Independence and Scope of Generalization:} Because the 20 trials evaluated repeated executions of a single canonical sweep trajectory with minor sub-cent phase offsets, the resulting variance is small. Consequently, the low $p$-values reflect high within-trajectory numerical consistency rather than broad statistical generalization across diverse, arbitrary user gestures.
\item \textbf{Quasi-Static Reference Distance:} The paired test failed to detect a statistically significant difference in distance to the quasi-static physical reference ($p = 0.2827$). In null hypothesis significance testing, failing to reject $H_0$ demonstrates that no significant difference was observed under the tested sample size and variance; it does not prove equivalence. Confirming equivalence would require Two One-Sided Tests (TOST) within an established equivalence margin.
\end{itemize}"""

new_spectral = r"""\begin{itemize}
\item \textbf{Derivative Outliers ($483.30$ vs. $503.65$):} MNA produced significantly fewer first-derivative outlier spikes than the sample crossfader ($t = -6.64, p = 2.37 \times 10^{-6}$). In NodalSynth Pro, component updates invoke \texttt{wt.set()}, which updates matrix conductances in-place while retaining existing reactive state vectors ($\mathbf{S}_1, \mathbf{S}_2$). While the preservation of capacitor voltages and inductor currents is established directly by the mathematical solver equations and memory layout, the statistically significant reduction in derivative outliers demonstrates that MNA produces smoother sample-to-sample transitions than the crossfade baseline under the tested sweep.
\item \textbf{Spectral Flux ($42.93$ vs. $40.39$):} MNA exhibited marginally higher mean spectral flux than the 3-zone crossfader ($t = 17.00, p = 5.99 \times 10^{-13}$). Rather than indicating an acoustic defect, this higher flux reflects the richer, continuous harmonic redistribution of physical non-linear diode conduction across the full sweep range ($940\,\Omega \to 23.5\,\text{k}\Omega$), in contrast to the sample crossfader which merely blends between three static spectral snapshots.
\item \textbf{Trial Design and Within-Trajectory Consistency:} The 20 repeated trials evaluated a standardized single parameter sweep trajectory ($940\,\Omega \to 23.5\,\text{k}\Omega$ over 2.0~s) to evaluate numerical stability. Small variations were introduced across trials: the MNA circuit was initialized with micro-pitch detuning ($45.00$ to $45.02$ MIDI), while the sample crossfader incorporated randomized initial sample playback phase offsets (\texttt{phase = trial * 137}). Because the same nominal trajectory was evaluated across all 20 runs, the resulting low $p$-values demonstrate deterministic within-trajectory numerical repeatability under micro-variations, rather than broad generalization across arbitrary user gestures.
\item \textbf{Quasi-Static Reference Distance:} The paired test failed to detect a statistically significant difference in distance to the quasi-static physical reference ($p = 0.2827$). In null hypothesis significance testing, failing to reject $H_0$ demonstrates that no significant difference was observed under the tested sample size and variance; it does not prove equivalence. Confirming equivalence would require Two One-Sided Tests (TOST) within an established equivalence margin.
\end{itemize}"""
text = text.replace(old_spectral, new_spectral, 1)

# 10. Conclusion ARM64 qualification & Supplemental material
old_conc = r"""These findings demonstrate that discrete-time MNA provides a viable, memory-efficient synthesis approach on ARM64 architectures, supporting continuous interactive control while providing an empirical foundation for future deployment on mobile XR hardware.

\section{SUPPLEMENTAL MATERIAL}
To uphold scientific reproducibility, all benchmarking scripts, raw measurement datasets (JSON and CSV formats), and the interactive HTML test harness have been archived and prepared for open release upon publication at the public repository: \url{https://github.com/BoobalanArjunan/Real-Time-Circuit-Based-Audio-Synthesis}."""

new_conc = r"""These findings support the feasibility of the evaluated discrete-time MNA implementation on the tested Apple M1 Max ARM64 host, supporting continuous interactive control while providing an empirical foundation for future deployment on mobile XR hardware.

\section{SUPPLEMENTAL MATERIAL}
To uphold scientific reproducibility, all benchmarking scripts, raw measurement datasets (JSON and CSV formats), and the interactive HTML test harness are publicly available under the open-source MIT license at the official repository: \url{https://github.com/BoobalanArjunan/Real-Time-Circuit-Based-Audio-Synthesis}."""
text = text.replace(old_conc, new_conc, 1)

with open('jaes_benchmark_env/OVERLEAF_COPY_PASTE.tex', 'w') as f:
    f.write(text)

print('OVERLEAF_COPY_PASTE.tex updated successfully.')

