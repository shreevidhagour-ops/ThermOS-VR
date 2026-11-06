# Reference Candidates (preparation phase 1)

Prepared 2026-10-21. Every entry below was checked during this phase (see `literature_verification.md` for the method and status definitions).

- **Section A** lists only fully VERIFIED references.
- **Section B** lists references that exist and whose core metadata were confirmed, but where one field (usually the DOI) still needs a manual check before submission.
- **Section C** lists items that must not be cited as they stand.
- **Section D** lists the topics still to be searched.

Nothing here is padded: **27 verified + 20 partially verified + 1 unverified = 48 checked items.**

Citation strings are drafted in IEEE style from the verified metadata only. Fields we did not confirm are marked `[confirm]` rather than guessed.

---

## A. VERIFIED (27)

### Real-time and deadline-aware scheduling
| # | Reference (IEEE style) | Verification source | Supports in our paper |
|---|---|---|---|
| A1 | C. L. Liu and J. W. Layland, "Scheduling algorithms for multiprogramming in a hard-real-time environment," *J. ACM*, vol. 20, no. 1, pp. 46–61, 1973, doi: 10.1145/321738.321743. | MIT JACM bibliography; DOI on citation index | Origin of EDF; definition of the deadline-driven baseline |
| A2 | S. K. Dhall and C. L. Liu, "On a real-time scheduling problem," *Oper. Res.*, vol. 26, no. 1, pp. 127–140, 1978, doi: 10.1287/opre.26.1.127. | IDEAS/RePEc record | Global EDF is not optimal on multiprocessors (Dhall effect) |
| A3 | R. I. Davis and A. Burns, "A survey of hard real-time scheduling for multiprocessor systems," *ACM Comput. Surv.*, vol. 43, no. 4, Art. 35, 2011, doi: 10.1145/1978802.1978814. | University of York record | Background on global vs partitioned multiprocessor scheduling |
| A4 | J. Lelli, C. Scordino, L. Abeni, and D. Faggioli, "Deadline scheduling in the Linux kernel," *Softw. Pract. Exper.*, vol. 46, no. 6, pp. 821–839, 2016, doi: 10.1002/spe.2335. | Wiley Online Library page | SCHED_DEADLINE (EDF + CBS) as the real Linux deadline mechanism, contrasted with our plain EDF |
| A5 | S. K. Baruah, N. K. Cohen, C. G. Plaxton, and D. A. Varvel, "Proportionate progress: A notion of fairness in resource allocation," *Algorithmica*, vol. 15, pp. 600–625, 1996, doi: 10.1007/BF01940883. | Springer DOI record | Multiprocessor fairness (Pfair); why our 2-core EEVDF variant loses its lag bound |

### Proportional-share and fair scheduling
| # | Reference | Verification source | Supports |
|---|---|---|---|
| A6 | I. Stoica and H. Abdel-Wahab, "Earliest eligible virtual deadline first: A flexible and accurate mechanism for proportional share resource allocation," Dept. Comput. Sci., Old Dominion Univ., Tech. Rep. TR-95-22, 1995 (rev. Jan. 1996). Online: https://people.eecs.berkeley.edu/~istoica/papers/eevdf-tr-95.pdf | Author-hosted copy | Definition of EEVDF (lag, eligibility, virtual deadline); single-resource lag bound of one quantum |
| A7 | A. Chandra, M. Adler, P. Goyal, and P. Shenoy, "Surplus fair scheduling: A proportional-share CPU scheduling algorithm for symmetric multiprocessors," in *Proc. 4th USENIX OSDI*, 2000, pp. 45–58. Online: https://www.usenix.org/conference/osdi-2000/surplus-fair-scheduling-proportional-share-cpu-scheduling-algorithm-symmetric | USENIX official page | Infeasible weights on multiprocessors cause unfairness: explains the observed 2-core EEVDF lag growth |
| A8 | J. Corbet, "An EEVDF CPU scheduler for Linux," *LWN.net*, Mar. 9, 2023. Online: https://lwn.net/Articles/925371/ | LWN page | History: Zijlstra's proposal to replace CFS with EEVDF |

### Linux scheduler documentation (read directly; pages showed "7.3.0")
| # | Reference | Supports |
|---|---|---|
| A9 | The Linux Kernel Documentation, "EEVDF Scheduler." Online: https://docs.kernel.org/scheduler/sched-eevdf.html | EEVDF in Linux since 6.6; lag, VD, `sched_setattr()` slices, deferred dequeue |
| A10 | The Linux Kernel Documentation, "Energy Aware Scheduling." Online: https://docs.kernel.org/scheduler/sched-energy.html | EAS needs asymmetric capacity, an Energy Model and `schedutil`: justifies leaving EAS out of scope |
| A11 | The Linux Kernel Documentation, "Deadline Task Scheduling." Online: https://docs.kernel.org/scheduler/sched-deadline.html | SCHED_DEADLINE = EDF + CBS, admission control |
| A12 | The Linux Kernel Documentation, "Capacity Aware Scheduling." Online: https://docs.kernel.org/scheduler/sched-capacity.html | Definition of CPU capacity; asymmetric-capacity systems |

### Thermal-aware scheduling and DVFS
| # | Reference | Verification source | Supports |
|---|---|---|---|
| A13 | W.-L. Hung, Y. Xie, N. Vijaykrishnan, M. Kandemir, and M. J. Irwin, "Thermal-aware task allocation and scheduling for embedded systems," in *Proc. DATE*, 2005, doi: 10.1109/DATE.2005.310. | Penn State repository (Scopus) | Early thermal-aware allocation (**`OS.docx` gave 2007; correct year is 2005**) |
| A14 | J. Pérez Rodríguez and P. M. Yomsi, "An efficient proactive thermal-aware scheduler for DVFS-enabled single-core processors," in *Proc. 29th RTNS*, 2021, doi: 10.1145/3453417.3453430. | CISTER record | Proactive thermal-aware scheduling with DVFS |
| A15 | Y. Lee, K. G. Shin, and H. S. Chwa, "Thermal-aware scheduling for integrated CPUs–GPU platforms," *ACM Trans. Embed. Comput. Syst.*, vol. 18, no. 5s, Art. 90, 2019, doi: 10.1145/3358235. | Univ. Michigan / DGIST records | RT-TAS: thermal balancing with real-time guarantees (also POD-TAS's comparison baseline) |
| A16 | J. Kong, S. W. Chung, and K. Skadron, "Recent thermal management techniques for microprocessors," *ACM Comput. Surv.*, vol. 44, no. 3, 2012, doi: 10.1145/2187671.2187675. | Korea Univ. repository; ACM record | Survey: OS-level thermal management and DTM taxonomy |
| A17 | A. Pathania, Q. Jiao, A. Prakash, and T. Mitra, "Integrated CPU-GPU power management for 3D mobile games," in *Proc. 51st DAC*, 2014, doi: 10.1145/2593069.2593151. | ACM / Unpaywall record | Mobile gaming power management (CPU-GPU DVFS) |
| A18 | S. Mittal, "A survey of techniques for improving energy efficiency in embedded computing systems," *Int. J. Comput. Aided Eng. Technol.*, vol. 6, no. 4, 2014, doi: 10.1504/IJCAET.2014.065419. Pages `[confirm: 440–459 vs 450–459]`. | Inderscience (aid=65419); hgpu BibTeX | Embedded power/thermal management background |
| A19 | J. Chen, M. Manivannan, B. Goel, and M. Pericàs, "JOSS: Joint exploration of CPU-memory DVFS and task scheduling for energy efficiency," in *Proc. 52nd ICPP*, 2023, pp. 828–838, doi: 10.1145/3605573.3605586. | Chalmers research portal | Joint DVFS and scheduling (energy); contrast: we model no energy |

### Heterogeneous multicore and mobile scheduling
| # | Reference | Verification source | Supports |
|---|---|---|---|
| A20 | R. Kumar, K. I. Farkas, N. P. Jouppi, P. Ranganathan, and D. M. Tullsen, "Single-ISA heterogeneous multi-core architectures: The potential for processor power reduction," in *Proc. 36th IEEE/ACM MICRO*, 2003, pp. 81–92, doi: 10.1109/MICRO.2003.1253185. | Crossref | Motivation for heterogeneous cores (our cores are *not* heterogeneous: limitation) |
| A21 | X. Dou, L. Liu, and L. Xiao, "An intelligent scheduling approach on mobile OS for optimizing UI smoothness and power," *ACM Trans. Archit. Code Optim.*, vol. 22, no. 1, Art. 12, 2025, doi: 10.1145/3674910. | Crossref; local PDF | Learning-based mobile DVFS; Android `schedutil`/EAS baseline on a Snapdragon 888 |
| A22 | Q. Xie, M. J. Dousti, and M. Pedram, "Therminator: A thermal simulator for smartphones producing accurate chip and skin temperature maps," in *Proc. ISLPED*, 2014, pp. 117–122, doi: 10.1145/2627369.2627641. | Author PDF; OpenAlex | Contrast between detailed mobile thermal simulation and our lumped model |

### AR/VR systems
| # | Reference | Verification source | Supports |
|---|---|---|---|
| A23 | M. Huzaifa *et al.*, "ILLIXR: Enabling end-to-end extended reality research," in *Proc. IEEE IISWC*, 2021, pp. 24–38, doi: 10.1109/IISWC53511.2021.00014. | Crossref | Real XR system pipelines (as opposed to our synthetic 6-task workloads); future-work testbed |
| A24 | Z. Lai, Y. C. Hu, Y. Cui, L. Sun, and N. Dai, "Furion: Engineering high-quality immersive virtual reality on today's mobile devices," in *Proc. 23rd ACM MobiCom*, 2017, pp. 409–421, doi: 10.1145/3117811.3117815. | Crossref | Mobile VR performance constraints |
| A25 | Android Developers, "Android Dynamic Performance Framework (ADPF)." Online: https://developer.android.com/games/optimize/adpf | Official documentation | Industry thermal-hint API (Thermal API, Performance Hint API) |

### Evaluation methodology
| # | Reference | Verification source | Supports |
|---|---|---|---|
| A26 | T. Hoefler and R. Belli, "Scientific benchmarking of parallel computing systems: Twelve ways to tell the masses when reporting performance results," in *Proc. SC15*, 2015, Art. 73, doi: 10.1145/2807591.2807644. | USI evaluate database; ACM | Why we make no statistical claims from single deterministic runs |
| A27 | R. Jain, *The Art of Computer Systems Performance Analysis*. New York, NY, USA: Wiley, 1991, ISBN 978-0-471-50336-1. | Wiley product page | Simulation and evaluation methodology |

---

## B. PARTIALLY VERIFIED (20): usable after the stated check

| # | Reference (verified fields only) | What is confirmed | Still to confirm | Recommendation |
|---|---|---|---|---|
| B1 | D. Brooks and M. Martonosi, "Dynamic thermal management for high-performance microprocessors," in *Proc. 7th HPCA*, 2001, pp. 171–182. | Venue, pages, author PDF | DOI 10.1109/HPCA.2001.903261 seen only in a citing paper's reference list | Cite after confirming the DOI on IEEE Xplore |
| B2 | K. Skadron, M. R. Stan, W. Huang, S. Velusamy, K. Sankaranarayanan, and D. Tarjan, "Temperature-aware microarchitecture," in *Proc. 30th ISCA*, 2003, pp. 2–13. | Venue, pages, author page | DOI; author order differs between versions | Cite; confirm DOI and byline |
| B3 | W. Huang, S. Ghosh, S. Velusamy, K. Sankaranarayanan, K. Skadron, and M. R. Stan, "HotSpot: A compact thermal modeling methodology for early-stage VLSI design," *IEEE Trans. VLSI Syst.*, vol. 14, no. 5, pp. 501–513, 2006. | Volume, pages | DOI | Cite; confirm DOI |
| B4 | P. Pillai and K. G. Shin, "Real-time dynamic voltage scaling for low-power embedded operating systems," in *Proc. 18th ACM SOSP*, 2001 (*ACM SIGOPS Oper. Syst. Rev.*, vol. 35, no. 5, pp. 89–102). | Venue, pages, SOSP PDF | **DOI conflict**: 10.1145/502034.502044 vs 10.1145/502059.502044 | Cite; resolve the DOI on ACM DL |
| B5 | L. Abeni and G. Buttazzo, "Integrating multimedia applications in hard real-time systems," in *Proc. 19th IEEE RTSS*, 1998, pp. 4–13. | Venue, award record | DOI 10.1109/REAL.1998.739726 seen only in a reference list | Cite (CBS origin); confirm DOI |
| B6 | K. Jeffay, D. F. Stanat, and C. U. Martel, "On non-preemptive scheduling of periodic and sporadic tasks," in *Proc. 12th IEEE RTSS*, 1991, pp. 129–139. | DBLP; course reading lists | DOI | Cite for non-preemptive EDF; confirm DOI |
| B7 | I. Stoica, H. Abdel-Wahab, K. Jeffay, S. K. Baruah, J. E. Gehrke, and C. G. Plaxton, "A proportional share resource allocation algorithm for real-time, time-shared systems," in *Proc. 17th IEEE RTSS*, 1996. | Cited in TR-95-22; UNC TR 96-038 | Pages, DOI | Optional |
| B8 | A. K. Coskun, T. S. Rosing, and K. Whisnant, "Temperature aware task scheduling in MPSoCs," in *Proc. DATE*, 2007, pp. 1–6. | Author PDF; FAU bibliography | DOI 10.1109/DATE.2007.364540 from a secondary bibliography only | Cite; confirm DOI |
| B9 | M. Chrobak, C. Dürr, M. Hurand, and J. Robert, "Algorithms for temperature-aware task scheduling in microprocessor systems," in *Proc. AAIM*, 2008 (arXiv:0801.4238). | arXiv | Springer DOI 10.1007/978-3-540-68880-8_13 (seen only on Academia.edu) | Cite; confirm DOI |
| B10 | A. Dowling, L. Jiang, M.-C. Cheng, and Y. Liu, "Regulating CPU temperature with thermal-aware scheduling using a reduced order learning thermal model," arXiv:2310.00854, 2023. | arXiv; local PDF | Peer-reviewed venue (none found); **the filename's "2025" is unsupported** | Cite as an arXiv preprint |
| B11 | J. Jerald and M. C. Whitton, "Relating scene-motion thresholds to latency thresholds for head-mounted displays," in *Proc. IEEE VR*, 2009, pp. 211–218. | Two bibliographic listings with the same DOI | DOI 10.1109/VR.2009.4811025 on the publisher page | Cite for latency perception; confirm DOI |
| B12 | J. Zhao, R. S. Allison, M. Vinnikov, and S. Jennings, "Estimating the motion-to-photon latency in head mounted displays," in *Proc. IEEE VR*, 2017, pp. 313–314. | NJIT record | DOI | Cite for motion-to-photon measurement; confirm DOI |
| B13 | X. Zhang, H. Vadodaria, N. Li, K.-D. Kang, and Y. Liu, "A smartphone thermal temperature analysis for virtual and augmented reality," in *Proc. IEEE AIVR*, 2020, pp. 301–306. | SUNY and NSF-PAR records | DOI (**`OS.docx` gave 2018; correct year is 2020**) | Key AR/VR thermal motivation; confirm DOI |
| B14 | A. Partap *et al.*, "On-device CPU scheduling for sense-react systems," arXiv:2207.13280, 2022. | arXiv | Peer-reviewed venue | Cite as an arXiv preprint |
| B15 | K. Dev, I. Paul, W. Huang, Y. Eckert, W. Burleson, and S. Reda, "Implications of integrated CPU-GPU processors on thermal and power management techniques," arXiv:1808.09651, 2018. | arXiv | Peer-reviewed venue | Optional; cite as a preprint |
| B16 | A. H. Ansari, M. Ansari, A. Ejlali, and J. Henkel, "HAMLET: Heterogeneous adaptive mapping and low-energy task scheduling for heterogeneous multicore IoT devices," *IEEE Internet Things J.*, 2026. IEEE Xplore doc. 11488220. | IEEE Xplore listing; KIT record | DOI, volume, pages; **local PDF `P1_HAMLET_2026.pdf` missing** | Cite after confirming the metadata |
| B17 | G. C. Buttazzo, *Hard Real-Time Computing Systems: Predictable Scheduling Algorithms and Applications*, 3rd ed. New York, NY, USA: Springer, 2011. | Library catalogue | DOI 10.1007/978-1-4614-0676-1 (catalogue only; ISBN listings differ) | Cite; confirm on Springer |
| B18 | P. Greenhalgh, "big.LITTLE processing with ARM Cortex-A15 & Cortex-A7," ARM white paper, Sept. 2011. | Secondary copies (Design-Reuse, EETimes reprint) | ARM-hosted original | Optional background on heterogeneous cores |
| B19 | K. K. Vangaru, "Adaptive heterogeneity-aware CPU scheduling using deep reinforcement learning for energy-efficient real-time VR/AR on mobile platforms," *J. Comput. Sci. Technol. Stud.*, vol. 7, no. 7, pp. 908–920, 2025, doi: 10.32996/jcsts.2025.7.7.100. | Local PDF; JCSTS issue pages | — (record OK) | **Not recommended**: low scientific reliability (see `literature_verification.md`) |
| B20 | J. Pérez Rodríguez *et al.*, "A thermal-aware approach for DVFS-enabled multi-core architectures," CISTER Tech. Rep. CISTER-TR-221205, 2022. | CISTER record | Author list; peer-reviewed version | Do not cite until the authors are confirmed |

---

## C. UNVERIFIED or excluded (do not cite)

| Item | Reason |
|---|---|
| "Liu et al. (2021), Thermal-Aware Task Scheduling for Heterogeneous Multi-Core Systems" (from `OS.docx`) | **UNVERIFIED**: no matching publication found |
| `P1_HAMLET_2026.pdf` (as a local file) | File does not exist in the project (the paper itself is B16) |
| Any "sub-20 ms motion-to-photon" or "90 Hz+" requirement taken from P4 (Vangaru) | Unreliable source; find primary sources (see D) |
| Any Snapdragon XR2 Gen 2 core configuration | Not verified against Qualcomm's official specification |

---

## D. Gaps: topics still to search (no references claimed yet)

To reach about 30–40 *verified* references without padding:

1. **AR/VR frame timing and refresh rates.** A primary source (peer-reviewed or official headset documentation) for the per-frame budget at 72/90/120 Hz, and for motion-to-photon targets. Avoid blogs.
2. **Measured cost of context switches and migrations** (for example, peer-reviewed measurement studies of context-switch cost and cache effects). This would let us relate our hypothetical 0.1–0.5-tick costs to reality qualitatively.
3. **Linux `schedutil` / CPUFreq governor documentation** (official kernel docs) and the Energy Model framework page, to describe what real DVFS governors do.
4. **Measurement studies of mobile thermal throttling**, especially smartphones and standalone headsets.
5. **Thermal coupling between cores** (our model assumes none).
6. **Statistically rigorous evaluation**: for example, work on repeated runs and confidence intervals in systems evaluation, beyond A26.
7. **Peer-reviewed versions** of B10, B14 and B15, if any exist.
8. **Global EDF tardiness bounds for soft real-time** (relevant because our workloads are overloaded and late tasks continue running).
9. **Thermal-aware scheduling on Arm big.LITTLE / heterogeneous mobile SoCs**: peer-reviewed work to replace B18 and B19.

After the remaining DOI checks in Section B, the realistic total is **about 40 verified references**, of which roughly 30–35 are directly relevant.
