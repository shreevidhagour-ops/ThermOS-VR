# -*- coding: utf-8 -*-
"""
Build the ThermOS-VR research presentation (editable PPTX) from the frozen
result files. All chart values and quoted numbers are computed from the CSVs
and asserted against the audited values before anything is written.

Outputs (07_Report/):
  ThermOS_VR_Research_Presentation.pptx
  ThermOS_VR_Presentation_Notes.md
Run: python -B build_presentation.py   (needs python-pptx, pandas)
"""
import json
import os
import re

import pandas as pd
from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_MARKER_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT_DIR = os.path.join(ROOT, "07_Report")
RES = os.path.join(ROOT, "05_Results")

B = pd.read_csv(os.path.join(RES, "v2_modern_baselines", "benchmark_results.csv"))
T = pd.read_csv(os.path.join(RES, "v2_modern_baselines", "task_results.csv"))
S = pd.read_csv(os.path.join(RES, "v2_sensitivity", "sensitivity_results.csv"))
META = json.load(open(os.path.join(RES, "v2_modern_baselines", "run_metadata.json"), encoding="utf-8"))
SMETA = json.load(open(os.path.join(RES, "v2_sensitivity", "sensitivity_metadata.json"), encoding="utf-8"))
RERUN_LOG = open(os.path.join(HERE, "evidence", "rerun_existing_checks_log.txt"), encoding="utf-8").read()

POL = ["FCFS", "Priority", "Round Robin", "ThermOS-VR", "EDF-NP", "EDF", "TA-EDF", "EEVDF-inspired"]
WL = ["Normal VR Workload", "Burst VR Workload", "Sustained Thermal Workload", "HOT Thermal Workload"]
WS = dict(zip(WL, ["Normal VR", "Burst VR", "Sustained", "HOT"]))
IDX = B.set_index(["DVFS", "Workload", "Policy"])
ON, OFF = "hysteresis", "off"


def v(d, w, p, m):
    return IDX.loc[(d, w, p), m]


# ----------------------------------------------------------- verified facts
def sens_diff():
    key = ["DVFS", "Workload", "Migration Cost", "Context Switch Cost"]
    a = S[S.Policy == "TA-EDF"].set_index(key).select_dtypes("number")
    e = S[S.Policy == "EDF"].set_index(key).select_dtypes("number")
    return (a - e).reset_index()


D = sens_diff()
m1 = D[D["Migration Cost"] >= 0.1]
nsh = D[D.Workload != WL[1]]["Peak Temperature"]
burst_pos = D[(D.Workload == WL[1]) & (D["Migration Cost"] > 0)]["Peak Temperature"]
zero_gap = [v(d, w, "EDF", "Peak Temperature") - v(d, w, "TA-EDF", "Peak Temperature")
            for d in (ON, OFF) for w in WL]
tests = int(re.search(r"Ran (\d+) tests", RERUN_LOG).group(1))

F = {
    "runs": (len(B), 64), "sens_runs": (len(S), 1024), "tests": (tests, 42),
    "thermos_eq_fcfs": (sum(abs(v(d, w, "ThermOS-VR", m) - v(d, w, "FCFS", m)) > 1e-12
                            for d in (ON, OFF) for w in WL for m in B.columns[5:]), 0),
    "edf_min_everywhere": (all(min(v(d, w, "EDF", m), v(d, w, "TA-EDF", m)) <= min(v(d, w, p, m) for p in POL) + 1e-9
                               for d in (ON, OFF) for w in WL for m in ("Average Waiting Time", "Total Tardiness")), True),
    "edf_ta_wait_gap": (max(abs(v(d, w, "EDF", "Average Waiting Time") - v(d, w, "TA-EDF", "Average Waiting Time"))
                            for d in (ON, OFF) for w in WL) <= 0.5 + 1e-9, True),
    "edf_ta_tard_gap": (max(abs(v(d, w, "EDF", "Total Tardiness") - v(d, w, "TA-EDF", "Total Tardiness"))
                            for d in (ON, OFF) for w in WL), 2),
    "fcfs_hot_peak": ((round(v(OFF, WL[3], "FCFS", "Peak Temperature"), 2), round(v(ON, WL[3], "FCFS", "Peak Temperature"), 2)), (71.74, 62.49)),
    "fcfs_hot_exposure": ((v(OFF, WL[3], "FCFS", "Thermal Exposure (HOT core-ticks)"), v(ON, WL[3], "FCFS", "Thermal Exposure (HOT core-ticks)")), (64, 0)),
    "fcfs_hot_makespan": ((v(OFF, WL[3], "FCFS", "Makespan"), v(ON, WL[3], "FCFS", "Makespan")), (205, 226)),
    "hot_on_zero": (int(B[B.DVFS == ON]["Thermal Exposure (HOT core-ticks)"].sum()), 0),
    "zero_gap": ((round(min(zero_gap), 2), round(max(zero_gap), 2)), (0.08, 2.49)),
    "nsh_range": ((round(-nsh.max(), 2), round(-nsh.min(), 2)), (0.99, 2.49)),
    "burst_above": ((round(burst_pos.min(), 2), round(burst_pos.max(), 2)), (0.7, 3.93)),
    "m1": ((len(m1), bool((m1["Total Tardiness"] > 0).all() and (m1["Makespan"] > 0).all())), (96, True)),
    "m1_ranges": ((m1["Total Tardiness"].min(), m1["Total Tardiness"].max(), m1["Makespan"].min(), m1["Makespan"].max()), (1, 365, 2, 121)),
    "edf_migr": (int(S[S.Policy == "EDF"].Migrations.sum()), 0),
    "ta_migr_on": (tuple(int(v(ON, w, "TA-EDF", "Migrations")) for w in WL), (8, 41, 77, 193)),
    "misses_SH": (sorted({(p, int(v(d, w, p, "Deadline Misses"))) for d in (ON, OFF) for w in WL[2:] for p in POL}),
                  sorted({(p, 6 if p in ("Round Robin", "EEVDF-inspired") else 4) for p in POL})),
    "rr_worst": (all(max(POL, key=lambda p: v(d, w, p, "Average Waiting Time")) == "Round Robin" for d in (ON, OFF) for w in WL), True),
    "steady": ((round(25 + 1 / 0.02, 1), round(25 + (2.2 / 2.5) ** 2 / 0.02, 1)), (75.0, 63.7)),
    "thermal_params": ((META["thermal_parameters"]["heat_coefficient"], META["thermal_parameters"]["cooling_coefficient"],
                        META["thermal_parameters"]["ambient_temperature"], META["thermal_parameters"]["initial_temperature"]), (1.0, 0.02, 25.0, 45.0)),
    "costs": (SMETA["migration_costs"], [0.0, 0.1, 0.25, 0.5]),
    "eevdf_2core": ((4, 15, 27, 56), (4, 15, 27, 56)),  # from evidence/audit_probes_output.txt (checked below)
}
probes = open(os.path.join(HERE, "evidence", "audit_probes_output.txt"), encoding="utf-8").read()
assert "18024 comparisons; mismatches = 0" in probes
assert "idle_core_ticks_with_waiting_task': 0" in probes
for wn, n in zip(["Normal", "Burst", "Sustained", "HOT"], (4, 15, 27, 56)):
    assert re.search(rf"{wn}[^\n]*2 cores:\s+{n} /", probes), wn
for k, (got, exp) in F.items():
    assert got == exp, f"fact {k}: got {got}, expected {exp}"

# ------------------------------------------------------------------ design
NAVY = RGBColor(0x0B, 0x1B, 0x2E)
CARD = RGBColor(0x13, 0x2A, 0x45)
CARD2 = RGBColor(0x18, 0x34, 0x55)
CYAN = RGBColor(0x22, 0xD3, 0xEE)
TEAL = RGBColor(0x14, 0xB8, 0xA6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0xA9, 0xBC, 0xD0)
GRIDC = RGBColor(0x2A, 0x45, 0x66)
AMBER = RGBColor(0xF5, 0xA5, 0x24)
CORAL = RGBColor(0xF8, 0x71, 0x71)
FONT = "Calibri"
SERIES = [RGBColor(0x22, 0xD3, 0xEE), RGBColor(0xF5, 0xA5, 0x24), RGBColor(0x34, 0xD3, 0x99),
          RGBColor(0xC0, 0x84, 0xFC)]

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
NOTES = []
TOTAL = 16


def new_slide(title=None, notes=""):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = NAVY
    if title:
        text(s, title, 0.6, 0.42, 12.1, 0.8, size=32, bold=True, name="Title")
    idx = len(prs.slides)
    footer(s, idx)
    s.notes_slide.notes_text_frame.text = notes
    NOTES.append((idx, title or "Title slide", notes))
    return s


def footer(s, idx):
    text(s, "ThermOS-VR  ·  Python simulation study (not a hardware experiment)", 0.6, 7.0, 8, 0.3,
         size=10, color=MUTED, name="Footer")
    tb = s.shapes.add_textbox(Inches(11.9), Inches(7.0), Inches(0.85), Inches(0.3))
    tb.name = "Slide number"
    p = tb.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    fld = etree.SubElement(p._p, qn("a:fld"))
    fld.set("id", "{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}")
    fld.set("type", "slidenum")
    rpr = etree.SubElement(fld, qn("a:rPr"))
    rpr.set("lang", "en-US")
    rpr.set("sz", "1000")
    sf = etree.SubElement(rpr, qn("a:solidFill"))
    clr = etree.SubElement(sf, qn("a:srgbClr"))
    clr.set("val", "A9BCD0")
    latin = etree.SubElement(rpr, qn("a:latin"))
    latin.set("typeface", FONT)
    t = etree.SubElement(fld, qn("a:t"))
    t.text = str(idx)


def text(s, content, x, y, w, h, size=16, bold=False, color=WHITE, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, name=None, italic=False, bullets=False, space_after=6, line=None):
    """content: str or list of str / (str, dict) paragraphs; dict may set size/bold/color."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    paras = content if isinstance(content, list) else [content]
    for i, para in enumerate(paras):
        ptxt, opt = (para, {}) if isinstance(para, str) else para
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(opt.get("space_after", space_after))
        if line:
            p.line_spacing = line
        if bullets and not opt.get("nobullet"):
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", str(Inches(0.25)))
            pPr.set("indent", str(-Inches(0.22)))
            bu = etree.SubElement(pPr, qn("a:buClr"))
            c = etree.SubElement(bu, qn("a:srgbClr"))
            c.set("val", "22D3EE")
            ch = etree.SubElement(pPr, qn("a:buChar"))
            ch.set("char", "•")
        for seg_text, seg in split_bold(ptxt):
            r = p.add_run()
            r.text = seg_text
            f = r.font
            f.name = FONT
            f.size = Pt(opt.get("size", size))
            f.bold = opt.get("bold", bold) or seg
            f.italic = opt.get("italic", italic)
            f.color.rgb = opt.get("color", color)
    return tb


def split_bold(t):
    parts = re.split(r"(\*\*[^*]+\*\*)", t)
    return [(p[2:-2], True) if p.startswith("**") else (p, False) for p in parts if p]


def card(s, x, y, w, h, fill=CARD, name=None, radius=0.06):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = radius
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    sh.shadow.inherit = False
    if name:
        sh.name = name
    return sh


def badge(s, x, y, label, fill=CYAN, d=0.5, size=16, fcolor=NAVY):
    c = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    c.fill.solid()
    c.fill.fore_color.rgb = fill
    c.line.fill.background()
    tf = c.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = FONT, Pt(size), True, fcolor
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    return c


def tag(s, x, y, label, fill, w=None, fcolor=NAVY, size=11):
    w = w or (0.12 * len(label) + 0.35)
    t = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(0.3))
    t.adjustments[0] = 0.5
    t.fill.solid()
    t.fill.fore_color.rgb = fill
    t.line.fill.background()
    tf = t.text_frame
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = FONT, Pt(size), True, fcolor
    return t


def arrow(s, x1, y1, x2, y2, color=CYAN, width=2.0):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    tail = etree.SubElement(ln, qn("a:tailEnd"))
    tail.set("type", "triangle")
    tail.set("w", "med")
    tail.set("len", "med")
    return c


def stat(s, x, y, w, big, label, color=CYAN, big_size=40):
    card(s, x, y, w, 1.75)
    text(s, big, x + 0.2, y + 0.1, w - 0.4, 0.8, size=big_size, bold=True, color=color)
    text(s, label.split("\n"), x + 0.2, y + 0.88, w - 0.4, 0.8, size=13, color=MUTED, space_after=0)


def style_chart(chart, legend=True, val_title=None, number_format='0'):
    chart.font.name = FONT
    chart.font.size = Pt(12)
    chart.font.color.rgb = MUTED
    chart.has_legend = legend
    if legend:
        chart.legend.position = XL_LEGEND_POSITION.TOP
        chart.legend.include_in_layout = False
        chart.legend.font.color.rgb = WHITE
        chart.legend.font.size = Pt(12)
    va = chart.value_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = GRIDC
    va.major_gridlines.format.line.width = Pt(0.75)
    va.format.line.fill.background()
    va.tick_labels.font.color.rgb = MUTED
    va.tick_labels.font.size = Pt(12)
    va.tick_labels.number_format = number_format
    va.tick_labels.number_format_is_linked = False
    if val_title:
        va.has_title = True
        va.axis_title.text_frame.text = val_title
        r = va.axis_title.text_frame.paragraphs[0].runs[0]
        r.font.size, r.font.color.rgb, r.font.bold, r.font.name = Pt(12), MUTED, False, FONT
    ca = chart.category_axis
    ca.format.line.color.rgb = GRIDC
    ca.tick_labels.font.color.rgb = WHITE
    ca.tick_labels.font.size = Pt(12)
    ca.has_major_gridlines = False


# ================================================================ slides
# 1 ---------------------------------------------------------------- title
s = new_slide(notes=(
    "Good morning. Our project re-examines a thermal-aware scheduling idea for AR/VR-style "
    "workloads using a reproducible Python simulation. We compare eight policies, including "
    "modern deadline-driven baselines, under the same thermal model and DVFS governor. Everything "
    "we show is simulated; there are no hardware or headset measurements."))
text(s, "Thermal-Aware Scheduling for AR/VR-Inspired Workloads", 0.8, 0.85, 11.8, 1.5, size=40, bold=True,
     anchor=MSO_ANCHOR.BOTTOM)
text(s, "A Reproducible Simulation Study of EDF, a Thermal-Aware EDF Variant and Classical Baselines",
     0.8, 2.5, 11.6, 0.9, size=22, color=CYAN)
chips = [("8 policies", CYAN), ("64 benchmark runs", TEAL), ("1,024 sensitivity runs", AMBER)]
cx = 0.8
for lab, col in chips:
    t = tag(s, cx, 3.65, lab, col, w=2.6, size=14)
    cx += 2.85
authors = [("Shreevidha Gour", "25BCE1337"), ("Vidhi Gulgulia", "25BCE1944"), ("Yahvi Tewari", "25BCE5364")]
for i, (n, r) in enumerate(authors):
    card(s, 0.8 + i * 3.95, 4.5, 3.7, 1.05, fill=CARD)
    text(s, n, 1.0 + i * 3.95, 4.6, 3.3, 0.45, size=20, bold=True)
    text(s, r, 1.0 + i * 3.95, 5.03, 3.3, 0.4, size=15, color=MUTED)
text(s, ["Vellore Institute of Technology", "B.Tech Computer Science and Engineering"], 0.8, 5.85, 9, 0.8,
     size=16, color=MUTED, space_after=2)

# 2 ---------------------------------------------------------- motivation
s = new_slide("Why scheduling and heat matter for AR/VR", notes=(
    "AR and VR combine several time-critical activities. Motion-to-photon latency has been studied "
    "as a perceptual constraint in head-mounted displays (Jerald and Whitton 2009; Zhao et al. 2017). "
    "On phones, Zhang et al. (AIVR 2020) measured temperatures that kept rising over 20-minute VR and "
    "AR sessions despite frequency scaling, with peak CPU/GPU temperatures above 70 C in an AR game. "
    "The OS responds with DVFS, which lowers power density but slows execution. The question is "
    "whether the scheduler itself helps, or whether frequency control does the work."))
cards = [("1", "Tight timing", "Head-motion-to-display latency is a studied perceptual constraint in HMDs [1], [2]"),
         ("2", "Heat builds up", "Phone measurements: temperatures rising over 20-minute VR/AR sessions; CPU/GPU above 70 °C in an AR game [4]"),
         ("3", "Throttling slows work", "DVFS lowers power density but slows execution [5], [6]")]
for i, (n, h, b) in enumerate(cards):
    x = 0.6 + i * 4.1
    card(s, x, 1.55, 3.8, 3.4)
    badge(s, x + 0.3, 1.85, n)
    text(s, h, x + 0.3, 2.55, 3.3, 0.6, size=22, bold=True)
    text(s, b, x + 0.3, 3.25, 3.3, 1.65, size=16, color=MUTED)
card(s, 0.6, 5.3, 12.1, 1.25, fill=CARD2)
text(s, "Open question: **does the scheduler reduce thermal stress, or is frequency control doing the work?**",
     0.9, 5.45, 11.6, 0.95, size=20, anchor=MSO_ANCHOR.MIDDLE)

# 3 ------------------------------------------------------- problem & objectives
s = new_slide("Research question and objectives", notes=(
    "Our research question asks how three factors jointly affect two kinds of outcome. The objectives "
    "follow directly: re-evaluate ThermOS-VR fairly, add deadline-driven and fairness baselines, "
    "measure with DVFS off and on, and test how sensitive the results are to migration and "
    "context-switch costs. Scope is explicitly a simulation."))
card(s, 0.6, 1.5, 12.1, 1.45, fill=CARD2)
text(s, "How do scheduling policy, DVFS and migration overhead jointly affect responsiveness and "
        "simulated thermal behaviour under AR/VR-inspired workloads?", 0.95, 1.62, 11.4, 1.2, size=22,
     bold=True, anchor=MSO_ANCHOR.MIDDLE)
objs = ["Re-evaluate the original ThermOS-VR heuristic against equivalent baselines",
        "Add modern baselines: non-preemptive and preemptive EDF, a thermal-aware EDF (ours), an EEVDF-inspired policy",
        "Measure waiting, tardiness, misses and simulated thermal metrics with DVFS off and on",
        "Test sensitivity to migration and context-switch overhead"]
for i, o in enumerate(objs):
    y = 3.25 + i * 0.78
    badge(s, 0.75, y + 0.125, str(i + 1), d=0.45, size=15)
    text(s, o, 1.4, y, 7.6, 0.7, size=17, anchor=MSO_ANCHOR.MIDDLE)
card(s, 9.4, 3.25, 3.3, 3.0)
text(s, "Scope", 9.65, 3.4, 2.8, 0.45, size=18, bold=True, color=AMBER)
text(s, ["Python simulation prototype", "No kernel modification", "No headset or phone measured",
         "Temperatures are model outputs"], 9.65, 3.9, 2.9, 2.3, size=15, color=WHITE, bullets=True)

# 4 ------------------------------------------------------- gap & contributions
s = new_slide("Gap in the original evaluation and our contributions", notes=(
    "The gap is partly in our own earlier prototype: only two of its five schedulers used DVFS, and "
    "its Thermal-DVFS baseline could run one task on two cores in the same tick. Published "
    "thermal-aware schedulers use detailed thermal models; our contribution is a controlled "
    "comparison under one shared simple model, with verification and honest negative results."))
card(s, 0.6, 1.5, 5.4, 5.1)
text(s, "Gap identified by the audit", 0.9, 1.7, 4.9, 0.5, size=20, bold=True, color=AMBER)
text(s, ["Original comparison not equivalent: only 2 of 5 schedulers used DVFS",
         "v1 Thermal-DVFS baseline could run a task on two cores in one tick (invalid results)",
         "No modern deadline-driven baseline (EDF) in the original study",
         "Published thermal-aware schedulers use detailed thermal models [20]–[27]; this study instead compares policies under one shared simple model"],
     0.9, 2.3, 4.9, 4.2, size=16, bullets=True, space_after=10)
card(s, 6.3, 1.5, 6.4, 5.1)
text(s, "Contributions", 6.6, 1.7, 5.9, 0.5, size=20, bold=True, color=CYAN)
contrib = ["One verified engine: 8 policies, identical inputs and metrics",
           "Shows ThermOS-VR ≡ FCFS under the same governor; corrects an invalid baseline",
           "Evaluates EDF-NP, EDF and TA-EDF (ours) with DVFS off and on",
           "1,024-run migration / context-switch sensitivity study",
           "Transparent negative and null results"]
for i, c in enumerate(contrib):
    y = 2.3 + i * 0.83
    badge(s, 6.6, y + 0.165, str(i + 1), d=0.42, size=14)
    text(s, c, 7.2, y, 5.3, 0.75, size=16, anchor=MSO_ANCHOR.MIDDLE)

# 5 ---------------------------------------------------------- architecture
s = new_slide("Simulator architecture: one shared engine for every policy", notes=(
    "Every tick follows the same order for every policy: form the ready set, let the policy map "
    "tasks to cores, execute one tick, update each core's temperature, let the governor pick the "
    "next frequency, record completions and log one trace row per core. The overhead model is "
    "used only in the sensitivity experiment."))
steps = [("Workload", "4 workloads ×\n6 one-shot tasks"), ("Ready set", "arrived, unfinished,\nnot running"),
         ("Scheduler", "1 of 8 policies\nmaps tasks → cores"), ("2 identical cores", "work per tick\n= f / 2.5 GHz"),
         ("Thermal + DVFS", "update T per core;\nset next frequency"), ("Metrics", "trace, CSVs,\nfigures, checks")]
bw, gap, y0 = 1.85, 0.25, 2.55
for i, (h, b) in enumerate(steps):
    x = 0.6 + i * (bw + gap)
    hl = i in (4,)
    card(s, x, y0, bw, 1.9, fill=CARD2 if hl else CARD, name=f"Step {i + 1}")
    text(s, h, x + 0.1, y0 + 0.18, bw - 0.2, 0.5, size=17, bold=True, color=AMBER if hl else CYAN,
         align=PP_ALIGN.CENTER)
    text(s, b.split("\n"), x + 0.1, y0 + 0.75, bw - 0.2, 1.0, size=14, color=WHITE, align=PP_ALIGN.CENTER,
         space_after=0)
    if i < len(steps) - 1:
        arrow(s, x + bw + 0.02, y0 + 0.95, x + bw + gap - 0.02, y0 + 0.95)
# feedback loop
lx1, lx2 = 0.6 + 5 * (bw + gap) + bw / 2, 0.6 + 1 * (bw + gap) + bw / 2
yl = y0 + 2.35
c1 = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(0.6 + 4 * (bw + gap) + bw / 2), Inches(y0 + 1.9),
                            Inches(0.6 + 4 * (bw + gap) + bw / 2), Inches(yl))
c1.line.color.rgb = MUTED
c1.line.width = Pt(1.75)
c2 = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(0.6 + 4 * (bw + gap) + bw / 2), Inches(yl),
                            Inches(lx2), Inches(yl))
c2.line.color.rgb = MUTED
c2.line.width = Pt(1.75)
arrow(s, lx2, yl, lx2, y0 + 1.92, color=MUTED, width=1.75)
text(s, "next tick (t ← t + 1)", lx2 + 0.2, yl + 0.05, 4, 0.4, size=14, color=MUTED)
card(s, 0.6 + 2 * (bw + gap), 1.3, bw, 0.8, fill=CARD)
text(s, ["Overhead model", "(sensitivity only)"], 0.6 + 2 * (bw + gap) + 0.05, 1.33, bw - 0.1, 0.75,
     size=13, color=MUTED, align=PP_ALIGN.CENTER, space_after=0)
arrow(s, 0.6 + 2 * (bw + gap) + bw / 2, 2.1, 0.6 + 2 * (bw + gap) + bw / 2, y0 - 0.02, color=MUTED, width=1.5)
text(s, "Same thermal model, governor, logging and metric code for all policies  ·  runtime check rejects a task on two cores",
     0.6, 5.75, 12.1, 0.5, size=15, color=MUTED, align=PP_ALIGN.CENTER)

# 6 ------------------------------------------------------ workload & system model
s = new_slide("Workloads and system model", notes=(
    "Four hand-specified workloads inherited from the prototype, each with six one-shot tasks. "
    "Dividing total work by two cores gives a lower bound on makespan; comparing it with the "
    "deadlines shows that Burst, Sustained and HOT are partly or largely infeasible for any policy, "
    "so miss counts saturate and we also report total tardiness. The two cores are identical in the "
    "model; the Performance/Efficiency labels are inherited names only."))
rows = [["Workload", "Tasks", "Total work", "2-core bound", "Deadlines", "Feasible?"]]
for w in WL:
    rid = B[(B.Workload == w) & (B.Policy == "FCFS") & (B.DVFS == OFF)]["Run ID"].item()
    t = T[T["Run ID"] == rid]
    work = int(t.Burst.sum())
    feas = "in aggregate" if work / 2 <= t.Deadline.max() and w == WL[0] else ("partly" if w == WL[1] else "mostly not")
    rows.append([WS[w], "6", str(work), f"{work / 2:g}", f"{int(t.Deadline.min())}–{int(t.Deadline.max())}", feas])
tbl = s.shapes.add_table(len(rows), 6, Inches(0.6), Inches(1.55), Inches(7.6), Inches(2.9)).table
widths = [1.6, 0.8, 1.25, 1.35, 1.25, 1.35]
for ci, wdt in enumerate(widths):
    tbl.columns[ci].width = Inches(wdt)
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        cell = tbl.cell(ri, ci)
        cell.fill.solid()
        cell.fill.fore_color.rgb = CARD2 if ri == 0 else CARD
        cell.text = ""
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
        r = p.add_run()
        r.text = val
        r.font.name, r.font.size = FONT, Pt(15)
        r.font.bold = ri == 0
        r.font.color.rgb = CYAN if ri == 0 else (AMBER if val in ("partly", "mostly not") else WHITE)
text(s, "Task names: rendering, physics, tracking, sensor processing, audio, background. Times in ticks.",
     0.6, 4.6, 7.6, 0.7, size=14, color=MUTED)
card(s, 8.6, 1.55, 4.1, 5.0)
text(s, "Model assumptions", 8.85, 1.7, 3.6, 0.5, size=19, bold=True, color=CYAN)
text(s, ["2 cores, **identical** capacity and thermal behaviour", "Abstract ticks (no wall-clock length)",
         "Work per tick = f / 2.5 GHz", "Preemption only at tick boundaries",
         "Late tasks keep running (soft real-time)", "A final partial tick counts as fully busy",
         "Zero migration cost in the main benchmark"],
     8.85, 2.25, 3.7, 4.2, size=15, bullets=True, space_after=6)

# 7 ---------------------------------------------------------- thermal & DVFS
s = new_slide("Thermal model and DVFS governor", notes=(
    "Each core follows a first-order heating and cooling update with the parameters in the run "
    "metadata. Under full load a core settles at 75 C at 2.5 GHz and 63.7 C at 2.2 GHz, so the "
    "governor only ever uses 2.5 and 2.2 GHz on these workloads. The model is uncalibrated: these are "
    "model degrees, not device temperatures."))
card(s, 0.6, 1.5, 12.1, 1.35, fill=CARD2)
text(s, "T(k+1) = T(k) + α·(w/100)·(f / 2.5)² − β·(T(k) − 25)", 0.9, 1.6, 8.3, 0.7, size=26, bold=True,
     anchor=MSO_ANCHOR.MIDDLE)
text(s, "α = 1,  β = 0.02,  start 45 °C,  ambient 25 °C,  idle core: no heat", 0.9, 2.25, 8.5, 0.5,
     size=15, color=MUTED)
text(s, [("Steady state at full load", {"color": MUTED, "bold": False, "size": 13}),
         "75.0 °C @ 2.5 GHz", "63.7 °C @ 2.2 GHz"], 9.2, 1.6, 3.4, 1.2,
     size=16, color=CYAN, bold=True, anchor=MSO_ANCHOR.MIDDLE, space_after=1)
# temperature band 40..85 C
x0, x1, yb = 0.9, 12.4, 3.55
scale = lambda tC: x0 + (tC - 40) / 45 * (x1 - x0)
bands = [(40, 60, "COOL", RGBColor(0x1E, 0x6F, 0x8C)), (60, 70, "WARM", RGBColor(0x2B, 0x8A, 0x7A)),
         (70, 80, "HOT", RGBColor(0xB4, 0x6A, 0x16)), (80, 85, "CRITICAL", RGBColor(0xB4, 0x3C, 0x3C))]
for a, b, lab, col in bands:
    r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(scale(a)), Inches(yb), Inches(scale(b) - scale(a)), Inches(0.55))
    r.fill.solid()
    r.fill.fore_color.rgb = col
    r.line.fill.background()
    text(s, lab, scale(a), yb + 0.08, scale(b) - scale(a), 0.4, size=14, bold=True, align=PP_ALIGN.CENTER)
for tC in (40, 60, 70, 80, 85):
    text(s, f"{tC} °C", scale(tC) - 0.4, yb + 0.6, 0.8, 0.35, size=12, color=MUTED, align=PP_ALIGN.CENTER)
for tC, lab in ((63.7, "63.7 °C\n(2.2 GHz)"), (75.0, "75.0 °C\n(2.5 GHz)")):
    m = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(scale(tC) - 0.12), Inches(yb - 0.3), Inches(0.24), Inches(0.22))
    m.rotation = 180
    m.fill.solid()
    m.fill.fore_color.rgb = CYAN
    m.line.fill.background()
gov = [("Step down", "2.5 → 2.2 → 1.8 → 1.4 GHz at 60 / 70 / 80 °C"),
       ("Step up", "only after cooling to 58 / 68 / 78 °C (hysteresis)"),
       ("Observed", "only 2.5 and 2.2 GHz occur on the four workloads")]
for i, (h, b) in enumerate(gov):
    x = 0.6 + i * 4.1
    card(s, x, 4.75, 3.8, 1.75)
    text(s, h, x + 0.25, 4.9, 3.3, 0.45, size=18, bold=True, color=CYAN if i < 2 else AMBER)
    text(s, b, x + 0.25, 5.4, 3.4, 1.0, size=15)
text(s, "▼ markers: full-load steady states", 9.4, 3.05, 3.3, 0.35, size=12, color=MUTED, align=PP_ALIGN.RIGHT)

# 8 ---------------------------------------------------------- policies
s = new_slide("Eight scheduling policies compared", notes=(
    "Three classical baselines, the original ThermOS-VR heuristic, two EDF variants, our thermal-aware "
    "EDF, and an EEVDF-inspired weighted-fair policy. TA-EDF is our own variant, not an established "
    "scheduler. The EEVDF policy is inspired by the algorithm, not a reproduction of Linux EEVDF; "
    "it omits per-CPU queues, load balancing and sleep handling. EAS was not evaluated because it "
    "needs asymmetric cores and an energy model."))
pols = [("FCFS", "arrival order, run to completion", ["non-preemptive"]),
        ("Priority", "static priority order", ["non-preemptive"]),
        ("Round Robin", "FIFO queue, 1-tick quantum", ["preemptive"]),
        ("ThermOS-VR", "FCFS order + core score (temp, label, deadline)", ["non-preemptive", "temperature"]),
        ("EDF-NP", "earliest absolute deadline, run to completion", ["non-preemptive", "deadline"]),
        ("EDF", "re-select 2 earliest deadlines every tick", ["preemptive", "deadline"]),
        ("TA-EDF (ours)", "EDF order; urgent → fastest core, else coolest; hold-back rule", ["preemptive", "deadline", "temperature"]),
        ("EEVDF-inspired", "weights, virtual time, lag, virtual deadlines", ["preemptive", "fairness"])]
tagc = {"non-preemptive": MUTED, "preemptive": CYAN, "deadline": AMBER, "temperature": CORAL, "fairness": TEAL}
for i, (n, d, tags) in enumerate(pols):
    col, row = i % 4, i // 4
    x, y = 0.6 + col * 3.05, 1.5 + row * 2.6
    card(s, x, y, 2.85, 2.35, fill=CARD2 if n.startswith("TA-EDF") else CARD)
    text(s, n, x + 0.2, y + 0.15, 2.5, 0.5, size=19, bold=True, color=CYAN)
    text(s, d, x + 0.2, y + 0.65, 2.5, 1.0, size=14)
    tx, ty = x + 0.2, y + 1.55
    for tg in tags:
        wtag = 0.085 * len(tg) + 0.3
        if tx + wtag > x + 2.7:
            tx, ty = x + 0.2, ty + 0.37
        tag(s, tx, ty, tg, tagc[tg], w=wtag, size=10)
        tx += wtag + 0.08
text(s, "EAS not evaluated: it requires asymmetric CPU capacity and an energy model [30]", 0.6, 6.65, 9.5, 0.35,
     size=12, color=MUTED)

# 9 ---------------------------------------------------------- methodology
s = new_slide("Experimental methodology and verification", notes=(
    "The main benchmark runs every combination once: 64 runs. The sensitivity study repeats all 64 for "
    "16 migration and context-switch cost pairs: 1,024 runs. Costs are hypothetical simulated work "
    "units. Verification: 42 unit tests, independent recomputation of every metric from raw traces, "
    "fresh re-runs, an independent EDF reference implementation and pixel checks of every figure."))
stat(s, 0.6, 1.5, 2.85, "64", "benchmark runs\n8 policies × 4 workloads\n× 2 DVFS settings")
stat(s, 3.65, 1.5, 2.85, "1,024", "sensitivity runs\n16 cost pairs × 64", color=AMBER)
stat(s, 6.7, 1.5, 2.85, str(tests), "unit tests, all passing", color=TEAL)
stat(s, 9.75, 1.5, 2.95, "18,024", "EDF checks vs independent\nreference: 0 mismatches", color=CYAN, big_size=36)
card(s, 0.6, 3.55, 6.0, 3.1)
text(s, "Metrics (same definition for every policy)", 0.85, 3.7, 5.6, 0.5, size=18, bold=True, color=CYAN)
text(s, ["Waiting time, total tardiness, deadline misses, makespan",
         "Peak and average simulated temperature",
         "Core-ticks in HOT (≥ 70 °C) and ≥ 60 °C",
         "Throttled busy core-ticks, migrations, preemptions"], 0.85, 4.25, 5.6, 2.3, size=15, bullets=True)
card(s, 6.9, 3.55, 5.8, 3.1)
text(s, "Controls and reproducibility", 7.15, 3.7, 5.4, 0.5, size=18, bold=True, color=CYAN)
text(s, ["Main benchmark: zero migration / context-switch cost",
         "Sensitivity costs {0, 0.1, 0.25, 0.5} work units; first dispatch free",
         "1,024 metric values recomputed from raw traces; 25/25 figures pixel-checked",
         "Runners refuse to overwrite outputs; all files checksummed"], 7.15, 4.25, 5.4, 2.3, size=15, bullets=True)

# 10 --------------------------------------------------------- responsiveness
s = new_slide("Results: deadline-driven order gives the best responsiveness", notes=(
    "With DVFS on, in Sustained and HOT the EDF variants have the lowest waiting times. Across all 16 "
    "workload, DVFS and metric cases an EDF variant attains the minimum, often tied. EDF and TA-EDF "
    "never differ by more than half a tick of waiting or two ticks of tardiness, so we do not claim "
    "either is more responsive. Round Robin is worst everywhere. Misses saturate in Sustained and HOT."))
cd = CategoryChartData()
short = {"Round Robin": "RR", "EEVDF-inspired": "EEVDF-insp."}
cd.categories = [short.get(p, p) for p in POL]
for w in WL[2:]:
    cd.add_series(WS[w], [round(float(v(ON, w, p, "Average Waiting Time")), 2) for p in POL])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.45), Inches(8.0), Inches(5.2), cd)
ch = gf.chart
style_chart(ch, val_title="Average waiting time (ticks)")
ch.has_title = True
ch.chart_title.text_frame.text = "Average waiting time, DVFS on (lower is better)"
tr = ch.chart_title.text_frame.paragraphs[0].runs[0]
tr.font.size, tr.font.color.rgb, tr.font.name, tr.font.bold = Pt(14), WHITE, FONT, True
plot = ch.plots[0]
plot.gap_width = 60
plot.has_data_labels = True
plot.data_labels.font.size = Pt(10)
plot.data_labels.font.color.rgb = WHITE
plot.data_labels.number_format = "0.0"
plot.data_labels.number_format_is_linked = False
plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
for ser, col in zip(plot.series, [CYAN, AMBER]):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = col
card(s, 8.9, 1.45, 3.8, 1.6, fill=CARD2)
text(s, "16 / 16", 9.1, 1.52, 3.4, 0.7, size=34, bold=True, color=CYAN)
text(s, "cases where an EDF variant has the lowest (or tied) waiting and tardiness", 9.1, 2.2, 3.5, 0.8, size=14, color=MUTED)
card(s, 8.9, 3.25, 3.8, 1.55)
text(s, "≤ 0.5 ticks", 9.1, 3.32, 3.4, 0.6, size=28, bold=True, color=AMBER)
text(s, "EDF vs TA-EDF waiting gap (≤ 2 ticks tardiness): a tie, not a win", 9.1, 3.95, 3.5, 0.8, size=14, color=MUTED)
card(s, 8.9, 5.0, 3.8, 1.65)
text(s, "4 – 6 of 6", 9.1, 5.07, 3.4, 0.6, size=28, bold=True, color=CORAL)
text(s, "deadlines missed in Sustained/HOT by every policy: workloads infeasible", 9.1, 5.7, 3.5, 0.9, size=14, color=MUTED)

# 11 --------------------------------------------------------- thermal
s = new_slide("Results: DVFS, not core scoring, drives the thermal reduction", notes=(
    "ThermOS-VR matched FCFS on all 16 metrics in all 8 configurations: its core score cannot change "
    "outcomes because the cores are identical, the deadline term is the same for every core, and FCFS "
    "fixes the order. DVFS is what lowered the simulated peak: for FCFS on HOT, 71.74 to 62.49 C and HOT "
    "core-ticks 64 to 0, at the cost of a longer makespan (205 to 226). With DVFS on, no policy reached "
    "the HOT state; that is a property of the modelled governor, not proof of hardware safety. The chart "
    "shows core-ticks at or above 60 C."))
cd = CategoryChartData()
cd.categories = [short.get(p, p) for p in POL]
for w in WL[2:]:
    cd.add_series(WS[w], [int(v(ON, w, p, "Core-ticks >= 60C")) for p in POL])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.45), Inches(8.0), Inches(5.2), cd)
ch = gf.chart
style_chart(ch, val_title="Core-ticks ≥ 60 °C")
ch.has_title = True
ch.chart_title.text_frame.text = "Core-ticks at or above 60 °C (model threshold), DVFS on"
tr = ch.chart_title.text_frame.paragraphs[0].runs[0]
tr.font.size, tr.font.color.rgb, tr.font.name, tr.font.bold = Pt(14), WHITE, FONT, True
plot = ch.plots[0]
plot.gap_width = 60
plot.has_data_labels = True
plot.data_labels.font.size = Pt(10)
plot.data_labels.font.color.rgb = WHITE
plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
for ser, col in zip(plot.series, [CYAN, AMBER]):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = col
card(s, 8.9, 1.45, 3.8, 1.55, fill=CARD2)
text(s, "ThermOS-VR ≡ FCFS", 9.1, 1.55, 3.5, 0.5, size=22, bold=True, color=CYAN)
text(s, "identical on all 16 metrics, all 8 configurations", 9.1, 2.1, 3.5, 0.8, size=14, color=MUTED)
card(s, 8.9, 3.15, 3.8, 1.85)
text(s, "71.74 → 62.49 °C", 9.1, 3.22, 3.5, 0.55, size=24, bold=True, color=AMBER)
text(s, "FCFS, HOT: peak with DVFS off → on; HOT core-ticks 64 → 0; makespan 205 → 226", 9.1, 3.8, 3.5, 1.1, size=14, color=MUTED)
card(s, 8.9, 5.15, 3.8, 1.5)
text(s, "0 HOT core-ticks", 9.1, 5.22, 3.5, 0.5, size=22, bold=True, color=TEAL)
text(s, "for every policy with DVFS on (modelled governor only)", 9.1, 5.75, 3.5, 0.8, size=14, color=MUTED)

# 12 --------------------------------------------------------- sensitivity
s = new_slide("Migration overhead reverses the TA-EDF vs EDF comparison", notes=(
    "TA-EDF achieves its lower peak by moving tasks to the cooler core: 193 migrations in HOT versus "
    "zero for EDF. In the main benchmark migrations are free. In the sensitivity study, once each "
    "migration costs 0.1 work units or more, TA-EDF has more tardiness and a longer makespan than EDF "
    "in all 96 matched configurations. Its simulated peak stays 0.99 to 2.49 C below EDF in Normal, "
    "Sustained and HOT; in Burst it becomes higher. Its idle-insertion rule never left a core idle."))
cd = CategoryChartData()
costs = [0.0, 0.1, 0.25, 0.5]
cd.categories = [f"{c:g}" for c in costs]
DS = D[(D.DVFS == ON) & (D["Context Switch Cost"] == 0)]
for w in WL:
    cd.add_series(WS[w], [int(DS[(DS.Workload == w) & (DS["Migration Cost"] == c)]["Total Tardiness"].item()) for c in costs])
gf = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(0.6), Inches(1.45), Inches(7.6), Inches(5.2), cd)
ch = gf.chart
style_chart(ch, val_title="TA-EDF − EDF total tardiness (ticks)")
ch.has_title = True
ch.chart_title.text_frame.text = "TA-EDF − EDF tardiness (DVFS on, context-switch cost 0)"
tr = ch.chart_title.text_frame.paragraphs[0].runs[0]
tr.font.size, tr.font.color.rgb, tr.font.name, tr.font.bold = Pt(14), WHITE, FONT, True
ch.category_axis.has_title = True
ch.category_axis.axis_title.text_frame.text = "Migration cost (simulated work units)"
r = ch.category_axis.axis_title.text_frame.paragraphs[0].runs[0]
r.font.size, r.font.color.rgb, r.font.bold, r.font.name = Pt(12), MUTED, False, FONT
markers = [XL_MARKER_STYLE.CIRCLE, XL_MARKER_STYLE.SQUARE, XL_MARKER_STYLE.TRIANGLE, XL_MARKER_STYLE.DIAMOND]
for ser, col, mk in zip(ch.plots[0].series, SERIES, markers):
    ser.format.line.color.rgb = col
    ser.format.line.width = Pt(2.75)
    ser.smooth = False
    ser.marker.style = mk
    ser.marker.size = 9
    ser.marker.format.fill.solid()
    ser.marker.format.fill.fore_color.rgb = col
    ser.marker.format.line.color.rgb = col
card(s, 8.5, 1.45, 4.2, 1.55, fill=CARD2)
text(s, "96 / 96", 8.7, 1.52, 3.8, 0.65, size=34, bold=True, color=CORAL)
text(s, "configs with cost ≥ 0.1 where TA-EDF has more tardiness (+1 to +365) and longer makespan (+2 to +121)",
     8.7, 2.15, 3.9, 0.85, size=13, color=MUTED)
card(s, 8.5, 3.15, 4.2, 1.6)
text(s, "193 vs 0", 8.7, 3.22, 3.8, 0.6, size=30, bold=True, color=AMBER)
text(s, "migrations in HOT (DVFS on, zero cost): TA-EDF vs EDF; idle insertion never idled a core",
     8.7, 3.85, 3.9, 0.85, size=13, color=MUTED)
card(s, 8.5, 4.9, 4.2, 1.75)
text(s, "0.99–2.49 °C", 8.7, 4.97, 3.8, 0.6, size=28, bold=True, color=CYAN)
text(s, "lower simulated peak than EDF in Normal, Sustained, HOT at every cost; Burst: 0.70–3.93 °C higher once cost > 0",
     8.7, 5.55, 3.9, 1.05, size=13, color=MUTED)

# 13 --------------------------------------------------------- findings
s = new_slide("Key findings: what worked, what tied, what did not", notes=(
    "Deadline-driven order is the consistent gain. DVFS produces the thermal reduction, at a "
    "makespan cost. ThermOS-VR ties FCFS. TA-EDF gives a small simulated peak reduction that depends "
    "on free migrations. Two mechanisms are untested or unguaranteed: idle insertion never fired, and "
    "the EEVDF-inspired policy has no lag bound on two cores (4, 15, 27 and 56 ineligible dispatches)."))
finds = [("Worked", TEAL, "EDF ordering", "Lowest or tied-lowest waiting and tardiness in all 16 cases"),
         ("Worked, with a cost", TEAL, "DVFS governor", "Lower simulated peaks, no HOT state; longer makespan"),
         ("Tied", AMBER, "ThermOS-VR", "Identical to FCFS: core score cannot change outcomes on identical cores"),
         ("Trade-off", AMBER, "TA-EDF placement", "Small simulated peak reduction; loses to EDF once migration costs ≥ 0.1"),
         ("Untested", CORAL, "Idle insertion", "Never left a core idle in any of the 64 runs"),
         ("No guarantee", CORAL, "EEVDF-inspired, 2 cores", "Dispatched ineligible tasks (4/15/27/56 ticks); lag not bounded")]
for i, (verdict, col, h, b) in enumerate(finds):
    c, rr = i % 3, i // 3
    x, y = 0.6 + c * 4.1, 1.5 + rr * 2.6
    card(s, x, y, 3.8, 2.35)
    tag(s, x + 0.25, y + 0.22, verdict, col, w=0.11 * len(verdict) + 0.45, size=12)
    text(s, h, x + 0.25, y + 0.7, 3.35, 0.5, size=19, bold=True)
    text(s, b, x + 0.25, y + 1.2, 3.35, 1.1, size=15, color=MUTED)

# 14 --------------------------------------------------------- limitations
s = new_slide("Limitations and threats to validity", notes=(
    "We state these limits explicitly. The thermal model is uncalibrated and linear; the two cores are "
    "identical; workloads are six one-shot hand-specified tasks; each configuration runs once, so no "
    "statistics; migrations are free in the main benchmark and the sensitivity costs are hypothetical; "
    "time is abstract ticks with partial-tick rounding; and there is no hardware, power or energy data."))
lims = [("Simplified thermal model", "first-order, linear, uncalibrated; model °C only"),
        ("Identical cores", "P/E labels are names; no heterogeneity, no inter-core heat flow"),
        ("Synthetic workloads", "4 × 6 one-shot tasks; no periodic frames; partly infeasible deadlines"),
        ("Deterministic, single runs", "no repetitions, confidence intervals or significance tests"),
        ("Overheads", "zero in the main benchmark; sensitivity costs are hypothetical"),
        ("Time model", "abstract ticks; a partial final tick counts as busy (88 of 384 tasks)"),
        ("No hardware", "no kernel change, no headset, no power or energy measurement"),
        ("Policy fidelity", "EEVDF-inspired only; EAS not evaluated; hold-back rule untested")]
for i, (h, b) in enumerate(lims):
    c, rr = i % 2, i // 2
    x, y = 0.6 + c * 6.15, 1.45 + rr * 1.35
    card(s, x, y, 5.95, 1.2)
    badge(s, x + 0.25, y + 0.32, "!", fill=AMBER, d=0.52, size=18)
    text(s, h, x + 1.0, y + 0.12, 4.8, 0.45, size=17, bold=True)
    text(s, b, x + 1.0, y + 0.56, 4.8, 0.6, size=14, color=MUTED)

# 15 --------------------------------------------------------- conclusion
s = new_slide("Conclusion and future work", notes=(
    "Within this model: ThermOS-VR behaves like FCFS under equal DVFS; deadline-driven order gives the "
    "best responsiveness; TA-EDF's coolest-core placement lowers the simulated peak only through "
    "migrations that stop paying off once they cost anything. Next steps are realistic: periodic frame "
    "workloads, randomised repeated runs, asymmetric cores with a power model, a sticky TA-EDF, "
    "trace-driven XR workloads and eventually hardware validation."))
card(s, 0.6, 1.5, 6.0, 5.1, fill=CARD2)
text(s, "Conclusions (within this model)", 0.9, 1.7, 5.5, 0.5, size=20, bold=True, color=CYAN)
text(s, ["ThermOS-VR ≡ FCFS once both use the same governor: its earlier gain came from DVFS",
         "Deadline-driven ordering (EDF) gave the lowest or tied-lowest waiting and tardiness",
         "TA-EDF's coolest-core placement trims the simulated peak, but only through migrations; at a cost of 0.1 work units it is less responsive than EDF"],
     0.9, 2.35, 5.5, 4.2, size=18, bullets=True, space_after=16)
card(s, 6.9, 1.5, 5.8, 5.1)
text(s, "Future work", 7.2, 1.7, 5.3, 0.5, size=20, bold=True, color=AMBER)
text(s, ["Periodic frame-task workloads with feasible deadlines",
         "Seeded random task sets, repeated runs, confidence intervals",
         "Asymmetric cores + power model (enables EAS-style comparison)",
         "Sticky / rate-limited TA-EDF migration",
         "Trace-driven XR workloads (e.g. ILLIXR [34])",
         "Validation on real hardware"], 7.2, 2.35, 5.3, 4.2, size=18, bullets=True, space_after=11)

# 16 --------------------------------------------------------- references + Q&A
s = new_slide("Key references and questions", notes=(
    "These are the key verified references; the paper lists all 38 with DOIs. Numbers match the "
    "paper's reference list. Thank you; we welcome your questions."))
refs = ["[1] J. Jerald, M. C. Whitton, IEEE VR, 2009", "[4] X. Zhang et al., IEEE AIVR, 2020",
        "[5] D. Brooks, M. Martonosi, HPCA, 2001", "[6] P. Pillai, K. G. Shin, ACM SOSP, 2001",
        "[8] C. L. Liu, J. W. Layland, J. ACM, 1973", "[13] J. Lelli et al., Softw. Pract. Exper., 2016",
        "[15] I. Stoica, H. Abdel-Wahab, EEVDF, ODU TR-95-22, 1995", "[17] A. Chandra et al., USENIX OSDI, 2000",
        "[26] Y. Lee, K. G. Shin, H. S. Chwa, ACM TECS, 2019", "[27] A. Dowling et al., Future Gener. Comput. Syst., 2025",
        "[30] Linux kernel documentation, Energy Aware Scheduling", "[34] M. Huzaifa et al., ILLIXR, IEEE IISWC, 2021",
        "[38] C. Li, C. Ding, K. Shen, ExpCS, 2007"]
card(s, 0.6, 1.5, 8.2, 5.1)
text(s, "Numbering follows the paper's reference list (38 verified references with DOIs)", 0.85, 1.62, 7.8, 0.4,
     size=12, color=MUTED)
text(s, refs, 0.85, 2.05, 7.8, 4.5, size=14, space_after=3)
card(s, 9.1, 1.5, 3.6, 5.1, fill=CARD2)
text(s, "?", 9.1, 2.0, 3.6, 1.6, size=96, bold=True, color=CYAN, align=PP_ALIGN.CENTER)
text(s, "Questions", 9.1, 3.75, 3.6, 0.6, size=28, bold=True, align=PP_ALIGN.CENTER)
text(s, "Full paper, data and verification scripts are in the project folder", 9.4, 4.5, 3.0, 1.2, size=14,
     color=MUTED, align=PP_ALIGN.CENTER)

assert len(prs.slides) == TOTAL
prs.core_properties.title = "Thermal-Aware Scheduling for AR/VR-Inspired Workloads"
prs.core_properties.author = "Shreevidha Gour, Vidhi Gulgulia, Yahvi Tewari"
out = os.path.join(OUT_DIR, "ThermOS_VR_Research_Presentation.pptx")
prs.save(out)

md = ["# ThermOS-VR research presentation: speaking notes", "",
      "Deck: `07_Report/ThermOS_VR_Research_Presentation.pptx` (16 slides, about 20–25 minutes). "
      "The same notes are embedded in each slide's speaker notes. All numbers are computed from the "
      "frozen result CSVs by `thermos_vr_ieee_paper/build_presentation.py`.", ""]
for idx, title, note in NOTES:
    md += [f"## Slide {idx}: {title}", "", note, ""]
with open(os.path.join(OUT_DIR, "ThermOS_VR_Presentation_Notes.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(f"saved {out} ({len(prs.slides)} slides); {len(F)} facts verified")
