# Independent pilot verification — 23 September 2026

## Reconciliation with main's full downloader run

During rebase onto main (`cbe2f7f`), the other agent's committed manifest established that all 259 catalogued URLs had been attempted: 228 downloaded, 18 returned 403, 11 returned 404, and two returned HTML instead of documents. Eight catalog rows have no URL. This supersedes the earlier uncertainty below about untested URLs and the 18 inferred Hero failures: the full run individually confirmed those failures. It does not resolve content classification or historical completeness. The independent pilot results below remain dated evidence of that separate experiment.

The matrix-URL downloader and ZIP extraction already exist on main; recommendations below concern validation and future discovery infrastructure. The pilot did not change the matrix, but the other agent's downloader did update its statuses and add `download_status`; those changes are retained. The two new APAR sources are linked below and await catalog reconciliation. Gitignored downloads are worktree-local, so committed download statuses do not establish file presence in a different checkout.

## Verdict

The archive-download approach works in this sample, but the original catalog is not yet a reliable coverage measure. Company websites are useful sources in some cases, and at least one successfully downloaded filing is misclassified. Discovery, content validation, historical issuer metadata, and access rights all need resolving before a production build.

## Method and evidence

Tested a fixed, purposive sample of 24 URLs: 17 existing matrix entries across all five companies, three newly discovered document links, and four web pages. Selection covered NSE annual/corporate archives, BSE redirects/direct archives/legacy annual reports, company hosting, old and recent documents, and previously untested and blocked entries. This is not a random sample or a complete history audit.

Used plain `curl -L` GETs with a normal browser User-Agent, no cookies, 30-second timeout, and three seconds between requests. No concurrent exchange requests, NSE API calls, challenge solving, or browser fingerprint changes. An initial sandbox DNS failure was resolved through approved network access; it was not counted as a source failure. One preliminary Esconet download preceded the fixed sample. Additional web searches and policy/regulation reads are outside the 24-URL count.

The pilot recorded HTTP status, MIME type, final URL, redirect count, bytes, SHA-256, magic bytes and ZIP members. Raw pilot artifacts are retained locally outside the repository; this commit contains only Markdown documentation. Matrix row numbers count the header as row 1. The pilot did not change the catalog or re-certify untested entries. Source links and substantive content findings are provided below.

Used an isolated `pypdf` 6.19.0 environment, without adding project dependencies. Text inspection checks issuer, document type and period; it does not validate every number, signature or table. Some font warnings mean extracted text is not guaranteed faithful enough for automated financial analysis.

## Results

| Test | Result |
|---|---|
| 15 exchange-hosted documents | All downloaded: 14 PDFs and one ZIP |
| Two existing company-hosted documents | APAR transcript succeeded; Hero transcript returned 403 |
| Three newly discovered company documents | APAR results and shareholding succeeded; Hero shareholding returned 403 |
| Screener Esconet page | 200, with actual links to NSE annual reports and corporate documents |
| APAR investor-relations page | 200, with document links |
| NSE homepage | 403 in this environment |
| BSE homepage | 200 HTML application shell; this does not establish working filing search |

Overall: 17 PDFs, one ZIP, three HTML responses, three 403 responses; approximately 138.7 MB transferred in the fixed sample. All 16 successful existing-document downloads had been recorded as either `200` or `untested`; the sampled Hero entry remained blocked. These outcomes do not establish archive-wide reliability or verify the other matrix URLs.

## Corrections to earlier claims

1. **A `200` PDF can be the wrong filing.** Matrix row 76, C2C's supposed H1 FY2025–26 results, is a four-page October 22, 2025 disclosure of preferential equity and warrant allotments. All four pages were inspected; there are no half-yearly financial statements. The filename's `Outcome_of_Board_Meeting` and `updated_FS` are not sufficient classification evidence. Exclude this entry from results coverage until replaced. The source URL remains in the catalog and its downloaded body hash is recorded in main’s download manifest.

2. **Company sites are not universally blocked.** APAR's IR page, May 2018 earnings-call transcript, FY2024–25 results and December 2018 shareholding PDF all downloaded. The original matrix already contained an APAR company-hosted `200`, contradicting its own blanket conclusion. Hero returned 403 for both the old transcript and newly found shareholding URL. Treat access as an observation about a URL, time and client environment.

3. **Shareholding filings are discoverable.** [APAR's December 2018 report](https://apar.com/wp-content/uploads/2021/02/Q3-22.pdf) is eight pages and identifies Regulation 31 and the reporting quarter. This is an issuer-hosted filing-format document, not Screener-derived percentages. Exchange receipt/authentication was not independently checked. [Hero's September 2025 report](https://www.heromotocorp.com/content/dam/hero-aem-website/in/en-in/company-section/investors/statutory-filings/statutory-filings-pdfs/shareholding-pattern/2025-26/september-25-shareholding-pattern.pdf) is discoverable in web search but direct curl access returned 403. Discovery and retrieval must be separate statuses. The remaining companies and periods are unresolved.

4. **APAR's periodic-results gap is partly closed.** [May 14, 2025 board outcome](https://apar.com/wp-content/uploads/2025/05/Outcome-of-Board-Meeting_Results-fy25.pdf) contains the audited standalone/consolidated Q4 and FY2024–25 financial results package (25 pages), not just an earnings presentation. This proves a useful company-source path, not complete historical coverage. Hero's periodic-results PDF gap remains open in this pilot.

5. **Not every annual report is delivered as PDF.** E2E FY2022–23 arrives as a valid 31.7 MB ZIP containing a PDF. The original matrix noted this, but the report's claim that all earlier successes were `application/pdf` was inaccurate. BSE `AnnPdfOpen` redirects were reproduced. Check signature and parser success, not extension alone; handle archive members with size/path limits.

6. **Historical tier must be dated.** E2E's downloaded FY2022–23 annual report says mainboard trading began April 12, 2022 after migration from SME EMERGE. Its current mainboard label must not be applied to the entire 2018-onward history. C2C's FY2024–25 annual report says it listed December 3, 2024, contradicting “FY2025–26 only.” `C2C` in document metadata and `C2CAS` in archive filenames also show why filenames cannot serve as the security master.

7. **267 entries are not 267 content-validated documents.** There are 259 nonempty, distinct URLs and eight gap placeholders. At the independent pilot's starting point, the 18 original `blocked` Hero rows contained notes extrapolating from sampled host failures; the original report overstated that evidence. This pilot individually checked only one of those 18 URLs; main's separate full downloader run subsequently supplied individual failure records for all 18. Coverage must count validated company/type/period combinations, not rows or download successes.

8. **NSE API blocking was not independently retested.** Repository rules prohibit those calls. This run observed a homepage 403, which cannot prove that every discovery route is blocked or identify the protection vendor. BSE's homepage returned an HTML shell rather than 403. A search-index/web-tool response is not evidence that a direct client can fetch the same URL.

## What changes at scale

- **Rights are a prerequisite, not a document-count threshold.** [NSE's current terms](https://www.nseindia.com/static/nse-terms-of-use), clause 9, prohibit systematic/automated collection. They do not provide a low-volume exemption. [Screener's terms](https://www.screener.in/guides/terms/) limit the service license to personal, non-commercial transitory viewing and restrict copying/commercial use. Public download success does not establish permission to construct or redistribute a bulk corpus. The repository's low-volume rule is an operational limit, not a grant of rights.
- **A paid product is not automatically a historical PDF archive.** [NSE's published corporate-data offering](https://www.nseindia.com/static/market-data/corporate-data-subscription) lists an end-of-day corporate-announcement feed via SFTP after 20:00 IST at ₹500,000 per annum for domestic customers. Verify historical backfill to 2015, SME coverage, original attachments, all five categories, corrections, permitted retention and downstream use, taxes and any other fees before purchasing. [NSE's data policy](https://www.nseindia.com/static/market-data/nse-data-policy) makes use and redistribution agreement-specific and provides a research-request route. [BSE's market-data portal](https://marketdata.bseindia.com/) advertises financials and disclosures; its detailed license and pricing were not established here.
- **Re-estimate size from expected periods.** The five-company average is biased by young listings and missing entire categories. Illustratively, a continuously listed mainboard company over ten complete years has 10 annual-report, 40 results-period and 40 shareholding-period slots: 90 before calls/presentations. Across 3,000–4,000 such companies that is 270,000–360,000 slots. With four calls and four presentations per year, the illustrative total becomes 510,000–680,000. These are planning scenarios, not a forecast: SME frequency, listing age, voluntary publication and bundled documents change the count.
- **Measure completeness per company, historical tier, type and period.** Distinguish not searched, not located, not applicable/not published, access blocked, retrieved, and content validated. Calls and presentations should not be assumed to exist every quarter. Keep standalone/consolidated scope and period-end separate from filing/call dates.
- **SME frequency affects shareholding too.** The [current consolidated SEBI LODR regulations](https://www.sebi.gov.in/legal/regulations/jul-2026/securities-and-exchange-board-of-india-listing-obligations-and-disclosure-requirements-regulations-2015-last-amended-on-july-14-2026-_102974.html), amended July 14, 2026, retain the half-yearly SME provisions for shareholding (31(1), PDF page 62) and financial results (33(5), PDF page 74). The underlying PDF was downloaded and text-checked. Apply rules effective in each historical period rather than retroactively assuming today's rules.
- **Preserve provenance and versions.** Record discovery URL, requested/final document URLs, observed HTTP result, UTC timestamp, document hash, issuer identity/ISIN, actual period and semantic validation. Deduplicate the same filing across NSE/BSE/company mirrors; retain corrected filings with supersession relationships. Missing `filed_date` values prevent a trustworthy point-in-time history.
- **Budget for extraction and recovery.** This sample spans about 0.3–31.7 MB per successful download. PDFs can be scans or have difficult fonts; plan an OCR/manual-review path, archive limits, bounded retries, checkpoints and per-host throttling. A three-second gap alone costs 125–208 hours for 150,000–250,000 requests before download time; it is an illustration, not an approved exchange rate limit. Cache verified documents instead of repeatedly downloading them for status checks.

## Recommended next step

Before building discovery infrastructure, run a bounded coverage audit over a few specified periods for these five issuers, correcting the C2C classification and using dated listing tiers. Reconcile the two APAR additions and re-discover alternatives for the 13 non-403 failures recorded by the existing downloader. In parallel, obtain a concrete data-product coverage/license specification. Decide whether company-hosted filing copies and structured exchange formats satisfy the requirement, or whether exchange-hosted PDFs are mandatory. No bulk-access decision was made in this session.
