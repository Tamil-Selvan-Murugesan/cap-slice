"""Flag pages where the model got stuck repeating itself, and (optionally) merge clean re-runs back.

A page is flagged when, in its markdown text (tags stripped):
  - one 1-4-word phrase repeats >= MIN_REPEATS times and covers >= MIN_SHARE of all words, or
  - it has >= 40 non-empty lines and fewer than 30% of them are distinct.
Phrases made only of filler (dashes, pipes, "0.00", "nil", ...) are ignored, so ordinary financial tables
with many empty cells do not trigger it. Seen in practice: "\\quad" loops on a table-of-contents slide,
"3X 30%" / "123456" loops in text read from pictures, "MUMBAI" loops on auditor seals.

  # 1. find loops in a run; writes <run>/loops.jsonl (page manifest rows) + <run>/loops.csv
  python detect_loops.py --run /workspace/results_full/paddleocr-vl-1.6/full --manifest $P/manifest.jsonl
  # 2. re-run only those pages with a repetition penalty
  python run_paddle.py --manifest <run>/loops.jsonl ... --repetition-penalty 1.05 --run-name full_rerun
  # 3. copy re-run outputs that are no longer looping over the originals (originals kept as *.orig.md/json)
  python detect_loops.py --run <run> --manifest $P/manifest.jsonl --merge-from <results>/paddleocr-vl-1.6/full_rerun
"""
import argparse
import csv
import json
import re
import shutil
from collections import Counter
from pathlib import Path

MIN_REPEATS = 30
MIN_SHARE = 0.25
TAGS = re.compile(r"<[^>]+>")
FILLER = re.compile(r"^(?:[-–—|.,:;*_#()\[\]{}$]+|0+(?:\.0+)?|nil|na|n\.a\.|-)$", re.I)


def words(md: str) -> list[str]:
    return TAGS.sub(" ", md).split()


def loop_reason(md: str) -> str | None:
    w = words(md)
    if len(w) >= MIN_REPEATS:
        for n in (1, 2, 3, 4):
            grams = Counter(tuple(w[i:i + n]) for i in range(len(w) - n + 1))
            for gram, count in grams.most_common(5):
                if all(FILLER.match(t) for t in gram):
                    continue
                if count >= MIN_REPEATS and count * n / len(w) >= MIN_SHARE:
                    return f"phrase {' '.join(gram)[:40]!r} x{count} ({round(100 * count * n / len(w))}% of words)"
                break
    lines = [ln.strip() for ln in TAGS.sub(" ", md).splitlines() if ln.strip()]
    if len(lines) >= 40 and len(set(lines)) / len(lines) < 0.30:
        return f"{len(set(lines))}/{len(lines)} distinct lines"
    return None


def scan(md_dir: Path) -> dict[str, str]:
    flagged = {}
    for f in sorted(md_dir.glob("*.md")):
        if f.name.endswith((".raw.md", ".orig.md")):
            continue
        reason = loop_reason(f.read_text(errors="replace"))
        if reason:
            flagged[f.stem] = reason
    return flagged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="results/<model>/<run> directory (contains md/)")
    ap.add_argument("--manifest", required=True, help="page manifest used for the run (rendered paths)")
    ap.add_argument("--merge-from", help="re-run directory whose clean outputs replace flagged pages")
    a = ap.parse_args()

    run = Path(a.run)
    md_dir = run / "md"
    rows = {json.loads(l)["page_id"]: json.loads(l)
            for l in Path(a.manifest).read_text().splitlines() if l.strip()}
    flagged = scan(md_dir)
    n_pages = sum(1 for f in md_dir.glob("*.md") if not f.name.endswith((".raw.md", ".orig.md")))
    print(f"{len(flagged)} of {n_pages} pages flagged as loops")

    if a.merge_from:
        src = Path(a.merge_from) / "md"
        fixed, still = [], []
        for pid in flagged:
            new_md = src / f"{pid}.md"
            if not new_md.exists():
                continue
            if loop_reason(new_md.read_text(errors="replace")):
                still.append(pid)
                continue
            for ext in (".md", ".json"):
                cur, new = md_dir / f"{pid}{ext}", src / f"{pid}{ext}"
                if new.exists():
                    if cur.exists() and not (md_dir / f"{pid}.orig{ext}").exists():
                        shutil.copy(cur, md_dir / f"{pid}.orig{ext}")
                    shutil.copy(new, cur)
            fixed.append(pid)
        print(f"merged {len(fixed)} clean re-runs; {len(still)} still looping after re-run: {still[:20]}")
        flagged = scan(md_dir)
        print(f"after merge: {len(flagged)} pages still flagged")

    with open(run / "loops.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["page_id", "reason"])
        w.writerows(sorted(flagged.items()))
    with open(run / "loops.jsonl", "w") as f:
        for pid in sorted(flagged):
            if pid in rows:
                f.write(json.dumps(rows[pid]) + "\n")
    for pid, reason in sorted(flagged.items())[:15]:
        print(f"  {pid}: {reason}")
    print(f"-> {run / 'loops.jsonl'} (re-run manifest), {run / 'loops.csv'}")


if __name__ == "__main__":
    main()
