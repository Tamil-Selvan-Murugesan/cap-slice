# Two bugs in docling-parse, explained simply

During the full Docling run on 2026-10-04, two of our 228 PDFs could not be parsed:

| PDF | What we saw |
|---|---|
| `data/E2E/annual_reports/2022-07-29_FY2021-22.pdf` | The runner process used all the pod's memory (62 GB) and was killed. No error was written, and the 19 documents queued behind it never ran. |
| `data/C2C/investor_presentations/2025-11-20_Nov-2025-b.pdf` | `ConversionError: Page 4 failed to parse` |

Neither is caused by our code or by a broken file. Both are bugs in **docling-parse**, the C++ library Docling uses to read text out of PDFs (version 7.22.1, the latest when we looked). We showed this by running docling-parse on its own, without Docling and without any of our code: it failed on exactly the same pages. A different PDF reader (pypdfium) read both pages without trouble in about 4 seconds and 1.2 GB.

The two bugs are unrelated, so they get two separate fixes and two separate pull requests.

---

## Bug 1: a range written backwards makes the parser ask for ~34 GB

### Background: how a PDF says which letter a glyph is

Inside a PDF, text is not stored as letters. It is stored as **codes** (numbers), and each font carries a small lookup table, the **ToUnicode map**, that says which letter each code stands for.

To save space, the table can describe a whole run of codes in one line, a **range**:

```
<0041> <0043> <0061>
```

This reads: "codes 0x41 to 0x43 map to letters starting at 0x61", that is:

| code | letter |
|---|---|
| 0x41 | a |
| 0x42 | b |
| 0x43 | c |

The first number is the **start**, the second is the **end**. The end should never be smaller than the start.

### What was wrong in our PDF

The E2E annual report was written by a tool called "3-Heights PDF Optimization Shell". In the font `Flama-Book`, used on page 2 (the table of contents), it wrote one range backwards:

```
<ffff> <00ff> ...
```

Start = 65535, end = 255. The end is smaller than the start. That's invalid, but real-world PDFs are messy, so a parser must cope with it.

### What docling-parse did with it

To prepare space for the range, docling-parse works out how many codes it contains:

```
count = end - begin + 1
```

With normal numbers that would be `255 - 65535 + 1 = -65279`, a negative count, which is obviously wrong.

But the code uses **unsigned 32-bit numbers**: numbers that cannot be negative. When a subtraction would go below zero, they wrap around to the top, like a car's odometer rolling back past 0 to 999999. So the result is:

```
count = 4,294,967,291      (about 4.3 billion)
```

The parser then reserves room for 4.3 billion entries, about **34 GB** before storing a single letter:

- **With a memory limit**, the request fails at once: `std::bad_alloc` ("Page 2 failed to parse").
- **Without a limit** (our pod), the process grows until the machine runs out of memory and the kernel kills it, which is what we saw.

### The fix

Before using a range, check that it makes sense:

```cpp
// the start must not be after the end, and the range must be a sane size
if (begin <= end and (end - begin) < 65536) { use the range }
else { log a warning and skip this one range }
```

Only the broken range is skipped. Every other range in the same font still works, so the rest of page 2 is read correctly.

This rule isn't new. docling-parse already applies exactly this check, with the same 65,536 limit, to a similar kind of table elsewhere (`cidrange`, in `font_cid.h`), with a comment saying it exists so "a corrupt bound cannot turn into a multi-gigabyte allocation". The ToUnicode code path simply didn't have it.

**Changed:** `src/parse/pdf_resources/page_font/cmap.h` (a small `is_valid_range` check, called at the start of both `set_range` functions).

---

## Bug 2: a "pointer" that was left pointing at freed memory

### Background: saving and restoring drawing settings

A PDF page is drawn by a small program: "set colour red, draw a rectangle, ...". Two commands matter here:

- `q`: **save** the current drawing settings (colour, line width, and so on).
- `Q`: **restore** the settings that were saved last.

docling-parse keeps the saved settings in a list, used as a stack: `q` adds an entry on top, `Q` removes the top one.

### Background: a reference is like a seat number

In C++, a function can receive a **reference** to a value instead of its own copy. A reference is like being told "the value is in seat 12 of the bus" instead of being handed the value.

The list (`std::vector`) is like a bus with a fixed number of seats. When it is full and one more entry is added, the list **moves everything to a bigger bus and scraps the old one**. Anyone still holding "seat 12 of the old bus" now points at a scrapped bus. This is called a **dangling reference**, and reading through it is a "use-after-free" bug.

### What docling-parse did

When a shape is filled with a **pattern** (a gradient, for example), docling-parse calls `do_pattern_fill`, giving it the pattern's **name**, but as a reference into the top entry of the settings stack ("the name is in seat N").

`do_pattern_fill` then:

1. calls `q()` to save the settings, which adds an entry to the stack;
2. if the stack was full, it **moves to new memory and frees the old memory**;
3. later copies the pattern's name, **from the old, freed memory**.

A tiny version of the same mistake:

```cpp
std::vector<std::string> stack = {"P1"};
const std::string& name = stack.back();   // "seat 1 of the old bus"
stack.push_back("more");                  // full -> moves to a new bus, old one freed
std::string copy = name;                  // reads freed memory: anything can happen
```

What happens next depends on what is lying in the freed memory:

- **Usually** the old bytes are still there, the copy happens to work, and nobody notices.
- **On the C2C presentation, page 4**, the freed memory held garbage. The "length" of the name read as about 4.6×10¹⁸ bytes, and the copy failed with `std::bad_alloc` ("Page 4 failed to parse").
- **In general** it could also silently corrupt memory or crash the program.

### The fix

Give `do_pattern_fill` **its own copy of the name** (pass it "by value") instead of a seat number. The copy is made before anything moves, so it can't go stale:

```cpp
// before                                        // after
bool do_pattern_fill(const std::string& name,    bool do_pattern_fill(std::string name,
                     bool even_odd);                                  bool even_odd);
```

It's a one-word change, plus a comment explaining why. We checked every other place that calls `q()`: none of them hold a reference into the stack, so this is the only spot.

**Changed:** `src/parse/pdf_decoders/stream.h`.

---

## How we know the fixes work

| Check | Before the fix | After the fix |
|---|---|---|
| E2E annual report, page 2 | `std::bad_alloc` (or all memory used) | parsed in 0.0 s, 0.1 GB; text is the table of contents ("Corporate Information 1, About the Company 2, ...") |
| E2E annual report, all 98 pages | runner killed | all 98 parsed, peak 1.5 GB |
| C2C presentation, page 4 | `std::bad_alloc` | parsed in 0.3 s, 0.1 GB; text is the leadership slide |
| C2C presentation, all 52 pages | page 4 fails | all 52 parsed, peak 0.6 GB |
| New test: backwards range | fails with `MemoryError: std::bad_alloc` | passes (text "AB") |
| New test: pattern fill at stack depths 0–17, run under **valgrind** (a tool that reports reads of freed memory) | 35 errors, all reading the freed pattern name | 0 errors |
| 3 normal documents (Hero AR FY2025-26 270 p, Esconet AR FY2023-24 128 p, APAR presentation Sep-2024 151 p) | (reference output) | identical text on every page, same speed |

Note on the pattern test: in a normal test run it passes even without the fix, because freed memory usually still holds the old bytes. The bug only shows up reliably under a memory checker such as valgrind or AddressSanitizer. The test is still worth having: it runs the exact code path, and any CI with a memory checker will catch a regression.

## Pull requests (upstream: `docling-project/docling-parse`)

Two separate PRs, one per bug, each with its own test, signed off by Tamil Selvan Murugesan (the project requires a DCO `Signed-off-by` line on every commit):

| Branch | Commit title | Files |
|---|---|---|
| `fix/cmap-reversed-bfrange` | `fix: ignore malformed ToUnicode bfranges instead of reserving ~4G map entries` | `cmap.h`, `tests/test_unit_cmap_encoding.py` |
| `fix/pattern-fill-dangling-name` | `fix: take the pattern name by value in do_pattern_fill` | `stream.h`, `tests/test_unit_patterns.py` |

Status (2026-10-04): opened as [#381](https://github.com/docling-project/docling-parse/pull/381) (backwards range) and [#382](https://github.com/docling-project/docling-parse/pull/382) (pattern name), from the fork `Tamil-Selvan-Murugesan/docling-parse`. DCO checks pass; waiting for maintainer review. Status and follow-up steps are tracked in [`upstream-contributions.md`](upstream-contributions.md).

## In our project, until the fix is released

We skip the two PDFs for Docling (decision in `PROGRESS.md`, details in `docs/gpu-run.md` §5). Once a docling-parse release includes both fixes, we can upgrade and parse them again.

## Words used above

| Word | Meaning |
|---|---|
| glyph code | the number a PDF stores instead of a letter |
| ToUnicode map | a font's table translating glyph codes into letters |
| range (`bfrange`) | one line of that table covering a run of codes: start, end, first letter |
| unsigned number | a number type that cannot be negative; going below 0 wraps around to a huge value |
| `std::bad_alloc` | C++'s error for "could not get that much memory" |
| OOM kill | the operating system stopping a process because the machine is out of memory |
| `q` / `Q` | PDF commands to save / restore drawing settings |
| reference | a "seat number" pointing at a value instead of a copy of it |
| dangling reference / use-after-free | using a seat number after the bus was scrapped |
| valgrind | a tool that runs a program and reports every read of freed or invalid memory |
