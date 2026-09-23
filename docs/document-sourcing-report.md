# NSE/BSE Document Sourcing — Pilot Findings

> Historical pilot report. The [independent verification on 2026-09-23](pilot-verification-2026-09-23.md) corrects several claims below: APAR company sources work; APAR results/shareholding documents were found; C2C's catalogued results PDF is misclassified; E2E's listing tier changed in 2022. Main's full downloader run has now attempted all 259 catalogued URLs (228 downloaded, 31 failed), including individual confirmation of all 18 Hero 403s. See [PROGRESS.md](../PROGRESS.md) for reconciled current status.

**Scope:** 5 companies (Esconet Technologies, E2E Networks, C2C Advanced Systems, APAR Industries, Hero MotoCorp), 5 document types (annual report, quarterly/half-yearly results, shareholding pattern, concall transcript, investor presentation), target window 2015–2026.

**Purpose:** understand the real data sources, the workarounds they require, the subscription/ToS landscape, and the issues that would emerge scaling this from 5 companies to ~3,000–4,000 NSE-listed companies over a 10-year window — before building any fetching infrastructure.

Backing data: `data/document_availability_matrix.csv` (267 cataloged documents, one row per document).

---

## 1. There are two layers, not one

| Layer | Examples | Access |
|---|---|---|
| Application/discovery layer | `www.nseindia.com` (search, quote, API endpoints), `www.bseindia.com` (main site), company-owned IR pages | **Bot-walled.** NSE runs Akamai Bot Manager — even with a valid session cookie, correct Referer, and full browser headers, API endpoints (`/api/search/autocomplete`, `/api/quote-equity`) return either a fake "Resource not found" decoy page or a straight 403. BSE's main site and company IR sites (tested: TCS, and sampled Hero MotoCorp's own site) also returned 403. |
| Document archive layer | `nsearchives.nseindia.com/corporate/*.pdf`, `archives.nseindia.com/annual_reports/*.pdf`, `bseindia.com/xml-data/corpfiling/AttachHis/*.pdf` | **Open.** Plain `curl` with a normal browser User-Agent, no cookies or session, returns the PDF directly (`200 application/pdf`) — confirmed across all 5 companies, both SME-listed and large-cap. |

The practical consequence: **retrieval is trivial once you have the URL; discovery of that URL is the actual hard problem**, and it currently depends on a channel outside NSE's/BSE's own protected front ends.

## 2. The workaround used in this pilot

Screener.in (a third-party equity research aggregator) already does discovery — it lists a company's historical annual reports, concall transcripts, and investor presentations with dates, and links to the underlying primary-source PDF on NSE's or BSE's archive domain. This pilot used Screener purely as an index: fetch the company's Screener page, extract the real archive URL, fetch that URL directly.

This worked for all 5 companies but has an important implication: **your discovery layer's reliability is now Screener's reliability**, not NSE's or BSE's. If Screener changes its page structure, rate-limits, or restricts automated access, discovery breaks even though the underlying archive URLs remain fine.

## 3. Subscription / ToS landscape

- NSE's Terms of Use explicitly prohibit "systematic or automated data collection activities (including scraping, data mining, data extraction and data harvesting)" without express written consent, and license the site for personal, non-commercial use. Bulk/commercial access is meant to go through **NSE Data & Analytics Ltd** (NSE's paid data subsidiary); a separate request route exists for research institutions via NSE's Economic Policy Research Department.
- BSE's equivalent bulk-data terms were not checked in this pilot — worth doing before scaling.
- Screener.in's terms regarding automated/bulk querying were not checked either, and matter more now: at scale, Screener stops being "a page I glanced at" and becomes infrastructure you depend on for every company.
- The **personal/low-volume framing** that made ad hoc lookups reasonable for 5 companies does not hold at 3,000–4,000 companies × 10 years. That volume is unambiguously systematic/automated under NSE's own definition, and generates real request volume against both the exchange archive domains and Screener. This is the point where the paid NSE Data route (or an equivalent licensed feed) stops being optional-in-principle and starts being the realistic long-term answer, rather than scraping-at-scale.

## 4. What the 5-company pilot actually found

267 documents cataloged, 14–121 per company depending on size/age:

| Company | Tier | Docs found | Notes |
|---|---|---|---|
| APAR Industries | Mainboard | 121 | Full 2012–2026 coverage for annual reports & concalls |
| Hero MotoCorp | Mainboard | 66 | Annual reports to FY2011-12; concalls only to Feb 2018 (Screener's own archive limit) |
| E2E Networks | Mainboard | 58 | Full history, but starts 2018 — company's actual IPO date |
| Esconet Technologies | NSE SME | 14 | Only FY2024 onward — converted to public company Aug 2023 |
| C2C Advanced Systems | NSE SME | 8 | Only FY2025-26 — very recently listed, 2 annual reports total |

By document type: concall transcripts 108, investor presentations 103, annual reports 44, periodic results 7, shareholding pattern 5.

Verification: 17 of 267 URLs were individually re-fetched and confirmed `200 application/pdf` this session; 224 were pattern-matched (same URL structure, not individually re-checked); 18 came back `blocked`; 8 came back `not found`.

*Update 2026-09-23 (full download):* every one of the 259 URLs was then fetched. 228 downloaded as real documents; 18 were still `blocked` (403, Hero MotoCorp's own site); 13 were wrong: 11 returned 404 and 2 returned an HTML page instead of a PDF (10 APAR, 3 Hero MotoCorp). So about 5% of the cataloged URLs were wrong, all of them in the two large mainboard companies.

## 5. Structural issues (will compound, not stay flat, at scale)

**a. SME vs. mainboard aren't a filter, they're a fork.** SME-listed companies file half-yearly, not quarterly, and use a `SME_AR_` filename prefix instead of `AR_` for annual reports. A meaningful share of a 3-4k-company universe will be SME-listed — this needs to be a first-class branch in any fetcher's logic, not an edge case handled after the fact.

**b. Shareholding pattern could not be sourced as an official filed PDF for *any* of the 5 companies.** Screener only exposes derived quarterly percentages (promoter/FII/DII/public %); targeted searches for the actual Regulation-31 filing (`site:nsearchives.nseindia.com`, `site:bseindia.com` + symbol + "shareholding pattern") returned only unrelated disclosures every time. This looks systemic, not company-specific — expect it to recur across the full universe unless a different discovery channel (e.g. a real browser session against NSE's/BSE's shareholding-pattern filing list) is found.

**c. Periodic results (quarterly/half-yearly) PDFs were isolable for the two SME companies and E2E, but not for APAR or Hero MotoCorp.** At large-cap companies, the results filing sits among many similarly-named announcements (press releases, credit ratings, concall material), and without the bot-walled API's structured "subject"/category metadata, pattern-matching alone couldn't reliably pick it out. This is likely the single biggest blocker for `periodic_results` specifically at scale.

**d. Company-owned IR sites are not a usable fallback.** Hero MotoCorp's own site (used for pre-2022 concalls before they moved to filing via BSE) returned 403 on all 18 sampled URLs — consistent with TCS's IR page failing earlier in this exercise. "Check the company website" doesn't hold up as a supplementary source.

**e. URL patterns are undocumented, not contractual.** Filenames embed internal transaction IDs and timestamps that can only be discovered, never derived or templated. Nothing here is a documented public API — the archive domains are "currently open," not "guaranteed open." NSE or BSE could add protection to them without notice.

**f. Verification is itself a cost that scales.** Only 17 of 267 URLs were individually re-fetched this session; the rest were trusted on pattern-match. At 3-4k companies, even light verification of every discovered URL becomes meaningful request volume against the same currently-open archive domains — worth deciding deliberately how much to verify vs. trust before automating it.

**g. Older NSE annual reports are ZIPs, not PDFs.** *(Added 2026-09-23, found during the full download.)* `archives.nseindia.com/annual_reports/` serves annual reports for FY2022-23 and earlier as `.zip` files, each wrapping a single PDF; from FY2023-24 onward they are plain PDFs. This held for both `AR_` and `SME_AR_` files (E2E FY2017-18 to FY2022-23, APAR FY2011-12). BSE's `bseplus/AnnualReport/` serves PDFs for every year. One ZIP stored its PDF under a nested path (`<name>.zip/<file>.pdf`), so inner filenames can't be assumed either. At scale, a large share of a 10-year window of NSE-sourced annual reports will arrive as ZIPs, so any fetcher has to detect the real file type (from the first bytes, not the URL extension) and unpack before parsing.

## 6. Rough scale math

- This pilot's average was ~53 documents/company (skewed high by APAR at 121, skewed low by the two recent SME listings at 8–14).
- Extrapolated loosely to 3,000–4,000 companies: **very roughly 150,000–250,000 documents** — a wide range, since density depends heavily on company age, sector disclosure norms (some sectors concall every quarter, others rarely), and listing tier (SME vs mainboard).
- Discovery alone would require fetching ~3,000–4,000 Screener company pages at minimum, likely more given this pilot needed re-prompting to get full (non-summarized) document lists per company. That volume is squarely in "systematic/automated" territory under NSE's ToS, independent of how the resulting PDFs are then retrieved.

## 7. Open questions for discussion

1. Is Screener.in an acceptable long-term discovery dependency, or does discovery need its own primary-source solution (e.g. browser automation against NSE's/BSE's own filing search) before scaling further?
2. Is the shareholding-pattern gap acceptable to leave as "derived data only," or does it need a dedicated discovery path?
3. At what point does volume justify pursuing NSE Data & Analytics' paid/licensed route instead of continuing the workaround approach?
4. How should periodic-results discovery work for mainboard/large-cap companies, given pattern-matching alone didn't reliably isolate it from surrounding filings?
