# Why build a financial-document chatbot when the data is public?

Conversation recorded on 2026-10-02.

## Question

Ok. Tell me this. The aim of this application is to index all the docs, annual reports, results, shareholding patters, concalls, presentations, credit ratings for all the indian publicly traded companies and give it as a chatbot to users. Which they can go and query for accurate information. First of all, all the data are public. So, why can't you or claude can do it if user asks a specific question?

## Response

**We can answer many specific questions about those public documents. Your application’s value would be making that process consistently complete, accurate and fast.** Public availability alone doesn’t provide those guarantees.

If someone asks, “What was E2E Networks’ revenue in FY2025?”, an assistant with web access can often find the annual report, read the relevant statement and cite it. For that kind of straightforward question, a general assistant is already a strong competitor.

The difficulty increases with the question:

| User question | What answering reliably requires |
|---|---|
| “What was this company’s FY2025 revenue?” | Find the correct report and distinguish standalone from consolidated revenue. |
| “How has management’s capacity-expansion guidance changed over eight quarters?” | Find every relevant transcript and presentation, extract statements and compare their dates. |
| “Which companies increased promoter pledging while their credit outlook deteriorated?” | Broad coverage of shareholding disclosures and rating actions, with aligned reporting periods. |
| “Did management deliver on its promises over five years?” | Connect historical guidance to subsequent results, accounting for revisions and changed definitions. |

There are several reasons a general assistant can struggle even though the underlying information is public.

**1. Public does not mean discoverable or accessible to the assistant.**
A PDF may be buried in an exchange archive, absent from search results, or behind a website that blocks automated access. Your own research found exactly this: direct archive PDFs were accessible, but finding their URLs was difficult.

**2. Finding some documents is easier than establishing complete coverage.**
An assistant might find three transcripts and miss a fourth containing a guidance withdrawal. A maintained collection can track what exists, what is missing and when it was last checked. That matters whenever the answer implies “all,” “never,” or “over the last five years.”

**3. Reading financial documents correctly is a separate problem.**
A number can be transcribed correctly but assigned to the wrong year, entity or unit. Your comparison demonstrates this: preserving text did not necessarily preserve its table relationships. Indexing everything with weak parsing would reproduce those mistakes at greater scale.

**4. A chat request has a limited research budget.**
Searching, downloading and comparing hundreds of documents from scratch takes time. Your application can do that preparation once and reuse it across users. The advantage is particularly strong for historical and cross-company questions.

**5. Accuracy needs more than retrieval.**
The system must distinguish consolidated versus standalone, quarterly versus cumulative results, original versus revised filings, and management guidance versus reported outcomes. Calculations need consistent inputs. Answers should cite the precise supporting page and acknowledge missing evidence.

**So the competitive distinction depends on your scope.**

If the product is **“ask a question about one company’s latest annual report,”** the differentiation from general assistants is relatively small.

If it is **“query a maintained, auditable history of Indian listed companies, compare across companies and periods, and trace every material claim to its source,”** there is a substantial problem to solve.

For that broader product, I would think of the foundation as **a document collection plus a structured financial-data layer**, with a chatbot on top. Documents support explanations, guidance and qualitative disclosures; structured records make exact comparisons and screening more reliable.

**The key promise should be evidence-backed answers with explicit coverage—not accuracy simply because all the PDFs have been indexed.**
