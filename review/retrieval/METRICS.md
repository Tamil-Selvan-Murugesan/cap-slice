# Retrieval metrics: what the standard tools measure, and our final pipeline on all of them (2026-11-25)

Final pipeline:

1. MinerU advanced parse, chunked as `r2-b2s`.
2. Voyage 4 Large at 2048 dimensions.
3. Question-based soft filter, dense top 100.
4. Voyage rerank-3 on the top 50.
5. Round-robin query expansion with Sonnet 5.5 sub-queries.

Runs: `review/retrieval/expand/expand-B-roundrobin.jsonl` (200 questions) and
`review/retrieval/fresh/expand-B-roundrobin.jsonl` (50 fresh questions).

## What the open-source evaluators measure

Retrieval metrics come in two families: **label-based** and **LLM-judged**.

**Label-based** metrics need relevance labels: here, pages checked on images. They are deterministic and free,
but blind to answering pages the key doesn't list.

| Metric | Used by | What it asks |
|---|---|---|
| Hit rate / Success@k | LlamaIndex `hit_rate`, ranx, ir_measures | Is at least one relevant item in the top k? |
| MRR@k | LlamaIndex, BEIR, ranx | 1 / rank of the first relevant item (0 if none in the top k) |
| Recall@k | BEIR, MTEB, LlamaIndex, pytrec_eval | Share of all relevant items that are in the top k |
| Precision@k | LlamaIndex, pytrec_eval | Share of the top k that is relevant |
| MAP@k (average precision) | TREC, BEIR, LlamaIndex `ap` | Precision at each rank where a relevant item appears, averaged over all relevant items; rewards finding everything early |
| nDCG@k | **BEIR and MTEB headline metric**, LlamaIndex | Discounted gain (1/log2(rank+1)) of relevant items, divided by the best possible ranking |
| Context precision (non-LLM, with reference) | RAGAS `NonLLMContextPrecisionWithReference` | Same formula as RAGAS's LLM context precision below, with relevance taken from labels instead of an LLM |
| R-precision, bpref | TREC | Precision at rank R (R = number of relevant items); bpref handles incomplete judgments |

**LLM-judged** metrics need a model, and some need a reference answer. They see the *text* a generator would get,
so they credit any chunk that states the answer and penalise a chunk on the right page whose text lost the number.

| Metric | Used by | What it asks |
|---|---|---|
| **Context recall** | RAGAS `LLMContextRecall`, DeepEval Contextual Recall | Split the reference answer into claims; what share of claims can be attributed to the retrieved contexts? |
| **Context precision** | RAGAS `LLMContextPrecisionWithReference`, DeepEval Contextual Precision | For each retrieved chunk: is it useful for reaching the reference answer? Then Σ(Precision@k × v_k) / number of useful chunks in the top K, so useful chunks should rank first |
| Context relevance / relevancy | TruLens (RAG triad), DeepEval Contextual Relevancy, RAGAS (NVIDIA metrics), ARES | How much of the retrieved text is relevant to the *question*, with no reference answer |
| Context entities recall | RAGAS | Share of the reference answer's named entities found in the contexts |
| Faithfulness, answer relevancy, noise sensitivity | RAGAS, DeepEval, TruLens | These grade the **generated answer**, not retrieval; they need the answer step |

## What we had, and what was missing

Until now we reported Recall@1/5/10/20, MRR@10, lenient R@10 and doc@10. **Our "Recall@k" is what the tools call
hit rate / Success@k.** It counts a question as found if one answer page is there; for multi-page questions, if
every page is there.

The following were missing and are now added:

- **Label-based, in `cap-slice-retrieval-score`** (both sets, every run):
  - fact recall@5/@10
  - precision@5/@10
  - RAGAS-style context precision@10
  - MAP@10
  - nDCG@10
- **LLM-judged, in `cap-slice-context-judge`:**
  - RAGAS-style context recall@10
  - context precision@10
  - "fully supported", the share of questions where every claim is supported

How the label-based metrics are adapted to our keys:

- **Relevant items are the question's facts, not pages.** Each fact lists every page that prints it; on the
  200-question set, a `match=any` question is one fact and a `match=all` question has one fact per page.
- **Recall, MAP and nDCG** give a chunk a gain only for a fact no earlier chunk covered, so the same slide in
  five decks counts once. The ideal ranking puts one page per fact first. Counting every copy as a relevant
  item would punish a run for not returning all five decks.
- **Precision@k and RAGAS context precision** count every chunk that covers any answer page. That is RAGAS's
  definition: duplicate copies are useful context.
- **Precision@k is low by construction.** Most questions have one or two answer pages, so precision@10 can rarely
  exceed 0.1–0.3. Read it relative to other runs, not as a percentage of quality.

The LLM judge, `src/cap_slice/context_judge.py`:

- **Inputs:** Sonnet 5.5, effort medium, structured output, one call per question. It gets the question, the
  reference answer and the top-10 chunks as the answer step would see them (b2s `embed_text`, with header).
- **Prompt:** hash `6a7a430c56ea`, fixed before the full run. After a 3-question trial it was told to ignore the
  parenthetical decoy figures in our reference answers (prior year etc.).
- **Verdicts:** cached in `review/retrieval/judge/`. Cost: 1.66M input + 44K output tokens (about $5.60 for
  250 questions).

**Not added:**

- **R-precision and bpref:** with one to three relevant items per question they repeat MRR and recall, and our
  keys are complete enough that bpref has nothing to correct.
- **Context entities recall:** our answers are mostly figures, which the claim-level recall already covers.
- **Question-only context relevancy:** overlaps the reference-based precision.
- **Generation metrics** (faithfulness, answer relevancy): need the answer step.

## All metrics, final pipeline

Strict key, top 10 unless stated. "All 250" is weighted by question count.

| Metric | Family / source | 200 questions | Fresh 50 | All 250 | Production without expansion (250) |
|---|---|---|---|---|---|
| Hit rate@1 (our R@1) | label · LlamaIndex, ranx | 0.620 | 0.560 | 0.608 | 0.608 |
| Hit rate@5 (our R@5) | label | 0.875 | 0.940 | 0.888 | 0.852 |
| **Hit rate@10 (our R@10)** | label | **0.930** | **0.940** | **0.932** | 0.912 |
| Hit rate@20 (our R@20) | label | 0.945 | 0.940 | 0.944 | 0.936 |
| Hit rate@10, lenient key | label (ours) | 0.935 | 0.940 | 0.936 | 0.916 |
| doc@10 (right document in top 10) | label (ours) | 0.985 | 0.960 | 0.980 | 0.980 |
| MRR@10 | label · BEIR, LlamaIndex | 0.733 | 0.720 | 0.730 | 0.719 |
| Fact recall@5 | label · BEIR/LlamaIndex recall | 0.895 | 0.950 | 0.906 | 0.884 |
| Fact recall@10 | label · BEIR/LlamaIndex recall | 0.945 | 0.950 | 0.946 | 0.934 |
| Precision@5 | label · LlamaIndex, pytrec_eval | 0.256 | 0.492 | 0.303 | 0.291 |
| Precision@10 | label | 0.169 | 0.318 | 0.199 | 0.192 |
| MAP@10 | label · TREC, BEIR | 0.752 | 0.845 | 0.771 | 0.757 |
| **nDCG@10** | label · **BEIR/MTEB headline** | **0.802** | **0.878** | **0.817** | 0.806 |
| Context precision@10 (labels) | label · RAGAS non-LLM | 0.688 | 0.793 | 0.709 | 0.701 |
| **Context recall@10 (LLM)** | LLM · RAGAS, DeepEval | **0.958** | **0.940** | **0.955** | not run |
| Context precision@10 (LLM) | LLM · RAGAS, DeepEval | 0.842 | 0.878 | 0.849 | not run |
| Fully supported (every claim) | LLM (ours, from context recall) | 0.915 | 0.920 | 0.916 | not run |

The fresh set's higher precision comes from its keys listing every copy of a fact.

## What the new metrics add

- **The label metrics agree with hit rate.** Expansion improves every rank metric a little and never hurts:
  nDCG@10 0.806 → 0.817, MAP@10 0.757 → 0.771. R@1 is unchanged because expansion keeps the original list first.
- **The LLM judge and the answer key mostly agree.** Fully supported is 0.916 against hit rate 0.932, and the
  disagreements are informative:
  - **The key misses, the judge finds the answer (9 questions):**
    - The 200-question set has 8: R061, R064, R076, R083, R115, R118, R159, R182. Five of them (R064, R115,
      R118, R159, R182) are the multi-page questions suspected of answer-key gaps: the facts are in that year's
      own filing.
    - Fresh set, F016: APAR's FY20 exports are printed in the Jun-2020 deck (p60), a page the key doesn't
      list because its chart has no text layer to search.
    - None of these pages has been checked on the image yet, so the key is unchanged.
  - **The key hits, the judge doesn't (13 questions):**
    - The page is retrieved but its chunk text lacks the figure. F002 (the 6,962 capex chart label was dropped
      by the parser) and F009 (donut chart) are examples.
    - The 11 on the 200-question set (R026, R079, R095, R112, R120, R157, R174, R175, R177, R184, R190) were
      not opened one by one. Some may be judge strictness rather than parse gaps.
- **Read the judge as a second opinion, not ground truth.** Its 0.955 context recall is an estimate of what an
  answer step could support from the top 10, and it is the number closest to end-to-end answer accuracy that we
  have before building the answer step.

Reproduce:

```bash
uv run cap-slice-retrieval-score review/retrieval/expand/expand-B-roundrobin.jsonl
uv run cap-slice-retrieval-score --set fresh review/retrieval/fresh/expand-B-roundrobin.jsonl
# judge (cached verdicts, no calls unless the prompt changes); key: ~/.config/cap-slice/llm.env as ANTHROPIC_API_KEY
uv run cap-slice-context-judge review/retrieval/expand/expand-B-roundrobin.jsonl --set main
uv run cap-slice-context-judge review/retrieval/fresh/expand-B-roundrobin.jsonl --set fresh
```
