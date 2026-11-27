# RAG over Indian company filings from first principles: 41% to 93%, and what surprised us

We wanted to answer questions about Indian listed companies from their own filings: annual reports, quarterly results, earnings-call transcripts and investor decks. "What was APAR's standalone profit in FY2016-17?" "What did Hero MotoCorp say about EV margins in February 2024?" "How did E2E's capex change after it bought GPUs?" The goal is thousands of companies and more than ten million pages. Before building for that scale, we ran a five-company pilot to choose each part of the pipeline on evidence rather than on defaults.

This post has two aims:

1. **To show our first-principles approach to building retrieval that scales:** a frozen test set before any experiment, one variable per round, and every result checked question by question, applied to each layer in turn, from getting the documents to measuring retrieval.
2. **To pass on what we learned and what surprised us**, for anyone building retrieval over thousands of PDFs.

On 250 questions whose answers we read off the pages ourselves, search that finds the right page went from 41% with keyword search to 93%. Most of that gain came from places we didn't expect. The code, test sets and every run are on [GitHub](https://github.com/Tamil-Selvan-Murugesan/cap-slice).

## The problem

Five companies, chosen to cover the variety we'll meet at scale:

- three mainboard companies: APAR Industries, Hero MotoCorp and E2E Networks;
- two on the NSE SME platform: Esconet Technologies and C2C Advanced Systems;
- 228 PDFs and 12,980 pages, from FY2011-12 to 2026.

Financial filings are hard for retrieval in four ways, and each one shaped how we set up the experiments:

- **Every number appears with look-alikes.** The same table is printed every year, and each report repeats last year's figures as a comparison column. Standalone and consolidated statements sit side by side with nearly identical row labels. Quarterly decks repeat the same slides.
- **Periods are slippery.** India's fiscal year ends in March, so "FY24" is April 2023 to March 2024. A concall in July discusses the quarter that ended in June. SME companies report half-yearly, not quarterly.
- **Units change between documents.** The same company reports in crore one year, lakh the next, and full rupees in older reports.
- **The content is mostly not prose.** Tables, slide charts, KPI tiles, call transcripts laid out in two columns (speaker name on the left, what they said on the right), and 441 pages with no text layer at all. One results PDF even carries a wrong embedded OCR layer ("rrom operating activitirs").

A system that answers "₹182 crore" when the truth is ₹176 crore is worse than one that says it doesn't know. That shaped every decision below.

## Our approach: first principles

Before any experiment we set five rules. They did more for the result than any single component.

1. **A frozen test set.** 200 questions, with answers read off page images, were written before the first retrieval experiment and never edited to suit a method. Later, 50 fresh questions on unseen pages checked that we hadn't fitted to the first 200.
2. **One variable per round.** Parser, then chunking, then embedding model, then reranker. Everything else stays fixed.
3. **Measure the ceiling and read the misses before changing anything.** Before a round we ran an upper bound, such as filters taken from the answer key instead of from the question, and opened every miss. Each round then tested a fix for the biggest real cause of failure, not the most popular technique.
4. **Compare question by question, not by averages.** For two runs we count the questions each wins and loses and run an exact sign test. With 200 questions, headline differences under about four points are noise. 
5. **A decision rule fixed in advance.** A change wins only if it improves overall *and* no group of 15 or more questions (tables, concalls, scanned pages…) drops by more than one question in ten.

## Getting the documents

India's exchanges split cleanly into two layers. The discovery layer (NSE's website and API, BSE's site, company investor pages) sits behind bot protection and returned decoy pages or 403s even with a browser session. The archive layer, where the PDFs themselves live, is open to a plain request with a browser user agent. So we found documents through an aggregator's company pages and always recorded the exchange's own archive URL as the source. Downloads ran sequentially, three seconds apart; this is low-volume research, and bulk access belongs on the exchanges' paid data route.

What we learned about the sources, all of which carries over to thousands of companies:

- **Archive URLs can be discovered, not built.** File names embed internal IDs and timestamps, and the patterns are undocumented: they work today and could be closed without notice.
- **An aggregator's coverage becomes yours.** Hero's concall transcripts reached back only to February 2018, because that is where the aggregator's list stopped.
- **About 5% of the links were wrong.** Of 259, eleven returned 404 and two returned an HTML page with status 200. Check a file's first bytes (`%PDF` or a ZIP header), not the status code or the extension.
- **NSE serves annual reports up to FY2022-23 as ZIPs** wrapping a single PDF, once under a nested path.
- **SME companies are a fork, not a filter.** They file half-yearly, and their annual reports use a different naming scheme.
- **Some documents have no reliable route.** Large companies' quarterly results sit among dozens of similarly named announcements; the official shareholding-pattern filing didn't turn up for any of the five companies; company investor sites blocked automated requests.

## Parsing: the decision that matters most

If a number doesn't survive parsing, no retriever can find it. We measured parsers on facts.

**The yardstick.** We wrote 301 "golden facts" in three sets, each read off a page image. A fact is scored only against chunks from its own page, at four levels:

| Level | The chunk contains… |
|---|---|
| L1 | the value |
| L2 | the value with its row label |
| L3 | plus the period header and the unit |
| L4 | plus the value under the right column |

L4 is the level that matters for finance: a value under the wrong year is a wrong answer.

**The run.** We parsed all 12,980 pages on one rented RTX 5090 with four parsers: MinerU 2.5-Pro (standard and advanced tiers), Docling, PaddleOCR-VL 1.6, and a plain PyMuPDF baseline. 

**Making the comparison fair took longer than the run.** Many apparent failures were formatting, not reading:

- a units line placed somewhere else;
- a literal `\n` inside a table cell;
- a LaTeX superscript instead of a footnote mark;
- thousands separators.

We wrote one shared clean-up step and applied it to every parser, fixed our scorer, and only then compared. Then the first two fact sets stopped separating the top parsers. So we added a third set of 123 hard facts: charts, scans, tables printed sideways on the page, and tables with two rows of column headers (three plants, each split into current and previous year).

| Parser | v1 /28 | v2 /150 | v3 /123 | Pages/s | Cost at 11–14M pages |
|---|---|---|---|---|---|
| **MinerU 2.5-Pro, advanced** | 28 | 134 | 101 | 3.9 | $790–1,000 |
| PaddleOCR-VL 1.6 | 27 | 138 | 105 | 2.6 | $1,200–1,530 |
| MinerU, standard | 20 | 119 | 72 | 10.5 | $300–380 |
| Docling (OCR only where needed) | 27 | 111 | 55 (of 114) | 3.0 | $1,015–1,290 |

PaddleOCR-VL gets a few more facts right, yet we chose MinerU advanced. The deciding test was **number fidelity**. We compared every number each parser printed on 7,318 digital pages against the PDF's own text layer. MinerU changed 22 numbers per 10,000; Paddle changed 46. Then we checked 15 flagged numbers from each by eye. The two parsers fail differently:

- **MinerU mostly invents chart values.** Eight of its 15 were values estimated from the shape of line and bar charts that print no labels, such as 8,320 where only the axis tick 8,300 is printed. Three were misread printed figures (a 1,250% dividend written as 2250, 2705 as 2750), and three were false alarms from the PDF's own text layer.
- **Paddle mostly misreads printed figures**, and on audited financial statements it shifted subtotals and changed values: plausible wrong amounts, the worst kind.

Estimated chart values can be found and stripped; a misread figure in a balance sheet looks like any other. MinerU was also 52% faster. We hold the choice with moderate confidence and keep Paddle as the challenger.

Three things here surprised us:

- **MinerU estimates chart values from the bars' shapes** and writes picture descriptions it made up. These must be stripped and never quoted as printed figures.
- **The cheaper MinerU tier collapses some financial statements into a single table row.** It scored 20 of 28 against 28 for the advanced tier.
- **In Docling, OCR was 90–97% of the run time**, mostly re-reading ruled tables on pages that already had perfect text. Running OCR only on pages that need it fixed that. Separately, more threads made Docling slower.

## An open-source contribution we didn't plan

Two PDFs broke Docling's default PDF reader. On one, a single page made memory grow without limit: within seconds the process had run through all 62 GB the machine had, and the kernel killed it. No error was written, and every document queued behind it was blocked. The other failed with a parse error.

Because every run logged each document and kept a cache per document, the silent kill pointed to one PDF, then to one page. Under a memory cap the runaway became a clean error, and Docling's other PDF reader parsed both pages in seconds. That put the fault in `docling-parse`, Docling's C++ library, not in the files. There were two bugs:

- **A malformed font table.** A range written backwards wrapped around, and the library tried to reserve about 4.3 billion entries.
- **Memory read after it was freed.** One page read a string length of about 4.6 × 10¹⁸.

C++ isn't our language. But with the problem narrowed to two pages and one library, we fixed both with an AI coding agent, with a test for each and before-and-after checks on unaffected documents. The maintainers merged both within a day ([#381](https://github.com/docling-project/docling-parse/pull/381), [#382](https://github.com/docling-project/docling-parse/pull/382)). We didn't go looking for an open-source contribution; measuring carefully led us to one.

## Chunking and metadata

**Chunking.** Our chunker treats tables as units. It never splits a table without repeating its header, carries the page's units statement ("₹ in crore") into every table chunk, and starts chunks at headings. Building it took 21 recorded bugs. One example: a cash-flow statement labelled with the name of the signatory from the previous page. Several "improvements" during development turned out to be bugs once we opened the chunks behind the score. That became our first lesson: **a score change is a claim, not a fact; read the output behind it.**

**Metadata.** This turned out to be the cheapest big win:

- **A period normaliser** gives every document a fiscal year and period. Concalls and decks are dated by the event, so a July call maps to the quarter that ended in June. Checked overrides cover the exceptions, like a COVID-delayed call.
- **A rules-based question reader**, with no model, pulls the company, the year and the document type out of the question. It gets the year right for 183 of 200 questions.

Filtering on what the reader finds took keyword search from 41% to 66% of questions answered in the top 10.

There are two ways to use what the reader finds. A **hard filter** searches only the matching documents: for "Hero's EV margins in February 2024", only Hero's FY2023-24 filings. A **soft filter** searches everything but multiplies the score of each matching document by 1.5 per matching field, so the right filings rise to the top without the others being excluded.

The difference shows when the reader is wrong. Ask about "the year to March 2024" and a reader that takes "2024" as FY2024-25 sends a hard filter to the wrong year's filings: the right page can't be found at all. With a soft filter the right page competes at a disadvantage and often still wins on content. For dense search, soft beat hard by six questions to none.

## Retrieval, one round at a time

Every number below is the share of questions with an answer page in the top 10 ("hit rate@10", we called it Recall@10), with question-based soft filters.

**Round 1: embedding model.** We tested Voyage 4 Large (an API model) against Nemotron 3 Embed 8B (open weights, self-hosted), both at 2048 dimensions in a Qdrant server. **Voyage won with 0.81 against 0.76**, and led in every filter setup. One gotcha cost us seven points before we caught it. Models like these embed a question and a document differently, and the API takes a field saying which one a text is; our Nemotron server silently ignored that field. Writing the marker into the text itself fixed it, on both sides: `passage: ` before every chunk when indexing, `query: ` before every question when searching.

**Hybrid search, tested early and rejected.** Adding BM25 to dense search with standard fusion (RRF, DBSF) made things *worse*: 0.81 fell to 0.74–0.77. The surprise was why:

- **The two lists mostly disagree.** The dense and keyword top 10s share only 3.8 chunks on average.
- **Where they agree, it's on look-alikes.** The shared chunks were the same note in another year's report, or the same slide in the next deck.
- **Fusion rewards agreement.** In six questions, dense search had the answer at rank 1 and fusion pushed it to rank 14–28.
- **Keyword search has little to work with here.** With 140 of 200 questions paraphrased and tables full of numbers, BM25 mostly agreed on the wrong pages.

**Vector size.** Truncating and quantising the stored vectors costs nothing to test. Gains flatten by 1024–2048 dimensions, and int8 loses nothing. At 11–14 million pages (about 34–44 million chunks), 2048-dim int8 vectors need roughly 80–100 GB of RAM in a production layout; 4096 dimensions would roughly double that for no gain. We ruled out 4096.

**Diagnosis before round 2.** We opened all 39 misses. In 29 of them, the right *document* was already in the top 10; only the page was wrong (wrong year column, wrong scope, text repeated every year). Filtering on the answer key instead of the question fixed only 11. That filter takes the company, year and document type of the filing that holds the answer, as if the question reader were perfect; so the question reader was not the bottleneck. The embedding understood the question. It couldn't tell apart pages that differ only by year, scope or event, because the chunks didn't say which they were.

**Round 2: chunking.** We built five variants from the same parse:

| Variant | What it changes | Result |
|---|---|---|
| **b2, the winner** | Embeds a short context header with each chunk: company · document · period · standalone or consolidated, plus the heading path | **0.805 → 0.865** (+13 / −1, p = 0.002); top-1 accuracy 0.40 → 0.51. The returned text is unchanged. |
| c | Table descriptions | Lost 13 points on tables |
| d | One slide or concall exchange per chunk | Lost 12 points on concalls |
| e | Small-to-big retrieval | +4 / −5: no gain |


**Round 3: reranker.** We ran Voyage rerank-3 over the top 50 dense results. It scored **0.865 → 0.915** (+10 / −0, p = 0.002), and top-1 accuracy rose to 0.61. Reranking 100 candidates was no better than 50. Hybrid plus reranker scored 0.91 against 0.915: one question apart, which is noise, so hybrid didn't do worse, it just didn't do better. A reranker can only reorder the candidates it is given, and BM25's extra candidates held no answer that dense search hadn't already offered, only more look-alikes. With no gain to show for a second index to build and run, hybrid stayed out. At list price reranking costs about $0.0008 per query.

**A chunker bug hiding in concalls.** The parser read two-column transcripts (speaker | words) as tables, so our chunker kept them as speaker tables (1,085 of them), with section labels left over from earlier speakers. We re-chunked them as turns: four tables were left, and no stale labels. The overall hit rate stayed at 0.915, but answers rank higher: top-1 accuracy 0.605 → 0.62, and on concall questions 0.71 → 0.76.

**Query expansion for multi-page questions.** At this point our weakest questions needed two facts from two documents, like "profit growth between FY2012-13 and FY2016-17". One question becomes one vector, and it lands near one side of the comparison. So an LLM (Claude Sonnet 5.5) now reads each question first. If one search can't answer it, it writes two to four self-contained sub-queries, one fact each. Each sub-query runs through the full pipeline, and the lists are merged.

How we merged mattered more than whether we expanded:

- **Reranking the combined list against the original question changed nothing.** The reranker simply put back its preference for the latest filing.
- **Round-robin worked.** Take the best result of each list in turn, original first.

With round-robin, multi-page questions with every fact in the top 10 rose from 5 to 8 of 14, and the overall hit rate from 0.915 to 0.93, with no question lost. The cost is about $0.002 per question.

**The fresh set.** Three gained questions is too few to trust, and some misses looked like gaps in our own answer key: a fact found in its own year's report, while the key listed a later report's comparison column. So we wrote **50 new questions on pages no earlier set had touched**. They lean towards charts, KPI tiles and multi-page comparisons, and this time the key lists every page that prints each fact, each checked on an image. We changed nothing in the pipeline. Production scored 0.90 on them; with expansion, **0.94**, and 13 of 14 multi-page questions fully found (from 11). Across all 250 questions, expansion has won five and lost none.

| Stage | Hit rate@10 |
|---|---|
| Keyword search (BM25), no filter | 0.41 |
| + question-based filter | 0.66 |
| Dense (Voyage 4 Large) + soft filter | 0.81 |
| + context header in chunks (round 2) | 0.865 |
| + reranker on the top 50 (round 3) | 0.915 |
| + query expansion, round-robin | **0.93** (200 questions), **0.94** (fresh 50) |

## Measuring like the rest of the field, and where the measures disagree

Our "Recall@10" is what LlamaIndex and ranx call *hit rate*. To make the work comparable, we added the standard metrics:

- **Rank metrics from BEIR, MTEB and TREC:** recall, precision, MAP and nDCG@10.
- **LLM-judged context metrics from RAGAS and DeepEval:** a model splits the reference answer into claims, reads the top 10 chunks, and reports what share of claims they support (context recall) and whether the useful chunks come first (context precision).

The final pipeline, over all 250 questions:

| Metric | Value |
|---|---|
| Hit rate@1 / @5 / @10 | 0.608 / 0.888 / 0.932 |
| MRR@10 | 0.730 |
| nDCG@10 | 0.817 |
| MAP@10 | 0.771 |
| Fact recall@10 | 0.946 |
| Context recall@10 (LLM-judged) | 0.955 |
| Context precision@10 (LLM-judged) | 0.849 |

How to read the less familiar ones:

- **nDCG@10** scores each needed fact by the rank where it first appears (1 at rank 1, 0.63 at rank 2, 0.5 at rank 3, 0.29 at rank 10) and divides by the best possible score. A one-fact question answered at rank 3 scores 0.5.
- **MAP@10** averages the precision at each rank where a fact appears. It falls faster with rank: the same answer at rank 3 scores 0.33.
- **Fact recall@10** asks whether a page our key lists for each fact is in the top 10. **Context recall@10** asks whether the *text* of the top 10 states each claim of the reference answer, whatever page it came from.

The most useful part was where the judge and our answer key *disagreed*, on 22 questions. They fall into two kinds:

- **The key says "miss", but the answer is there (9 questions).** Take "How much did Hero's standalone profit grow between FY2023-24 and FY2025-26?" The key listed the FY2024-25 report, where FY24 appears as last year's column. Search returned FY24's own report, which prints the same ₹3,967.96 crore. Search was right and the key was too narrow.
- **The key says "hit", but the text can't answer it (13 questions).** E2E's capex slide was retrieved, but the parser had dropped the bar label "6,962", so the chunk only mentions the GPU work in progress. Right page, unusable text.

Label metrics can't see either case; a judge can, but a judge is a model. Report both, and treat the gap between them as a work list.

## What surprised us

- **Metadata beat models.** A rules-based question reader and a period normaliser gave larger gains than switching embedding models.
- **Hybrid search hurt.** On paraphrased questions over repetitive documents, keyword agreement points at look-alikes.
- **The biggest chunking win changed no returned text.** Telling the embedding which company, period and scope a chunk belongs to did more than any restructuring.
- **A reranker undoes query expansion** if you rerank the merged list against the original question.
- **Answer keys go stale in subtle ways.** The same figure lives in its own year's report and in next year's comparison column. Key one and you'll punish a retriever for finding the other.
- **"Found the page" is not "can answer".** Chart labels lost in parsing hide behind good retrieval scores.
- **Performance knobs lie.** More threads were slower; most of Docling's time went to OCR on pages that didn't need it.

## If you're building RAG over thousands of PDFs

1. **Build ground truth from page images before you build anything else.** About 300 facts and 250 questions paid for every decision after.
2. **Treat parsing as the foundation, and choose the parser on number fidelity.** Get parsing wrong and you'll have a perfect retrieval pipeline with nothing to retrieve. Check printed numbers against the text layer where one exists. A plausible wrong number is worse than a missing one.
3. **Normalise periods and read the question.** Year, company and document type as soft filters are cheap and large wins in any domain with repeated documents.
4. **Put context into the embedded text.** Company, document, period and scope in a short header: one line of text, our biggest chunking gain.
5. **Add a reranker before anything clever.** It was +10 / −0 for a fraction of a cent per query, and filings are where it earns its place. The same table appears in every year's report, and standalone sits next to consolidated. A soft filter leaves other years' pages in the running in case the question was misread; the reranker reads the question together with each chunk's header and picks the right year and scope.
6. **Split multi-fact questions, and merge by round-robin.** Give each sub-query its own slots in the top 10.
7. **Compare runs question by question, and write down what counts as a win before you run.** Count the questions each run gains and loses, and check the count with a sign test; ours also required that no group of questions (tables, concalls, scans) got worse. Averages hide groups that get worse, and a rule fixed afterwards bends to the result you hoped for.
8. **Open the outputs behind every score change.** Our most convincing "improvements" were bugs.
9. **Keep a fresh, unseen question set** for when you've made enough decisions on the first one.
10. **Report label metrics and an LLM judge side by side.** Their disagreements show you both your key's gaps and your parser's.

## What's next

Retrieval is good enough to build on. Next comes the answer step, measured on the same 250 questions for answer accuracy, not just retrieval. Two pieces of work wait for it:

- **Chart values the parser drops.** Search finds these pages; their text just doesn't hold the number, so no retriever can supply it. Many charts print their values as real text in the PDF, which the parser read past, so the first fix is to recover them from the text layer. For charts that are pictures, a vision model will describe them, the descriptions stored in a field marked as generated, and we'll compare answers with and without them.
- **Quality gates for the parser:** automatic checks on every parsed document, such as printed numbers against the text layer, runaway repeated output, year and column order in tables, and generated chart values kept apart from printed ones. At millions of pages nobody reads the output, so these checks decide what gets indexed.

Then we scale. The pilot settled every choice in the pipeline; what remains is to build it for three thousand companies and measure it again, on questions drawn from many more of them.

Everything in this post can be checked: the code, the question sets with their answer pages, every run and its scores are in the [cap-slice repository](https://github.com/Tamil-Selvan-Murugesan/cap-slice).

## Contributors

- [Naga Sirisha Chava](https://www.linkedin.com/in/sirisha-chava-9628a8331/)
- [Tamil Selvan Murugesan](https://www.linkedin.com/in/tamil-selvan-murugesan/)
