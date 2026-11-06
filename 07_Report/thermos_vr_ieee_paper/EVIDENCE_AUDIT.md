# EVIDENCE_AUDIT: Phase A (inspection and preservation) and Phase B (results audit)

Paper workspace: `07_Report/thermos_vr_ieee_paper/` (new; created 2026-10-21).
Project root: `G:\My Drive\ThermOS-VR` (Google Drive sync folder).
All Python was run with `python -B`. No existing file was modified.

## A. Repository inspection

| Item | Finding |
|---|---|
| Version control | **Not a Git repository** (`git status` → "not a git repository"). No branch or uncommitted-change state exists; integrity is tracked by checksum manifests. |
| Phase 1 documents (`11_Paper/`) | All 5 present and read: `literature_verification.md`, `claim_evidence_matrix.md`, `reference_candidates.md`, `results_plan.md`, `paper_outline.md` (plus `evidence_inventory.md` and the freeze manifest) |
| `03_Code/day5_modern_baselines/` | Present: 10 `.py`, 6 test files, `README.md`, `CONFIRMED_BUGS.md`, `AUDIT_FIXES.md` |
| `05_Results/v2_modern_baselines/` | Present: 6 files (benchmark, task results, tick trace, metric definitions, run metadata, first test log) |
| `05_Results/v2_sensitivity/` | Present: 5 files (results, task results, trace `.csv.gz`, metadata, validation log) |
| `06_Figures/v2_modern_baselines/` | Present: 25 PNG + `figure_manifest.csv` |
| `06_Figures/v2_sensitivity/` | **Does not exist.** The sensitivity figure must be created in Phase C. |
| `10_Backups/` | `v1_original_2026-10-21/`, `v2_pre_audit_fixes_2026-10-21/` |
| `07_Report/OS.docx` | Present (earlier report: problem statement, abstract, literature review, research gaps). Not modified, and not used as a paper source except to flag its citation errors. |
| Existing paper drafts | **None** (no `.tex`, `.bib` or paper `.docx` other than `OS.docx`), so no draft backup was needed |
| LaTeX toolchain | **Not installed**: pdflatex, latexmk, xelatex, lualatex, bibtex, biber and tectonic all NOT FOUND. Blocks compilation and the 15-page check (see `OPEN_ISSUES.md`). |

## B. Preservation

- **Phase 1 freeze:** `11_Paper/evidence_freeze_manifest_2026-10-21.sha256` (172 files) still verifies **172 / 172 OK**.
- **Phase 2 freeze:** `evidence/phase2_freeze_manifest.sha256` checksums **179 files**: the 172 above plus the 7 Phase-1 documents. It was taken before any Phase-2 analysis.
- **v1 and v2 baseline manifests:** both re-verified by `verify_outputs.py` (49 v1 files and 32 v2 baseline outputs unchanged).
- **New files** are written only inside `07_Report/thermos_vr_ieee_paper/`.

## C. Re-execution of the recorded validation (read-only)

Log: `evidence/rerun_existing_checks_log.txt` (2026-10-21T01:35).

| Check | Result | Matches the earlier record? |
|---|---|---|
| Unit tests (`python -B -m unittest discover -s tests`) | **Ran 42 tests, OK** | Yes (42 in the latest log) |
| `verify_outputs.py` | **ALL CHECKS PASSED**: 64 runs, 1,024 metrics recomputed, 64 fresh re-runs, 768 plotted values, 25 / 25 PNGs pixel-identical, 1,798 trace points, 384 task rows (88 partial final ticks), 49 + 32 protected files unchanged | Yes |
| `verify_sensitivity.py` | **ALL SENSITIVITY CHECKS PASSED**: 1,024 runs, zero-overhead rows = benchmark (64 × 16), 6,144 task rows recomputed, 1,024 fresh re-runs, 81 protected files unchanged | Yes |

## D. Configuration coverage and schema (independent script)

Script: `evidence/evidence_checks.py`; output: `evidence/evidence_checks_output.txt`.

| Item | Result |
|---|---|
| Benchmark rows | **64** = 8 policies × 4 workloads × 2 DVFS settings, no duplicate configuration |
| Task rows | **384** = 64 × 6 |
| Sensitivity rows | **1,024** = 16 cost pairs ({0, 0.1, 0.25, 0.5}²) × 64, no duplicates |
| Missing values | **0** NaN cells in either results file |
| Metric definitions | `metric_definitions.csv` covers all 16 metric columns |
| Sensitivity extra columns | Migration Cost, Context Switch Cost, Migration Events Charged, Resume Events Charged, Total Overhead Work |

**Units, as defined in the code and metadata:**
- Time: abstract ticks.
- Temperature: model °C (uncalibrated).
- Heat: unit-less model term (w/100)(f/2.5)².
- Overhead costs: simulated work units (1.0 = one tick of work at 2.5 GHz).
- Counts: core-ticks or events.

## E. Recalculated key comparisons

24 of 25 checks pass; the 1 FAIL is a deliberately retained record of a documented discrepancy (item F1). The full list with values is in `CLAIM_EVIDENCE_TABLE.md`.

Highlights (all recomputed from the CSVs):
- **ThermOS-VR vs FCFS:** identical in all 128 metric comparisons (8 configurations × 16 metrics).
- **EDF variants:** an EDF variant attains the minimum waiting time and total tardiness in all 16 (DVFS × workload × metric) cases. The EDF vs TA-EDF gap is at most 0.5 ticks of waiting and 2 ticks of tardiness.
- **Thermal, DVFS on:** HOT core-ticks are 0 in all 32 runs. With DVFS off they are non-zero only in the HOT workload (RR 18, TA-EDF 26, EDF-NP 35, FCFS = Priority = ThermOS-VR 64, EDF 65, EEVDF 104).
- **Heat, DVFS off:** total model heat is identical across policies (18.20, 58.00, 205.00, 359.25).
- **Sensitivity:** with migration cost ≥ 0.1, TA-EDF has more tardiness and a longer makespan than EDF in **96 of 96** matched configurations, matched on DVFS, workload, migration cost and context-switch cost. Differences: tardiness +1 to +365, makespan +2 to +121.

## F. Discrepancies found (documented, not silently corrected)

| # | Discrepancy | Evidence | Resolution for the paper |
|---|---|---|---|
| F1 | `AUDIT_FIXES.md`, `README.md` and Phase-1 documents state TA-EDF stays "1.0–2.5 °C" below EDF's peak in Normal / Sustained / HOT at every cost. The recomputed minimum is **0.99 °C** (HOT, DVFS on, zero overhead), so the wording is a rounding overstatement. | check `C6.5-as-documented` FAIL; `C6.5-exact` PASS (0.99–2.49) | The paper uses **0.99–2.49 °C**. The frozen documents are left unchanged; logged in `OPEN_ISSUES.md`. |
| F2 | Phase 1 classified POD-TAS (Dowling et al.) as an arXiv preprint only. It **is published**: *Future Generation Computer Systems*, vol. 166, 2025, Art. 107687 (ScienceDirect PII S0167739X24006514). | web verification (see `REFERENCE_AUDIT.md`) | Cite the journal version; the DOI is still to be confirmed |
| F3 | `metric_definitions.csv` describes Migrations as "resumed on a different core"; the engine also counts moves between consecutive ticks. | `sim_engine.py:_apply`; `verify_sensitivity.py` | Use the corrected definition in the paper |
| F4 | The first test log (`05_Results/v2_modern_baselines/test_and_verification_log.txt`) records 32 tests; the current suite has 42. | both logs | Cite 42 (current); the earlier log predates the audit fixes |

## G. Audit-only numbers made reproducible

Phase 1 cited three sets of numbers that existed only in session scratch. They are now reproduced by `evidence/reproduce_audit_probes.py` (output `evidence/audit_probes_output.txt`), and the values match the earlier records exactly:

| Probe | Result |
|---|---|
| P1 EDF vs independent reference simulator | 3,004 task sets × 3 core counts × 2 variants = **18,024 comparisons, 0 mismatches** |
| P2 EEVDF-inspired, DVFS on | **1 core:** 0 ineligible dispatches, max lag 0.73–0.94 slices. **2 cores:** **4 / 15 / 27 / 56** ineligible dispatches, max lag 2.26 / 3.55 / 7.67 / **22.59** slices (Normal / Burst / Sustained / HOT) |
| P3 TA-EDF idle insertion | **0** idle core-ticks with a waiting task in all 64 runs. Per DVFS setting: 3 (Sustained) + 28 (HOT) ticks with a hot core and a slack-rich task; 31 placements on a cooler core, 9 cases where the cores were already filled, 1 skip (HOT, t = 32, *Extreme Rendering*, slack 10.0, core 2 at 59.14 °C) |

## H. Statement of scope (for every downstream document)

- This is a deterministic Python simulation with two identical modelled cores, four workloads of six one-shot tasks, one run per configuration, uncalibrated thermal units and hypothetical overhead costs.
- No kernel was modified, and no hardware temperature, power, energy or latency was measured.
- EAS was not evaluated. The EEVDF variant is "EEVDF-inspired" only.
