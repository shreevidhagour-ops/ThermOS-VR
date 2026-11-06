"""
Generate CITATION_CLAIM_LEDGER.csv from paper_content.py: one row per
(sentence, cited reference), with the reference number used in the paper,
its full citation and how it was verified (from REFERENCE_AUDIT.md).
The 'Author check' column is left for the authors to fill in.
Run: python -B make_ledger.py
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paper_content as C  # noqa: E402
import paper_refs as R  # noqa: E402
import build_paper as BP  # noqa: E402

VERIFIED_BY = {
    "kdoc_deadline": "Official kernel documentation, read 2026-10-21",
    "kdoc_eevdf": "Official kernel documentation, read 2026-10-21",
    "kdoc_eas": "Official kernel documentation, read 2026-10-21",
    "kdoc_capacity": "Official kernel documentation, read 2026-10-21",
    "stoica1995": "Author-hosted technical report",
    "chandra2000": "USENIX official page",
    "corbet2023": "LWN.net page",
    "jain1991": "Wiley product page (ISBN 978-0-471-50336-1)",
}


def clean(s):
    s = re.sub(r"\{\{([^}]+)\}\}", lambda m: BP.ref_text(m.group(1)), s)
    s = re.sub(r"\[@([^\]]+)\]", lambda m: BP.cite_label([k.strip().lstrip("@") for k in m.group(1).split(";")]), s)
    return s.replace("*", "").replace("`", "")


rows, section = [], ""
for b in C.BODY:
    if b[0] in ("h1", "h2"):
        section = f"{BP.SEC[b[1]]} {b[2]}"
    texts = [b[1]] if b[0] == "p" else (b[1] if b[0] == "ul" else [])
    for t in texts:
        for sent in re.split(r"(?<=[.;])\s+(?=[A-Z*])", t):
            for m in re.finditer(r"\[@([^\]]+)\]", sent):
                for k in [x.strip().lstrip("@") for x in m.group(1).split(";")]:
                    rows.append({
                        "Section": section,
                        "Ref no.": BP.CITE_NUM[k],
                        "Key": k,
                        "Claim (sentence as it appears in the paper)": clean(sent),
                        "Reference": R.ieee_plain(k),
                        "DOI / URL": R.REFS[k].get("doi") or R.REFS[k].get("url", ""),
                        "Verified by": VERIFIED_BY.get(k, "Crossref / publisher record (REFERENCE_AUDIT.md)"),
                        "Support level": "abstract/official-text level; authors must confirm against full text",
                        "Author check (yes/no + initials)": "",
                    })
with open(os.path.join(HERE, "CITATION_CLAIM_LEDGER.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} claim-citation rows covering {len({r['Key'] for r in rows})} references")
