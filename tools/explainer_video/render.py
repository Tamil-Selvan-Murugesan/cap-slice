"""Render the PyMuPDF4LLM vs Docling explainer video.

    uv run python tools/explainer_video/render.py WORK_DIR OUT.mp4

WORK_DIR must contain page.png and data.json (from extract.py). If
WORK_DIR/audio/<scene>.mp3 exist (from tts.py), scenes are timed to the
narration and the audio is muxed in; otherwise scenes are timed to reading
speed and the video is silent with captions. Frames are piped straight into
ffmpeg (no frame files on disk).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
W, H, FPS = 1280, 720, 12
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
BG, INK, MUTED, PANEL = (15, 23, 42), (241, 245, 249), (148, 163, 184), (30, 41, 59)
GREEN, RED, AMBER, BLUE = (34, 197, 94), (239, 68, 68), (245, 158, 11), (59, 130, 246)
P4L_COLOR, DL_COLOR = (245, 158, 11), (56, 189, 248)
LABEL_COLORS = {"table": (59, 130, 246), "text": (148, 163, 184), "section_header": (168, 85, 247),
                "section-header": (168, 85, 247), "page_header": (236, 72, 153), "page-header": (236, 72, 153),
                "page_footer": (236, 72, 153), "page-footer": (236, 72, 153), "picture": (34, 197, 94),
                "key_value_region": (20, 184, 166)}
COL_COLORS = [(148, 163, 184), (168, 85, 247), (34, 197, 94), (59, 130, 246)]

_fonts: dict = {}


def font(size: int, kind: str = "regular") -> ImageFont.FreeTypeFont:
    path = {"regular": FONT, "bold": BOLD, "mono": MONO}[kind]
    if (path, size) not in _fonts:
        _fonts[(path, size)] = ImageFont.truetype(path, size)
    return _fonts[(path, size)]


class Assets:
    def __init__(self, work: Path) -> None:
        self.d = json.loads((work / "data.json").read_text())
        self.pw, self.ph = self.d["size"]
        page = Image.open(work / "page.png").convert("RGB")
        self.px_per_pt = page.width / self.pw
        # Left: full page
        self.page_h = 560
        self.page_s = self.page_h / self.ph
        self.page_img = page.resize((round(self.pw * self.page_s), self.page_h), Image.LANCZOS)
        self.page_xy = (40, 80)
        # Right: zoom on header rows .. cash row
        self.zoom_pts = (30, 96, 585, 252)
        x0, y0, x1, y1 = (round(v * self.px_per_pt) for v in self.zoom_pts)
        self.zoom_w = 700
        self.zoom_s = self.zoom_w / (self.zoom_pts[2] - self.zoom_pts[0])
        crop = page.crop((x0, y0, x1, y1))
        self.zoom_img = crop.resize((self.zoom_w, round(crop.height * self.zoom_w / crop.width)), Image.LANCZOS)
        self.zoom_xy = (540, 150)

    def on_page(self, box):
        x0, y0, x1, y1 = box
        ox, oy = self.page_xy
        s = self.page_s
        return (ox + x0 * s, oy + y0 * s, ox + x1 * s, oy + y1 * s)

    def on_zoom(self, box):
        x0, y0, x1, y1 = box
        zx0, zy0, zx1, zy1 = self.zoom_pts
        cx0, cy0, cx1, cy1 = max(x0, zx0), max(y0, zy0), min(x1, zx1), min(y1, zy1)
        if cx0 >= cx1 or cy0 >= cy1:
            return None
        ox, oy = self.zoom_xy
        s = self.zoom_s
        return (ox + (cx0 - zx0) * s, oy + (cy0 - zy0) * s, ox + (cx1 - zx0) * s, oy + (cy1 - zy0) * s)


def quad_bbox(q):
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    return (min(xs), min(ys), max(xs), max(ys))


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ---------- drawing helpers ----------

def base(a: Assets, part: str, step: str, color, show_page=True, show_zoom=False) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(img, "RGBA")
    if part:
        dr.rounded_rectangle((40, 18, 40 + dr.textlength(part, font(18, "bold")) + 24, 50), 8, fill=color)
        dr.text((52, 22), part, font=font(18, "bold"), fill=BG)
        dr.text((70 + dr.textlength(part, font(18, "bold")), 21), step, font=font(22, "bold"), fill=INK)
    if show_page:
        img.paste(a.page_img, a.page_xy)
        x, y = a.page_xy
        dr.rectangle((x - 1, y - 1, x + a.page_img.width, y + a.page_img.height), outline=(71, 85, 105))
    if show_zoom:
        img.paste(a.zoom_img, a.zoom_xy)
        x, y = a.zoom_xy
        dr.rectangle((x - 1, y - 1, x + a.zoom_img.width, y + a.zoom_img.height), outline=(71, 85, 105))
        dr.text((x, y - 24), "Zoom: header rows to the cash row", font=font(15), fill=MUTED)
        if show_page:  # mark the zoomed area on the page
            dr.rectangle(a.on_page(a.zoom_pts), outline=(255, 255, 255, 160), width=2)
    return img, dr


def caption(dr: ImageDraw.ImageDraw, text: str, t: float = 0.0, d: float = 1.0) -> None:
    """Two caption lines at a time; longer captions page through in proportion
    to their length, so the visible lines roughly track the narration."""
    dr.rectangle((0, H - 62, W, H), fill=(2, 6, 23, 235))
    groups: list[list[str]] = []
    for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
        candidate = textwrap.wrap(" ".join(groups[-1] + [sentence]), 118) if groups else None
        if candidate and len(candidate) <= 2:
            groups[-1] = candidate
        else:
            lines_ = textwrap.wrap(sentence, 118)
            groups += [lines_[i:i + 2] for i in range(0, len(lines_), 2)]
    weights = [sum(len(l) for l in g) for g in groups]
    pos, acc, lines = t / max(d, 1e-6) * sum(weights), 0, groups[-1]
    for g, w in zip(groups, weights):
        acc += w
        if pos <= acc:
            lines = g
            break
    for i, line in enumerate(lines):
        dr.text((40, H - 56 + i * 25), line, font=font(18), fill=INK)


def box(dr, rect, color, width=2, fill_alpha=0):
    if rect is None:
        return
    fill = color + (fill_alpha,) if fill_alpha else None
    dr.rectangle(rect, outline=color + (255,), width=width, fill=fill)


def label_tag(dr, xy, text, color, size=13):
    x, y = xy
    w = dr.textlength(text, font(size, "bold")) + 8
    x = max(4, min(x, W - w - 8))
    y = max(size + 6, y)
    dr.rectangle((x, y - size - 4, x + w, y), fill=color + (230,))
    dr.text((x + 4, y - size - 3), text, font=font(size, "bold"), fill=BG)


def panel_text(dr, x, y, lines, size=20, gap=10, width=None):
    for line in lines:
        if isinstance(line, tuple):
            text, kind, color = line
        else:
            text, kind, color = line, "regular", INK
        for wrapped in (textwrap.wrap(text, width) if width else [text]):
            dr.text((x, y), wrapped, font=font(size, kind), fill=color)
            y += size + gap
    return y


def code_block(dr, x, y, lines, highlight=None, color=GREEN, size=15, w=700):
    h = len(lines) * (size + 9) + 16
    dr.rounded_rectangle((x, y, x + w, y + h), 8, fill=(2, 6, 23))
    for i, line in enumerate(lines):
        ly = y + 8 + i * (size + 9)
        if highlight is not None and i in highlight:
            dr.rectangle((x + 4, ly - 2, x + w - 4, ly + size + 4), fill=color + (60,))
        dr.text((x + 10, ly), line, font=font(size, "mono"), fill=INK)
    return y + h


# ---------- scenes ----------

def s01_title(a, t, d, dr_img=None):
    img, dr = base(a, "", "", INK, show_page=True)
    dr.text((540, 170), "How two PDF parsers read", font=font(40, "bold"), fill=INK)
    dr.text((540, 220), "a scanned balance sheet", font=font(40, "bold"), fill=INK)
    x = 540
    for word, f, c in (("PyMuPDF4LLM", font(34, "bold"), P4L_COLOR), ("vs", font(34), MUTED),
                       ("Docling", font(34, "bold"), DL_COLOR)):
        dr.text((x, 300), word, font=f, fill=c)
        x += dr.textlength(word, f) + 22
    panel_text(dr, 540, 380, [("E2E Networks · Annual Report FY2022-23 · PDF page 123", "regular", MUTED),
                              ("Every box in this video is real output from the two parsers.", "regular", MUTED)], size=18)
    return img, dr


def s02_problem(a, t, d):
    img, dr = base(a, "", "The problem: this page is a picture", INK)
    f = ease(t / 1.5)
    if f > 0:
        dr.rectangle(a.on_page((0, 0, a.pw, a.ph)), fill=RED + (int(50 * f),), outline=RED + (255,), width=3)
        label_tag(dr, a.on_page((0, 0, a.pw, a.ph))[:2], "1 image covering the page", RED, 15)
    panel_text(dr, 540, 140, [("What the PDF contains", "bold", INK)], size=26)
    stats = [("Text layer:", f"{a.d['text_layer_chars']} characters", RED),
             ("Images:", f"{a.d['images']} (the whole page)", RED)]
    for i, (k, v, c) in enumerate(stats):
        if t > 1 + i * 0.8:
            dr.text((540, 200 + i * 50), k, font=font(24), fill=MUTED)
            dr.text((700, 200 + i * 50), v, font=font(24, "bold"), fill=c)
    if t > 3:
        panel_text(dr, 540, 330, ["No characters to read directly.",
                                  "The text must be recognised from pixels:",
                                  ("OCR = optical character recognition", "bold", AMBER)], size=22, gap=14)
    return img, dr


def flow(dr, x, y, steps, active, color):
    for i, s in enumerate(steps):
        on = i == active
        done = i < active
        fill = color if on else (PANEL if not done else (51, 65, 85))
        dr.rounded_rectangle((x, y + i * 46, x + 330, y + i * 46 + 38), 8, fill=fill)
        dr.text((x + 12, y + i * 46 + 9), f"{i + 1}. {s}", font=font(16, "bold" if on else "regular"),
                fill=BG if on else (INK if done else MUTED))


P4L_STEPS = ["Read PDF text layer", "OCR decision model", "OCR (RapidOCR)", "Layout model (GNN)", "Table grid → Markdown"]
DL_STEPS = ["Render page image", "Layout model (RT-DETR)", "OCR where no PDF text", "TableFormer (grid)", "Fill cells → Markdown"]


def s03_p4l_decide(a, t, d):
    img, dr = base(a, "Option 2 · PyMuPDF4LLM", "Steps 1–2: read text, decide on OCR", P4L_COLOR)
    flow(dr, 540, 90, P4L_STEPS, 0 if t < 3 else 1, P4L_COLOR)
    if t > 1:
        dr.text((900, 100), "→ 0 characters found", font=font(17, "bold"), fill=RED)
    if t > 3:
        dec = a.d["ocr_decision"]
        y = 360
        dr.text((540, y), "OCR decision model (0.5 MB ONNX classifier)", font=font(18, "bold"), fill=INK)
        bx0, bx1, by = 540, 1160, y + 60
        dr.rounded_rectangle((bx0, by, bx1, by + 26), 6, fill=PANEL)
        f = ease((t - 3.5) / 1.5)
        dr.rounded_rectangle((bx0, by, bx0 + (bx1 - bx0) * dec["probability"] * f, by + 26), 6, fill=AMBER)
        tx = bx0 + (bx1 - bx0) * 0.93
        dr.line((tx, by - 10, tx, by + 36), fill=INK, width=3)
        dr.text((tx - 70, by + 40), "threshold 0.93", font=font(15), fill=MUTED)
        if f >= 1:
            dr.text((bx0, by - 32), f"P(needs OCR) = {dec['probability']:.3f}  →  YES, run OCR", font=font(20, "bold"), fill=AMBER)
    return img, dr


def s04_p4l_ocr(a, t, d):
    img, dr = base(a, "Option 2 · PyMuPDF4LLM", "Step 3: OCR with RapidOCR", P4L_COLOR, show_zoom=True)
    lines = a.d["ocr_lines"]
    n = int(len(lines) * ease((t - 0.3) / max(1.0, d * 0.45)))
    for ln in lines[:n]:
        bb = quad_bbox(ln["box"])
        box(dr, a.on_page(bb), GREEN, 1)
        box(dr, a.on_zoom(bb), GREEN, 2)
    dr.text((540, 90), f"Text boxes found and read: {n} / {len(lines)}", font=font(20, "bold"), fill=GREEN)
    if t > d * 0.55:
        for k, ln in enumerate(l for l in lines if l["text"] in ("1,631.31", "384.34")):
            r = a.on_zoom(quad_bbox(ln["box"]))
            box(dr, r, AMBER, 4)
            # first tag above its box, second below, so they never overlap
            y = r[1] - 4 if k == 0 else r[3] + 22
            label_tag(dr, (r[0] - 10, y), f"{ln['text']}  ({ln['score']:.3f})", AMBER, 14)
        panel_text(dr, 540, 390, [("Cash row: both numbers read correctly,", "bold", INK),
                                  ("as two separate boxes.", "bold", INK),
                                  ("Confidence 0.999 and 1.000", "regular", MUTED)], size=20)
    return img, dr


def s05_p4l_layout(a, t, d):
    img, dr = base(a, "Option 2 · PyMuPDF4LLM", "Step 4: layout model labels the boxes", P4L_COLOR)
    flow(dr, 540, 90, P4L_STEPS, 3, P4L_COLOR)
    boxes = a.d["p4l_boxes"]
    n = int(len(boxes) * ease((t - 0.3) / max(1.0, d * 0.5))) + (1 if t > 0.3 else 0)
    for b in boxes[:n]:
        c = LABEL_COLORS.get(b["cls"], MUTED)
        r = a.on_page(b["bbox"])
        box(dr, r, c, 3, 40)
        if b["cls"] in ("table", "page-header", "page-footer") or (b["bbox"][3] - b["bbox"][1]) > 40:
            label_tag(dr, (r[0], r[1]), b["cls"], c, 12)
    panel_text(dr, 540, 350, [("Graph neural network over the text boxes", "bold", INK),
                              "Each box is a node, neighbours are linked,",
                              "and every box gets a label.",
                              (f"{len(boxes)} regions on this page, one of them a table", "regular", MUTED)], size=19)
    return img, dr


def s06_p4l_grid(a, t, d):
    img, dr = base(a, "Option 2 · PyMuPDF4LLM", "Step 5: guess the columns → Markdown", P4L_COLOR, show_zoom=True)
    cash = [quad_bbox(l["box"]) for l in a.d["ocr_lines"] if l["text"] in ("1,631.31", "384.34")]
    head = [quad_bbox(l["box"]) for l in a.d["ocr_lines"] if "March" in l["text"]]
    if t > 0.8 and cash:
        for group, lbl in ((cash, "ONE cell: 2023 + 2022 values"), (head, "ONE header cell: both years")):
            if not group:
                continue
            x0 = min(b[0] for b in group) - 4; y0 = min(b[1] for b in group) - 3
            x1 = max(b[2] for b in group) + 4; y1 = max(b[3] for b in group) + 3
            r = a.on_zoom((x0, y0, x1, y1))
            box(dr, r, RED, 4, 50)
            label_tag(dr, (r[0], r[3] + 22), lbl, RED, 14)
    if t > 2.5:
        dr.text((540, 395), "Real PyMuPDF4LLM output (3 columns):", font=font(17, "bold"), fill=INK)
        code_block(dr, 540, 425, ["|  |Notes|~~Asat~~<br>As at<br>March31,2023<br>March 31,2022|",
                                  "|(i) Cash and cash equivalents<br>|10<br>|1,631~~.~~31<br>384~~.~~34|"],
                   highlight={0, 1}, color=RED, size=14)
        dr.text((540, 510), "Numbers right, but which year is which? Lost.", font=font(19, "bold"), fill=RED)
    return img, dr


def s07_dl_layout(a, t, d):
    img, dr = base(a, "Option 3 · Docling", "Steps 1–2: page image → layout model (RT-DETR)", DL_COLOR)
    flow(dr, 540, 90, DL_STEPS, 1, DL_COLOR)
    regs = a.d["dl_regions"]
    n = int(len(regs) * ease((t - 0.5) / max(1.0, d * 0.5)))
    for r in regs[:n]:
        c = LABEL_COLORS.get(r["label"], MUTED)
        rr = a.on_page(r["bbox"])
        box(dr, rr, c, 2, 35)
        if r["label"] in ("table", "page_header", "section_header", "page_footer"):
            label_tag(dr, (rr[0], rr[1]), r["label"], c, 11)
    panel_text(dr, 540, 350, [("Vision model on the whole page image", "bold", INK),
                              "Draws a box around every region and labels it",
                              "(17 possible labels; 164 MB, PyTorch).",
                              (f"Regions found: {n} / {len(regs)}", "bold", DL_COLOR)], size=19)
    return img, dr


def s08_dl_ocr(a, t, d):
    img, dr = base(a, "Option 3 · Docling", "Step 3: OCR only where the PDF has no text", DL_COLOR)
    flow(dr, 540, 90, DL_STEPS, 2, DL_COLOR)
    cells = [c for r in a.d["dl_regions"] for c in r["ocr_cells"]]
    n = int(len(cells) * ease((t - 0.3) / max(1.0, d * 0.5)))
    for c in cells[:n]:
        box(dr, a.on_page(c), GREEN, 1)
    panel_text(dr, 540, 350, [("Same OCR engine family (RapidOCR)", "bold", INK),
                              "but only inside regions without PDF text.",
                              "On this scanned page: everywhere.",
                              (f"OCR'd text pieces: {n} / {len(cells)}", "bold", GREEN)], size=19)
    return img, dr


def s09_dl_table(a, t, d):
    img, dr = base(a, "Option 3 · Docling", "Step 4: TableFormer predicts the grid", DL_COLOR, show_zoom=True)
    tb = a.d["dl_tables"][0]
    cells = sorted(tb["cells"], key=lambda c: (c["row"], c["col"]))
    n = int(len(cells) * ease((t - 0.3) / max(1.0, d * 0.5)))
    for c in cells[:n]:
        col = COL_COLORS[c["col"] % 4]
        box(dr, a.on_page(c["bbox"]), col, 1, 50)
        box(dr, a.on_zoom(c["bbox"]), col, 3 if c["header"] else 2, 70 if c["header"] else 45)
    dr.text((540, 90), f"Grid: {tb['rows']} rows × {tb['cols']} columns   (cells drawn: {n} / {len(cells)})",
            font=font(19, "bold"), fill=DL_COLOR)
    if t > d * 0.6:
        x = 540
        for i, name in enumerate(["label", "notes", "Mar 31, 2023", "Mar 31, 2022"]):
            dr.rectangle((x, 390, x + 16, 406), fill=COL_COLORS[i])
            dr.text((x + 22, 388), name, font=font(16), fill=INK)
            x += dr.textlength(name, font(16)) + 60
        panel_text(dr, 540, 425, [("Transformer looks at the table image and predicts", "regular", INK),
                                  ("rows, columns and header cells (203 MB, PyTorch).", "regular", INK)], size=18)
    return img, dr


def s10_dl_output(a, t, d):
    img, dr = base(a, "Option 3 · Docling", "Step 5: fill each cell → Markdown", DL_COLOR, show_zoom=True)
    tb = a.d["dl_tables"][0]
    cash_row = next(c["row"] for c in tb["cells"] if "Cash and cash" in c["text"])
    for c in tb["cells"]:
        if c["row"] in (0, cash_row) and c["col"] >= 2:
            box(dr, a.on_zoom(c["bbox"]), GREEN, 4, 60)
    if t > 1.2:
        dr.text((540, 395), "Real Docling output (4 columns):", font=font(17, "bold"), fill=INK)
        code_block(dr, 540, 425, ["| | Notes | As at March 31, 2023 | As at March 31, 2022 |",
                                  "| (ii) Cash and cash equivalents | 10 | 1,631.31 | 384.34 |"],
                   highlight={0, 1}, color=GREEN, size=14)
        dr.text((540, 510), "Each value sits under its own year.", font=font(19, "bold"), fill=GREEN)
    return img, dr


def s11_compare(a, t, d):
    img, dr = base(a, "", "Same characters, different order", INK, show_page=False)
    cols = [(60, "PyMuPDF4LLM", P4L_COLOR, ["1. Read text (OCR)", "2. Label the boxes", "3. Guess the columns", "→ text first, structure after"]),
            (660, "Docling", DL_COLOR, ["1. Find regions in the image", "2. Predict the table grid", "3. Read text into cells", "→ structure first, text after"])]
    for x, name, c, steps in cols:
        dr.rounded_rectangle((x, 80, x + 560, 330), 12, fill=PANEL)
        dr.text((x + 20, 95), name, font=font(28, "bold"), fill=c)
        for i, s in enumerate(steps):
            dr.text((x + 24, 150 + i * 40), s, font=font(20, "bold" if i == 3 else "regular"), fill=INK if i < 3 else c)
    if t > d * 0.4:
        rows = [("", "PyMuPDF4LLM", "Docling"),
                ("Golden facts fully intact (of 28)", "21", "27"),
                ("Scanned statements intact (of 6)", "0", "5"),
                ("Seconds per page (this laptop, CPU)", "3.3", "15.2"),
                ("Models run on", "ONNX (small)", "PyTorch (~370 MB)")]
        for i, (k, v1, v2) in enumerate(rows):
            y = 360 + i * 46
            if i:
                dr.rectangle((60, y - 6, 1220, y + 34), fill=PANEL if i % 2 else BG)
            dr.text((80, y), k, font=font(20, "bold" if i == 0 else "regular"), fill=INK)
            dr.text((720, y), v1, font=font(20, "bold"), fill=P4L_COLOR)
            dr.text((980, y), v2, font=font(20, "bold"), fill=DL_COLOR)
    return img, dr


def s12_takeaway(a, t, d):
    img, dr = base(a, "", "Takeaway: route pages to the right parser", INK, show_page=False)
    dr.rounded_rectangle((80, 230, 330, 330), 12, fill=PANEL)
    dr.text((110, 262), "Every page", font=font(26, "bold"), fill=INK)
    dr.polygon([(360, 270), (440, 270), (440, 255), (480, 280), (440, 305), (440, 290), (360, 290)], fill=MUTED)
    dr.rounded_rectangle((500, 215, 790, 345), 12, fill=PANEL)
    for i, line in enumerate(("Has a text layer", "and no complex", "table?")):
        dr.text((522, 235 + i * 32), line, font=font(20, "bold"), fill=INK)
    for y, label, (l1, l2), c in ((120, "yes", ("Fast parser", "PyMuPDF / PyMuPDF4LLM"), P4L_COLOR),
                                  (390, "no", ("Docling", "scans, financial tables"), DL_COLOR)):
        dr.line((790, 280, 880, y + 45), fill=c, width=5)
        dr.text((815, (280 + y + 45) // 2 - 30), label, font=font(18, "bold"), fill=c)
        dr.rounded_rectangle((890, y, 1235, y + 90), 12, outline=c, width=3)
        dr.text((910, y + 14), l1, font=font(22, "bold"), fill=c)
        dr.text((910, y + 50), l2, font=font(18), fill=INK)
    if t > d * 0.5:
        dr.text((80, 560), "Only 3.4% of pages in the collection lack a text layer.", font=font(20), fill=MUTED)
        dr.text((80, 595), "Proposal — not yet tested.", font=font(20, "bold"), fill=AMBER)
    return img, dr


SCENES = [s01_title, s02_problem, s03_p4l_decide, s04_p4l_ocr, s05_p4l_layout, s06_p4l_grid,
          s07_dl_layout, s08_dl_ocr, s09_dl_table, s10_dl_output, s11_compare, s12_takeaway]


def duration(audio: Path | None, text: str) -> float:
    if audio and audio.exists():
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                              str(audio)], capture_output=True, text=True, check=True).stdout
        return float(out) + 0.8
    return len(text.split()) / 2.6 + 1.5  # reading speed when there's no narration


def main(work: Path, out: Path) -> None:
    a = Assets(work)
    script = {s["id"]: s["say"] for s in json.loads((HERE / "script.json").read_text())}
    audio_dir = work / "audio"
    plan = []
    for fn in SCENES:
        clip = audio_dir / f"{fn.__name__}.mp3"
        plan.append((fn, script[fn.__name__], duration(clip, script[fn.__name__]),
                     clip if clip.exists() else None))
    have_audio = all(c for *_, c in plan)
    total = sum(d for _, _, d, _ in plan)
    print(f"{len(plan)} scenes, {total:.0f} s, narration: {'yes' if have_audio else 'no (captions only)'}")

    silent = out.with_suffix(".video.mp4") if have_audio else out
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                           "-crf", "30", "-tune", "animation", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                           str(silent)], stdin=subprocess.PIPE)
    for fn, text, d, _ in plan:
        frames = round(d * FPS)
        for i in range(frames):
            t = i / FPS
            img, dr = fn(a, t, d)
            caption(dr, text, t, d)
            fade = min(1.0, t / 0.25, (d - t) / 0.25)
            if fade < 1:
                img = Image.blend(Image.new("RGB", (W, H), BG), img, max(0.0, fade))
            ff.stdin.write(img.tobytes())
    ff.stdin.close()
    ff.wait()

    if have_audio:
        parts = []
        for fn, _, d, clip in plan:
            wav = work / "audio" / f"{fn.__name__}.pad.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip), "-af",
                            f"adelay=300:all=1,apad=whole_dur={d}", "-ac", "1", "-ar", "44100", str(wav)], check=True)
            parts.append(wav)
        lst = work / "audio" / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-f", "concat", "-safe", "0",
                        "-i", str(lst), "-c:v", "copy", "-c:a", "aac", "-b:a", "64k", "-shortest",
                        "-movflags", "+faststart", str(out)], check=True)
        silent.unlink()
    print("wrote", out, f"{out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
