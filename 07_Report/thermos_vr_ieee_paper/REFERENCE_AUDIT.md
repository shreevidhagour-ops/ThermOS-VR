# REFERENCE_AUDIT (Phase B)

Checked 2026-10-21. This audit supersedes the counts in `11_Paper/reference_candidates.md` (27 verified / 20 partial / 1 unverified), which are now out of date. Each Phase-1 entry was re-checked and, where needed, completed.

**Methods**
- **Crossref by DOI:** 16 lookups, 15 returned a record (HTTP 200); one was not reached in that pass and was retrieved in the title pass.
- **Crossref by title:** 7 lookups, all returned a record.
- **Other sources:** web search of publisher, institutional and DBLP pages; official Linux and Android documentation read directly; local PDFs (P2–P4) by text extraction.
- **Prompt-injection note:** two fetched pages contained injected instruction-like text, which the fetchers ignored. No metadata was taken from such text.

**Status**
- **VERIFIED:** title, authors, venue, year and identifier confirmed by Crossref, the publisher, the official proceedings, official documentation or the authors' institution.
- **PARTIAL:** exists, but a field or the content was not confirmed.
- **UNVERIFIED:** not found.

"Supports" names the statement each source may back in the paper. Each source was checked against its abstract or text for that statement only.

## Summary

| Status | Count |
|---|---|
| VERIFIED | **43** |
| PARTIAL | **7** |
| UNVERIFIED | **1** |
| Total checked | 51 |
| Recommended for the paper (Section C) | **38** (all VERIFIED) |

## Changes since Phase 1 (important)

| Item | Phase 1 | Now | Evidence |
|---|---|---|---|
| POD-TAS (Dowling et al.) | arXiv preprint only | **Journal article:** *Future Gener. Comput. Syst.*, vol. 166, Art. 107687, 2025, doi:10.1016/j.future.2024.107687 | Crossref title query; ScienceDirect PII S0167739X24006514 |
| Hung et al. | DATE 2005, pages unknown | Pages **898–899** (a 2-page paper) | Crossref 10.1109/DATE.2005.310 |
| Pillai & Shin | DOI conflict | Both DOIs are valid and linked as the same paper in Crossref: SOSP proceedings 10.1145/502034.502044 (cite this one) and SIGOPS OSR 35(5) 10.1145/502059.502044 | Crossref |
| Zhang et al. (AIVR) | DOI unknown | doi:10.1109/AIVR50618.2020.00061, pp. 301–306 | Crossref |
| Zhao et al. (IEEE VR 2017) | DOI unknown | doi:10.1109/VR.2017.7892302, pp. 313–314 | Crossref |
| HAMLET | DOI, volume and pages unknown | *IEEE Internet Things J.*, vol. 13, no. 13, pp. 28490–28504, Jul. 2026, doi:10.1109/JIOT.2026.3685219 | Crossref |
| Jeffay et al. | DOI unknown | doi:10.1109/REAL.1991.160366, pp. 129–139. The Crossref and DBLP titles read "period", the printed title "periodic"; Crossref has no year, but the container is "[1991] Proceedings Twelfth Real-Time Systems Symposium" | Crossref; DBLP; Chalmers reading list |
| Brooks & Martonosi; Abeni & Buttazzo; Coskun et al.; Chrobak et al.; Jerald & Whitton; Huang et al. (HotSpot); Skadron et al. | DOI from secondary listings or unknown | **DOI confirmed by Crossref** | Crossref |
| Mittal | pages conflict | Crossref gives first page 440 only | Crossref |
| Kong et al. | article number unknown | Crossref gives pp. 1–42 | Crossref |

## A. VERIFIED (43)

| # | Reference (metadata as verified) | Verified by | Supports |
|---|---|---|---|
| 1 | C. L. Liu, J. W. Layland, "Scheduling algorithms for multiprogramming in a hard-real-time environment," *J. ACM*, 20(1):46–61, 1973, doi:10.1145/321738.321743 | JACM bibliography; DOI | EDF origin; optimality on a single processor |
| 2 | S. K. Dhall, C. L. Liu, "On a real-time scheduling problem," *Oper. Res.*, 26(1):127–140, 1978, doi:10.1287/opre.26.1.127 | IDEAS/RePEc | Multiprocessor scheduling difficulty (Dhall effect) |
| 3 | R. I. Davis, A. Burns, "A survey of hard real-time scheduling for multiprocessor systems," *ACM Comput. Surv.*, 43(4), Art. 35, 2011, doi:10.1145/1978802.1978814 | York record | Global vs partitioned multiprocessor scheduling |
| 4 | J. Lelli, C. Scordino, L. Abeni, D. Faggioli, "Deadline scheduling in the Linux kernel," *Softw. Pract. Exper.*, 46(6):821–839, 2016, doi:10.1002/spe.2335 | Wiley | SCHED_DEADLINE design |
| 5 | L. Abeni, G. Buttazzo, "Integrating multimedia applications in hard real-time systems," *Proc. 19th IEEE RTSS*, 1998, pp. 4–13, doi:10.1109/REAL.1998.739726 | Crossref | Constant Bandwidth Server |
| 6 | K. Jeffay, D. F. Stanat, C. U. Martel, "On non-preemptive scheduling of periodic and sporadic tasks," *Proc. 12th IEEE RTSS*, 1991, pp. 129–139, doi:10.1109/REAL.1991.160366 | Crossref (title-wording note above) | Non-preemptive EDF |
| 7 | G. C. Buttazzo, *Hard Real-Time Computing Systems*, 3rd ed. Springer, 2011, doi:10.1007/978-1-4614-0676-1 | Crossref (no edition field); edition from library record | Real-time scheduling textbook background |
| 8 | S. K. Baruah, N. K. Cohen, C. G. Plaxton, D. A. Varvel, "Proportionate progress: A notion of fairness in resource allocation," *Algorithmica*, 15:600–625, 1996, doi:10.1007/BF01940883 | Springer | Multiprocessor fairness |
| 9 | I. Stoica, H. Abdel-Wahab, "Earliest eligible virtual deadline first: A flexible and accurate mechanism for proportional share resource allocation," Old Dominion Univ., Tech. Rep. TR-95-22, 1995. https://people.eecs.berkeley.edu/~istoica/papers/eevdf-tr-95.pdf | Author-hosted report | EEVDF definition; lag bound of one quantum (single resource) |
| 10 | A. Chandra, M. Adler, P. Goyal, P. Shenoy, "Surplus fair scheduling: A proportional-share CPU scheduling algorithm for symmetric multiprocessors," *Proc. 4th USENIX OSDI*, 2000, pp. 45–58 | USENIX | Infeasible weights on SMPs cause unfairness |
| 11 | J. Corbet, "An EEVDF CPU scheduler for Linux," *LWN.net*, Mar. 9, 2023. https://lwn.net/Articles/925371/ | LWN | History of EEVDF in Linux |
| 12 | Linux Kernel Documentation, "EEVDF Scheduler," https://docs.kernel.org/scheduler/sched-eevdf.html (accessed 2026-10-21; page shows 7.3.0) | Read directly | Linux EEVDF features we do not model |
| 13 | Linux Kernel Documentation, "Energy Aware Scheduling," https://docs.kernel.org/scheduler/sched-energy.html (accessed 2026-10-21) | Read directly | EAS requirements; why EAS is out of scope |
| 14 | Linux Kernel Documentation, "Deadline Task Scheduling," https://docs.kernel.org/scheduler/sched-deadline.html (accessed 2026-10-21) | Read directly | SCHED_DEADLINE = EDF + CBS; admission control |
| 15 | Linux Kernel Documentation, "Capacity Aware Scheduling," https://docs.kernel.org/scheduler/sched-capacity.html (accessed 2026-10-21) | Read directly | CPU capacity; asymmetric systems |
| 16 | D. Brooks, M. Martonosi, "Dynamic thermal management for high-performance microprocessors," *Proc. 7th IEEE HPCA*, 2001, pp. 171–182, doi:10.1109/HPCA.2001.903261 | Crossref; author PDF (Crossref year absent; HPCA-7 = 2001) | Dynamic thermal management |
| 17 | K. Skadron, M. R. Stan, W. Huang, S. Velusamy, K. Sankaranarayanan, D. Tarjan, "Temperature-aware microarchitecture," *Proc. 30th ISCA*, 2003, pp. 2–13, doi:10.1145/859618.859620 | Crossref (first page only); author page (pp. 2–13) | Temperature-aware design; DTM; HotSpot origin |
| 18 | W. Huang, S. Ghosh, S. Velusamy, K. Sankaranarayanan, K. Skadron, M. R. Stan, "HotSpot: A compact thermal modeling methodology for early-stage VLSI design," *IEEE Trans. VLSI Syst.*, 14(5):501–513, 2006, doi:10.1109/TVLSI.2006.876103 | Crossref | Compact RC thermal models (contrast with our lumped model) |
| 19 | J. Kong, S. W. Chung, K. Skadron, "Recent thermal management techniques for microprocessors," *ACM Comput. Surv.*, 44(3):1–42, 2012, doi:10.1145/2187671.2187675 | Crossref | Survey of thermal management, including OS-level techniques |
| 20 | P. Pillai, K. G. Shin, "Real-time dynamic voltage scaling for low-power embedded operating systems," *Proc. 18th ACM SOSP*, 2001, pp. 89–102, doi:10.1145/502034.502044 | Crossref | DVFS within real-time scheduling |
| 21 | W.-L. Hung, Y. Xie, N. Vijaykrishnan, M. Kandemir, M. J. Irwin, "Thermal-aware task allocation and scheduling for embedded systems," *Proc. DATE*, 2005, pp. 898–899, doi:10.1109/DATE.2005.310 | Crossref | Thermal-aware allocation (earliest of our cited works) |
| 22 | A. K. Coskun, T. S. Rosing, K. Whisnant, "Temperature aware task scheduling in MPSoCs," *Proc. DATE*, 2007, pp. 1–6, doi:10.1109/DATE.2007.364540 | Crossref | OS-level thermal-aware scheduling on MPSoCs |
| 23 | M. Chrobak, C. Dürr, M. Hurand, J. Robert, "Algorithms for temperature-aware task scheduling in microprocessor systems," *Proc. AAIM* (LNCS), 2008, pp. 120–130, doi:10.1007/978-3-540-68880-8_13 | Crossref (Crossref title wording differs slightly; LNCS volume not given) | Theory of temperature-aware scheduling |
| 24 | J. Pérez Rodríguez, P. Meumeu Yomsi, "An efficient proactive thermal-aware scheduler for DVFS-enabled single-core processors," *Proc. 29th RTNS*, 2021, pp. 144–154, doi:10.1145/3453417.3453430 | Crossref | Proactive thermal-aware scheduling with DVFS |
| 25 | Y. Lee, K. G. Shin, H. S. Chwa, "Thermal-aware scheduling for integrated CPUs–GPU platforms," *ACM Trans. Embed. Comput. Syst.*, 18(5s), Art. 90, 2019, doi:10.1145/3358235 | Crossref | RT-TAS: thermal balancing with timing guarantees |
| 26 | A. Dowling, L. Jiang, M.-C. Cheng, Y. Liu, "Regulating CPU temperature with thermal-aware scheduling using a reduced order learning thermal model," *Future Gener. Comput. Syst.*, 166, Art. 107687, 2025, doi:10.1016/j.future.2024.107687 | Crossref; ScienceDirect; local preprint text | POD-TAS; simulation-based TAS evaluation |
| 27 | A. H. Ansari, M. Ansari, A. Ejlali, J. Henkel, "HAMLET: Heterogeneous adaptive mapping and low-energy task scheduling for heterogeneous multicore IoT devices," *IEEE Internet Things J.*, 13(13):28490–28504, 2026, doi:10.1109/JIOT.2026.3685219 | Crossref; IEEE Xplore listing (abstract only) | Thermal- and energy-aware mapping on heterogeneous cores (abstract-level claim only) |
| 28 | R. Kumar, K. I. Farkas, N. P. Jouppi, P. Ranganathan, D. M. Tullsen, "Single-ISA heterogeneous multi-core architectures: The potential for processor power reduction," *Proc. 36th MICRO*, 2003, pp. 81–92, doi:10.1109/MICRO.2003.1253185 | Crossref | Heterogeneous cores (contrast: ours are identical) |
| 29 | X. Dou, L. Liu, L. Xiao, "An intelligent scheduling approach on mobile OS for optimizing UI smoothness and power," *ACM Trans. Archit. Code Optim.*, 22(1), Art. 12, 2025, doi:10.1145/3674910 | Crossref; local PDF | Learning-based mobile DVFS; Android schedutil/EAS context |
| 30 | A. Pathania, Q. Jiao, A. Prakash, T. Mitra, "Integrated CPU-GPU power management for 3D mobile games," *Proc. 51st DAC*, 2014, doi:10.1145/2593069.2593151 | ACM / Unpaywall | Mobile gaming power management |
| 31 | J. Chen, M. Manivannan, B. Goel, M. Pericàs, "JOSS: Joint exploration of CPU-memory DVFS and task scheduling for energy efficiency," *Proc. 52nd ICPP*, 2023, pp. 828–838, doi:10.1145/3605573.3605586 | Chalmers portal | Joint DVFS and scheduling for energy |
| 32 | S. Mittal, "A survey of techniques for improving energy efficiency in embedded computing systems," *Int. J. Comput. Aided Eng. Technol.*, 6(4):440–, 2014, doi:10.1504/IJCAET.2014.065419 | Crossref (start page only) | Embedded power-management background |
| 33 | Q. Xie, M. J. Dousti, M. Pedram, "Therminator: A thermal simulator for smartphones producing accurate chip and skin temperature maps," *Proc. ISLPED*, 2014, pp. 117–122, doi:10.1145/2627369.2627641 | Author PDF; OpenAlex | Detailed mobile thermal simulation (contrast) |
| 34 | X. Zhang, H. Vadodaria, N. Li, K.-D. Kang, Y. Liu, "A smartphone thermal temperature analysis for virtual and augmented reality," *Proc. IEEE AIVR*, 2020, pp. 301–306, doi:10.1109/AIVR50618.2020.00061 | Crossref; SUNY / NSF-PAR | Measured AR/VR thermal behaviour on phones (motivation) |
| 35 | M. Huzaifa *et al.*, "ILLIXR: Enabling end-to-end extended reality research," *Proc. IEEE IISWC*, 2021, pp. 24–38, doi:10.1109/IISWC53511.2021.00014 | Crossref | XR system pipelines; trace-driven future work |
| 36 | Z. Lai, Y. C. Hu, Y. Cui, L. Sun, N. Dai, "Furion: Engineering high-quality immersive virtual reality on today's mobile devices," *Proc. 23rd ACM MobiCom*, 2017, pp. 409–421, doi:10.1145/3117811.3117815 | Crossref | Mobile VR performance constraints |
| 37 | J. Jerald, M. C. Whitton, "Relating scene-motion thresholds to latency thresholds for head-mounted displays," *Proc. IEEE VR*, 2009, pp. 211–218, doi:10.1109/VR.2009.4811025 | Crossref | Latency perception in HMDs (motivation) |
| 38 | J. Zhao, R. S. Allison, M. Vinnikov, S. Jennings, "Estimating the motion-to-photon latency in head mounted displays," *Proc. IEEE VR*, 2017, pp. 313–314, doi:10.1109/VR.2017.7892302 | Crossref | Motion-to-photon latency measurement (motivation) |
| 39 | Android Developers, "Android Dynamic Performance Framework (ADPF)," https://developer.android.com/games/optimize/adpf (accessed 2026-10-21) | Official docs | Industry thermal/performance hint APIs |
| 40 | C. Li, C. Ding, K. Shen, "Quantifying the cost of context switch," *Proc. Workshop on Experimental Computer Science (ExpCS)*, 2007, doi:10.1145/1281700.1281702 | Crossref; author PDF | Context switches have real indirect (cache) costs: motivates the overhead sensitivity |
| 41 | T. Hoefler, R. Belli, "Scientific benchmarking of parallel computing systems: Twelve ways to tell the masses when reporting performance results," *Proc. SC15*, 2015, Art. 73, doi:10.1145/2807591.2807644 | USI database; ACM | Reporting practice; why no statistical claims are made |
| 42 | A. Georges, D. Buytaert, L. Eeckhout, "Statistically rigorous Java performance evaluation," *Proc. 22nd OOPSLA*, 2007, pp. 57–76, doi:10.1145/1297027.1297033 | Crossref (OOPSLA record; the SIGPLAN Notices version is 10.1145/1297105.1297033) | Need for repeated measurements under non-determinism |
| 43 | R. Jain, *The Art of Computer Systems Performance Analysis*. Wiley, 1991, ISBN 978-0-471-50336-1 | Wiley | Simulation and evaluation methodology |

## B. PARTIAL (7): not recommended unless completed

| Reference | Issue | Recommendation |
|---|---|---|
| I. Stoica *et al.*, "A proportional share resource allocation algorithm for real-time, time-shared systems," IEEE RTSS 1996 | No DOI or pages confirmed | Omit (the EEVDF TR, #9, suffices) |
| A. Partap *et al.*, "On-device CPU scheduling for sense-react systems," arXiv:2207.13280, 2022 | Peer-reviewed venue not found | Optional, cited as a preprint; not needed |
| K. Dev *et al.*, "Implications of integrated CPU-GPU processors on thermal and power management techniques," arXiv:1808.09651, 2018 | Venue not found | Omit |
| P. Greenhalgh, "big.LITTLE processing with ARM Cortex-A15 & Cortex-A7," ARM white paper, 2011 | Only secondary copies found | Omit (Kumar *et al.* #28 covers heterogeneity) |
| Linux Kernel Documentation, "CPU Performance Scaling" (cpufreq), https://docs.kernel.org/admin-guide/pm/cpufreq.html | Page exists; its schedutil content was not read | Read before citing, or omit |
| J. Pérez Rodríguez *et al.*, CISTER-TR-221205, 2022 | Authors not confirmed | Omit |
| K. K. Vangaru, JCSTS 7(7):908–920, 2025, doi:10.32996/jcsts.2025.7.7.100 | Record exists; **low scientific reliability** (internal inconsistencies; hardware description conflicts with press reports) | **Exclude**; no quantitative use |

## C. UNVERIFIED (1)

| Reference | Recommendation |
|---|---|
| "Liu et al. (2021), Thermal-Aware Task Scheduling for Heterogeneous Multi-Core Systems" (from `OS.docx`) | **Exclude.** No matching publication was found. |

## D. Proposed bibliography: 38 references, all VERIFIED

Include #1–6, #8–20, #21–26, #28–30, #33–38, #40–43 above. Excluded from the VERIFIED set:
- **#7 Buttazzo textbook:** redundant with #1, #3 and #4.
- **#27 HAMLET:** abstract-only knowledge; include only if the authors want an example from 2026.
- **#31 JOSS and #32 Mittal:** energy focus, peripheral to our question.
- **#39 ADPF:** optional.

That gives 38 references (39 if HAMLET is added). The final number is decided in Phase D, when each reference must be cited in the body. A reference that ends up uncited will be removed rather than kept as padding.

**Page check:** 38 IEEE references take roughly 1.3–1.6 two-column pages, consistent with the 1.5-page budget. This must be confirmed on a compiled PDF; no LaTeX toolchain is available yet (see `OPEN_ISSUES.md`).

## E. Errors in `07_Report/OS.docx` (for the authors' awareness)

`OS.docx` is not modified. Its literature review should not be reused verbatim; the paper's Related Work will be written fresh.

| `OS.docx` text | Correction |
|---|---|
| Hung et al. (2007) | DATE **2005**; five authors (Kandemir missing) |
| Zhang et al. (2018) | IEEE AIVR **2020** |
| Dowling et al. (2023) | The 2023 date is the arXiv preprint; the published version is *FGCS* **2025** |
| Liu et al. (2021) | Not found; remove |
| Pérez Rodríguez et al. (2022) | Technical report only; authors unconfirmed |
