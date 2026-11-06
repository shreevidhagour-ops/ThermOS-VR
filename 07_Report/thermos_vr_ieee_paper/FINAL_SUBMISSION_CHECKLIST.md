# FINAL SUBMISSION CHECKLIST: ThermOS-VR IEEE paper

Status at 2026-10-21. ☑ = done and verified here; ☐ = **you must do or confirm before submitting**.

## 1. Deliverables

| File | Status |
|---|---|
| `ThermOS_VR_Research_Report.docx` | ☑ Built (python-docx). Exported through Microsoft Word: **14 pages** (US Letter, two columns, Times New Roman 10 pt, references included) |
| `ThermOS_VR_Research_Report_from_DOCX.pdf` | ☑ The Word export of the DOCX above (14 pages), for review |
| `ThermOS_VR_Research_Report.tex` | ☑ IEEEtran conference source. Compiles with Tectonic 0.17.0 with no errors; static checks pass |
| `ThermOS_VR_Research_Report.pdf` | ☑ The compiled LaTeX version: **13 pages**, within the 15-page limit. All 38 references and all cross-references resolve |
| `references.bib` | ☑ 38 entries, all VERIFIED in `REFERENCE_AUDIT.md`; every entry cited, every citation defined |
| `figures/` | ☑ 2 new figures (validated against the CSV) + 5 byte-identical copies of the v2 figures |
| `CITATION_CLAIM_LEDGER.csv` | ☑ 50 sentence-to-reference rows (all 38 references) with an author-check column |

## 2. What was verified (actually executed)

- ☑ **54 prose numbers asserted against the frozen CSVs** at build time (`build_report.txt`). The build stops if any number disagrees; one did during drafting (5.59 vs 5.58 °C) and was corrected.
- ☑ **All 8 tables are generated from the CSVs**, so none is typed by hand.
- ☑ **Experiment outputs re-verified**: 42 unit tests OK; `verify_outputs.py` and `verify_sensitivity.py` both pass (`evidence/rerun_existing_checks_log.txt`).
- ☑ Independent evidence checks: 24 / 25 pass (`evidence/evidence_checks_output.txt`). The single FAIL is a deliberately retained record of the superseded "1.0–2.5 °C" wording; the paper uses **0.99–2.49 °C**.
- ☑ Audit probes reproduced (`evidence/audit_probes_output.txt`):
  - EDF matches an independent reference implementation in 18,024 comparisons (0 mismatches).
  - EEVDF-inspired policy on two cores: 4 / 15 / 27 / 56 ineligible dispatches.
  - TA-EDF's hold-back rule never left a core idle.
- ☑ The new sensitivity figure's plotted lines equal a fresh recomputation from the CSV.
- ☑ **Static LaTeX checks pass** (`python -B check_tex_static.py`): citations, labels, environment and brace balance, figure files.
- ☑ **Preservation**: 179 frozen files unchanged (SHA-256); no file outside `07_Report/thermos_vr_ieee_paper/` was modified; no `.pyc` written.

## 3. ☐ Must do before submission

1. **Check the LaTeX layout if you submit through pdfLaTeX.** The 13-page PDF was compiled with Tectonic, which uses XeTeX, so pdfLaTeX may lay it out slightly differently:
   - Upload `ThermOS_VR_Research_Report.tex`, `references.bib` and the `figures/` folder to Overleaf.
   - Set the compiler to pdfLaTeX. `IEEEtran.cls` and `IEEEtran.bst` are built into Overleaf.
   - **Check the page count is ≤ 15.** The figures are full-width `figure*` floats, so check where they land.
2. **Choose the submission format** (DOCX or LaTeX PDF) and the template the course or venue requires. No conference was named, so the generic IEEE conference format was used. **Do not add an event name that does not exist.**
3. **Author block**: add e-mail addresses and campus or city only if you want them. They were not invented. Confirm the affiliation line ("School of Computer Science and Engineering, Vellore Institute of Technology"), which is taken from `OS.docx`.
4. **Check every citation against the full paper.** Open `CITATION_CLAIM_LEDGER.csv` and confirm each row's claim against the source, then fill in the author-check column. Most sources were verified at abstract or official-text level, not full text.
   - **Hung et al. [22]** is a 2-page DATE paper; make sure the sentence citing it is not over-stated.
   - **HAMLET** (IEEE IoT J. 2026) was excluded because only its abstract was available.
5. **Run your institution's similarity check** (e.g. Turnitin) yourself. No similarity check has been run, and no score is claimed.
6. **Apply your university's AI-use policy**; see the draft disclosure in §6 below.
7. **Read the whole paper once yourself** and make sure you can explain every section (§5).
8. **Optional tidy-up** in Word: page numbers, keeping table captions with their tables, and widow/orphan lines. These are cosmetic; the content is final.

## 4. Scientific-integrity checks (confirmed in the text)

- ☑ Described as a Python simulation; no kernel modification, hardware or headset measurement is claimed.
- ☑ Cores stated as identical; the P/E labels are explicitly not heterogeneity.
- ☑ Zero migration/context-switch cost in the main benchmark is disclosed; nonzero costs are analysed separately (Table VIII, Fig. 7).
- ☑ ThermOS-VR ≡ FCFS is reported, and the reason is explained (the deadline term is constant across cores; the cores are identical; FCFS order is fixed).
- ☑ TA-EDF's idle insertion is reported as never having idled a core; no benefit is claimed for it.
- ☑ TA-EDF's peak advantage is given as 0.99–2.49 °C (with costs) and 0.08–2.49 °C (zero overhead, all 8 configurations). The outdated 1.0–2.5 °C is not used.
- ☑ "No policy reaches HOT with DVFS on" is attributed to the modelled governor and parameters, explicitly not to hardware safety.
- ☑ Simulated °C, model heat units and ticks are distinguished from physical temperature, power and energy throughout.
- ☑ The partial-tick accounting limitation is stated (88 of 384 task records; at most 0.96 work units).
- ☑ Ties and negative results are reported; no statistical significance is claimed.
- ☑ EEVDF is labelled "EEVDF-inspired" with its limitations; EAS is stated as not evaluated.
- ☑ Excluded: Vangaru (low reliability), the unverified "Liu et al. 2021", the v1 Thermal-DVFS numbers and the v1 figures.

## 5. Originality review and author verification

**Originality (manual review, not a similarity score)**

| Section | Source dependence | Notes for review |
|---|---|---|
| Abstract, Introduction | Low | Written around the project's own question and results. Background facts are cited [1]–[7]. |
| Related Work | Moderate (necessarily) | Each summary was written independently from verified abstracts and documentation, and every summary is cited. **Review these sentences most carefully against the sources** for accidental close paraphrase, especially the summaries of [5], [15], [17], [27] and [30]. |
| System Model, Policies, Methodology | Low | Describes our own code; equations come from our implementation. |
| Results, Discussion, Limitations | Low | Our own data and interpretation; every number is asserted against the CSVs. |
| `OS.docx` | **Not reused** | The new Related Work was written fresh. `OS.docx` has citation errors (wrong years, an unverifiable source). |

**You (the authors) should be able to answer these:**

1. Why does ThermOS-VR give exactly the same results as FCFS here, and what would have to change for its score to matter?
2. In the thermal model (1), why can't core placement change total heat when DVFS is off?
3. Why does the governor never use 1.8 or 1.4 GHz on these workloads? (Hint: equation (2).)
4. What is the difference between EDF-NP and EDF, and why did EDF-NP only beat FCFS in two workloads?
5. What does TA-EDF do differently from EDF, and why did its hold-back rule never idle a core?
6. Why does a migration cost of 0.1 work units reverse TA-EDF's tardiness compared with EDF?
7. Why does the EEVDF-inspired policy lose its lag bound on two cores?
8. Why are deadline misses saturated in Sustained and HOT, and why do we report total tardiness?
9. Why can't this study claim statistical significance, energy savings or headset results?
10. How would you re-run the experiments, and what does `verify_outputs.py` check?

## 6. AI-assistance disclosure: DRAFT for author and university-policy review

> *Draft (edit to match what actually happened and what your university requires):*
> "The authors used an AI assistant (Anthropic Claude, via Claude Code) during this project. It was used to help audit and extend the simulation code (unified engine, EDF, TA-EDF and EEVDF-inspired policies, tests and verification scripts), run the experiments, check reference metadata against Crossref and publisher records, generate figures and tables from the result files, and draft the text of this paper. The authors reviewed the code, results, references and text, and take responsibility for the content. All experimental results were produced by the project's simulator and can be reproduced with the scripts provided."

Check whether your course permits this use, and whether a disclosure must appear in the paper itself, in a cover note or in neither.

## 7. Known remaining issues

- LaTeX compiled with Tectonic only, not pdfLaTeX, so the page count on Overleaf is unverified.
- The DOCX page count (14) is from Word's layout, which is not identical to IEEEtran's.
- Several Related Work citations are supported at abstract level only (see the ledger).
- Kernel documentation references cite live web pages (accessed 2026-10-21), which may change.
- The sensitivity figure shows context-switch cost 0 only. The full 16-pair grid is summarised in the text and in `05_Results/v2_sensitivity/sensitivity_results.csv`.
