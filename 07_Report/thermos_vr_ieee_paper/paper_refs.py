"""
Bibliographic records for the paper: the 38 references recommended in
REFERENCE_AUDIT.md section D, all VERIFIED. Only verified fields are filled;
nothing is guessed. Used to generate references.bib and the DOCX reference
list, so both always agree.
"""

ACCESSED = "Oct. 21, 2026"

REFS = {
    "liu1973": dict(type="article", authors=["C. L. Liu", "J. W. Layland"],
        title="Scheduling algorithms for multiprogramming in a hard-real-time environment",
        journal="J. ACM", volume="20", number="1", pages="46--61", year="1973",
        doi="10.1145/321738.321743"),
    "dhall1978": dict(type="article", authors=["S. K. Dhall", "C. L. Liu"],
        title="On a real-time scheduling problem", journal="Oper. Res.", volume="26",
        number="1", pages="127--140", year="1978", doi="10.1287/opre.26.1.127"),
    "davis2011": dict(type="article", authors=["R. I. Davis", "A. Burns"],
        title="A survey of hard real-time scheduling for multiprocessor systems",
        journal="ACM Comput. Surv.", volume="43", number="4", eid="35", year="2011",
        doi="10.1145/1978802.1978814"),
    "jeffay1991": dict(type="inproceedings", authors=["K. Jeffay", "D. F. Stanat", "C. U. Martel"],
        title="On non-preemptive scheduling of periodic and sporadic tasks",
        booktitle="Proc. 12th IEEE Real-Time Syst. Symp. (RTSS)", pages="129--139", year="1991",
        doi="10.1109/REAL.1991.160366"),
    "abeni1998": dict(type="inproceedings", authors=["L. Abeni", "G. Buttazzo"],
        title="Integrating multimedia applications in hard real-time systems",
        booktitle="Proc. 19th IEEE Real-Time Syst. Symp. (RTSS)", pages="4--13", year="1998",
        doi="10.1109/REAL.1998.739726"),
    "lelli2016": dict(type="article", authors=["J. Lelli", "C. Scordino", "L. Abeni", "D. Faggioli"],
        title="Deadline scheduling in the Linux kernel", journal="Softw. Pract. Exper.",
        volume="46", number="6", pages="821--839", year="2016", doi="10.1002/spe.2335"),
    "kdoc_deadline": dict(type="online", authors=["The Linux Kernel Documentation"],
        title="Deadline task scheduling", year="2026",
        url="https://docs.kernel.org/scheduler/sched-deadline.html"),
    "stoica1995": dict(type="techreport", authors=["I. Stoica", "H. Abdel-Wahab"],
        title="Earliest eligible virtual deadline first: A flexible and accurate mechanism for proportional share resource allocation",
        institution="Dept. Comput. Sci., Old Dominion Univ.", number="TR-95-22", year="1995",
        url="https://people.eecs.berkeley.edu/~istoica/papers/eevdf-tr-95.pdf"),
    "baruah1996": dict(type="article", authors=["S. K. Baruah", "N. K. Cohen", "C. G. Plaxton", "D. A. Varvel"],
        title="Proportionate progress: A notion of fairness in resource allocation",
        journal="Algorithmica", volume="15", pages="600--625", year="1996",
        doi="10.1007/BF01940883"),
    "chandra2000": dict(type="inproceedings", authors=["A. Chandra", "M. Adler", "P. Goyal", "P. Shenoy"],
        title="Surplus fair scheduling: A proportional-share CPU scheduling algorithm for symmetric multiprocessors",
        booktitle="Proc. 4th USENIX Symp. Operating Syst. Des. Implement. (OSDI)", pages="45--58",
        year="2000",
        url="https://www.usenix.org/conference/osdi-2000/surplus-fair-scheduling-proportional-share-cpu-scheduling-algorithm-symmetric"),
    "corbet2023": dict(type="online", authors=["J. Corbet"],
        title="An EEVDF CPU scheduler for Linux", howpublished="LWN.net", year="2023",
        month="Mar.", url="https://lwn.net/Articles/925371/"),
    "kdoc_eevdf": dict(type="online", authors=["The Linux Kernel Documentation"],
        title="EEVDF scheduler", year="2026",
        url="https://docs.kernel.org/scheduler/sched-eevdf.html"),
    "brooks2001": dict(type="inproceedings", authors=["D. Brooks", "M. Martonosi"],
        title="Dynamic thermal management for high-performance microprocessors",
        booktitle="Proc. 7th Int. Symp. High-Perform. Comput. Archit. (HPCA)", pages="171--182",
        year="2001", doi="10.1109/HPCA.2001.903261"),
    "skadron2003": dict(type="inproceedings",
        authors=["K. Skadron", "M. R. Stan", "W. Huang", "S. Velusamy", "K. Sankaranarayanan", "D. Tarjan"],
        title="Temperature-aware microarchitecture",
        booktitle="Proc. 30th Annu. Int. Symp. Comput. Archit. (ISCA)", pages="2--13", year="2003",
        doi="10.1145/859618.859620"),
    "huang2006": dict(type="article",
        authors=["W. Huang", "S. Ghosh", "S. Velusamy", "K. Sankaranarayanan", "K. Skadron", "M. R. Stan"],
        title="HotSpot: A compact thermal modeling methodology for early-stage VLSI design",
        journal="IEEE Trans. Very Large Scale Integr. (VLSI) Syst.", volume="14", number="5",
        pages="501--513", year="2006", doi="10.1109/TVLSI.2006.876103"),
    "kong2012": dict(type="article", authors=["J. Kong", "S. W. Chung", "K. Skadron"],
        title="Recent thermal management techniques for microprocessors",
        journal="ACM Comput. Surv.", volume="44", number="3", pages="1--42", year="2012",
        doi="10.1145/2187671.2187675"),
    "pillai2001": dict(type="inproceedings", authors=["P. Pillai", "K. G. Shin"],
        title="Real-time dynamic voltage scaling for low-power embedded operating systems",
        booktitle="Proc. 18th ACM Symp. Operating Syst. Principles (SOSP)", pages="89--102",
        year="2001", doi="10.1145/502034.502044"),
    "hung2005": dict(type="inproceedings",
        authors=["W.-L. Hung", "Y. Xie", "N. Vijaykrishnan", "M. Kandemir", "M. J. Irwin"],
        title="Thermal-aware task allocation and scheduling for embedded systems",
        booktitle="Proc. Design, Autom. Test Eur. (DATE)", pages="898--899", year="2005",
        doi="10.1109/DATE.2005.310"),
    "coskun2007": dict(type="inproceedings", authors=["A. K. Coskun", "T. S. Rosing", "K. Whisnant"],
        title="Temperature aware task scheduling in MPSoCs",
        booktitle="Proc. Design, Autom. Test Eur. (DATE)", pages="1--6", year="2007",
        doi="10.1109/DATE.2007.364540"),
    "chrobak2008": dict(type="inproceedings",
        authors=["M. Chrobak", "C. D\\\"urr", "M. Hurand", "J. Robert"],
        plain_authors=["M. Chrobak", "C. Dürr", "M. Hurand", "J. Robert"],
        title="Algorithms for temperature-aware task scheduling in microprocessor systems",
        booktitle="Proc. 4th Int. Conf. Algorithmic Aspects Inf. Manage. (AAIM)", series="LNCS",
        pages="120--130", year="2008", doi="10.1007/978-3-540-68880-8_13"),
    "perez2021": dict(type="inproceedings", authors=["J. P\\'{e}rez Rodr\\'{i}guez", "P. Meumeu Yomsi"],
        plain_authors=["J. Pérez Rodríguez", "P. Meumeu Yomsi"],
        title="An efficient proactive thermal-aware scheduler for DVFS-enabled single-core processors",
        booktitle="Proc. 29th Int. Conf. Real-Time Netw. Syst. (RTNS)", pages="144--154", year="2021",
        doi="10.1145/3453417.3453430"),
    "lee2019": dict(type="article", authors=["Y. Lee", "K. G. Shin", "H. S. Chwa"],
        title="Thermal-aware scheduling for integrated CPUs--GPU platforms",
        journal="ACM Trans. Embed. Comput. Syst.", volume="18", number="5s", eid="90", year="2019",
        doi="10.1145/3358235"),
    "dowling2025": dict(type="article", authors=["A. Dowling", "L. Jiang", "M.-C. Cheng", "Y. Liu"],
        title="Regulating CPU temperature with thermal-aware scheduling using a reduced order learning thermal model",
        journal="Future Gener. Comput. Syst.", volume="166", eid="107687", year="2025",
        doi="10.1016/j.future.2024.107687"),
    "kumar2003": dict(type="inproceedings",
        authors=["R. Kumar", "K. I. Farkas", "N. P. Jouppi", "P. Ranganathan", "D. M. Tullsen"],
        title="Single-ISA heterogeneous multi-core architectures: The potential for processor power reduction",
        booktitle="Proc. 36th Annu. IEEE/ACM Int. Symp. Microarchit. (MICRO)", pages="81--92",
        year="2003", doi="10.1109/MICRO.2003.1253185"),
    "kdoc_capacity": dict(type="online", authors=["The Linux Kernel Documentation"],
        title="Capacity aware scheduling", year="2026",
        url="https://docs.kernel.org/scheduler/sched-capacity.html"),
    "kdoc_eas": dict(type="online", authors=["The Linux Kernel Documentation"],
        title="Energy aware scheduling", year="2026",
        url="https://docs.kernel.org/scheduler/sched-energy.html"),
    "dou2025": dict(type="article", authors=["X. Dou", "L. Liu", "L. Xiao"],
        title="An intelligent scheduling approach on mobile OS for optimizing UI smoothness and power",
        journal="ACM Trans. Archit. Code Optim.", volume="22", number="1", eid="12", year="2025",
        doi="10.1145/3674910"),
    "pathania2014": dict(type="inproceedings", authors=["A. Pathania", "Q. Jiao", "A. Prakash", "T. Mitra"],
        title="Integrated CPU-GPU power management for 3D mobile games",
        booktitle="Proc. 51st ACM/EDAC/IEEE Design Autom. Conf. (DAC)", year="2014",
        doi="10.1145/2593069.2593151"),
    "xie2014": dict(type="inproceedings", authors=["Q. Xie", "M. J. Dousti", "M. Pedram"],
        title="Therminator: A thermal simulator for smartphones producing accurate chip and skin temperature maps",
        booktitle="Proc. Int. Symp. Low Power Electron. Des. (ISLPED)", pages="117--122", year="2014",
        doi="10.1145/2627369.2627641"),
    "zhang2020": dict(type="inproceedings",
        authors=["X. Zhang", "H. Vadodaria", "N. Li", "K.-D. Kang", "Y. Liu"],
        title="A smartphone thermal temperature analysis for virtual and augmented reality",
        booktitle="Proc. IEEE Int. Conf. Artif. Intell. Virtual Reality (AIVR)", pages="301--306",
        year="2020", doi="10.1109/AIVR50618.2020.00061"),
    "huzaifa2021": dict(type="inproceedings", authors=["M. Huzaifa", "others"],
        title="ILLIXR: Enabling end-to-end extended reality research",
        booktitle="Proc. IEEE Int. Symp. Workload Characterization (IISWC)", pages="24--38",
        year="2021", doi="10.1109/IISWC53511.2021.00014"),
    "lai2017": dict(type="inproceedings", authors=["Z. Lai", "Y. C. Hu", "Y. Cui", "L. Sun", "N. Dai"],
        title="Furion: Engineering high-quality immersive virtual reality on today's mobile devices",
        booktitle="Proc. 23rd Annu. Int. Conf. Mobile Comput. Netw. (MobiCom)", pages="409--421",
        year="2017", doi="10.1145/3117811.3117815"),
    "jerald2009": dict(type="inproceedings", authors=["J. Jerald", "M. C. Whitton"],
        title="Relating scene-motion thresholds to latency thresholds for head-mounted displays",
        booktitle="Proc. IEEE Virtual Reality Conf. (VR)", pages="211--218", year="2009",
        doi="10.1109/VR.2009.4811025"),
    "zhao2017": dict(type="inproceedings",
        authors=["J. Zhao", "R. S. Allison", "M. Vinnikov", "S. Jennings"],
        title="Estimating the motion-to-photon latency in head mounted displays",
        booktitle="Proc. IEEE Virtual Reality (VR)", pages="313--314", year="2017",
        doi="10.1109/VR.2017.7892302"),
    "li2007": dict(type="inproceedings", authors=["C. Li", "C. Ding", "K. Shen"],
        title="Quantifying the cost of context switch",
        booktitle="Proc. Workshop Exp. Comput. Sci. (ExpCS)", year="2007",
        doi="10.1145/1281700.1281702"),
    "jain1991": dict(type="book", authors=["R. Jain"],
        title="The Art of Computer Systems Performance Analysis", publisher="Wiley",
        address="New York, NY, USA", year="1991"),
    "hoefler2015": dict(type="inproceedings", authors=["T. Hoefler", "R. Belli"],
        title="Scientific benchmarking of parallel computing systems: Twelve ways to tell the masses when reporting performance results",
        booktitle="Proc. Int. Conf. High Perform. Comput., Netw., Storage Anal. (SC)", eid="73",
        year="2015", doi="10.1145/2807591.2807644"),
    "georges2007": dict(type="inproceedings", authors=["A. Georges", "D. Buytaert", "L. Eeckhout"],
        title="Statistically rigorous Java performance evaluation",
        booktitle="Proc. 22nd ACM SIGPLAN Conf. Object-Oriented Program. Syst. Lang. Appl. (OOPSLA)",
        pages="57--76", year="2007", doi="10.1145/1297027.1297033"),
}


def _join(names):
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + ", and " + names[-1]


def ieee_plain(key):
    """IEEE-style reference string (plain text) for the DOCX reference list."""
    r = REFS[key]
    names = r.get("plain_authors", r["authors"])
    authors = f"{names[0]} et al." if names[-1] == "others" else _join(names)
    pages = r.get("pages", "").replace("--", "–")
    t = r["type"]
    if t == "article":
        s = f'{authors}, “{r["title"]},” {r["journal"]}'
        if r.get("volume"):
            s += f', vol. {r["volume"]}'
        if r.get("number"):
            s += f', no. {r["number"]}'
        if r.get("eid"):
            s += f', Art. no. {r["eid"]}'
        if pages:
            s += f", pp. {pages}"
        s += f', {r["year"]}'
    elif t == "inproceedings":
        s = f'{authors}, “{r["title"]},” in {r["booktitle"]}, {r["year"]}'
        if r.get("eid"):
            s += f', Art. no. {r["eid"]}'
        if pages:
            s += f", pp. {pages}"
    elif t == "techreport":
        s = (f'{authors}, “{r["title"]},” {r["institution"]}, Tech. Rep. {r["number"]}, {r["year"]}')
    elif t == "book":
        s = f'{authors}, {r["title"]}. {r["address"]}: {r["publisher"]}, {r["year"]}'
    else:  # online
        s = f'{authors}, “{r["title"]}.”'
        if r.get("howpublished"):
            s += f' {r["howpublished"]}, {r.get("month", "")} {r["year"]}.'.replace("  ", " ")
        s = s.rstrip(".") + "."
        s += f' [Online]. Available: {r["url"]} (accessed {ACCESSED})'
        return s
    if r.get("doi"):
        s += f', doi: {r["doi"]}.'
    elif r.get("url"):
        s += f'. [Online]. Available: {r["url"]}'
    else:
        s += "."
    return s


def bibtex():
    out = ["% references.bib -- generated from paper_refs.py (all entries VERIFIED in REFERENCE_AUDIT.md)",
           "% Do not edit by hand; edit paper_refs.py and rebuild.", ""]
    for key, r in REFS.items():
        t = r["type"]
        btype = {"online": "misc"}.get(t, t)
        fields = []
        authors = " and ".join("others" if a == "others" else
                               (f"{{{a}}}" if a.startswith("The Linux") else a) for a in r["authors"])
        fields.append(("author", authors))
        fields.append(("title", "{" + r["title"] + "}"))
        for f in ("journal", "booktitle", "volume", "number", "pages", "year", "month",
                  "publisher", "address", "institution", "series", "doi", "howpublished"):
            if r.get(f):
                fields.append((f, r[f]))
        if t == "techreport" and r.get("number"):
            pass
        if r.get("eid"):
            fields.append(("articleno" if t != "article" else "eid", r["eid"]))
            fields.append(("note", f"Art. no. {r['eid']}"))
        if r.get("url"):
            fields.append(("url", r["url"]))
        if t == "online":
            fields.append(("note", f"Accessed: {ACCESSED}"))
        body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields)
        out.append(f"@{btype}{{{key},\n{body}\n}}\n")
    return "\n".join(out)
