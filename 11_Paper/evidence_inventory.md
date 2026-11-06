# Evidence Inventory and Freeze (preparation phase 1)

Prepared 2026-10-21. Read-only inventory; nothing listed here was modified.

## Freeze record

- **`11_Paper/evidence_freeze_manifest_2026-10-21.sha256`** holds the SHA-256 of **172 files**: everything under `01_Research_Papers`, `03_Code`, `05_Results`, `06_Figures`, `07_Report` and `10_Backups`, excluding `desktop.ini` and `__pycache__`.
- It was taken **before** any phase-1 file was written.
- Re-check from the project root: `sha256sum -c --quiet 11_Paper/evidence_freeze_manifest_2026-10-21.sha256`

## Version control

- **Git: not available.** The project folder is not a Git repository (`git rev-parse` → "not a git repository"), so there is no branch, commit or uncommitted-change state to report.
- Integrity is tracked by the checksum manifests instead.

## Inventory

| Group | Location | Files | Notes |
|---|---|---|---|
| v1 source | `03_Code/day1_basic_scheduler`, `day2_thermal_model`, `day3_thermos_scheduler`, `day4_experiments` (`03_Code/final` is empty) | 24 `.py` | Original implementation. Known issues in `CONFIRMED_BUGS.md` (B1–B11). |
| v1 results | `05_Results/experiment_results.csv` | 1 | 20 rows (5 schedulers × 4 workloads). **Thermal-DVFS rows invalid (B1).** |
| v1 figures | `06_Figures/*.png` (root) | 23 | Produced from the v1 CSV. **Not for the paper.** |
| v2 source | `03_Code/day5_modern_baselines/` | 19 (10 `.py` + 6 files in `tests/` + 3 `.md` docs, excluding `desktop.ini`) | Engine, 8 policies, metrics, runners, verifiers, tests. Simulation sources unchanged since the benchmark (hashes match `run_metadata.json`). |
| v2 benchmark (64 runs, zero overhead) | `05_Results/v2_modern_baselines/` | 6 | `benchmark_results.csv` (64), `task_results.csv` (384), `tick_trace.csv`, `metric_definitions.csv`, `run_metadata.json` (2026-10-21T00:15:54), `test_and_verification_log.txt` |
| v2 figures | `06_Figures/v2_modern_baselines/` | 25 PNG + `figure_manifest.csv` | 24 metric figures (12 metrics × DVFS off/on) and 1 HOT trace figure. All 25 are pixel-identical to re-renders; the manifest holds 768 plotted values (24 figures × 32). |
| v2 sensitivity (1,024 runs) | `05_Results/v2_sensitivity/` | 5 | `sensitivity_results.csv` (1,024), `sensitivity_task_results.csv` (6,144), `sensitivity_tick_trace.csv.gz`, `sensitivity_metadata.json` (2026-10-21T00:49:49; Python 3.14.0, pandas 3.0.5, matplotlib 3.10.7, numpy 2.3.4), `validation_log_2026-10-21.txt` |
| Validation logs | `05_Results/v2_modern_baselines/test_and_verification_log.txt` (first validation: 32 tests); `05_Results/v2_sensitivity/validation_log_2026-10-21.txt` (latest: 42 tests OK, both verifiers passed, guards refuse, checksums OK) | 2 | The latest log supersedes the earlier one for test counts |
| Backups | `10_Backups/v1_original_2026-10-21/` (50 files incl. manifest); `10_Backups/v2_pre_audit_fixes_2026-10-21/` (14 files: pre-fix day5 sources and 2 checksum manifests) | 64 | Read-only |
| Report draft | `07_Report/OS.docx` | 1 | Problem statement, abstract, literature review (15 items; several metadata errors, see `literature_verification.md`), research gaps. No methods or results. |
| Research PDFs | `01_Research_Papers/` | 3 | P2 (POD-TAS, arXiv), P3 (MobiRL, ACM TACO), P4 (Vangaru, JCSTS). **`P1_HAMLET_2026.pdf` does not exist.** |
| Empty folders | `02_Research_Notes`, `04_Experiments`, `08_Presentation`, `09_References` | 0 | No bibliography (`.bib`, `.ris`) files anywhere in the project |

## Read in full or inspected for this phase

`AUDIT_FIXES.md`, `README.md`, `CONFIRMED_BUGS.md`, `run_metadata.json`, `metric_definitions.csv`, `benchmark_results.csv`, `task_results.csv`, `sensitivity_metadata.json`, `sensitivity_results.csv`, `figure_manifest.csv`, both validation logs (summary lines), `experiment_results.csv` (v1), and the three PDFs (text extraction).
