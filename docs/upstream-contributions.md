# Upstream contributions

Fixes we contributed back to open-source projects we depend on. One row per pull request; update the status when it changes.

## Open pull requests

| PR | Project | What it fixes | Opened | Status |
|---|---|---|---|---|
| [#381](https://github.com/docling-project/docling-parse/pull/381) | docling-parse | A ToUnicode range written backwards (`<ffff> <00ff>`) made the parser reserve ~4.3 billion entries: `std::bad_alloc`, or the process was OOM-killed | 2026-10-04 | Open, waiting for maintainer review. Checks: DCO pass, Mergify merge protections pass |
| [#382](https://github.com/docling-project/docling-parse/pull/382) | docling-parse | A pattern name read from freed memory after the graphics-state stack moved (use-after-free): `std::bad_alloc` or a crash | 2026-10-04 | Open, waiting for maintainer review. Checks: DCO pass, Mergify merge protections pass |

Author: Tamil Selvan Murugesan ([Tamil-Selvan-Murugesan](https://github.com/Tamil-Selvan-Murugesan)). Both PRs come from the fork `Tamil-Selvan-Murugesan/docling-parse` and target upstream `main`. Each description says Claude Code was used as an assistant for debugging and drafting, with the investigation driven by the author.

## docling-parse #381 and #382

**Why we made them:** in the full Docling run of 2026-10-04, two of our 228 PDFs could not be parsed. The E2E FY2021-22 annual report (page 2) made a runner use all 62 GB and get killed; the C2C Nov-2025-b presentation (page 4) failed with "Page 4 failed to parse". Both turned out to be bugs in docling-parse 7.22.1 itself, not in our code. For the full explanation in plain terms, see [`docling-parse-bugs.md`](docling-parse-bugs.md).

**What each PR contains:**

| PR | Branch | Code change | New test |
|---|---|---|---|
| #381 | `fix/cmap-reversed-bfrange` | `cmap.h`: skip a range unless start ≤ end and it spans < 65,536 codes (the same rule the library already uses for `cidrange`) | `test_unit_cmap_encoding.py::test_reversed_bfrange_is_ignored` |
| #382 | `fix/pattern-fill-dangling-name` | `stream.h`: `do_pattern_fill` takes the pattern name by value (its own copy) instead of by reference | `test_unit_patterns.py::test_shading_pattern_fill_survives_graphics_state_growth[0..17]` |

**Evidence given in the PRs:**

| Check | Without the fix | With the fix |
|---|---|---|
| Reversed-range test | fails: `std::bad_alloc` | passes |
| Pattern test | crashed the test process (segmentation fault); valgrind: 35 invalid reads | passes; valgrind: 0 errors |
| Our two PDFs | E2E: runner OOM-killed; C2C: page 4 fails | E2E: 98/98 pages (peak 1.5 GB); C2C: 52/52 pages |
| 3 unaffected documents of ours (549 pages) | reference text | identical text on every page, same speed |
| docling-parse's full test suite (both fixes together) | — | 325 passed, 16 skipped, 1 failed. The failure (`test_rendered_pages_match_groundtruth`) fails identically without our changes (same image metrics on all 940 pages), so it is unrelated |

## Following up

- **Where the work lives (pod):** `/workspace/docling-parse-fix/`
  - `dp-src/`: clone with both branches. The remote `fork` is our fork; `origin` is upstream.
  - `pr1_body.md`, `pr2_body.md`: the PR descriptions as posted.
  - `*.log`: the test and valgrind runs behind the evidence above.
- **If a reviewer asks for changes:** commit on the same branch (with `git commit -s`, so the DCO sign-off is kept), then `git push fork <branch>`. The open PR updates by itself. Rebuild and rerun the two test files before pushing.
- **Check status:** `gh pr view 381 -R docling-project/docling-parse` (same for 382), or `gh pr checks <n> -R docling-project/docling-parse`.
- **Once merged and released:** upgrade docling-parse in the `docling` venv, re-parse the two skipped PDFs (`E2E/annual_reports/2022-07-29_FY2021-22.pdf`, `C2C/investor_presentations/2025-11-20_Nov-2025-b.pdf`), and remove the skip note in `docs/gpu-run.md` §5 and `PROGRESS.md`.

## History

| Date | Event |
|---|---|
| 2026-10-04 | Bugs found during the full Docling run; root causes traced in docling-parse with a debug build, gdb and valgrind |
| 2026-10-04 | #381 and #382 opened; DCO and Mergify checks pass |
