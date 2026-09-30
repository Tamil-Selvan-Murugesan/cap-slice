"""Shared metadata selection for NSE announcement attachments."""
import re
from urllib.parse import unquote, urlparse

RESULTS = re.compile(r"financial[\s_-]*results?|(?:un)?audited[\s_-]*results?", re.I)
NOTICE = re.compile(r"investor[\s_/-]*meet|analysts?/|con\.[\s_]*call|schedule|invitation|trading[\s_-]*window|newspaper|board[\s_-]*meeting[\s_-]*intimation", re.I)


def classify_announcement(row: dict) -> str:
    """Select likely report attachments; this is not PDF content verification."""
    subject = str(row.get("desc") or "")
    description = str(row.get("attchmntText") or "")
    filename = unquote(urlparse(str(row.get("attchmntFile") or "")).path).rsplit("/", 1)[-1]
    text = " ".join((subject, description, filename)).lower()
    if "transcript" in text:
        return "concall_transcript"
    if "presentation" in text and ("investor" in text or "analyst" in text):
        return "investor_presentation"
    if re.search(r"credit[\s_-]*rating|rating[\s_-]*rationale|rating[\s_-]*action", text):
        return "credit_rating"
    # Filenames rescue results filed under broad subjects such as board outcomes.
    # Explicit results subjects include clarifications with actual result tables.
    if RESULTS.search(filename):
        return "financial_results"
    if NOTICE.search(subject + " " + filename):
        return "announcement"
    if RESULTS.search(subject + " " + description):
        return "financial_results"
    return "announcement"
