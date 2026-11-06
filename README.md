# ThermOS-VR

A reproducible Python simulation study of thermal-aware CPU scheduling for AR/VR-inspired workloads, with the accompanying IEEE-style paper, presentation and evidence audits.

Paper: *Thermal-Aware Scheduling for AR/VR-Inspired Workloads: A Reproducible Simulation Study of EDF, a Thermal-Aware EDF Variant and Classical Baselines*. Authors: S. Gour, V. Gulgulia, Y. Tewari (VIT).

> **Simulation outputs only.** Every temperature, frequency, heat value and throttling count here comes from a simplified discrete-time model. Nothing is a measured CPU, SoC or headset value. The model has no power, voltage or energy, and "heat" is a unit-less model term. The project does not modify a kernel or run on a headset.

## Objective

The study asks how scheduling policy, dynamic voltage and frequency scaling (DVFS) and task-migration overhead jointly affect responsiveness and simulated thermal behaviour under AR/VR-inspired workloads.

## Features

- **One shared simulation engine** for all policies, with one tick order and one set of metric definitions.
- **Eight scheduling policies:** FCFS, Priority, Round Robin, the original ThermOS-VR heuristic, non-preemptive EDF (EDF-NP), preemptive global EDF, Thermal-aware EDF (TA-EDF, this project's own variant) and an EEVDF-inspired weighted-fair policy.
- **Two DVFS settings:** fixed 2.5 GHz (`off`) and a four-level `hysteresis` governor.
- **Four workloads** of six one-shot tasks each: Normal VR, Burst VR, Sustained Thermal and HOT Thermal.
- **64-run benchmark** (8 policies × 4 workloads × 2 DVFS settings) with zero overhead.
- **1,024-run overhead sensitivity experiment** over 16 migration and context-switch cost pairs.
- **Automated verification:** unit and equivalence tests, metrics recomputed from raw traces, fresh re-runs compared with stored results, figures compared pixel by pixel, and SHA-256 checks of protected files.
- **Overwrite protection:** scripts that generate output refuse to write into a non-empty folder unless given `--overwrite`.
- **Paper pipeline:** one source generates the DOCX and LaTeX versions, with tables generated from the result CSVs and prose numbers asserted against them at build time.

EAS (Linux Energy-Aware Scheduling) is **not implemented**, because the model has no asymmetric cores or energy model.

## Key findings

All findings apply to this deterministic model, with one run per configuration and six tasks per workload. No difference can be called statistically significant.

- **ThermOS-VR v1 behaves exactly like FCFS** under the same DVFS setting, on every metric and workload. Its v1 thermal improvements came from DVFS, not its core-selection score.
- **The preemptive EDF variants** (EDF and TA-EDF) have the lowest or joint-lowest average waiting time and total tardiness at zero overhead, on all four workloads and under both DVFS settings.
- **With free migrations,** TA-EDF matches EDF's responsiveness (within ±0.5 ticks of waiting and ±2 of tardiness) and has a lower simulated peak temperature on all four workloads (0.08–2.49 °C).
- **At a migration cost of 0.1 work units or more,** TA-EDF has more tardiness and a longer makespan than EDF in all 96 tested configurations. It stays 0.99–2.49 °C below EDF's peak in Normal, Sustained and HOT, but is 0.7–3.9 °C above it in Burst VR.
- **TA-EDF's idle-insertion rule never idled a core** in the benchmark, so that mechanism is effectively untested. The differences from EDF come from migration-based coolest-core placement.
- **The EEVDF-inspired policy has no fairness or lag guarantee on two cores,** and it is not an implementation of Linux EEVDF.
- **The v1 Thermal-DVFS results are invalid** because of a double-assignment bug. Do not cite those rows in `05_Results/experiment_results.csv` or the v1 figures as a baseline.

The full list of supported and unsupported claims is in [AUDIT_FIXES.md](03_Code/day5_modern_baselines/AUDIT_FIXES.md).

## Technology stack

- **Language:** Python. The recorded results were verified with Python 3.14.0 on Windows 11.
- **Simulation and analysis:** Python standard library, pandas, NumPy.
- **Figures:** matplotlib.
- **Tests:** Python `unittest`.
- **Paper and slides:** python-docx, python-pptx, LaTeX (IEEEtran) and BibTeX.

## Architecture

The v2 engine in `03_Code/day5_modern_baselines/` reuses the v1 `Process`, `Core` and `ThermalModel` classes and the v1 workloads unchanged.

```
day1: process.py, core.py, workloads.py ─┐
day2: thermal_model.py ──────────────────┤
                                         ▼
policies.py ──► sim_engine.py ──► metrics_v2.py ──► run_benchmark.py ──► 05_Results/v2_modern_baselines/
                     │                                     │                    │
                     ▼                                     ▼                    ▼
             overhead_engine.py ──► run_sensitivity.py   plot_results.py   verify_outputs.py
                                          │                │
                                          ▼                ▼
                       05_Results/v2_sensitivity/    06_Figures/v2_modern_baselines/
```

**Tick order:** dispatch → execute (`frequency / 2.5` work units) → thermal update → DVFS → `t += 1` → completions → log.

**Model:**
- **Cores:** two identical cores. They are labelled Performance and Efficiency, but this is not real heterogeneity, and no heat moves between them.
- **Thermal:** ambient 25 °C, start 45 °C, heat `(w/100)(f/2.5)²` per busy tick and cooling `0.02(T−25)`.
- **Deadlines:** soft. Late tasks run to completion.

The full model, policy definitions and metric definitions are in the [day5 README](03_Code/day5_modern_baselines/README.md).

## Folder structure

```
ThermOS-VR/
├── 01_Research_Papers/        Source papers (third-party PDFs)
├── 03_Code/
│   ├── day1_basic_scheduler/  v1: process, core and workload classes
│   ├── day2_thermal_model/    v1: thermal model and its test scripts
│   ├── day3_thermos_scheduler/ v1: ThermOS-VR and thermal-DVFS schedulers
│   ├── day4_experiments/      v1: baselines, experiment runner, graphs
│   ├── day5_modern_baselines/ v2: engine, policies, experiments, verifiers, tests/
│   └── v1_tools/              Working replacements for the broken v1 scripts
├── 05_Results/
│   ├── experiment_results.csv v1 results (contains invalid Thermal-DVFS rows)
│   ├── v2_modern_baselines/   64-run benchmark results and metadata
│   └── v2_sensitivity/        1,024-run sensitivity results and validation log
├── 06_Figures/                v1 figures
│   └── v2_modern_baselines/   25 v2 figures and manifest
├── 07_Report/                 Project report, presentation and notes
│   └── thermos_vr_ieee_paper/ Paper sources, build scripts, audits, evidence/, figures/
├── 10_Backups/                Frozen v1 and pre-audit v2 snapshots with checksums
├── 11_Paper/                  Paper planning, literature checks, evidence freeze manifest
├── README.md
└── requirements.txt
```

The local folders `02_Research_Notes/`, `04_Experiments/`, `08_Presentation/`, `09_References/` and `03_Code/final/` are empty, so Git does not track them.

## Installation

```
git clone <repository-url>
cd ThermOS-VR
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

`.gitattributes` disables line-ending conversion so that the checksum checks keep working. Keep this setting if you copy or re-host the project.

## Usage

Run these from `03_Code/day5_modern_baselines/`. The `-B` flag stops Python writing `__pycache__` files into the v1 folders.

```
python -B run_benchmark.py   [--overwrite]   # 64 runs   -> 05_Results/v2_modern_baselines/
python -B plot_results.py    [--overwrite]   # 25 PNGs   -> 06_Figures/v2_modern_baselines/
python -B run_sensitivity.py [--overwrite]   # 1024 runs -> 05_Results/v2_sensitivity/
```

Without `--overwrite`, these scripts exit with code 2 and change nothing if the output folder already has files.

### Running the v1 code

The v1 code is frozen for provenance, so its known bugs stay in place. They are listed in [CONFIRMED_BUGS.md](03_Code/day5_modern_baselines/CONFIRMED_BUGS.md). Use the working replacements in `03_Code/v1_tools/`, and run them from that folder:

| Instead of | Run | What is different |
|---|---|---|
| `day4_experiments/experiment_runner.py` | `python -B run_v1_experiments.py --output <file.csv> [--overwrite]` | Writes only to the named file and deletes nothing. The original **deletes `05_Results/experiment_results.csv` every time it runs**, so do not run it. |
| `day4_experiments/check_thermos_dvfs.py` | `python -B check_thermos_dvfs.py [--workload "HOT Thermal Workload"]` | Runs and writes no files. The original crashes on a missing argument. |
| `day1_basic_scheduler/main.py` | `python -B run_day1_fcfs.py` | Imports the FCFS scheduler from `fcfs_basic.py`. The original imports a module that does not exist in day1. |

The replacements fix how the scripts run, not the v1 scheduling logic. The Thermal-DVFS rows from `run_v1_experiments.py` still reproduce the invalid v1 results.

### Rebuilding the paper

Run these from `07_Report/thermos_vr_ieee_paper/`. See that folder's [README](07_Report/thermos_vr_ieee_paper/README.md) for details.

```
python -B build_paper.py                # DOCX, TeX, BibTeX and build_report.txt
python -B figures/make_paper_figures.py # the two paper-specific figures
python -B make_ledger.py                # CITATION_CLAIM_LEDGER.csv
python -B check_tex_static.py           # static LaTeX checks
```

`build_paper.py` also needs python-docx. To compile the LaTeX source, run `tectonic ThermOS_VR_Research_Report.tex` or use Overleaf. `IEEEtran.cls` and `IEEEtran.bst` are not in this repository, but both tools provide them.

## Testing

From `03_Code/day5_modern_baselines/` (these commands are read-only):

```
python -B -m unittest discover -s tests -v
python -B verify_outputs.py
python -B verify_sensitivity.py
```

From `03_Code/v1_tools/`. These tests also check that the safe runner reproduces `05_Results/experiment_results.csv` byte for byte:

```
python -B -m unittest test_v1_tools -v
```

From `07_Report/thermos_vr_ieee_paper/`:

```
python -B check_tex_static.py
```

To check the frozen files, run these from the repository root:

```
sha256sum -c 11_Paper/evidence_freeze_manifest_2026-10-21.sha256
sha256sum -c 07_Report/thermos_vr_ieee_paper/evidence/phase2_freeze_manifest.sha256
```

`evidence/evidence_checks.py` records 24 of 25 checks passing. The one failure is kept deliberately as a record of the superseded "1.0–2.5 °C" wording, which the paper corrects to 0.99–2.49 °C.

## Limitations and open items

- Each configuration is a single deterministic run with no variance, and each workload has only six one-shot tasks.
- The thermal model is uncalibrated, ticks have no real-time length, and overhead costs are hypothetical rather than measured latencies.
- Deadlines in the Sustained and HOT workloads cannot be met by any policy, so deadline misses stay at 4–6 of 6. Total tardiness is reported because it still separates the policies.
- The LaTeX paper compiles to 13 pages with Tectonic, and a 14-page PDF exported from Word is also included. It has not been compiled with pdfLaTeX, so the layout may differ slightly on Overleaf.
- Remaining pre-submission tasks are in [FINAL_SUBMISSION_CHECKLIST.md](07_Report/thermos_vr_ieee_paper/FINAL_SUBMISSION_CHECKLIST.md).

## License

The source code in `03_Code/` is available under the [MIT License](LICENSE). The license does not cover anything else in this repository, including the paper, report, presentation, results and figures. The PDFs in `01_Research_Papers/` belong to their respective authors and publishers.
