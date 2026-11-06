# ThermOS-VR IEEE paper workspace

Paper: *Thermal-Aware Scheduling for AR/VR-Inspired Workloads: A Reproducible Simulation Study of EDF, a Thermal-Aware EDF Variant and Classical Baselines*. Authors: S. Gour, V. Gulgulia, Y. Tewari (VIT).

## Main outputs

- `ThermOS_VR_Research_Report.docx`: IEEE-style two-column Word paper (14 pages when exported by Word).
- `ThermOS_VR_Research_Report_from_DOCX.pdf`: the Word export of the DOCX.
- `ThermOS_VR_Research_Report.tex` + `references.bib` + `figures/`: IEEEtran conference source.
- `ThermOS_VR_Research_Report.pdf`: the LaTeX source compiled with Tectonic 0.17.0 (13 pages).
- `FINAL_SUBMISSION_CHECKLIST.md`: what is verified and what you must still do.

## Getting a final PDF

- **From Word:** open the `.docx` and use File → Save As → PDF. A 14-page export is already provided for review.
- **From LaTeX (Overleaf):** upload the `.tex`, the `.bib` and the `figures/` folder, select pdfLaTeX, then compile (Overleaf runs BibTeX automatically) and check the page count.
- **From LaTeX (Tectonic):** `tectonic ThermOS_VR_Research_Report.tex`. It runs BibTeX automatically and downloads `IEEEtran` on first use. Tectonic uses XeTeX, so the layout may differ slightly from pdfLaTeX.
- **From LaTeX (locally):** `pdflatex ThermOS_VR_Research_Report`, `bibtex ThermOS_VR_Research_Report`, then `pdflatex` twice. Requires `IEEEtran.cls` and `IEEEtran.bst`.

## Rebuilding

All commands are run from this folder.

- `python -B build_paper.py` regenerates the DOCX, TeX, BibTeX and `build_report.txt`. It needs `python-docx`, `pandas`, and the result CSVs.
- `python -B figures/make_paper_figures.py` regenerates the two new figures, then validates them against the CSV.
- `python -B make_ledger.py` regenerates `CITATION_CLAIM_LEDGER.csv`.
- `python -B check_tex_static.py` runs static LaTeX checks.
- `python -B evidence/evidence_checks.py` and `python -B evidence/reproduce_audit_probes.py` recompute the evidence.

`python-docx` was installed only in a session scratch folder, not system-wide; install it with `pip install python-docx` if you rebuild.

## Single source of truth

- **Text:** `paper_content.py`, rendered by `build_paper.py` to both DOCX and TeX.
- **References:** `paper_refs.py`, which generates both `references.bib` and the DOCX reference list.
- **Tables:** generated from `05_Results/v2_modern_baselines/*.csv` and `05_Results/v2_sensitivity/sensitivity_results.csv`.
- **Prose numbers:** asserted against those CSVs at build time.

## Evidence and audits (this folder)

`EVIDENCE_AUDIT.md`, `CLAIM_EVIDENCE_TABLE.md`, `REFERENCE_AUDIT.md`, `OPEN_ISSUES.md` and `evidence/` (freeze manifest, re-run logs, check scripts and outputs).

Note: `OPEN_ISSUES.md` reflects the state after Phase B. Its decisions were superseded by the final instructions, which used the generic IEEE template, did not install LaTeX, and excluded HAMLET and the optional references.

## Known limitations

This is a simulation study: two identical modelled cores, four six-task workloads, deterministic single runs and an uncalibrated thermal model. See Section VIII of the paper and the checklist.
