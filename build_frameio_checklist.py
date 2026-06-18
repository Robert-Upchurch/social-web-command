"""
Frame.io Setup Checklist for Social & Web Command
A printable, click-through guide to create the brand folder structure.
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_LEFT
from reportlab.graphics.shapes import Drawing, Rect

OUT = "/home/user/workspace/social-web-command/Frame_io_Setup_Checklist.pdf"

C_BG     = colors.HexColor("#0b0b0d")
C_ACCENT = colors.HexColor("#dc2626")
C_TXT    = colors.HexColor("#1c1d22")
C_MUTED  = colors.HexColor("#6b6f78")
C_LINE   = colors.HexColor("#e5e7eb")

def checkbox(size=11):
    d = Drawing(size+2, size+2)
    r = Rect(1, 1, size, size, rx=2, ry=2)
    r.fillColor = colors.white
    r.strokeColor = C_MUTED
    r.strokeWidth = 0.8
    d.add(r)
    return d

def section_swatch(color):
    d = Drawing(12, 12)
    r = Rect(1, 1, 10, 10, rx=2, ry=2)
    r.fillColor = colors.HexColor(color)
    r.strokeColor = colors.HexColor("#00000000")
    r.strokeWidth = 0
    d.add(r)
    return d

doc = SimpleDocTemplate(
    OUT,
    pagesize=LETTER,
    leftMargin=0.6*inch, rightMargin=0.6*inch,
    topMargin=0.6*inch, bottomMargin=0.6*inch,
    title="Frame.io Setup Checklist — Social & Web Command",
    author="Perplexity Computer",
)

s_title    = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=22, textColor=C_ACCENT, leading=26, spaceAfter=4)
s_subtitle = ParagraphStyle("subtitle", fontName="Helvetica", fontSize=11, textColor=C_MUTED, leading=14, spaceAfter=14)
s_h2       = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13, textColor=C_TXT, leading=16, spaceBefore=10, spaceAfter=6)
s_body     = ParagraphStyle("body", fontName="Helvetica", fontSize=10, textColor=C_TXT, leading=14, spaceAfter=4)
s_caption  = ParagraphStyle("caption", fontName="Helvetica-Oblique", fontSize=9, textColor=C_MUTED, leading=12, spaceAfter=4)
s_step     = ParagraphStyle("step", fontName="Helvetica", fontSize=10, textColor=C_TXT, leading=15)
s_brand    = ParagraphStyle("brand", fontName="Helvetica-Bold", fontSize=11, textColor=C_ACCENT, leading=14)

story = []

# ---------- HEADER ----------
story.append(Paragraph("Frame.io Setup Checklist", s_title))
story.append(Paragraph("Social &amp; Web Command — CTI Group Worldwide Services, Inc.", s_subtitle))

story.append(Paragraph(
    "This checklist creates the brand folder structure in Frame.io so the Social &amp; Web Command hub "
    "can index past YouTube masters, promo edits, and archived footage in one organized place. "
    "Estimated time: <b>10 minutes</b>.",
    s_body
))

# ---------- BEFORE YOU START ----------
story.append(Paragraph("Before you start", s_h2))
prereq_rows = [
    [checkbox(), Paragraph("Log in at <b>app.frame.io</b> with the CTI Group Worldwide team account.", s_step)],
    [checkbox(), Paragraph("Confirm you have <b>Admin</b> or <b>Team Member</b> role (required to create projects).", s_step)],
    [checkbox(), Paragraph("If a project named <b>CTI Group Worldwide</b> does not exist, click <b>+ New Project</b> and create it.", s_step)],
]
pt = Table(prereq_rows, colWidths=[0.35*inch, 6.85*inch])
pt.setStyle(TableStyle([
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LEFTPADDING", (0,0), (-1,-1), 0),
]))
story.append(pt)
story.append(Spacer(1, 8))

# ---------- THE STRUCTURE ----------
story.append(Paragraph("The structure you are building", s_h2))
story.append(Paragraph(
    "Inside the <b>CTI Group Worldwide</b> project, create six brand folders. "
    "Inside each brand folder, create three subfolders. Total: 6 folders + 18 subfolders.",
    s_body
))

BRANDS = [
    ("#7c3aed", "01 · J1 Division",            "J-1 visa sponsorship and exchange program content"),
    ("#0284c7", "02 · UNO (Uniforms Number One)", "Hospitality, marine, and corporate uniform line"),
    ("#d97706", "03 · Baron Promotions",       "Promotional products and trade-show services"),
    ("#0ea5e9", "04 · CTI Marine Travel",      "Cruise crew recruitment and travel logistics"),
    ("#dc2626", "05 · CTI Group",              "Corporate brand and umbrella entity"),
    ("#16a34a", "06 · CTI Properties",         "Real estate, dormitory, and tenant operations"),
]

SUBFOLDERS = [
    "_Active_Edits",
    "_Approved_Masters",
    "_Archive_2023-2024",
]

structure_rows = []
for hexc, name, desc in BRANDS:
    structure_rows.append([
        section_swatch(hexc),
        Paragraph(f"<b>{name}</b><br/><font color='#6b6f78' size='9'>{desc}</font>", s_step),
        Paragraph(" / ".join(f"<font color='#dc2626'>{s}</font>" for s in SUBFOLDERS), s_step),
    ])

stt = Table(structure_rows, colWidths=[0.3*inch, 2.8*inch, 4.1*inch])
stt.setStyle(TableStyle([
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("TOPPADDING", (0,0), (-1,-1), 7),
    ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ("LINEBELOW", (0,0), (-1,-2), 0.4, C_LINE),
    ("LEFTPADDING", (0,0), (-1,-1), 0),
]))
story.append(stt)
story.append(Spacer(1, 10))

# ---------- STEP-BY-STEP ----------
story.append(Paragraph("Step-by-step (per brand)", s_h2))
story.append(Paragraph(
    "Repeat the following five steps once per brand. Frame.io's <b>+ New Folder</b> button lives in the top-right of "
    "every project view.",
    s_body
))

steps = [
    "Open the <b>CTI Group Worldwide</b> project.",
    "Click <b>+ New Folder</b> in the top-right. Name it exactly as shown in the table above (for example, <i>01 · J1 Division</i>). Press Enter.",
    "Double-click the new folder to open it.",
    "Click <b>+ New Folder</b> three times to create the three subfolders: <i>_Active_Edits</i>, <i>_Approved_Masters</i>, and <i>_Archive_2023-2024</i>.",
    "Click the back arrow to return to the project root, then repeat for the next brand.",
]
for i, s in enumerate(steps, 1):
    story.append(Paragraph(f"<b>{i}.</b> {s}", s_step))
    story.append(Spacer(1, 3))

story.append(PageBreak())

# ---------- PAGE 2: TICK-OFF CHECKLIST ----------
story.append(Paragraph("Brand-by-brand checklist", s_title))
story.append(Paragraph(
    "Tick each box as you finish. When all 24 boxes are checked, the Frame.io structure is complete.",
    s_subtitle
))

for hexc, name, _ in BRANDS:
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<font color='{hexc}'>■</font> &nbsp; {name}", s_brand))
    rows = [
        [checkbox(), Paragraph(f"Created top-level folder &nbsp;<b>{name}</b>", s_step)],
        [checkbox(), Paragraph("Created subfolder &nbsp;<b>_Active_Edits</b>", s_step)],
        [checkbox(), Paragraph("Created subfolder &nbsp;<b>_Approved_Masters</b>", s_step)],
        [checkbox(), Paragraph("Created subfolder &nbsp;<b>_Archive_2023-2024</b>", s_step)],
    ]
    t = Table(rows, colWidths=[0.35*inch, 6.85*inch])
    t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
    ]))
    story.append(t)

story.append(Spacer(1, 16))
story.append(Paragraph("After you finish", s_h2))
after = [
    "Open the Social &amp; Web Command hub and click <b>Settings → Frame.io → Connect</b>.",
    "Paste your Frame.io developer token (get one at <font color='#0284c7'>developer.frame.io/app/tokens</font>) and click <b>Save</b>.",
    "Open <b>Library / Videos</b> in the hub. Frame.io assets will appear with their brand badge and a clickable link back to Frame.io.",
    "Move existing YouTube masters and promo files into the matching <b>_Archive_2023-2024</b> folders so the hub picks them up.",
]
for i, line in enumerate(after, 1):
    story.append(Paragraph(f"<b>{i}.</b> {line}", s_step))
    story.append(Spacer(1, 3))

story.append(Spacer(1, 14))
story.append(Paragraph(
    "<font color='#6b6f78' size='9'>Generated by Perplexity Computer — Social &amp; Web Command operations team. "
    "Live hub: robert-upchurch.github.io/social-web-command.</font>",
    s_caption
))

doc.build(story)
print("Built:", OUT)
