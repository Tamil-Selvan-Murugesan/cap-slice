"""Page clean-up before chunking — the same steps for every parser (cached parser output is untouched).

1. Text the parser invented about pictures goes out of the page text: MinerU's
   ``<details><summary>natural_image|chart|flowchart…</summary>…</details>`` descriptions and Mermaid
   diagrams. It is returned separately per page, so it can still be kept as a labelled
   "image description" field later.
2. Layout-only HTML wrappers are unwrapped (PaddleOCR-VL's ``<div style="text-align: center;">…</div>``):
   the text inside stays. A literal "\\n" inside a table cell becomes a space, and LaTeX superscripts
   around plain characters become plain text ("EBITDA $ ^{{*}} $" -> "EBITDA*", "31$^{st}$" -> "31st").
3. A units statement the parser missed is restored from the PDF's own text layer: if the PDF page has a
   short line such as "(All amounts are in INR lakhs…)" or "(₹ crore)" and the parser's text for that
   page has no short line of its own naming that unit, the line is put at the top of the page. PaddleOCR-VL's layout model
   skipped exactly these lines on some statement pages (E2E FY2024-25 pp. 107-108, APAR FY2013-14 p. 42),
   and the unit is what makes a statement's numbers usable.
"""

from __future__ import annotations

import re
from pathlib import Path

DETAILS = re.compile(r"<details>.*?</details>", re.S | re.I)
MERMAID = re.compile(r"```mermaid.*?```", re.S | re.I)
WRAPPER = re.compile(r"</?(div|center|span)\b[^>]*>", re.I)
# LaTeX superscripts around plain characters: "EBITDA $ ^{{*}} $", "31 $ ^{ST} $", "31$^{st}$"
# (spaces only, never newlines: a footnote line starting "$ ^{*} $" must not be glued onto the line above)
SUPERSCRIPT = re.compile(r"[ \t]*\$[ \t]*\^[ \t]*\{+[ \t]*(?:\\mathrm[ \t]*\{)?[ \t]*([^${}|\n]{1,12}?)[ \t]*\}+[ \t]*\$")
UNIT_WORD = re.compile(r"(?i)\b(lakhs?|crores?|millions?|mn|billions?)\b")
UNIT_LINE = re.compile(r"(?i)(amount|₹|`|\brs\.?|\binr\b|\bin\b)")


def text_layer_units(pdf: Path) -> dict[int, str]:
    """Page number -> first short units statement in the PDF's text layer."""
    import pymupdf
    out: dict[int, str] = {}
    with pymupdf.open(pdf) as doc:
        for n, page in enumerate(doc, 1):
            for line in page.get_text().splitlines():
                line = line.strip()
                if (len(line.split()) <= 20 and UNIT_WORD.search(line) and UNIT_LINE.search(line)
                        and line.startswith("(")):
                    out[n] = line
                    break
    return out


def clean_pages(pages: list[list], pdf: Path | None = None) -> tuple[list[list], dict]:
    """[(page, text)] -> cleaned [(page, text)] plus stats and the removed picture text."""
    units = text_layer_units(pdf) if pdf and pdf.exists() else {}
    cleaned, removed, restored = [], {}, []
    for n, text in pages:
        gone = DETAILS.findall(text) + MERMAID.findall(text)
        text = MERMAID.sub("", DETAILS.sub("", text))
        text = WRAPPER.sub("", text)
        text = SUPERSCRIPT.sub(lambda m: m.group(1).replace(" ", ""), text)
        # literal "\n" inside table cells (PaddleOCR-VL header cells) is a line break, not text
        text = "\n".join(l.replace("\\n", " ") if l.lstrip().startswith("|") else l for l in text.split("\n"))
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        if gone:
            removed[n] = "\n".join(gone)
        u = units.get(n)
        if u:
            word = UNIT_WORD.search(u).group(1).lower().rstrip("s")
            # restore unless the parser kept a units line of its own (a short line naming the unit);
            # a passing mention in a footnote ("loss of ₹1.02 crore") is not a units statement
            has_line = any(word in l.lower() and len(l.split()) <= 12 and not l.lstrip().startswith("|")
                           and (l.strip().startswith(("(", "[")) or "amount" in l.lower() or "figures" in l.lower())
                           for l in text.split("\n"))
            if not has_line:
                text = (u + "\n\n" + text).strip()
                restored.append(n)
        cleaned.append([n, text])
    return cleaned, {"pictures_removed_pages": len(removed),
                     "pictures_removed_chars": sum(map(len, removed.values())),
                     "units_restored_pages": restored, "removed": removed}
