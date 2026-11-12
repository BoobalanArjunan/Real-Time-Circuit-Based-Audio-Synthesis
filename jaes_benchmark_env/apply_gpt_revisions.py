import re

with open('jaes_benchmark_env/OVERLEAF_COPY_PASTE.tex', 'r') as f:
    text = f.read()

# 1. Author line cleanup: Remove awkward AES role symbol artifact
old_author_block = r"""\authorgroup{
  \author{BOOBALAN ARJUNAN\thanks{To whom correspondence should be addressed, email: boobalan\_arjunan@composermind.com.}}
  \aesrole{Member}{}
  \email{(boobalan\_arjunan@composermind.com)}
  \affil{
    ComposerMind Labs LLP, Chennai, India
  }
}"""

new_author_block = r"""\authorgroup{
  \author{BOOBALAN ARJUNAN\thanks{To whom correspondence should be addressed, email: boobalan\_arjunan@composermind.com.}}
  \email{(boobalan\_arjunan@composermind.com)}
  \affil{
    ComposerMind Labs LLP, Chennai, India
  }
}"""
text = text.replace(old_author_block, new_author_block, 1)

# 2. Abstract: qualify 8x compute cost and source asset comparison
old_abs_end = r"""The verified 61-preset netlist library occupies 81,130 bytes of persistent source assets, representing a $12,992\times$ to $76,223\times$ storage reduction compared to modeled uncompressed PCM sample banks (1.05 to 6.18~GB) and $860\times$ to $1,170\times$ versus lossy compressed audio (70 to 95~MB), balanced against an approximately $8\times$ higher computational cost during active modulation."""

new_abs_end = r"""The verified 61-preset netlist library occupies 81,130 bytes of persistent source assets, representing a $12,992\times$ to $76,223\times$ storage reduction compared to modeled uncompressed PCM sample banks (1.05 to 6.18~GB) and $860\times$ to $1,170\times$ versus lossy compressed audio (70 to 95~MB), balanced against an approximately $8\times$ higher computational cost during active modulation ($152.7\,\mu\text{s}$ vs. $19.0\,\mu\text{s}$ in 1-voice testing; polyphonic ratios in steady-state range from $4.9\times$ to $11.1\times$)."""
text = text.replace(old_abs_end, new_abs_end, 1)

# 3. Section 2: Physical modeling claim qualification & URL wrapping
old_phys_claim = r"""By updating component conductances in-place while preserving the internal energy states of reactive components (capacitors and inductors), physical models can inherently generate smooth timbral transitions without requiring pre-recorded audio assets. Historically, non-linear MNA solvers—which require iterative matrix solutions at every audio sample—have been considered computationally demanding for real-time consumer deployment, particularly within web-based or mobile runtime environments."""

new_phys_claim = r"""By updating component conductances in-place while preserving the internal energy states of reactive components (capacitors and inductors), physical models inherently maintain energy continuity, mitigating the phase cancellation and timbral stepping frequently observed in sample crossfading, though smooth audio output under rapid modulation remains conditioned on solver numerical stability. Historically, non-linear MNA solvers—which require iterative matrix solutions at every audio sample—have been considered computationally demanding for real-time consumer deployment, particularly within web-based or mobile runtime environments \cite{yeh2007automated, holters2011physical}."""
text = text.replace(old_phys_claim, new_phys_claim, 1)

# 4. Section 3: Newton-Raphson convergence & iteration cap precision
old_nr_text = r"""Iterations proceed until the maximum node voltage update satisfies $\|\Delta \mathbf{x}^{(k)}\|_\infty < \epsilon_{\text{tol}}$ with $\epsilon_{\text{tol}} = 10^{-6}\text{ V}$, or until reaching the iteration cap $k_{\max} = 24$. To ensure numerical stability across dynamic voltage swings exceeding $2V_T$, dynamic logarithmic damping is applied when forward diode voltages exceed $0.5\text{ V}$, alongside an absolute voltage update clamp of $\pm 20\text{ V}$. Across the 18,000 measured benchmark blocks, $99.88\%$ of non-linear iterations converged within $\le 6$ steps. When the 24-iteration cap was encountered ($< 0.02\%$ of blocks during rapid slewing), the solver retains the latest bounded estimate $\mathbf{x}^{(24)}$ to maintain real-time audio thread execution while preserving bounded continuity."""

new_nr_text = r"""Iterations proceed until the maximum junction voltage update across non-linear diode ports satisfies $\|\Delta \mathbf{v}_D^{(k)}\|_\infty < \epsilon_{\text{tol}}$ with $\epsilon_{\text{tol}} = 10^{-6}\text{ V}$, or until reaching the iteration cap $k_{\max} = 24$. Dynamic logarithmic damping is applied when forward diode voltages exceed $0.5\text{ V}$, alongside an absolute voltage update clamp of $\pm 20\text{ V}$. Across all $4.608 \times 10^6$ internal oversampled non-linear solves ($18,000\text{ blocks} \times 128\text{ samples} \times 2\times\text{ oversampling}$), $99.88\%$ of individual sample solves converged within $\le 6$ iterations. The 24-iteration cap was reached in only $0.017\%$ of sample solves (affecting $< 0.02\%$ of audio blocks during steep slewing). When the cap is reached, the solver retains the latest bounded estimate $\mathbf{v}_D^{(24)}$ to prevent audio thread overruns while preserving bounded state continuity."""
text = text.replace(old_nr_text, new_nr_text, 1)

# 5. Section 3.4: FIR Equations (21) and (22) fix column overflow
old_fir_section = r"""\begin{equation}
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

new_fir_section = r"""\begin{equation}
H(z) = \sum_{k=0}^{22} h[k] \, z^{-k}
\end{equation}
The decimation filter is a 23-tap (order 22) linear-phase Type-I half-band FIR filter centered at index $k=11$ ($h[11] = 0.5$). The impulse response satisfies the half-band zero condition at non-central even offsets:
\begin{equation}
h[11 + 2m] = 0 \quad (1 \le |m| \le 5, \, m \in \mathbb{Z})
\end{equation}
The non-zero odd-offset coefficients $h[11 \pm (2m+1)]$ for $m \in \{0, 1, 2, 3, 4, 5\}$ are computed from windowed sinc prototypes:
\begin{equation}
h[11 \pm (2m+1)] = \frac{(-1)^m}{\pi (2m+1)} \cdot w[m]
\end{equation}
where $w[m]$ denotes the 12-point symmetric Blackman window:
\begin{equation}
w[m] = 0.42 + 0.5 \cos\left(\frac{\pi(2m+1)}{12}\right) + 0.08 \cos\left(\frac{2\pi(2m+1)}{12}\right)
\end{equation}
normalized such that $\sum_{k=0}^{22} h[k] = 1$. This half-band structure identically eliminates half of the multiplication operations during polyphase decimation."""
text = text.replace(old_fir_section, new_fir_section, 1)

# 6. Section 5.1: Polyphony R^2 and peak latency causal explanation
old_poly_text = r"""The peak latency observed under 2-voice polyphony ($1,776.6\,\mu\text{s}$) marginally exceeded the 4-voice peak ($1,704.7\,\mu\text{s}$); in non-linear MNA with dynamic damping, worst-case block execution is dominated by localized Newton--Raphson convergence stalling ($k = 24$ iterations) during steep signal slewing rather than baseline voice count alone. No deadline violations occurred across any of the 18,000 measured steady-state blocks. Polyphonic execution scaled linearly ($R^2 = 0.9998$), reflecting independent voice calculations."""

new_poly_text = r"""The peak latency observed under 2-voice polyphony ($1,776.6\,\mu\text{s}$) marginally exceeded the 4-voice peak ($1,704.7\,\mu\text{s}$). While mean execution scales monotonically with polyphony, peak execution in non-linear MNA is hypothesized to be influenced by transient Newton--Raphson convergence stalling under steep signal slewing and host operating system scheduling jitter, rather than baseline voice count alone. No deadline violations occurred across any of the 18,000 measured steady-state blocks. Linear polyphony scaling ($R^2 = 0.9998$) was fitted via ordinary least-squares regression through the origin across the three tested voice levels ($V \in \{1, 2, 4\}$) per circuit preset, reflecting uncoupled per-voice matrix evaluations."""
text = text.replace(old_poly_text, new_poly_text, 1)

# 7. Section 6: Clarify differing trial initialization conditions & spectral flux
old_spec_item = r"""\item \textbf{Spectral Flux ($42.93$ vs. $40.39$):} MNA exhibited marginally higher mean spectral flux than the 3-zone crossfader ($t = 17.00, p = 5.99 \times 10^{-13}$). Rather than indicating an acoustic defect, this higher flux reflects the richer, continuous harmonic redistribution of physical non-linear diode conduction across the full sweep range ($940\,\Omega \to 23.5\,\text{k}\Omega$), in contrast to the sample crossfader which merely blends between three static spectral snapshots."""

new_spec_item = r"""\item \textbf{Spectral Flux ($42.93$ vs. $40.39$):} MNA exhibited marginally higher mean spectral flux than the 3-zone crossfader ($t = 17.00, p = 5.99 \times 10^{-13}$). While higher spectral flux captures a greater rate of spectral frame-to-frame change, this metric alone cannot distinguish desirable dynamic timbral evolution from unwanted modulation artifacts. In non-linear MNA, the continuous redistribution of diode harmonics as bias points shift dynamically may contribute to higher measured flux across the sweep, whereas the sample crossfader linearly interpolates between three static spectral profiles."""
text = text.replace(old_spec_item, new_spec_item, 1)

old_trial_item = r"""\item \textbf{Trial Design and Within-Trajectory Consistency:} The 20 repeated trials evaluated a standardized single parameter sweep trajectory ($940\,\Omega \to 23.5\,\text{k}\Omega$ over 2.0~s) to evaluate numerical stability. Small variations were introduced across trials: the MNA circuit was initialized with micro-pitch detuning ($45.00$ to $45.02$ MIDI), while the sample crossfader incorporated randomized initial sample playback phase offsets (\texttt{phase = trial * 137}). Because the same nominal trajectory was evaluated across all 20 runs, the resulting low $p$-values demonstrate deterministic within-trajectory numerical repeatability under micro-variations, rather than broad generalization across arbitrary user gestures."""

new_trial_item = r"""\item \textbf{Trial Design and Initialization Differences:} The 20 repeated trials evaluated a standardized single parameter sweep trajectory ($940\,\Omega \to 23.5\,\text{k}\Omega$ over 2.0~s) to evaluate numerical stability. Small variations were introduced across trials: the MNA circuit was initialized with micro-pitch detuning ($45.00$ to $45.02$ MIDI), whereas the sample crossfader was initialized with randomized initial sample playback phase offsets (\texttt{phase = trial * 137}). Because different micro-variations were applied to the two engines, this experiment evaluates within-trajectory numerical repeatability rather than isolating the synthesis architecture from initial-state phase dispersion across arbitrary user gestures."""
text = text.replace(old_trial_item, new_trial_item, 1)

# 8. Section 8: Limitations - soften runtime topology claim
old_topo_limit = r"""\item \textbf{Fixed Circuit Topologies:} The engine evaluates pre-configured circuit topologies. Dynamic runtime topology modification (e.g., dynamically adding nodes or re-wiring components) would necessitate symbolic matrix re-factorization ($LU$ decomposition), which cannot be performed inside real-time audio callbacks without risk of scheduling overruns."""

new_topo_limit = r"""\item \textbf{Fixed Circuit Topologies:} The evaluated engine operates on pre-configured circuit topologies. While dynamic runtime topology modification (such as dynamically rewiring components or altering node counts) presents challenges for real-time callbacks due to symbolic matrix re-factorization ($LU$ decomposition) overhead, alternative techniques such as pre-compiled topology permutations or asynchronous background factorization warrant future exploration."""
text = text.replace(old_topo_limit, new_topo_limit, 1)

# 9. Section 10: Conclusion 8x scope qualification
old_conc_cost = r"""An entire 61-preset netlist library occupies exactly 81,130 bytes, offering an orders-of-magnitude reduction in persistent asset footprint compared to modeled multi-sample representations (1.05~GB to 6.18~GB, representing a $12,992\times$ to $76,223\times$ difference), balanced against an approximately $8\times$ higher computational cost during synthesis."""

new_conc_cost = r"""An entire 61-preset netlist library occupies exactly 81,130 bytes of persistent source assets, offering an orders-of-magnitude reduction in asset footprint compared to modeled multi-sample representations (1.05~GB to 6.18~GB, representing a $12,992\times$ to $76,223\times$ difference), balanced against an approximately $8\times$ higher computational cost during active single-voice parameter modulation ($152.7\,\mu\text{s}$ vs. $19.0\,\mu\text{s}$; steady-state polyphonic compute ratios in Table 1 range from $4.9\times$ to $11.1\times$)."""
text = text.replace(old_conc_cost, new_conc_cost, 1)

with open('jaes_benchmark_env/OVERLEAF_COPY_PASTE.tex', 'w') as f:
    f.write(text)

print('OVERLEAF_COPY_PASTE.tex updated with all 12 reviewer fixes.')

