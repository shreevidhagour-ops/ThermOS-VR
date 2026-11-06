"""
Static checks of ThermOS_VR_Research_Report.tex (no LaTeX needed):
citations vs references.bib, labels vs refs, environment and brace balance,
figure files, and stray unescaped special characters. Not a substitute for
compiling; it only catches structural errors. Run: python -B check_tex_static.py
"""
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
tex = open(os.path.join(HERE, "ThermOS_VR_Research_Report.tex"), encoding="utf-8").read()
bib = open(os.path.join(HERE, "references.bib"), encoding="utf-8").read()
body = tex.split(r"\begin{document}", 1)[1]

bibkeys = set(re.findall(r"@\w+\{([^,\s]+),", bib))
cites = {k.strip() for g in re.findall(r"\\cite\{([^}]*)\}", tex) for k in g.split(",")}
labels = set(re.findall(r"\\label\{([^}]*)\}", tex))
refs = set(re.findall(r"\\(?:ref|eqref)\{([^}]*)\}", tex))
begins = Counter(re.findall(r"\\begin\{([^}]*)\}", tex))
ends = Counter(re.findall(r"\\end\{([^}]*)\}", tex))
graphics = re.findall(r"\\includegraphics\[[^\]]*\]\{([^}]*)\}", tex)

depth, never_negative = 0, True
for ch in re.sub(r"\\[{}%$&#_]", "", tex):
    depth += (ch == "{") - (ch == "}")
    never_negative &= depth >= 0
stray = [m.start() for m in re.finditer(r"(?<!\\)[&%#](?![^\\]*\\\\)", "")]  # placeholder
unescaped_pct = len(re.findall(r"(?<!\\)%", body))
dollars = len(re.findall(r"(?<!\\)\$", body))

checks = [
    ("every \\cite key exists in references.bib", not (cites - bibkeys), sorted(cites - bibkeys)),
    ("every bib entry is cited", not (bibkeys - cites), sorted(bibkeys - cites)),
    ("every \\ref has a \\label", not (refs - labels), sorted(refs - labels)),
    ("begin/end balanced", begins == ends, dict(begins)),
    ("braces balanced", depth == 0 and never_negative, depth),
    ("figure files exist", all(os.path.isfile(os.path.join(HERE, g)) for g in graphics), graphics),
    ("no unescaped % in body", unescaped_pct == 0, unescaped_pct),
    ("even number of $ in body", dollars % 2 == 0, dollars),
]
failed = 0
for name, ok, detail in checks:
    failed += not ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail if not ok or isinstance(detail, int) else ''}")
print(f"\n{len(cites)} cited keys, {len(bibkeys)} bib entries, {len(labels)} labels, "
      f"{len(graphics)} figures. {'ALL STATIC CHECKS PASSED' if not failed else f'{failed} FAILED'}")
print("NOTE: these are static checks only; compile to verify layout and page count.")
sys.exit(1 if failed else 0)
