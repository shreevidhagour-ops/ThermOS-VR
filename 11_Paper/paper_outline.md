# Paper Outline: 15-page IEEE-style paper (preparation phase 1)

Prepared 2026-10-21. **Not a draft:** headings, intended content, evidence pointers and page budgets only. Claim IDs → `claim_evidence_matrix.md`; table and figure IDs → `results_plan.md`; reference IDs → `reference_candidates.md`.

## Open question: please confirm before drafting

**Do the 15 pages include references?** The submission instructions are not in the project.
- The budget below assumes the **IEEE two-column conference template with references included** in the 15 pages.
- If references are excluded, add about 1.5 pages to Results and Discussion.
- Also confirm: the template (conference vs journal, e.g. IEEEtran), author/affiliation block, any appendix allowance, and whether an artifact or code link is permitted.

## Proposed title (choose one)

1. *Thermal-Aware Scheduling for AR/VR-Inspired Workloads: A Reproducible Simulation Study of EDF, a Thermal-Aware EDF Variant and Classical Baselines*
2. *What Really Cools the Core? Re-evaluating a Thermal-Aware Scheduler for AR/VR Workloads in a Deterministic Simulator*

Both titles avoid implying hardware results, real headsets or energy savings. The original project title ("…for Reducing Heat in AR/VR Gaming") overstates what the evidence supports.

## Abstract plan (~200 words, 0.25 page)

1. **Problem (C-motivation):** sustained AR/VR workloads heat mobile processors; throttling hurts responsiveness. Cite B13 (Zhang et al., AIVR 2020) for measured AR/VR thermal behaviour.
2. **What we did:** a deterministic Python simulator with 2 identical modelled cores, a lumped thermal model and a threshold DVFS governor. It compares 8 policies (FCFS, Priority, RR, the original ThermOS-VR, EDF-NP, EDF, our TA-EDF, an EEVDF-inspired policy) on 4 workloads of 6 one-shot tasks, plus a 1,024-run overhead sensitivity study.
3. **Key findings:**
   - ThermOS-VR ≡ FCFS once both use the same governor (C3.1).
   - The EDF variants give the lowest or tied-lowest waiting and tardiness (C5.1).
   - TA-EDF lowers the simulated peak relative to EDF by 0.08–2.49 °C at zero overhead (C7.7), but loses to EDF on tardiness once migrations cost ≥ 0.1 tick (C6.2).
4. **Honest scope:** simulation only; no hardware, energy or statistical claims.

## Keywords

Thermal-aware scheduling; earliest deadline first; dynamic voltage and frequency scaling; AR/VR workloads; discrete-event simulation; reproducibility.

---

## Section plan and page budget (15 pages, references included)

| # | Section | Pages | Content | Evidence / references |
|---|---|---|---|---|
| — | Title, abstract, keywords | 0.5 | As above | — |
| I | **Introduction** | 1.25 | AR/VR responsiveness vs heat; throttling trade-off; research question ("Can thermal-aware scheduling preserve responsiveness while reducing *simulated* thermal stress?"); contributions as a bulleted list (below); summary of findings, including negative ones | A21, A23–A25, B13; C3.1, C5.1, C6.2 |
| II | **Background and Related Work** | 2.0 | (a) Real-time scheduling: EDF, global multiprocessor EDF, non-preemptive EDF, CBS / SCHED_DEADLINE. (b) Proportional share and EEVDF; multiprocessor fairness. (c) Thermal management and DVFS: DTM, temperature-aware microarchitecture, thermal-aware scheduling, RT-TAS, POD-TAS. (d) Heterogeneous cores and Linux EAS. (e) Mobile and AR/VR thermal and performance studies; learning-based DVFS. Close with the gap: few reproducible, apples-to-apples comparisons with modern deadline baselines. | A1–A16, A19–A24, B1–B6, B8–B10, B13, B16 |
| III | **System Model and Assumptions** | 1.5 | Two identical cores (labels inherited from v1); tick-based time; lumped thermal equation and parameters (T2); governor thresholds and hysteresis; partial-tick rule; deadline semantics (soft real-time, absolute deadlines); what is **not** modelled (power, energy, heat transfer between cores, real capacities, frame periodicity) | C1.1–C1.5, C2.1–C2.3, C8.4; T2 |
| IV | **Scheduling Policies** | 2.0 | T3; precise rules for EDF / EDF-NP (ties, preemption, late tasks); **TA-EDF** (ours): urgency rule, coolest-core placement, hold-back rule with bounded delay; ThermOS-VR v1 score and why its deadline term cannot discriminate cores; EEVDF-inspired mechanisms vs simplifications; **why EAS is out of scope** (kernel-docs requirements); comparison with the real Linux mechanisms | C3.3, C5.5, C9.1–C9.5, C10.2; A4, A6, A9–A12 |
| V | **Experimental Methodology** | 1.5 | Workloads and feasibility (T1); 8 policies × 4 workloads × 2 DVFS settings = 64 runs; overhead sensitivity design (4 × 4 costs, charging rules, 1,024 runs); metric definitions (T4); fairness controls (shared engine, identical inputs); corrected v1 issues (short T11); verification (tests, independent recomputation, fresh re-runs, figure pixel checks, checksums; T12) | C1.5, C4.1–C4.3, C6.6, C6.7, C8.1–C8.2; A26, A27 |
| VI | **Results** | 3.25 | **A.** ThermOS-VR vs FCFS (C3.1–C3.2; T8, or text). **B.** Responsiveness, DVFS on (T5; Fig. waiting and/or tardiness). **C.** Simulated thermal outcomes, DVFS on and off (T6, T7; Fig. peak temperature, Fig. ≥ 60 °C, trace figure). **D.** TA-EDF mechanism analysis: migrations and idle insertion that never fired (C10.1, C10.4). **E.** Overhead sensitivity (T9, and T10 or text; F-new-1 if approved). **F.** EEVDF-inspired behaviour on two cores (C9.2) | Tables T5–T7, T9; 4–5 figures |
| VII | **Discussion and Threats to Validity** | 1.25 | Interpretation (why placement cannot cut total heat in a linear identical-core model; DVFS dominates; RR's "cool" result is interleaving). **Internal validity:** implementation checks; audit-only probes. **Construct validity:** simulated °C, model heat units, tick abstraction, Migrations wording. **External validity:** 6-task synthetic workloads, identical cores, no frame periodicity. **Conclusion validity:** no replication or statistics; ties | C7.4, C11.1–C11.4; A26 |
| VIII | **Limitations and Future Work** | 0.75 | Bulleted limitations (simulation only; identical cores; one-shot tasks; infeasible deadlines; hypothetical overheads; no energy model; EAS not evaluated; no hardware validation). Future work: periodic frame-task workloads with feasible deadlines; asymmetric cores with an energy model (EAS-style); thermal coupling; seeded randomised workloads with confidence intervals; trace-driven evaluation (e.g. ILLIXR); hardware validation | C11.x; A23, gap list D |
| IX | **Conclusion** | 0.5 | Answer the research question honestly: within this model, the deadline-aware order (EDF) helps responsiveness; DVFS, not core scoring, drives the thermal reduction; TA-EDF's placement offers a small simulated peak reduction that is sensitive to migration cost | C3.2, C5.1, C6.2 |
| — | **References** | 1.25 | About 35–40 entries (IEEE style), from Sections A and B of `reference_candidates.md` after the DOI checks | — |
| | **Total** | **15.0** | | |

### Proposed contributions list (each traced to evidence)

1. A unified, verified tick-based simulator in which 8 policies share identical inputs and metrics (C1.5, C5.5).
2. Evidence that the original ThermOS-VR score is equivalent to FCFS under equal DVFS, and correction of an invalid v1 baseline (C3.1, C4.1).
3. An evaluation of EDF variants and a thermal-aware EDF variant (TA-EDF, ours) on AR/VR-inspired workloads, with and without DVFS (C5, C7).
4. An overhead sensitivity analysis showing that TA-EDF's responsiveness parity depends on free migrations (C6.2).
5. A transparent account of limitations, including mechanisms that never activated (C10.1) and fairness guarantees that do not hold on two cores (C9.2).

### Figure and table budget

- **Main text:** 6 tables (T1, T3, T5, T6, T7, T9) at about 0.25–0.4 page each, and 4 figures (waiting or tardiness, peak temperature, ≥ 60 °C, HOT trace) at about 0.4 page each. Together these take roughly 3.5–4 pages, already inside the sections above (mostly V and VI).
- **If over budget:** drop the trace figure first, then merge T6 into T5.
- **Optional:** one architecture diagram (Section III).

---

## Items that need your decision before drafting

1. Whether references count toward the 15 pages; and the template.
2. Final title.
3. Whether to create **F-new-1** (sensitivity figure) with a new script writing to a new folder.
4. Whether to add the audit probes (EDF reference simulator, EEVDF two-core probe, idle-insertion breakdown) as **new shipped scripts**, so that those numbers become reproducible evidence rather than audit observations.
5. Whether to keep the project title wording "Reducing Heat in AR/VR Gaming" (not supported as worded).
6. Whether to drop P4 (Vangaru) and the unverified `OS.docx` item "Liu et al. (2021)".
