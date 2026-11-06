# OPEN_ISSUES (after Phase A and Phase B)

Status at 2026-10-21. Items are ordered by how much they block later phases.

## Blockers

| # | Issue | Impact | Proposed resolution | Needs decision? |
|---|---|---|---|---|
| B1 | **No LaTeX toolchain** (pdflatex, latexmk, bibtex, biber and tectonic all absent) | The PDF cannot be compiled and the **15-page limit cannot be verified**. The paper cannot be called submission-ready. | (a) Install a TeX distribution (e.g. MiKTeX or TeX Live), or (b) download the single-binary **Tectonic** into a scratch folder, or (c) compile on Overleaf from the generated sources. Until then, write `paper_draft.tex` + `references.bib` and mark compilation as **NOT DONE**. | **Yes**: choose (a), (b) or (c). Installing software changes your machine, so it needs your approval. |
| B2 | **IEEE template files are not in the project** (`IEEEtran.cls`, `IEEEtran.bst`) | Needed to compile | Obtain the official IEEE conference template (IEEE Template Selector / CTAN `ieeetran`). Most TeX distributions and Overleaf already include `IEEEtran`. **I will not hand-write a copy of the class.** | Part of B1 |

## Evidence discrepancies (documented; frozen files left unchanged)

| # | Issue | Resolution |
|---|---|---|
| E1 | "TA-EDF 1.0–2.5 °C below EDF" (`AUDIT_FIXES.md`, `README.md`, Phase-1 documents) is a rounding overstatement; the exact minimum is **0.99 °C** | The paper uses **0.99–2.49 °C** (check `C6.5-exact`). Optionally add an erratum line to the day5 docs later; **not done**, because the docs are frozen evidence. |
| E2 | POD-TAS was listed as a preprint in Phase 1; it is published in *FGCS* 2025 | Corrected in `REFERENCE_AUDIT.md` |
| E3 | The `Migrations` definition in `metric_definitions.csv` understates what is counted | The paper uses the corrected definition |
| E4 | The first validation log shows 32 tests; the current suite has 42 | The paper cites the current re-run (42 tests, OK) |
| E5 | Jeffay et al.: the Crossref/DBLP title says "period"; the printed title says "periodic". Crossref has no issued year. | Use the printed title and 1991 (from the proceedings name); note it in the `.bib` comments |

## Items to do in later phases

| # | Phase | Item |
|---|---|---|
| L1 | C | **Create `06_Figures/v2_sensitivity/`** with a new plotting script (TA-EDF vs EDF tardiness against migration cost, per workload, DVFS on/off), a manifest and a validation check. The folder does not exist yet. |
| L2 | C | `FINAL_TABLES.md` and `FIGURE_PLAN.md` (deferred to Phase C as per the execution order; all their numbers are already confirmed in `CLAIM_EVIDENCE_TABLE.md`) |
| L3 | C | **Architecture figure:** draw a new, non-data diagram (tick order and data flow). No existing file. |
| L4 | D | Every reference in the bibliography must be cited in the body; remove any left uncited (see the proposal in `REFERENCE_AUDIT.md` §D) |
| L5 | D | `ORIGINALITY_AUDIT.md`, `CITATION_CLAIM_LEDGER.csv`, `AUTHOR_VERIFICATION_CHECKLIST.md`, `AI_DISCLOSURE_DRAFT.md`, `README.md`, `paper_draft.tex`, `references.bib` |
| L6 | E | Page count, compile log, final checksum comparison against `evidence/phase2_freeze_manifest.sha256` |

## Decisions needed from the authors

1. **Toolchain** (B1): install a TeX distribution, use portable Tectonic, or compile on Overleaf?
2. **HAMLET (2026)**: include it in Related Work? Only its abstract was available.
3. **Optional references** (Buttazzo textbook, JOSS, Mittal, ADPF): include or leave out? The default is to leave them out unless a body citation needs them.
4. **Erratum** for E1 in the day5 docs: add a separate errata file next to them, or leave it documented only here? The default is to document it here only.
5. **Conference**: none named, so the generic IEEE conference template will be used. No event name, address, e-mail or deadline will be invented. Please supply author e-mails only if you want them on the paper.

## Limitations to state in the paper (already confirmed)

- Deterministic simulation; one run per configuration; no statistics.
- Two identical modelled cores; no heat transfer between cores; uncalibrated thermal model.
- Six one-shot tasks per workload; deadlines partly infeasible in three workloads.
- Hypothetical overhead costs; no measured latency.
- EAS not evaluated; EEVDF-inspired only; no hardware, power or energy measurement.
