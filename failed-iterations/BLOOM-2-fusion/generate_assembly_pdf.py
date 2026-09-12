"""Generate the BLOOM-2 centrifuge assembly drawing PDF."""

from pathlib import Path
import csv
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, PageTemplate, Paragraph, Spacer, Table,
    TableStyle, PageBreak, KeepTogether
)


ROOT = Path(__file__).resolve().parent
OUT = ROOT.parents[2] / "output" / "pdf" / "BLOOM-2_centrifuge_assembly_drawing.pdf"
VIEWS = ROOT / "views"
BOM = ROOT / "bom.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)

PAGE = landscape(A4)
W, H = PAGE
MARGIN = 12 * mm

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleX", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=23, leading=26, textColor=colors.HexColor("#11243A"), alignment=TA_LEFT, spaceAfter=4*mm))
styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], fontSize=9.5, leading=13, textColor=colors.HexColor("#49647E")))
styles.add(ParagraphStyle(name="H2X", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=15, textColor=colors.HexColor("#11243A"), spaceBefore=2*mm, spaceAfter=2*mm))
styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], fontSize=8.4, leading=11, textColor=colors.HexColor("#25384A")))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=7.3, leading=9, textColor=colors.HexColor("#25384A")))
styles.add(ParagraphStyle(name="TableSmall", parent=styles["BodyText"], fontSize=6.15, leading=7.1, textColor=colors.HexColor("#25384A")))
styles.add(ParagraphStyle(name="TableHeader", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=6.4, leading=7.2, textColor=colors.white))
styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.3, leading=10, textColor=colors.white, alignment=TA_CENTER))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#B8C6D2"))
    canvas.line(MARGIN, 8*mm, W-MARGIN, 8*mm)
    canvas.setFillColor(colors.HexColor("#49647E"))
    canvas.setFont("Helvetica", 7)
    canvas.drawString(MARGIN, 4.5*mm, "BLOOM-2 | PBMC Ficoll centrifuge | prototype engineering drawing")
    canvas.drawRightString(W-MARGIN, 4.5*mm, f"Page {doc.page}")
    canvas.restoreState()


doc = BaseDocTemplate(str(OUT), pagesize=PAGE, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=10*mm, bottomMargin=12*mm, title="BLOOM-2 Centrifuge Assembly Drawing", author="ComfyBloom")
frame = Frame(MARGIN, 12*mm, W-2*MARGIN, H-22*mm, id="main")
doc.addPageTemplates(PageTemplate(id="drawing", frames=[frame], onPage=footer))
story = []

story.append(Paragraph("BLOOM-2 swinging-bucket centrifuge", styles["TitleX"]))
story.append(Paragraph("Parametric Fusion 360 prototype for four 15 mL conical tubes and Ficoll/PBMC separation", styles["Sub"]))
story.append(Spacer(1, 4*mm))

iso = Image(str(VIEWS / "assembly_iso.png"), width=151*mm, height=113*mm)
metrics = [
    ["DESIGN POINT", "1545 rpm"],
    ["RESULTING RCF", "400.3 x g"],
    ["MID-FLUID RADIUS", "150 mm"],
    ["SWING PIVOT RADIUS", "86 mm"],
    ["AT-SPEED TIP RADIUS", "218 mm"],
    ["MINIMUM POT ID", "466 mm"],
    ["CAPACITY", "4 x 15 mL"],
    ["BUCKET TRAVEL", "vertical to 90 deg"],
]
metric_table = Table(metrics, colWidths=[49*mm, 32*mm], rowHeights=9.2*mm)
metric_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0D7C86")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#EDF4F6")),
    ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#B8C6D2")),
    ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
    ("FONTNAME", (1,0), (1,-1), "Helvetica"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("LEFTPADDING", (0,0), (-1,-1), 3*mm),
]))
story.append(Table([[iso, metric_table]], colWidths=[166*mm, 82*mm], style=[("VALIGN",(0,0),(-1,-1),"TOP")]))
story.append(Spacer(1, 3*mm))
story.append(Paragraph("Configuration shown: four buckets at the 90-degree at-speed hard stop. Optional direct and geared motor plates are excluded from the main assembly views for clarity. The rotating assembly is split into one hub, four identical arms, and four identical buckets so every printed part fits a 220 x 220 mm bed.", styles["BodyX"]))
story.append(PageBreak())

story.append(Paragraph("Assembly views and interfaces", styles["TitleX"]))
top = Image(str(VIEWS / "assembly_top.png"), width=126*mm, height=94.5*mm)
front = Image(str(VIEWS / "assembly_front.png"), width=126*mm, height=94.5*mm)
view_table = Table([
    [Paragraph("TOP - four-fold symmetry", styles["H2X"]), Paragraph("FRONT - bearing stack and bucket stop", styles["H2X"])],
    [top, front],
], colWidths=[132*mm,132*mm])
view_table.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"), ("BOX",(0,1),(-1,1),0.5,colors.HexColor("#B8C6D2")), ("INNERGRID",(0,1),(-1,1),0.5,colors.HexColor("#B8C6D2"))]))
story.append(view_table)
story.append(Spacer(1, 3*mm))

notes = [
    ["01", "Dual 608ZZ tower", "22.2 mm seats, 8.3 mm through bore; light axial preload and minimum shaft overhang."],
    ["02", "Shared rotor interface", "Two M3 fasteners per arm. Four-hole 24 mm BCD accepts direct coupler or driven gear without reprinting the rotor."],
    ["03", "Free swinging bucket", "M3x45 tangential pivot, 0.5 mm clevis clearance, low-friction washers, and printed 90-degree stop."],
    ["04", "Instrumentation", "Tall IR boss looks upward to the underside rotor target; MPU-6050 bolts rigidly to the chassis boss."],
    ["05", "Containment envelope", "436 mm diameter rotating envelope plus 15 mm wall clearance on both sides gives a 466 mm minimum clear pot ID."],
]
nt = Table(notes, colWidths=[12*mm,50*mm,196*mm], rowHeights=[11.5*mm]*len(notes))
nt.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#0D7C86")), ("TEXTCOLOR",(0,0),(0,-1),colors.white),
    ("FONTNAME",(0,0),(1,-1),"Helvetica-Bold"), ("FONTSIZE",(0,0),(-1,-1),7.7),
    ("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#B8C6D2")), ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("LEFTPADDING",(0,0),(-1,-1),2.2*mm), ("RIGHTPADDING",(0,0),(-1,-1),2.2*mm),
]))
story.append(nt)
story.append(PageBreak())

story.append(Paragraph("Bill of materials and manufacturing notes", styles["TitleX"]))
rows = []
with BOM.open(newline="") as f:
    for index, row in enumerate(csv.reader(f)):
        style = styles["TableHeader"] if index == 0 else styles["TableSmall"]
        rows.append([Paragraph(cell, style) for cell in row])
bom_table = Table(rows, colWidths=[22*mm,52*mm,15*mm,67*mm,102*mm], repeatRows=1)
bom_table.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#11243A")), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#B8C6D2")),
    ("VALIGN",(0,0),(-1,-1),"TOP"), ("LEFTPADDING",(0,0),(-1,-1),0.9*mm), ("RIGHTPADDING",(0,0),(-1,-1),0.9*mm),
    ("TOPPADDING",(0,0),(-1,-1),0.65*mm), ("BOTTOMPADDING",(0,0),(-1,-1),0.65*mm),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F3F7F9")]),
]))
story.append(bom_table)
story.append(Spacer(1, 3*mm))

bottom_notes = Table([
    [Paragraph("PRINT", styles["Callout"]), Paragraph("PETG only. Print hub and arms flat. Print buckets on their side so centrifugal load runs in the layer plane. Use 6 perimeters, 8 top/bottom layers, and 70-100% infill with solid pivot/bolt zones. Print each matched set in one job.", styles["TableSmall"])],
    [Paragraph("BALANCE", styles["Callout"]), Paragraph("Match printed buckets to +/-0.5 g. Match opposing loaded tubes to +/-0.1 g before every run. All four empty buckets must fall freely to the same hard stop.", styles["TableSmall"])],
    [Paragraph("CONTROL", styles["Callout"]), Paragraph("Smooth spin-up, no torque steps, and coast-only stop longer than 2 minutes. Disable active brake. Use the 5:1 option only if direct drive cannot start and hold the loaded rotor smoothly.", styles["TableSmall"])],
    [Paragraph("VALIDATE", styles["Callout"]), Paragraph("Prototype only. Containment and guarded overspeed testing precede biological use. Final functional test: four mass-matched tubes, dyed water over glycerol, 1545 rpm for 30 min, coast down. Clean interface passes; smear fails.", styles["TableSmall"])],
], colWidths=[22*mm,236*mm], rowHeights=[9.5*mm]*4)
bottom_notes.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#0D7C86")), ("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#B8C6D2")),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("LEFTPADDING",(0,0),(-1,-1),2*mm), ("RIGHTPADDING",(0,0),(-1,-1),2*mm),
]))
story.append(bottom_notes)

doc.build(story)
print(OUT)
