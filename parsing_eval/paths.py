"""Locations shared by the parsing_eval scripts.

Code lives in the repo (parsing_eval/); everything the scripts generate goes under DATA, which defaults to
<repo>/data/parsing_eval (git-ignored). Set PARSING_EVAL_DATA to use another location, e.g. a mounted
persistent volume.
"""
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DB_PATH = REPO / "data" / "pipeline.sqlite3"                       # cap-slice SQLite (read-only here)
QUESTIONS = REPO / "parsing_eval" / "eval_set" / "questions.json"  # 25 hand-verified questions

DATA = Path(os.environ.get("PARSING_EVAL_DATA", REPO / "data" / "parsing_eval"))
PROFILE = DATA / "page_profile" / "pages.csv"                      # profile_pages.py output
BASELINES = DATA / "baselines"                                     # pymupdf4llm / docling outputs
SETS = DATA / "sets"                                               # bench / repr / full sets + pack
RESULTS = DATA / "results"                                         # GPU run outputs copied back
PACK = SETS / "vlm_test_pack" / "pack"                             # 15 hand-checked pages
