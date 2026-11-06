# Literature Verification (preparation phase 1)

Prepared 2026-10-21.

**How the checking was done**
- **Local PDFs:** text was extracted read-only with `pypdf 5.1.0`, installed in a session scratch folder. The project and global environment were not changed.
- **Web checks:** web search; Crossref (3 of 15 queries succeeded, the rest were rate-limited with HTTP 429); official Linux kernel documentation read directly.

**Status definitions**
- **VERIFIED** — title, authors, venue and year are confirmed by a publisher page, a DOI registry, official proceedings, an institutional repository or the authors' own copy, *and* the identifier (DOI or stable official URL) is confirmed.
- **PARTIALLY VERIFIED** — the work exists and the main metadata are confirmed, but at least one field (usually the DOI, the peer-reviewed venue or the pages) is not confirmed by an authoritative source.
- **UNVERIFIED** — could not be matched to a real publication.

"Paper says" = statements taken from the paper's own text or abstract. "Interpretation" = our reading.

---

## Part 1 — Candidate papers in `01_Research_Papers/`

### P1 — `P1_HAMLET_2026.pdf`: **FILE NOT FOUND**

No file with this name, and no file containing "HAMLET", exists anywhere in the project or in `10_Backups/`. The paper itself was located online:

| Field | Value |
|---|---|
| Title | HAMLET: Heterogeneous Adaptive Mapping and Low-Energy Task Scheduling for Heterogeneous Multicore IoT Devices |
| Authors | Amir Hossein Ansari, Mohsen Ansari, Alireza Ejlali, Jörg Henkel |
| Venue / year | IEEE Internet of Things Journal, listed with a July 2026 date |
| Identifier | IEEE Xplore document 11488220 (https://ieeexplore.ieee.org/document/11488220/). **DOI, volume and pages not confirmed.** |
| Metadata sources | IEEE Xplore search listing; KIT library record (https://publikationen.bibliothek.kit.edu/1000192962) |
| Paper says (abstract only) | Offline multi-objective genetic optimisation of task-to-core mapping and replication, reducing peak power and energy under schedulability and reliability constraints. At run time, an LSTM predicts core temperatures, and DVFS and DPM act before thermal violations. It claims up to 84.39 % lower peak power, 81.98 % lower energy and 20.7 % better schedulability than state-of-the-art techniques. |
| Hardware / simulation context | Not confirmed (full text not read). |
| Limitations | Only the abstract was available; the numbers are the authors' own claims. |
| Use in our paper | Related work only: an example of combined thermal-, energy- and reliability-aware mapping on heterogeneous cores, contrasting with our symmetric two-core model. |
| **Status** | **PARTIALLY VERIFIED** (paper exists; DOI unconfirmed; local PDF missing) |

### P2 — `P2_Dowling_2025_POD-TAS.pdf`

| Field | Value |
|---|---|
| Exact title (PDF metadata and first page) | Regulating CPU Temperature With Thermal-Aware Scheduling Using a Reduced Order Learning Thermal Model |
| Authors | Anthony Dowling, Lin Jiang, Ming-Cheng Cheng, Yu Liu (Clarkson University) |
| Venue / year | **arXiv preprint 2310.00854** (local PDF created 2024-02-07 by pdfTeX). **No peer-reviewed venue found; the "2025" in the filename is unsupported.** |
| Identifier | arXiv:2310.00854 (https://arxiv.org/abs/2310.00854) |
| Metadata sources | arXiv / export.arxiv.org; Papers With Code listing; local PDF |
| Paper says | Proposes POD-TAS, a thermal-aware scheduler that manages a multi-core CPU through defined states and transitions, using a reduced-order Proper Orthogonal Decomposition thermal model instead of HotSpot. Evaluation is simulation-based (gem5 → McPAT → FEniCS), with COMBS benchmarks. With 4 benchmarks: "decreasing the peak thermal variance by 53.0 % and the peak chip temperature of 29.01 %". Against RT-TAS with 8 benchmarks: 29.57 % lower peak spatial variance and 26.26 % lower peak chip temperature. |
| Hardware / simulation context | Simulated CPU (gem5 / McPAT / FEniCS); not measured on hardware. |
| Limitations | Preprint (not peer reviewed, as far as found); simulation-only; benchmark set of 4–8 programs. |
| Use in our paper | (a) Precedent for simulation-based evaluation of thermal-aware scheduling. (b) Contrast: its model is a high-resolution, physics-based thermal model, whereas ours is a first-order lumped model. Supports a Related Work sentence and a Threats-to-Validity sentence. |
| Follow-up found | Dowling, Cheng, Liu, "Improving TAS Adaptability with a Variable Temperature Threshold", arXiv:2404.16646 (VTF-TAS). PARTIALLY VERIFIED, not needed. |
| **Status** | **PARTIALLY VERIFIED** (verified as an arXiv preprint; peer-reviewed publication UNVERIFIED) |

### P3 — `P3_MobiRL_2025.pdf`

| Field | Value |
|---|---|
| Exact title | An Intelligent Scheduling Approach on Mobile OS for Optimizing UI Smoothness and Power |
| Authors | Xinglei Dou, Lei Liu (corresponding), Limin Xiao (Beihang University) |
| Venue / year | ACM Transactions on Architecture and Code Optimization (TACO) 22(1), Article 12, March 2025, 27 pages |
| DOI | **10.1145/3674910** (printed in the PDF; matches the Crossref record) |
| Metadata sources | Crossref (https://api.crossref.org/works/10.1145%2F3674910); Beihang research portal; local PDF |
| Paper says | MobiRL is a reinforcement-learning scheduler that adjusts CPU/GPU frequency (and frequency limits) to optimise UI smoothness and power. Compared with the commercial scheduler on real devices, it reduces frame drop rate by 4.1 % and power by 42.8 %. Compared with a Q-learning approach, it achieves up to 2.5 % lower frame drop rate and 32.6 % lower power. "Our approach has been deployed in mobile phone products." Platform (Table 1): Qualcomm Snapdragon 888 (4× A55 @ 1.8 GHz, 3× A78 @ 2.4 GHz, 1× X1 @ 2.8 GHz), Android 12, kernel 5.4.147. It discusses `schedutil` and EAS as the baseline Android mechanisms. |
| Hardware context | Real smartphone hardware (Snapdragon 888). |
| Limitations (interpretation) | Targets frequency selection, not task-to-core placement or deadline scheduling; temperature is an input feature, not an optimisation target; UI smoothness, not AR/VR. |
| Use in our paper | Related work on learning-based DVFS for mobile responsiveness and power, and evidence that production Android uses `schedutil` / EAS. Contrast: our governor is a fixed threshold-hysteresis rule. |
| **Status** | **VERIFIED** |

### P4 — `P4_Vangaru_2025_VRAR.pdf`

| Field | Value |
|---|---|
| Exact title (first page) | Adaptive Heterogeneity-Aware CPU Scheduling using Deep Reinforcement Learning for Energy-Efficient Real-Time VR/AR on Mobile Platforms |
| Author | Krishna Kanth Vangaru, "Independent Researcher, USA" (the PDF metadata author field reads "Murad Sawalmeh", presumably from the publisher's template) |
| Venue / year | Journal of Computer Science and Technology Studies (JCSTS), Al-Kindi Center for Research and Development, 7(7): 908–920. Accepted 12 June 2025, published 23 July 2025 |
| DOI | **10.32996/jcsts.2025.7.7.100** (printed in the PDF; web search shows it resolving to a JCSTS 7(7) article on pp. 908–920; the title was not shown in the external record) |
| Metadata sources | Local PDF; Al-Kindi journal pages (al-kindipublisher.com/index.php/jcsts) |
| Paper says | An ML/RL heterogeneity-aware scheduler for task placement and frequency scaling. Claims 87.3 % accuracy at 100 ms lead time for predicting thermal and workload events, and a Meta Quest 3 test device with Keysight N6705C power monitoring and FLIR T540 thermal imaging. The abstract calls the results "Preliminary", while the contributions list claims "Rigorous evaluation across 15 VR/AR applications with statistical significance testing". |
| **Reliability concerns** | (1) Single independent author, with a six-week accept-to-publish interval. (2) Internal inconsistency between "preliminary results" and claimed rigorous, statistically tested evaluation. (3) The paper describes the Quest 3's Snapdragon XR2 Gen 2 as an 8-core 1+3+4 Cortex-X2/A710/A510 design; UploadVR reports a 6-core layout ("two performance cores and four efficiency cores", https://www.uploadvr.com/snapdragon-xr2-gen-2/). Not checked against Qualcomm's official specification, so the discrepancy is unresolved, but it is a warning sign. (4) A Quest 3 does not normally allow kernel scheduler replacement, and the paper does not explain how the scheduler was deployed. |
| Use in our paper | **Do not rely on it for any factual or quantitative claim.** At most it could be mentioned as an example of claimed RL-based VR/AR CPU scheduling, with no numbers. **Recommendation: omit.** |
| **Status** | **PARTIALLY VERIFIED** (bibliographic record exists; scientific reliability LOW) |

---

## Part 2 — Errors found in the existing report's literature review (`07_Report/OS.docx`)

The literature review in `OS.docx` cites 15 works by author and year only. Verification found these problems:

| `OS.docx` entry | Finding | Correct metadata (as verified) |
|---|---|---|
| 1. Hung et al. (2007) | **Wrong year; missing author.** Published at DATE **2005**; the 2007 date is the arXiv posting. Authors include M. Kandemir. | W.-L. Hung, Y. Xie, N. Vijaykrishnan, M. Kandemir, M. J. Irwin, "Thermal-aware task allocation and scheduling for embedded systems," DATE 2005, doi:10.1109/DATE.2005.310 (Penn State / Scopus record). VERIFIED |
| 2. Chrobak et al. (2008) | Correct year. | AAIM 2008; arXiv:0801.4238; Springer DOI 10.1007/978-3-540-68880-8_13 seen only on Academia.edu. PARTIALLY VERIFIED |
| 3. Pérez Rodríguez & Yomsi (2021) | Correct. | RTNS 2021, doi:10.1145/3453417.3453430 (CISTER record). VERIFIED |
| 4. Pérez Rodríguez et al. (2022) | Found only as a CISTER technical report (CISTER-TR-221205); **authors not confirmed**. | PARTIALLY VERIFIED: confirm the authors and any peer-reviewed version before citing |
| 5. Dowling et al. (2023) | Correct as an arXiv 2023 preprint (2310.00854); no peer-reviewed venue found. | PARTIALLY VERIFIED |
| 6. Partap et al. (2022) | Correct as arXiv:2207.13280 (2022); peer-reviewed venue not confirmed. | PARTIALLY VERIFIED |
| 7. Chen et al. (2023), JOSS | Correct. | ICPP 2023, pp. 828–838, doi:10.1145/3605573.3605586. VERIFIED |
| 8. Mittal (2014) | Correct. | Int. J. Computer Aided Engineering and Technology 6(4), doi:10.1504/IJCAET.2014.065419. Pages conflict across sources (440–459 vs 450–459). VERIFIED (check pages) |
| 9. Pathania et al. (2014) | Correct. | DAC 2014, doi:10.1145/2593069.2593151. VERIFIED |
| 10. Google ADPF | Official documentation exists. | https://developer.android.com/games/optimize/adpf. VERIFIED (documentation) |
| 11. Brooks & Martonosi (2001) | Correct. | HPCA-7, pp. 171–182; DOI 10.1109/HPCA.2001.903261 seen only in a citing paper's reference list. PARTIALLY VERIFIED |
| 12. **Liu et al. (2021)** "Thermal-Aware Task Scheduling for Heterogeneous Multi-Core Systems" | **No matching publication found.** | **UNVERIFIED. Remove** unless the original source is produced. |
| 13. Lee, Shin and Chwa (2019) | Correct. | Y. Lee, K. G. Shin, H. S. Chwa, "Thermal-Aware Scheduling for Integrated CPUs–GPU Platforms," ACM TECS 18(5s), Art. 90, 2019, doi:10.1145/3358235 (RT-TAS). VERIFIED |
| 14. Zhang et al. (2018) | **Wrong year.** Published **2020**. | X. Zhang, H. Vadodaria, N. Li, K.-D. Kang, Y. Liu, "A Smartphone Thermal Temperature Analysis for Virtual and Augmented Reality," IEEE AIVR 2020, pp. 301–306 (SUNY / NSF-PAR records). DOI not confirmed. PARTIALLY VERIFIED |
| 15. Dev et al. (2018) | Exists as arXiv:1808.09651 (2018); peer-reviewed venue not confirmed. | PARTIALLY VERIFIED |

Several `OS.docx` summaries also describe results that we could not check against full texts (for example, "results showed improvements in both thermal management and system responsiveness"). **The new paper's Related Work section should be written from the verified abstracts and texts, not from those summaries.**

---

## Part 3 — Linux scheduler mechanisms vs. our simplified policies

Source: official kernel documentation pages read on 2026-10-21. Each page showed "7.3.0" in its sidebar.
- https://docs.kernel.org/scheduler/sched-eevdf.html
- https://docs.kernel.org/scheduler/sched-energy.html
- https://docs.kernel.org/scheduler/sched-deadline.html
- https://docs.kernel.org/scheduler/sched-capacity.html

### EEVDF (Linux) vs our "EEVDF-inspired" policy

| Aspect | Linux (documentation says) | Our simulator |
|---|---|---|
| Origin | "first introduced in a scientific publication in 1995" | Same algorithm family (Stoica & Abdel-Wahab TR-95-22) |
| Adoption | "The Linux kernel began transitioning to EEVDF in version 6.6"; moved away from CFS "in favor of a version of EEVDF proposed by Peter Zijlstra in 2023" | Not Linux code |
| Lag / eligibility | "a task with a positive lag is owed CPU time"; "EEVDF picks tasks with lag greater or equal to zero" | Same rule: eligible if v ≤ V |
| Virtual deadline | picks "the task with the earliest VD" | Same |
| Slice | tasks can request time slices "using the new `sched_setattr()` system call" | Fixed slice = 1 tick |
| Sleep / wake-up | sleeping tasks are "marked for 'deferred dequeue', allowing its lag to decay" | **Not modelled** (tasks never sleep) |
| Preemption | "tasks can preempt others if their VD is earlier" | Re-picked every tick |
| Run queues | Per-CPU run queues and load balancing (general Linux design; *the EEVDF page itself does not state this*) | **One global queue**; ineligible tasks dispatched on the second core; no lag bound on two cores |

**Allowed wording:** "EEVDF-inspired weighted-fair policy". **Forbidden:** "Linux EEVDF", "EEVDF implementation".

### Energy Aware Scheduling (EAS): not implemented, and why

- **Asymmetry is required.** "EAS does not support platforms with symmetric CPU topologies." The kernel checks for "the presence of the SD_ASYM_CPUCAPACITY_FULL flag".
- **An Energy Model is required.** Platforms "must provide power cost tables to the EM framework".
- **The governor must be `schedutil`:** "Using EAS with any other governor than schedutil is not supported."
- **The decision it makes:** at wake-up, `find_energy_efficient_cpu()` compares energy estimates. EAS is disabled when CPUs are "over-utilized" (more than 80 % of capacity).
- **Our simulator has none of these:** the cores are identical, there is no power model and no `schedutil`-like governor. Therefore **no EAS-inspired policy was evaluated**. This is a stated scope limitation, not a result.

### SCHED_DEADLINE (Linux) vs our EDF / TA-EDF

| Aspect | Linux (documentation says) | Our simulator |
|---|---|---|
| Algorithm | "an implementation of the Earliest Deadline First (EDF) scheduling algorithm, augmented with … Constant Bandwidth Server, CBS" | Plain EDF on absolute deadlines; **no CBS** |
| Parameters | runtime, deadline, period per task | One absolute deadline per one-shot task |
| Admission control | Required for guarantees; total bandwidth capped (default 95 % per CPU in the root domain) | **None**; overloaded workloads are run anyway (soft real-time; late tasks continue) |
| Multi-CPU | Global EDF within a root domain; partitioned scheduling via cpusets | Global EDF over 2 cores |
| Reference | Cites Lelli et al., *Softw. Pract. Exper.* 46(6):821–839, 2016 | — |

**Allowed wording:** "global EDF (preemptive and non-preemptive) at tick granularity". **Forbidden:** "SCHED_DEADLINE".

### CPU capacity (context for the identical-core limitation)

The documentation defines capacity as "a measure of the performance a CPU can reach, normalized against the most performant CPU", computed as `capacity(cpu) = work_per_hz(cpu) * max_freq(cpu)`, and calls heterogeneous systems "asymmetric CPU capacity systems". **In our model both cores have identical capacity**, so capacity-aware mechanisms are out of scope.

---

## Part 4 — Access limitations encountered

- No PDF renderer was installed (`pdftoppm` missing); text extraction used `pypdf` from a scratch folder.
- Crossref returned HTTP 429 (rate limit) for 12 of 15 queries, so several DOIs remain unconfirmed. Re-checking those DOIs individually at doi.org or IEEE Xplore is a quick manual task.
- IEEE Xplore and ACM DL landing pages were not fetched directly. Where no other authoritative record was found, the status is PARTIALLY VERIFIED.
- The Qualcomm XR2 Gen 2 specification was not checked against an official Qualcomm page.
