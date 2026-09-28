# Chunks: Option 1: PyMuPDF text, line-preserving cleaning + structured chunker — e2e_ar_fy23

- PDF: `data/E2E/annual_reports/2023-09-21_FY2022-23.pdf` (page numbers = PDF viewer pages)
- 179 chunks, 64,255 tokens (38 table chunks)
- Text inside each block is exactly what would be embedded.

### Chunk 0

_text · pages 2–2 · 2 words · 6 tokens_

```text
Corporate Information1.
```

### Chunk 1

_table · pages 2–2 · 58 words · 105 tokens_

```text
Corporate Information1.

| About the Company2. | 1 |
| 3. Chairman’s Message | 2 |
| 4. | Director's Report | 9 |
| 5. Management Discussion and Analysis Report | 10 |
| 6. Corporate Governance Report | 46 |
| 7. | 52 | Financial Statements under Ind -AS including Auditor's Report | 103 |
```

### Chunk 2

_text · pages 12–12 · 63 words · 128 tokens_

```text
## FINANCIAL SUMMARY OF OPERATIONS
Dear Members,

Your Directors have immense pleasure in presenting the 14th Annual Report on the business and operations of
your Company, along with the Audited
Financial Statements, for the Financial year ended on March 31, 2023.

## FINANCIAL SUMMARY OF OPERATIONS

The financial performance during the Financial Year 2022-23 is summarized below:
(Amount in INR Lakhs)
Particulars Standalone
```

### Chunk 3

_table · pages 12–12 · 208 words · 511 tokens_

```text
## FINANCIAL SUMMARY OF OPERATIONS
Dear Members,
Your Directors have immense pleasure in presenting the 14th Annual Report on the business and operations of your Company, along with the Audited
Financial Statements, for the Financial year ended on March 31, 2023.
## FINANCIAL SUMMARY OF OPERATIONS
The financial performance during the Financial Year 2022-23 is summarized below:
(Amount in INR Lakhs)
Particulars Standalone

| FY 2022-23 | FY 2021-22 |
| Revenue from operations | 6620.18 | 5187.34 |
| Total Expenditure other than finance cost and depreciation | 3313.96 | 2893.01 |
| Earnings before Interest, Tax and Depreciation (EBITDA) | 3306.22 | 2294.33 |
| Other Income | 76.01 | 35.51 |
| Depreciation | 2011.15 | 1782.64 |
| Finance Costs | 47.46 | 18.60 |
| Profit/(Loss) before tax (PBT) | 1323.62 | 528.60 |
| Current Tax | 314.80 | - |
| Deferred Tax | 17.83 | (116.50) |
| Net Profit for the Year (PAT) | 990.99 | 645.10 |
| Other Comprehensive Income | 25.54 | 487.89 |
| Total comprehensive income for the period/year | 1016.53 | 1132.99 |
| Basic EPS (in INR) | 6.85 | 4.46 |
| Diluted EPS (in INR) | 6.77 | 4.44 |
```

### Chunk 4

_text · pages 12–13 · 136 words · 247 tokens_

```text
## FINANCIAL SUMMARY OF OPERATIONS
The Revenue from operations of the Company for the year ended March 31, 2023, was INR 6620.18 Lakhs as
compared to INR 5187.34 Lakhs during
the previous year ended March 31, 2022, indicating an increase in revenue by 27.62%.

The profit for the year under review was INR 990.99 Lakhs as compared to the profit of INR 645.10 Lakhs for
the previous year.

| E2E Networks Limited | 10 |

During FY 2022-23, your Company continued to invest in enhancing capabilities of its public cloud platform
focussing on the increased requirements
for AI/ML and DL workloads. The continued focus on customer success has yielded an increase in revenue.

A detailed analysis of the financial results is given in the Management Discussion and Analysis Report, which
forms a part of this report.
```

### Chunk 5

_text · pages 13–13 · 369 words · 537 tokens_

```text
## FUTURE PROSPECTS
As per the Avendus Report from May 2023 titled “Data Centres: Powering Digital India” India continues to have
a robust investment and demand
environment for data center capacity measured in megawatts and expected to be more than doubled from the
current capacity of nearly 800 MWs to
nearly 1700 MWs by Mar 2025. A lot of this demand for data center capacity is now driven by Cloud GPU
infrastructure required by economies betting
on AI/ML and Deep Learning.

Demand environment driven by AI/ML/DL workloads:

1. Various Sectoral and National Data Protection Imperatives to take part in global AI/ML/DL race there is a
lot of funding focussed on AI/Deep
Tech/Innovation missions and from investors in expected. Data as the new oil and could lead to a source of
competitive advantage for India.
India as a country is very rich in data due to the vast size of its population and as an early adopter of
Digital Public Infrastructure (DPI) and
combined with revolutionary increase in access to broadband for the majority of its population via 4G/5G
infrastructure.
2. Large innovation investors are seeing some efficiency in deployment of Cloud GPU capacity for workloads for
use in pre-investment
engagements.
3. Higher Education and Research continues to play a deep role in Large Language Model research into more
Indian languages.
4. Enterprises, Mature Startups and AI First Innovative companies

A healthy growth is expected in demanding AI/ML/DL workloads running on Accelerated Computing Platforms is
expected from all the above.

Our expertise in Cloud GPU technology and its commitment to driving AI innovation positions it favourably for
sustained growth. We have showcased
our ability to thrive in a competitive environment, through our focused strategic vision, and a customer-
centric approach.

Our sales cycle is driven by customer trials of our Cloud Platform, the more capacity deployment helps us in
more sales and towards that end we are
organizing more debt funding in the near term. To that end the plan is to ramp up investments into
Server/Networking and Accelerated Computing
hardware and its deployment into the Cloud Platform to increase its capacity. The increased capacity would
allow us to pursue additional recurring
revenue opportunities.

| E2E Networks Limited | 11 |
```

### Chunk 6

_text · pages 14–14 · 181 words · 295 tokens_

```text
## BRIEF DESCRIPTION OF THE STATE OF THE COMPANY’S AFFAIRS
Your Company provides accelerated Cloud which supports machine learning applications and other critical
workloads. Our cloud infrastructure is
used for workloads in various fields ranging from Data Science, NLP, Computer Vision / Image Processing,
various digital native workloads and
traditional enterprise workloads. We provide Cloud infrastructure services through our cloud platform which
can be accessed via our self-service
portal available at link https://myaccount.e2enetworks.com. Our self-service public cloud platform enables
rapid deployment of compute
workloads. It enables Customers to provision/manage and monitor Linux/Windows/GPU Cloud Machines with high
performance CPU, large
memory (RAM) or Smart Dedicated Compute featuring dedicated CPU cores. Our compute instances are available
from Indian data centers located
at Noida and Mumbai ensuring data locality for India centric computing workloads.

Compared to INR 4.9 Crores in March 2022, the monthly recurring revenue increased to INR 6.1 Crores in March
2023. Your Company continues to
build additional Cloud Capacity with a view to be able to have more customers trying out its services via
proof-of-concept trials and eventually
converting into customers.
```

### Chunk 7

_text · pages 14–14 · 123 words · 224 tokens_

```text
## LISTING INFORMATION
In the fiscal year ending on March 31, 2023, the Company successfully migrated to the National Stock
Exchange's Main Board. This decision was made
by the Board of Directors during a meeting held on January 7, 2022. The transition from the NSE SME EMERGE
platform to the NSE Main Board was
approved by the shareholders through a Postal Ballot on February 17, 2022. Following this, the requisite
application for migration was submitted to
the NSE, which granted approval for listing and trading on the NSE Main Board with effect from April 12, 2022.
The company has duly paid the Listing Fee for the financial year 2022-23 and 2023-24 to the NSE. The Company's
ISIN (International Securities
Identification Number) is INE255Z01019.
```

### Chunk 8

_text · pages 14–14 · 120 words · 212 tokens_

```text
## COMPANY'S WEBSITE
The website of your Company https://www.e2enetworks.com/ displays the Company's business operations up-front
on the home page. The site
carries a comprehensive database of information of all the products and services offered by the Company
including other information for investors
like the Financial Results of your Company, Shareholding Pattern, Directors & Senior Management personnel’s
profile, details of Board Committees,
Corporate Policies and business activities of your Company.

All the mandatory information and disclosures as per the requirements of the Companies Act, 2013 (hereinafter
referred as “the Act”) and as per the
SEBI (Listing Obligations and Disclosure Requirements) Regulations, 2015 (hereinafter referred as “SEBI LODR
Regulations”) have been uploaded on
the website.

| E2E Networks Limited | 12 |
```

### Chunk 9

_text · pages 15–15 · 158 words · 265 tokens_

```text
## CORPORATE GOVERNANCE
The Company does not have any Equity shares lying in the Demat Suspense/Unclaimed Suspense Account.

## CORPORATE GOVERNANCE

Your Company’s Corporate Governance philosophy is governed by its commitment to run its businesses in a legal,
ethical and transparent manner – a
dedication that comes from the top management and is imbibed throughout the organisation. The Company believes
that sound corporate governance
is critical in enhancing and retaining investor trust. Transparency, accountability, fairness and intensive
communication with stakeholders are integral
to our functioning.

The Board has framed Code of Conduct for all Board members and Senior Management of the Company and they have
affirmed the compliance for the
financial year ended March 31, 2023.

A detailed report on Corporate Governance along with the Certificate from MAKS & Co., Company Secretaries [FRN
P2018UP067700], confirming
compliance with conditions of Corporate Governance as stipulated under Schedule V of the SEBI LODR Regulations
forms an integral part of this
Report.
```

### Chunk 10

_text · pages 15–16 · 126 words · 208 tokens_

```text
## CHANGE IN THE NATURE OF BUSINESS
The Board of Directors of the Company has not recommended any dividend for the financial year ended March 31,
2023. Accordingly, there has been
no transfer to general reserves.

## CHANGE IN THE NATURE OF BUSINESS

There is no change in the nature of the business of the Company during the year under review.

## PUBLIC DEPOSITS
During the year under review, your Company does not have any subsidiary, joint-venture, or associate
companies.

| E2E Networks Limited | 13 |

## PUBLIC DEPOSITS

During the year under review, your Company has neither invited nor accepted any fixed deposits from the public
within the meaning of Section 73 of
the Act read with the Companies (Acceptance of Deposits) Rules, 2014.
```

### Chunk 11

_text · pages 16–16 · 173 words · 357 tokens_

```text
## SHARE CAPITAL
During the year under review, there is no change in Authorized Share Capital of the Company, and it stood at
INR 16,50,00,000/- (Indian
Rupees Sixteen Crores and Fifty Lakhs Only) divided into 1,65,00,000 (One Crore and Sixty-Five Lakhs ) Equity
Shares of INR 10/- (Indian Rupees
Ten Only) each as on March 31, 2023.

The issued and paid-up capital of the Company is at INR 14,47,51,260 (Indian Rupees Fourteen Crores Forty-
Seven Lakhs Fifty-One Thousands Two
Hundreds and Sixty Only) divided into 1,44,75,126 (One Crore Forty-Four Lakhs Seventy-Five Thousands One
Hundred and Twenty Six ) Equity
Shares of face value of INR 10/- (Indian INR Ten Only) each as on March 31, 2023.

Your Company has neither issued any equity shares with differential voting rights as to dividend, voting or
otherwise nor has issued any sweat equity
shares to the employees or Directors of the Company, under any scheme during the year under review. Your
Company has not issued any debentures,
bonds or any non-convertible securities during the year under review.
```

### Chunk 12

_text · pages 16–17 · 201 words · 358 tokens_

```text
## EMPLOYEE STOCK OPTION PLANS/SCHEMES
The Employee Stock Option Scheme of the Company aims to give benefit to eligible employees with a view to
attract and retain the best talent,
encourage employees to align individual performance with company objectives, and promote their increased
participation and involvement in the
growth of the Company.

The Nomination and Remuneration Committee of the Board of Directors of the Company, inter alia administers and
monitors the Employee Stock
Option Schemes of the Company i.e. E2E ESOS Scheme 2018 and E2E Networks Limited Employees Stock Option Scheme
– 2021 in accordance with
the Securities and Exchange Board of India (Share Based Employee Benefits and Sweat Equity) Regulations, 2021
(“SBEB Regulations”).

The disclosures as required under Regulation 14 of SBEB Regulations, is available on website of the Company
at:
https://www.e2enetworks.com/investors/employee-stock-option-schemes

| E2E Networks Limited | 14 |

The certificate from the Secretarial Auditors of the Company, that the Scheme has been implemented in
accordance with the SBEB Regulations and
the resolutions passed by the members of the company, shall be uploaded on the website of the Company i.e.
https://www.e2enetworks.com/ and
shall be available for inspection by members in electronic mode during the Annual General Meeting of the
Company.
```

### Chunk 13

_text · pages 17–18 · 384 words · 685 tokens_

```text
## PARTICULARS OF DIRECTORS AND KEY MANAGERIAL PERSONNEL
During the year under review, your Company has no outstanding instruments for which the credit rating needs to
be obtained.

## PARTICULARS OF DIRECTORS AND KEY MANAGERIAL PERSONNEL

DIRECTORS

The Board Diversity Policy of your Company requires the Board to have balance of skills, experience and
diversity of perspectives appropriate to your
Company. The skills, expertise and competencies of the Directors as identified by the Board, along with those
available in the present mix of the
Directors of your Company.

The Board of Directors of the Company has optimum combination of executive and non-executive directors
including independent directors and
woman director in compliance with the applicable provisions of the Act and SEBI LODR Regulations.

| E2E Networks Limited | 15 |

During the year under review, there have been following changes amongst the directors of the Company:-

Sr. Name of Particulars of Change Effective
No. Director (Appointment / Resignation/Others) Date of
change

| 1 | Mr. Gaurav | The tenure of Mr. Gaurav Munjal, Non-Executive Independent Director of the Company was ended on 8th | 9th February, |
| Munjal | February, 2023. However, he was re-appointed as Non-Executive Independent Director of the Company | 2023 |

for a second and final term of 5 consecutive years w.e.f 9th February, 2023 to 8th February, 2028.

| 2 | Mr. Varun | The tenure of Mr. Varun Pratap Rajda, Non-Executive Independent Director of the Company was ended on | 9th February, |
| Pratap Rajda | 8th February 2023. However, he was re-appointed as Non-Executive Independent Director of the Company | 2023 |

for a second and final term of 5 consecutive years w.e.f 9th February, 2023 to 8th February, 2028.

| 3 | Mrs. Srishti | The previous tenure of Mrs. Srishti Baweja as Whole Time Director of the Company was ended on January | 31st January, |
| Baweja | 30, 2023. | 2023 |

On the recommendation of Nomination and Remuneration Committee (“NRC”) and on the proposal of the
Board, the Shareholders of the Company at their 13th Annual General Meeting (“AGM”) held on 24th
August, 2022 re-appointed Mrs. Srishti Baweja as Whole Time Director of the Company for a further term
of three years commencing from 31st January, 2023 to 30th January, 2026.
```

### Chunk 14

_text · pages 18–19 · 420 words · 783 tokens · starts with overlap_

```text
## PARTICULARS OF DIRECTORS AND KEY MANAGERIAL PERSONNEL
Srishti Baweja as Whole Time Director of the Company for a further term
of three years commencing from 31st January, 2023 to 30th January, 2026.

| Mr. Tarun | The previous tenure of Mr. Tarun Dua as Managing Director of the Company was ended on January 30, | 31st January, |
| Dua | 2023. | 2023 4 |

On the recommendation of NRC and on the proposal of the Board, the shareholders of the Company at
their 13th AGM held on 24th August, 2022 re-appointed Mr. Tarun Dua as Managing Director of the
Company for a further term of three years commencing from 31st January, 2023 to 30th January, 2026.

| E2E Networks Limited | 16 |

Further, the following re-appointments are proposed in ensuing AGM:-

Sr. Particulars Details

| 1 | Re-appointment of Mrs. Srishti Pursuant to the provisions of Section 152(6) and other applicable provisions of the Act, Mrs. Srishti |
| Baweja, Retire by Rotation | Baweja (DIN: 08057000), Whole-time Director of the Company, retires by rotation at the ensuing AGM |

and being eligible, offers herself for re-appointment.

Based on the recommendation of NRC, the Board recommends her re-appointment to the shareholders
for her approval in the ensuing AGM.

2 Re-appointment of Mr. Naman K. Based on the recommendation of the NRC, the Board of Directors of the Company
at it’s meeting held on

| Sarawagi as the Non-Executive | 28th August, 2023 have approved the re-appointment of Mr. Naman K. Sarawagi (DIN 05295642) as Non- |
| Independent Director | Executive Independent Director for a second and final term of 5 consecutive years subject to the approval |

of the Shareholders.

The Company has received a Notice in writing from a Member under Section 160 of the Act, proposing his
candidature for the office of the Director, Mr. Naman K. Sarawagi has submitted a declaration that he
meets the criteria for Independence as provided in Section 149(6) of the Act and the rules made
thereunder and SEBI LODR Regulations. In the opinion of the Board they possess requisite qualifications,
experience, expertise, proficiency and hold high standards of integrity and he is independent of
management.

The Board of Directors recommends the re-appointment of Mr. Naman K. Sarawagi (DIN 05295642) as
the Non-Executive Independent Director for a second term of five consecutive years w.e.f. February 18,
2024 to February 17, 2029, to the shareholders for their approval in the ensuing AGM.

| E2E Networks Limited | 17 |
```

### Chunk 15

_text · pages 20–20 · 131 words · 247 tokens · starts with overlap_

```text
## PARTICULARS OF DIRECTORS AND KEY MANAGERIAL PERSONNEL
Naman K. Sarawagi (DIN 05295642) as
the Non-Executive Independent Director for a second term of five consecutive years w.e.f. February 18,
2024 to February 17, 2029, to the shareholders for their approval in the ensuing AGM. | E2E Networks Limited |
17 |

The brief resume of Mrs. Srishti Baweja and Mr. Naman K. Sarawagi along with other relevant details like
nature of their expertise and other
directorships/committee memberships held by them, as stipulated under Regulation 36(3) of the SEBI LODR
Regulations and Secretarial Standards
issued by ICSI, form part of Notice convening the 14th AGM.

Further, they have affirmed that they are not debarred from holding the office of a Director by virtue of any
SEBI order or any other such Authority.
```

### Chunk 16

_text · pages 20–20 · 132 words · 274 tokens_

```text
## KEY MANAGERIAL PERSONNEL
The details of Key Managerial Personnel of the Company pursuant to Section 2(51) and Section 203 of the Act
read with the Companies (Appointment
and Remuneration of Managerial Personnel) Rules, 2014 as on March 31, 2023 and details of changes during the
FY 2022-23 are as follows:-

S. No. Name Designation
1 Mr. Tarun Dua Chairman & Managing Director
2 Mrs. Srishti Baweja Whole Time Director
3 Mr. Megha Raheja Chief Financial Officer
4 Mrs. Neha Baid* Company Secretary

5 Mrs. Richa Gupta Company Secretary

* Resigned w.e.f. February 7, 2023.
Appointed w.e.f February 7, 2023.

Apart from this, during the year under review, there is no other change in Key Managerial Personnel.

DECLARATION OF INDEPENDENCE BY INDEPENDENT DIRECTORS & ADHERENCE TO THE COMPANY’S CODE OF CONDUCT FOR
```

### Chunk 17

_text · pages 20–21 · 289 words · 453 tokens_

```text
## INDEPENDENT DIRECTORS
All the Independent Directors have confirmed to the Board that they meet the criteria of independence as
specified under Section 149(6) of the Act
and that they qualify to be independent directors pursuant to the Rule 5 of the Companies (Appointment and
Qualification of Directors) Rules, 2014.
They have also confirmed that they meet the requirements of ‘Independent Director’ as mentioned under
Regulation 16(1)(b) of the SEBI LODR
Regulations.

| E2E Networks Limited | 18 |

Further, all the Independent Directors have affirmed that they have adhered and complied with the Company’s
Code of Conduct for Independent
Directors which is framed in accordance with Schedule IV of the Act.

Further, the Independent Directors have confirmed that they are not aware of any circumstance or situation,
which exist or may be reasonably
anticipated, that could impair or impact their ability to discharge their duties with an objective independent
judgment and without any external
influence
It may be noted that all the Independent Directors on the Board of the Company as on March 31, 2023, have been
registered in the data bank of
Independent Directors as per Rule 6 of the Companies (Appointment and Qualification of Directors) Rules, 2014.

The Company has taken the certificate from MAKS & Co., Company Secretaries [FRN P2018UP067700], that none of
the directors on the Board of the
Company have been debarred or disqualified from being appointed or continuing as directors of companies by the
Board/Ministry of Corporate Affairs
or any such statutory authority. The Certificate forms part of Corporate Governance Report..

The Board is of the opinion that the Independent Directors of the Company possess requisite qualifications,
experience and expertise and they hold
highest standards of integrity and are independent of management.
```

### Chunk 18

_text · pages 21–21 · 127 words · 219 tokens_

```text
## BOARD MEETINGS
None of the Directors of your Company are disqualified as per provision of Section 164(2) of the Act. The
Directors of the Company have made
necessary disclosures as required under various provisions of the Act and the SEBI LODR Regulations.

## BOARD MEETINGS

During the year under review, the Board of the Company met 5 times viz. April 30, 2022; May 27, 2022; July 25,
2022; November 2, 2022; and February
7, 2023. The gap between two Board Meetings did not exceed one hundred and twenty days. The Composition of the
Board and the attendance of each
Director in the Board Meetings and last AGM held on August 24, 2022 are provided in the Corporate Governance
Report which forms integral part of
this Report.
```

### Chunk 19

_text · pages 21–22 · 144 words · 226 tokens_

```text
## BOARD COMMITTEES
The Board Committees play a vital role in strengthening the Corporate Governance practices of the Company and
focus effectively on the issues and
ensure expedient resolution of the diverse matters. The Committees also make specific recommendations to the
Board on various matters as and when
required. All observations, recommendations and decisions of the Committees are placed before the Board for
information, noting or approval.

As on March 31, 2023, the following Committees have been constituted in terms of the Act and the SEBI LODR
Regulations: -

| E2E Networks Limited | 19 |

1. Audit Committee
2. Nomination and Remuneration Committee
3. Stakeholders Relationship Committee
4. Corporate Social Responsibility Committee
5. Borrowing Committee

The Composition of the Committees and the attendance of each Director in the Committee Meetings are provided
in Corporate Governance Report
which forms integral part of this Report.
```

### Chunk 20

_text · pages 22–22 · 118 words · 182 tokens_

```text
## FINANCIAL STATEMENTS
The Financial Statements for the year ended March 31, 2023, have been prepared in accordance with Indian
Accounting Standards (Ind AS) as issued
by the Institute of Chartered Accountants of India and as specified in Section 133 of the Act and the relevant
rules thereof and in accordance with
Regulation 33 of the SEBI LODR Regulations. The estimates and judgments relating to the Financial Statements
are made on a prudent basis, so as to
reflect in a true and fair manner, the form and substance of transactions and reasonably present the Company’s
state of affairs as of March 31, 2023,
and its profits and its cash flows for the year ended on March 31, 2023.
```

### Chunk 21

_text · pages 22–22 · 151 words · 292 tokens_

```text
## STATUTORY AUDITORS
The Board of Directors of the Company on recommendation of Audit Committee at its meeting held on May 27,
2022, approved the appointment of
M/s. GSA & Associates LLP, Chartered Accountants, (Firm Registration No. 000257N) as Statutory Auditors of the
Company w.e.f. May 27, 2022 to fill
the casual vacancy caused by resignation of M/s B. B. & Associates, Chartered Accountants (Firm Registration
No 023670N).

Further, the shareholders of the Company at the 13th AGM of the Company held on 24th August, 2022, on the
recommendations of the Audit Committee
and the Board of Directors, approved the proposal for appointment of M/s. GSA & Associates LLP, Chartered
Accountants (Firm Registration No.
000257N) as Statutory Auditors of the Company for a period of five years from the conclusion of this 13th AGM
until the conclusion of the 18th AGM of
the Company to be held in the year 2027.
```

### Chunk 22

_text · pages 22–23 · 194 words · 365 tokens_

```text
## SECRETARIAL AUDITORS
The Board had appointed M/s. MAKS & Co., Company Secretaries [FRN P2018UP067700] for conducting the
Secretarial Audit of the Company for the
Financial Year 2022-23. The Secretarial Audit Report for the Financial Year ended March 31, 2023, is annexed
herewith as Annexure - A to this report.
The Secretarial Audit Report does not contain any qualification, reservation, adverse remark or disclaimers
for the period under review. ‘

| E2E Networks Limited | 20 |

## REPORT ON FRAUDS U/S 143 (12) OF THE COMPANIES ACT, 2013
The maintenance of Cost Records as specified by the Central Government under Section 148(1) of the Act is not
applicable to the Company as the
company does not fall under any of the categories prescribed under Section 148(1) of the Act.

## REPORT ON FRAUDS U/S 143 (12) OF THE COMPANIES ACT, 2013

During the year under review, the Statutory Auditors and the Secretarial Auditor have not reported any
instances of frauds committed in the Company
by its Officers or Employees to the Audit Committee under Section 143(12) of the Act, therefore no detail is
required to be disclosed under Section
134(3)(ca) of the Act.
```

### Chunk 23

_text · pages 23–23 · 123 words · 235 tokens_

```text
## CHIEF EXECUTIVE OFFICER (CEO) AND CHIEF FINANCIAL OFFICER (CFO) CERTIFICATE
During the financial year ended March 31, 2023, no loan, guarantee, and investment was made by the Company in
terms of Section 186 of the Act and
rules made there under.

## CHIEF EXECUTIVE OFFICER (CEO) AND CHIEF FINANCIAL OFFICER (CFO) CERTIFICATE

In terms of the SEBI LODR Regulations, the Certificate, as prescribed in Part B of Schedule II of the SEBI
LODR Regulations, has been obtained from
Mr. Tarun Dua, Managing Director & Chief Executive Officer and Mrs. Megha Raheja, Chief Financial Officer of
the Company, for the Financial Year
2022 - 2023 with regard to the Financial Statements and other matters. The said Certificate forms part of
Corporate Governance Report.
```

### Chunk 24

_text · pages 23–24 · 185 words · 325 tokens_

```text
## CONSERVATION OF ENERGY, TECHNOLOGY ABSORPTION AND FOREIGN EXCHANGE
There are no material changes and commitments affecting the financial position of the Company which have
occurred between the end of the financial
year 2022-23 and date of this Report.

## CONSERVATION OF ENERGY, TECHNOLOGY ABSORPTION AND FOREIGN EXCHANGE

Even though operations of the Company are not energy intensive, the management has been highly conscious of
the importance of conservation of
energy and technology absorption at all operational levels and efforts are made in this direction on a
continuous basis. In view of the nature of activities
which are being carried on by the Company, the particulars as prescribed under Section 134(3)(m) of the Act,
read with rule 8 of the Companies

| E2E Networks Limited | 21 |

(Accounts) Rules, 2014 regarding Conservation of Energy and Technology Absorption are not applicable to the
Company and hence have not been
provided.

The Company has incurred expenditure of INR 156.05 Lakhs (previous year INR 103.10 Lakhs) in foreign exchange
and earned INR 211.88 Lakhs
(previous year INR 267.17 Lakhs) in foreign exchange during the year under review.
```

### Chunk 25

_text · pages 24–24 · 93 words · 154 tokens_

```text
## SIGNIFICANT AND MATERIAL ORDERS PASSED BY REGULATORS OR COURTS
During the year under review, the provision of section 125(2) of the Act does not apply as the company was not
required to transfer any amount to
the Investor Education and Protection Fund (IEPF) established by the Central Government of India.

## SIGNIFICANT AND MATERIAL ORDERS PASSED BY REGULATORS OR COURTS

During the year under review, there were no significant and material orders were passed by regulators or
courts or tribunals which could impact the
going concern status and company’s operation in future.
```

### Chunk 26

_text · pages 24–24 · 180 words · 277 tokens_

```text
## RISK MANAGEMENT
Pursuant to Section 92(3) read with Section 134(3)(a) of the Act, the Annual Return as on March 31, 2023 in
Form MGT-7 is available on the website
of the Company at https://www.e2enetworks.com/investors/annual-returns

## RISK MANAGEMENT

The Company has developed and implemented a Risk Management policy for identifying the risk associated with
business of the Company and
measures to be taken to control them. The company has established a well-defined process of risk management,
wherein the identification analysis
and assessment of the various risks, measuring of the probable impact of such risks, formulation of risk
mitigation strategy and implementation of the
same takes place in a structured manner. Though, the various risks associated with the business cannot be
eliminated completely, all efforts are made
to minimize the impact of such risks on the operations of the Company.

The Company is not required to form a Risk Management Committee. The Board of Directors of the Company and the
Audit Committee shall
periodically review and evaluate the risk management system of the Company.

| E2E Networks Limited | 22 |
```

### Chunk 27

_text · pages 25–25 · 90 words · 148 tokens_

```text
## INTERNAL CONTROL SYSTEMS INCLUDING INTERNAL FINANCIAL CONTROLS AND THEIR ADEQUACY
The Company has put in place an adequate Internal Control System, commensurate with size, scale and complexity
of its operations. They have been
designed to provide reasonable assurance with regard to recording and providing reliable financial and
operational information, complying with
applicable statutes, safeguarding assets from unauthorized use, executing transactions with proper
authorization and ensuring compliance of
corporate policies.

During the year under review, no material or serious observation has been highlighted for inefficiency or
inadequacy of such controls.
```

### Chunk 28

_text · pages 25–25 · 161 words · 318 tokens_

```text
## CORPORATE SOCIAL RESPONSIBILITY
In compliance with Section 135 of the Act read with the Companies (Corporate Social Responsibility Policy)
Rules, 2014 as amended, the Company
has established a Corporate Social Responsibility (“CSR”) Committee. The CSR Committee has formulated and
recommended to the Board, a CSR Policy
which provides the overview of projects or programs and the guiding principles for selection, implementation
and monitoring of the CSR activities,
which has been approved by the Board. The CSR Policy adopted by Board is available on the website of the
Company and is accessible through the

| link: | https://global-uploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27a66_Corporate-Social-Responsibility-Policy.pdf |

The Company was not required to spend money under CSR for financial year ended 2022-23 as prescribed under
Section 135 of the Act since the
Company incurred an average net loss of Rs. 175.64 Lakhs for previous three financial years.

The Annual Report on CSR activities of the Company has been attached as Annexure - B and forms part of this
Report.
```

### Chunk 29

_text · pages 25–26 · 295 words · 445 tokens_

```text
## PERFORMANCE EVALUATION OF BOARD, ITS COMMITTEES AND INDIVIDUAL DIRECTORS
Management Discussion and Analysis Report for the year under review as stipulated under Regulation 34 of the
SEBI LODR Regulations is presented
in a separate section forming part of this Report and shall be considered as an integral part of this Report.

## PERFORMANCE EVALUATION OF BOARD, ITS COMMITTEES AND INDIVIDUAL DIRECTORS

In terms of the provisions of the Act and the SEBI LODR Regulations a formal annual performance evaluation has
been done by the Board of its own
performance, the DirectoLakhs individually as well as the evaluation of its Committees.

| E2E Networks Limited | 23 |

The Chairperson of Nomination and Remuneration Committee has facilitated the performance evaluation process
and the performance evaluation
forms were circulated to all the directors of the Company.

Based on the criteria mentioned in the Evaluation Form, the exercise of evaluation was carried out through a
structured process covering various
aspects of the Board functioning such as composition of the Board and committees, experience & expertise,
performance of specific duties &
obligations, attendance, contribution at meetings etc. The performance evaluation of the Chairman was also
carried out. The performance Evaluation
of the Directors was carried out by the entire Board (excluding the Director being evaluated). The Directors
expressed their satisfaction with the
evaluation process.

The performance of the committees was evaluated by the Board after seeking feedback from members on the basis
of parameters/criteria such as
degree of fulfilment of key responsibilities, adequacy of committee composition, effectiveness of meetings,
etc.

Independent Directors of the Company in their separate meeting held on March 29, 2023, reviewed the
performance of the Non-Independent Directors
and the Board as a whole. They also reviewed the performance of the Chairperson of the Company.
```

### Chunk 30

_text · pages 26–26 · 83 words · 226 tokens_

```text
## FAMILIARIZATION PROGRAMME AND SEPARATE MEETINGS OF INDEPENDENT DIRECTORS
The Company in its Board Meeting held on 25th July, 2022 had conducted a familiarisation program for the
Independent Directors wherein the
Independent Directors briefed about the Company’s Business, amendments in compliances and roles,
responsibilities and duties of Independent
Directors. The details of the program has been uploaded on the website of the Company and can be assessed
through the link:
https://global-uploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f278a9_Policy-on-
Familiarisation-Programme-for-Independent-Directors.pdf
Further, separate meeting of Independent Directors was held on March 29, 2023.
```

### Chunk 31

_text · pages 26–27 · 191 words · 373 tokens_

```text
## PARTICULARS OF EMPLOYEES AND RELATED DISCLOSURE
The Company has no employee, who is in receipt of remuneration of INR 8,50,000/- per month or INR
1,02,00,000/- per annum and hence, the
Company is not required to give the information under Rule 5(2) and (3) of the Companies (Appointment and
Remuneration of Managerial Personnel)
Rules, 2014.

| E2E Networks Limited | 24 |

As required under Section 197(12) of the Act read with Rule 5(1) of the Companies (Appointment and
Remuneration of Managerial Personnel) Rules,
2014, the percentage increase in remuneration, ratio of remuneration of each Director and Key Managerial
Personnel to the median of employees’
remuneration is enclosed as Annexure - C to this Report.

The other information required under Section 197(12) of the Act read with Rule 5(2) and 5(3) of the Companies
(Appointment and Remuneration of
Managerial Personnel) Rules, 2014 forms part of this Report. Further, pursuant to first proviso to Section
136(1) of the Act, this report is being sent
to the members excluding the said annexure. Any member interested in obtaining a copy of the same may write to
the Company Secretary and
Compliance Officer at cs@e2enetworks.com.
```

### Chunk 32

_text · pages 27–27 · 126 words · 273 tokens_

```text
## NOMINATION AND REMUNERATION POLICY
The Board has adopted Nomination and Remuneration Policy for selection and appointment of Directors and Key
Managerial Personnel and to decide
their remuneration. The Nomination and Remuneration Policy of the Company acts as a guideline for determining,
inter alia, qualification, positive
attributes and independence of a Director, matters relating to the remuneration, appointment, removal and
evaluation of the performance of the
Director and Key Managerial Personnel. The remuneration paid to the Directors is in line with the Nomination
and Remuneration Policy formulated
in accordance with Section 178 of the Act and Regulation 19 of the SEBI LODR Regulations. The said policy of
the Company has been uploaded on the
website of the Company and can be assessed through the link:
https://global-uploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27893_Nomination-and-
Remuneration-Policy.pdf
```

### Chunk 33

_text · pages 27–27 · 163 words · 262 tokens_

```text
## CRITERIA OF MAKING PAYMENTS TO NON-EXECUTIVE DIRECTORS
The Company has in place the orderly succession plan for the appointments at the Board and Senior Management
level.

## CRITERIA OF MAKING PAYMENTS TO NON-EXECUTIVE DIRECTORS

The Non-Executive Independent Directors receive sitting fees only as per the provisions of the Act. The Amount
of sitting fees shall be subject to
ceiling/limits as provided under the Act and rules made there under or any other enactment for the time being
in force.

In addition to the above, Non-Executive Directors (NED)/Independent Directors (ID) will be entitled to
reimbursement of all expenses for participation
in Board and other meetings. ID and/or NED may be paid for the services rendered by such director in any other
capacity provided that:

a) The services rendered are of a professional nature; and
b) The Nomination and Remuneration Committee is of the opinion that the director possesses requisite
qualification for the practice of the profession.

| E2E Networks Limited | 25 |
```

### Chunk 34

_text · pages 28–28 · 168 words · 338 tokens_

```text
## VIGIL MECHANISM/WHISTLE BLOWER POLICY
Your Company believes in ethical and lawful business conduct and strives to carry on its business activities
in a fair, transparent and professional
manner. Pursuant to the provisions of Section 177 of the Act and other applicable provisions, the Company has
adopted a Vigil Mechanism/Whistle
Blower Policy for securing/ reporting/ deterring/ punishing/ rectifying any unethical, unlawful acts,
behaviour, leak/suspected leak of Unpublished
Price Sensitive information etc. and to enable to voice/ address bona fide concern of malpractice, deviation
from the policies of the Company internally
in an effective and systematic manner after its discovery. The policy also provides for adequate safeguards
against victimization of persons who use
such mechanisms and make provisions for direct access to the chairperson of the Audit Committee in appropriate
or exceptional cases. The said policy
is available on the Company’s website and can be assessed through the link:
https://global-uploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27a3c_Whistle-Blower-Policy.pdf

During the year under review, no complaint pertaining to the company was received under the Whistle Blower
Policy/Vigil Mechanism.
```

### Chunk 35

_text · pages 28–28 · 124 words · 266 tokens_

```text
## PREVENTION OF INSIDER TRADING
In accordance with the provisions of SEBI (Prohibition of Insider Trading) Regulation, 2015 the Company has
adopted a Code of Conduct for
Prevention of Insider Trading (“Insider Code”) with a view to regulate trading in securities by the Directors
and Designated persons of the Company.
The said policy is available on the Company’s website and can be assessed through the link:
https://global-uploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27890_Code-of-Conduct-for-
Prevention-of-Insider-Trading.pdfThe Insider Code of the Company stipulates the provisions regarding trading
plan, pre-clearance for dealing in the Company's shares and prohibits
the purchase or sale of Company shares by the Directors and the Designated Persons while in possession of
unpublished price sensitive information
in relation to the Company and during the period when the Trading Window is closed.
```

### Chunk 36

_text · pages 28–29 · 202 words · 396 tokens_

```text
## RELATED PARTY TRANSACTIONS
All transactions entered with Related Parties during the financial year under review were in the ordinary
course of business and on an arm’s length
basis. The details of the transactions with related parties are provided in the notes to accompanying
Standalone Financial Statements. Details
of transactions pursuant to compliance of Section 134(3)(h) of the Act and Rule 8(2) of the Companies
(Accounts) Rules, 2014 are annexed
herewith as per Annexure - D in the FORM AOC-2.

All Related Party Transactions (‘RPTs’) are placed before the Audit Committee for approval. Prior omnibus
approval of the Audit Committee is
obtained for the transactions which are of a foreseen and repetitive nature. A statement giving details of all
RPTs entered into pursuant to the
omnibus approval

| E2E Networks Limited | 26 |

so granted is placed before the Audit Committee for their review on a periodic basis. The policy on RPTs, as
approved by the Board, has been uploaded
on the Company’s website and can be accessed through the link:
https://global-uploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27895_Policy-on-Related-Party-
Transactions.pdf

During the financial year 2022-23, there were no transactions with related parties which qualify as material
transactions under the applicable
provisions of the Act and the SEBI LODR Regulations.
```

### Chunk 37

_text · pages 29–29 · 196 words · 291 tokens_

```text
## DIRECTORS’ RESPONSIBILITY STATEMENT
Pursuant to Section 134(5) of the Act, your directors state that:

1. In the preparation of the annual accounts, the applicable accounting standards have been followed along
with proper explanation relating to
material departures, if any;

2. Appropriate accounting policies have been selected and applied consistently and judgements and estimates
that are reasonable and prudent
have been made, so as to give a true and fair view of the state of affairs of the Company as of March 31,
2023, and of the profit of the Company
for the year ended March 31, 2023;

3. Proper and sufficient care has been taken for the maintenance of adequate accounting records in accordance
with the provisions of the
Companies Act, 2013 for safeguarding the assets of the Company and for preventing and detecting fraud and
other irregularities;

4. The annual accounts have been prepared on a going concern basis;

5. Proper internal financial controls were followed by the Company and such internal financial controls are
adequate and were operating
effectively;

6. Proper systems are devised to ensure compliance with the provisions of all applicable laws and that such
systems were adequate and operating
effectively.
```

### Chunk 38

_text · pages 29–30 · 155 words · 306 tokens_

```text
## POLICY AGAINST SEXUAL HARASSMENT
The Company has in place a Policy for Prevention, Prohibition and Redressal of Sexual Harassment of Women at
Workplace in line with the
requirements of the Sexual Harassment of Women at the Work Place (Prevention, Prohibition and Redressal) Act,
2013 and Rules made there under.

| E2E Networks Limited | 27 |

An Internal Compliant Committee is in place as per the requirements of the said Act to redress complaints
received regarding sexual harassment. All
employees are covered under this policy.

There was no case reported with the Committee during the period under review.

Further, your company ensures that there is a healthy and safe environment for every woman employee at the
workplace and makes the necessary
policies for a safe and secure environment for women employees.

The said policy of the Company has been uploaded on the website of the Company and can be assessed through the
link https://globaluploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27a38_Sexual-Harassment-of-
Women-at-Workplace.pdf
```

### Chunk 39

_text · pages 30–30 · 202 words · 378 tokens_

```text
## DEMATERIALISATION OF EQUITY SHARES
The Company's Equity Shares are admitted in the system of Dematerialization by both the Depositories namely,
NSDL and CDSL. Equity Shares of the
Company are compulsorily tradable in electronic form. As on March 31, 2023, 97.76% of the Equity Shares were
held in electronic form and only
2.24% Equity Shares were held in physical form. The Member(s) holding shares in physical form are advised to
avail of the facility of dematerialization.

## ANY PROCEEDINGS UNDER THE INSOLVENCY AND BANKRUPTCY CODE, 2016
During the financial year under review, the Company has complied with applicable Secretarial Standards on
Board and General Meetings specified by
the Institute of Company Secretaries of India pursuant to Section 118 of the Act.

## ANY PROCEEDINGS UNDER THE INSOLVENCY AND BANKRUPTCY CODE, 2016

There are no proceedings initiated/pending against your Company under the Insolvency and Bankruptcy Code, 2016
which materially impact the
business of the Company.

VALUATION FOR ONE TIME SETTLEMENT OR WHILE TAKING THE LOAN FROM THE BANKS OR FINANCIAL INSTITUTIONS

There were no instances where your Company required the valuation for one time settlement or while taking the
loan from the Banks or Financial
institutions.

| E2E Networks Limited | 28 |
```

### Chunk 40

_text · pages 31–32 · 225 words · 421 tokens_

```text
## HUMAN RESOURCE MANAGEMENT
Your company views its workforce as a valuable asset and is committed to nurturing, developing, and retaining
talent to meet present and future
business needs. During year, the human resources department, in collaboration with management, actively
pursued various initiatives to address the
challenges of employee retention and recruitment. These initiatives include regular management discussions,
acknowledgement of employees’
accomplishments, offering role enhancements with larger accountabilities, and maintaining transparency with
them. This has helped the Company in
building their confidence and trust in the Company. We continue to provide a conducive work environment and
opportunities for development of
employees.

ACKNOWLEDGEMENT

Your Directors wish to convey their gratitude and place on record their appreciation for the valuable support
and cooperation of the Company’s
employees, vendors, bankers, government and other statutory authorities, customers and shareholders, who have
reposed their continued trust and
confidence in the Company.

On behalf of the Board of Directors

Sd/-
Place: New Delhi Sd/- Srishti Baweja
Tarun Dua Whole Time Director

| Date: August 28, 2023 | Managing Director | DIN:08057000 | DIN: 02696789 |
| E2E Networks Limited | 29 |

Annexure -A

Secretarial Audit Report

For the Financial period ended 31st March 2023

[Pursuant to Section 204(1) of the Companies Act, 2013 and Rule No. 9 of the Companies (Appointment and
Remuneration of Managerial Personnel)
Rules, 2014]

The Members,
```

### Chunk 41

_text · pages 32–32 · 251 words · 435 tokens_

```text
## CIN: L72900DL2009PLC341980
Awfis, First Floor, A-24/9,
Mohan Cooperative Industrial Estate, Mathura Road, New Delhi – 110044

## CIN: L72900DL2009PLC341980

We have conducted secretarial audit of the compliance of applicable statutory provisions and adherence to good
corporate practices by M/s. E2E
Networks Limited (hereinafter called “the Company”). The secretarial audit was conducted in a manner that
provided us a reasonable basis for
evaluating the corporate conducts/statutory compliances and expressing our opinion thereon.

Based on our verification of the E2E Networks Limited’s books, papers, minute books, forms and returns filed
and other records maintained by the
Company and also the information provided by the Company, its officers and authorized representatives during
the conduct of secretarial audit, we
hereby report that in our opinion, the Company has, during the audit period covering the financial period
ended on 31st March 2023 (Commencing
from April 1, 2022 to March 31, 2023), complied with the statutory provisions listed hereunder and also that
the Company has proper Board processes
and compliance mechanism in place to the extent based on the management representation letter/ confirmation
received from the management, in
the manner and subject to the reporting made hereinafter. The members are requested to read this report along
with our letter dated August 09, 2023
annexed to this report as Annexure – A.

1. We have examined the books, papers, minute books, forms and returns filed and other records maintained by
the Company for the financial period
ended on March 31, 2023 according to the applicable provisions of:
```

### Chunk 42

_table · pages 32–33 · 145 words · 269 tokens · table continues across pages 32-33_

```text
## CIN: L72900DL2009PLC341980
1. We have examined the books, papers, minute books, forms and returns filed and other records maintained by the Company for the financial period
ended on March 31, 2023 according to the applicable provisions of:

| i. | The Companies Act, 2013 (the Act) and the rules made thereunder; |
| E2E Networks Limited | 30 |
| ii. | The Securities Contracts (Regulation) Act, 1956 (‘SCRA’) and the rules made thereunder; |
| iii. | The Depositories Act, 1996 and the regulations and bye–laws framed thereunder; |
| iv. | Foreign Exchange Management Act, 1999 and the rules and regulations made thereunder to the extent of Foreign Direct Investment, Overseas |
| Direct Investment and External Commercial Borrowings; |
| v. | The following Regulations and Guidelines prescribed under the Securities and Exchange Board of India Act, 1992 (‘SEBI Act): |
```

### Chunk 43

_text · pages 33–34 · 392 words · 714 tokens_

```text
## CIN: L72900DL2009PLC341980
a. The Securities and Exchange Board of India (Substantial Acquisition of Shares and Takeovers) Regulations,
2011;

b. The Securities and Exchange Board of India (Prohibition of Insider Trading) Regulations, 2015;
c. The Securities and Exchange Board of India (Issue of Capital and Disclosure Requirements) Regulations,
2018;

d. The Securities and Exchange Board of India (Share Based Employee Benefits and Sweat Equity) Regulations,
2021;

e. The Securities and Exchange Board of India (Issue and Listing of Non-Convertible Securities) Regulations,
2021; (Not applicable to the
Company during the Audit period);

f. The Securities and Exchange Board of India (Buyback of Securities) Regulations, 2018 (Not applicable to the
Company during the Audit
period);

g. The Securities and Exchange Board of India (Registrars to an issue and share transfer agents) Regulations,
1993 regarding the Companies
Act and dealing with clients (Not applicable as the Company is not registered as Registrar to an Issue and
Share Transfer Agent during the
audit period);

h. The Securities and Exchange Board of India (Delisting of Equity Shares) Regulations, 2009 (Not applicable
to the Company during the Audit
period); and

i. The Securities and Exchange Board of India (Listing Obligations and Disclosure Requirements) Regulations,
2015.

2. We further report that, having regard to the compliance system prevailing in the Company and on examination
of the relevant documents, records,
management confirmations in pursuance thereof, on test check basis, the Company has complied with Information
Technology Act, 2000 and the
rules made there under, applicable specifically to the Company, during the financial year 01st April 2022 to
31st March 2023.

| E2E Networks Limited | 31 |

3. We have also relied upon compliance reports from the management, the representation made by the Company and
its officers for systems and
mechanism framed by the Company to ensure the compliance with general laws like Labour Laws, Employees
Provident Funds Act, Employees
State Insurance Act, as applicable to the Company.

4. We have also examined compliance with the applicable clauses of the following:

i. Secretarial Standards issued by the Institute of Company Secretaries of India, with respect to Board and
General Meetings (hereinafter referred
as ‘Secretarial Standards’). We noted that the Company is regular in complying with the Secretarial Standards;
and

| ii. | The Securities and Exchange Board of India (Listing Obligations and Disclosure Requirements) Regulations, 2015 (hereinafter referred as |
```

### Chunk 44

_text · pages 34–35 · 404 words · 595 tokens · starts with overlap_

```text
## CIN: L72900DL2009PLC341980
We noted that the Company is regular in complying with the Secretarial Standards; and

| ii. | The Securities and Exchange Board of India (Listing Obligations and Disclosure Requirements) Regulations, 2015 (hereinafter referred as |

‘SEBI LODR 2015’) and the Listing Agreements entered into by the Company with the National Stock Exchange of
India Limited (hereinafter
referred as ‘NSE’).

5. During the period under review, to the best of our knowledge and belief and according to the information
and explanations given to us, the
Company has complied with the provisions of the Acts, Rules, Regulations and Agreements mentioned above.
6. We further report that compliance of applicable financial laws including Direct and Indirect Tax Laws by
the Company has not been reviewed in
this audit since the same has been subject to review by the Statutory Auditors and other designated
professionals.
7. We further report that:

i. The Board of Directors of the Company is duly constituted with proper balance of Executive Directors,
non–Executive Directors and
Independent Directors. The Board also has a woman director. There is no change in the composition of the Board
of Directors that took place
during the period under review however, re-appointments of two Independent Directors were carried out in
compliance with the provisions
of the Act.

ii. Adequate notice is given to all directors to schedule the Board Meetings. Notice of Board meetings was
sent at least seven days in advance and
where any Board Meeting was held on shorter notice the same was conducted in compliance with the Act. A system
exists for directors to seek
and obtain further information and clarifications on the agenda items before the meetings and for their
meaningful participation at the
meetings.

iii. Decisions of Board/Committee were carried through majority. We are informed that there were no dissenting
members’ views on any of the
matters during the year that were required to be captured and recorded as part of the minutes.

iv. There are adequate systems and processes in the Company commensurate with the size and operations of the
Company to monitor and ensure
compliance with applicable laws, rules, regulations and guidelines.

| E2E Networks Limited | 32 |

v. We further report that during the period covered under the audit, the Company has made the following
specific action having a major bearing
on the Company’s affairs in pursuance of the above referred laws, rules, regulations, standards, guidelines
etc.:
```

### Chunk 45

_text · pages 35–35 · 107 words · 189 tokens · starts with overlap_

```text
## CIN: L72900DL2009PLC341980
| E2E Networks Limited | 32 |

v. We further report that during the period covered under the audit, the Company has made the following
specific action having a major bearing
on the Company’s affairs in pursuance of the above referred laws, rules, regulations, standards, guidelines
etc.:

- On an application filed by the Company for migration of Equity Shares of the Company from ‘SME Emerge
Platform’ to ‘Capital Market Segment
(Main Board)’, the NSE on April 08, 2022 approved Company’s application for migration and listed the Equity
Shares of the Company on ‘Capital
Market Segment (Main Board)’.

For MAKS & Co.,
Company Secretaries
```

### Chunk 46

_text · pages 35–36 · 354 words · 673 tokens_

```text
## UDIN: F009719E000768862
Sd/-
Ankush Agarwal
Partner
Membership No.: F9719
COP No.: 14486
Peer Review Certificate No.: 2064/2022

## UDIN: F009719E000768862

Date: August 09, 2023
Place: Noida, U.P.

| E2E Networks Limited | 33 |

Annexure –A to Secretarial Audit Report dated August 09, 2023

The Members,
Awfis, First Floor, A-24/9,
Mohan Cooperative Industrial Estate, Mathura Road, New Delhi – 110 044

## [CIN: L72900DL2009PLC341980]
Our Secretarial Audit Report dated August 09, 2023, is to be read with this letter.

1. The compliance of provisions of all laws, rules, regulations and standards applicable to M/s. E2E Networks
Limited (‘the Company’) is the
responsibility of the management of the Company. Our examination was limited to the verification of records
and procedures on test check basis
for the purpose of issue of the Secretarial Audit Report.
2. Maintenance of secretarial and other records of applicable laws is the responsibility of the management of
the Company. Our responsibility is to
issue Secretarial Audit Report, based on the audit of the relevant records maintained and furnished to us by
the Company, along with explanations
where so required.
3. We have followed the audit practices and processes as were appropriate to obtain reasonable assurance about
the correctness of the contents of
the secretarial records. The verification was done on test basis to ensure that correct facts are reflected in
secretarial records. We believe that the
processes and practices we followed provide a reasonable basis for the purpose of issue of the Secretarial
Audit Report.
4. We have not verified the correctness and appropriateness of financial records and books of accounts of the
Company as it is taken care in the
statutory audit.
5. We have obtained the management’s representation about the compliance of laws, rules and regulations and
happening of events, wherever
required.
6. This Secretarial Audit report is neither an assurance as to the future viability of the Company nor of the
efficacy or effectiveness with which the
management has conducted the affairs of the Company.

For MAKS & Co., Company Secretaries [FRN P2018UP067700]
Ankush Agarwal
Partner
Membership No.: F9719 COP No.: 14486
Peer Review Certificate No.: 2064/2022
```

### Chunk 47

_text · pages 36–38 · 283 words · 580 tokens_

```text
## UDIN: F009719E000768862
Place: Noida, U.P

| E2E Networks Limited | 34 |

Annexure-B
Annual Report on Corporate Social Responsibility (CSR) Activities for the Financial Year ending March 31, 2023

[Pursuant to Section 135 of the Companies Act, 2013 read with the Companies (Corporate Social Responsibility
Policy) Rules, 2014, as amended]

1. Brief Outline on the Corporate Social Responsibility (‘CSR’) Policy of the Company:

As per CSR policy of the Company, following shall be the focus areas for its CSR initiatives: -

i. Education and Skill Development: To promote education and enhance vocational skills especially among
children, women and differently abled
persons.

ii. Health Care: To promote health care including rehabilitation facilities.

iii. Poverty and Malnutrition: To fight against hunger, poverty and malnutrition.

iv. Rural Development: To facilitate rural development and slum area development.

However, the CSR Committee shall have authority to decide to carry out any other CSR activities within the
purview of permissible activities under
the Companies Act, 2013 from time to time.

The Corporate Social Responsibility Policy (CSR Policy) adopted by Board is available on the website of the
Company and is accessible through the
https://global-uploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27a66_Corporate-Social-
Responsibility-Policy.pdfThe Company was not required to spend money under CSR for financial year ended
2022-23 as prescribed under Section 135 of the Act since the
Company incurred an average net loss of Rs. 175.64 Lakhs for previous three financial years.

| E2E Networks Limited | 35 |

2. Composition of CSR Committee.

The composition of Corporate Social Responsibility Committee of the Company as on March 31, 2023 is as
follows:-

S. Name of Member Designation Number of meetings of CSR Number of meetings of CSR Committee
No. Committee held during the attended during the year
```

### Chunk 48

_table · pages 38–38 · 145 words · 249 tokens_

```text
## UDIN: F009719E000768862
Company incurred an average net loss of Rs. 175.64 Lakhs for previous three financial years.
| E2E Networks Limited | 35 |
2. Composition of CSR Committee.
The composition of Corporate Social Responsibility Committee of the Company as on March 31, 2023 is as follows:-
S. Name of Member Designation Number of meetings of CSR Number of meetings of CSR Committee
No. Committee held during the attended during the year

| 1 | Mrs. Srishti Baweja | Whole Time Director – | 1 | 1 |
| Chairman |
| 2 | Mr. Gaurav Munjal | Independent Director – | 1 | 1 |
| Member |
| 3 | Mr. Varun Pratap Rajda | Independent Director – | 1 | 1 |
| Member |
| 4 | Mr. Naman K. Sarawagi | Independent Director – | 1 | 1 |
```

### Chunk 49

_text · pages 38–40 · 395 words · 783 tokens_

```text
## UDIN: F009719E000768862
Member

3. The web-link where Composition of CSR committee, CSR Policy and CSR projects approved by the board are
disclosed on the website of
the company:

The composition of the CSR Committee is available on the website at link
https://www.e2enetworks.com/investors/board-of-directors

The CSR Policy of the Company is available on the website at linkhttps://global-
uploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27a66_Corporate-Social-Responsibility-
Policy.pdfThe details of CSR Projects as approved by the Board are available on the website at link-
https://www.e2enetworks.com/investors/
corporate-governance/

4. The details of Impact assessment of CSR projects carried out in pursuance of sub-rule (3) of rule 8 of the
Companies (Corporate Social
Responsibility Policy) Rules, 2014, if applicable: Not Applicable

| E2E Networks Limited | 36 |

| 5. | i. | Average net profit of the company as per sub-section (5) of section 135.: INR 175.64 Lakhs |

ii. Two percent of average net profit of the company as per sub-section (5) of section 135: Nil
iii. Surplus arising out of the CSR Projects or programmes or activities of the previous financial years. NA
iv. Amount required to be set-off for the financial year, if any. Nil
v. Total CSR obligation for the financial year [(b)+(c)-(d)]. Nil

6. Amount Spent on CSR Project (both Ongoing Project and other than Ongoing Project)

i. Details of CSR amount spent against ongoing projects for the financial year:

Sl. Name Item from Local Location of Project Amount Amount Amount Mode of Mode of
No. of the the list of area the project duration allocated spent in transferred to impleme implementation
Project activities (Yes/No) (in for the the Unspent CSR ntation - -Through
in years) project current Account for the Direct implementing
schedule (in Rs. financial project as per (Yes/No) agency.

| VII | Lakhs) | year (in | Section 135(6) | State | District | Na | CSR |

to the Act Rs. (in Rs. Lakhs) me registratio
Lakhs) n number

Not Applicable

| E2E Networks Limited | 37 |

ii. Details of CSR amount spent against other than ongoing projects for the financial year:

Sl. Name Item from Local Location of Amount Spent for the Mode of Mode of
No. of the the list of area the project project implementation - implementation
Project activities in (Yes/No) Direct (Yes/No) -Through
schedule VII implementing
to the Act agency
State District Name CSR registration
number

Not Applicable

iii. Amount spent in Administrative Overheads- Nil
```

### Chunk 50

_text · pages 40–41 · 340 words · 606 tokens · starts with overlap_

```text
## UDIN: F009719E000768862
of the the list of area the project project implementation - implementation
Project activities in (Yes/No) Direct (Yes/No) -Through
schedule VII implementing
to the Act agency
State District Name CSR registration
number

Not Applicable

iii. Amount spent in Administrative Overheads- Nil

iv. Amount spent on Impact Assessment, if applicable- Not Applicable

| v. | Total amount spent for the Financial Year (6a+6b+6c)- Nil |

vi. CSR amount spent or unspent for the Financial Year:

Total Amount Spent for the Financial Amount Unspent (in Rs.)
Year
(in Rs.) Total Amount transferred to Amount transferred to any fund specified under
Unspent CSR Account as per subsection (6) of section Schedule VII as per second proviso to sub-section

| 135. | (5) |

of section 135.

Amount. Date of transfer. Name of the Amount. Date of transfer

NA NA NA NA NA NA

| E2E Networks Limited | 38 |

vii. Excess amount for set-off, if any:

Sl. No. Particular Amount
(in Rs.)

| 1 | Two percent of average net profit of the company as per sub-section (5) of section | Nil |

2 Total amount spent for the Financial Year Nil

3 Excess amount spent for the Financial Year [(ii)-(i)] N.A

4 Surplus arising out of the CSR projects or programmes or activities of the previous Financial Years, if any
N.A

5 Amount available for set off in succeeding Financial Years [(iii)-(iv)] N.A

7. (a) Details of Unspent CSR amount for the preceding three financial years:

Preceding Amount transferred Balance Amount spent Amount transferred to any fund Amount remaining
Sl. Financial to Unspent CSR Amount in Unspent in the reporting specified under Schedule VII as to be spent in

| No. | Year | Account under | CSR Account | Financial Year | per section 135(6), if any | succeeding |

section 135 (6) under subsection (in Rs.) financial years.

| (in Rs.) | (6) of | (in Rs.) |

section 135

| (in Rs.) |
| Name of the Amount Date of |

Fund (in Rs). transfer
```

### Chunk 51

_table · pages 41–41 · 126 words · 238 tokens_

```text
## UDIN: F009719E000768862
| No. | Year | Account under | CSR Account | Financial Year | per section 135(6), if any | succeeding |
section 135 (6) under subsection (in Rs.) financial years.
| (in Rs.) | (6) of | (in Rs.) |
section 135
| (in Rs.) |
| Name of the Amount Date of |
Fund (in Rs). transfer

| 1 | 2021-2022 | NA | Nil | Nil | NA | Nil | NA | Nil |
| 2 | 2020-2021 | NA | Nil | Nil | NA | Nil | NA | Nil |
| 3 | 2019-2020 | NA | Nil | Nil | NA | Nil | NA | Nil |
| E2E Networks Limited | 39 |
```

### Chunk 52

_text · pages 42–43 · 276 words · 495 tokens_

```text
## UDIN: F009719E000768862
8. Whether any capital assets have been created or acquired through Corporate Social Responsibility amount
spent in the Financial Year:

(i) Yes (ii) No ✔

If Yes, enter the number of Capital assets created/ acquired NA

Furnish the details relating to such asset(s) so created or acquired through Corporate Social Responsibility
amount spent in the Financial

S. Short particulars of the property or Pincode of the Date of Amount of Details of entity/ Authority/
beneficiary
No. asset(s) [including complete Property or creation CSR amount of the registered owner
address and location of the asset(s) spent CSR Registration Name Registered
property] Number, if Address
applicable
NA NA NA NA NA NA NA NA

(All the fields should be captured as appearing in the revenue record, flat no, house no, Municipal Office
/Municipal Corporation/ Gram panchayat are
to be specified and also the area of the immovable property as well as boundaries).

9. Specify the reason(s), if the company has failed to spend two per cent of the average net profit as per
subsection (5) of section 135: Not
Applicable

For E2E Networks Limited

Sd/- Sd/-
Srishti Baweja Tarun Dua
CSR Committee Chairman Managing Director
Date: August 28, 2023
Place: New Delhi

| E2E Networks Limited | 40 |

Annexure - C

Disclosures pursuant to Section 197(12) of Companies Act, 2013 and Rule 5(1) of Companies (Appointment and
Remuneration of
Managerial Personnel) Rules, 2014

1. The ratio of the Remuneration of each director to the median remuneration of the employees of the Company
for the financial year:

S. Name of the Director Category Ratio of the Remuneration to the median remuneration of the
No. Employees
```

### Chunk 53

_table · pages 43–43 · 133 words · 277 tokens_

```text
## UDIN: F009719E000768862
Fund (in Rs). transfer
1. The ratio of the Remuneration of each director to the median remuneration of the employees of the Company for the financial year:
S. Name of the Director Category Ratio of the Remuneration to the median remuneration of the
No. Employees

| 1. | Mr. Tarun Dua | Managing Director | 11.69 |
| 2. | Mrs. Srishti Baweja | Whole-time Director | 11.38 |
| 3. | Mr. Varun Pratap Rajda* | Non-Executive and Independent | 0.08 |
| Director |
| 4. | Mr. Gaurav Munjal* | Non-Executive and Independent | 0.12 |
| Director |
| 5. | Mr. Naman Kailashprasad | Non-Executive and Independent | 0.10 |
| Sarawagi* Director |
| Mr. Aditya Bhushan* | Non-Executive and Independent | 0.12 |
```

### Chunk 54

_text · pages 43–45 · 403 words · 749 tokens_

```text
## UDIN: F009719E000768862
Director 6.

* Independent Directors are being paid only sitting fees for attending the Board/Committee Meetings.

| E2E Networks Limited | 41 |

2. The percentage increase in remuneration of each Director, Chief Financial Officer, Chief Executive Officer,
Company Secretary or
Manager, if any, in the financial year:

S. Name of the Director / CFO / CS Category % Increase in remuneration in the
No. /Manager financial year

| 1. | D. Mr. Tarun Dua | Managing Director | 0% |
| 2. | Mrs. Srishti Baweja | Whole- time Director | 7.35% |

3. Mr. Varun Pratap Rajda* Non-Executive and Independent Director N.A.

4. Mr. Gaurav Munjal* Non-Executive and Independent Director N.A.

5. Mr. Naman Kailashprasad Sarawagi* Non-Executive and Independent Director N.A.

6. Mr. Aditya Bhushan* Non-Executive and Independent Director N.A.

| 7. | Mrs. Richa Gupta | Company Secretary (w.e.f 7th Feb 2023) | N.A |

8. Mrs. Megha Raheja Chief Financial Officer NA

* Since Independent and Non-Executive Directors received no remuneration, except the sitting fees for
attending Board / Committee Meetings, the
required details are not applicable.

Note: The percentage increase in remuneration is provided only for those directors and KMP who have drawn
remuneration from the Company for
full FY 21-22 and FY 22-23.

| E2E Networks Limited | 42 |

3. Percentage Increase in the median remuneration of employees in the financial year

The percentage increase in the median remuneration of employees in the financial year was -4.58%.

4. Number of Permanent Employees on the rolls of company

Number of Permanent Employees on the rolls of the Company as of March 31, 2023 are 110.

5. Average percentiles increase already made in the salaries of employees other than the managerial personnel
in the last financial year
and its comparison with the percentile increase in managerial remuneration and justification thereof and point
out if there are any
exceptional circumstances for increase in the managerial remuneration:

The average increase in remuneration for employees is 24.73%. The average increase in overall managerial
remuneration is 3.67%. The increase
in remuneration is done as per the policy of the Company and based on economic factors mainly on account of
inflation, performance rise,
availability of the required talent, the industry comparatives etc.

6. Affirmation that remuneration is as per the remuneration policy of the company:

The Company affirms that the remuneration is as per the remuneration policy of the Company.
```

### Chunk 55

_text · pages 45–47 · 423 words · 794 tokens · starts with overlap_

```text
## UDIN: F009719E000768862
6. Affirmation that remuneration is as per the remuneration policy of the company:

The Company affirms that the remuneration is as per the remuneration policy of the Company.

On behalf of the Board of Directors

Sd/-
Place: New Delhi Sd/- Srishti Baweja
Tarun Dua Whole Time Director

| Date: August 28, 2023 | Managing Director | DIN:08057000 | DIN: 02696789 |
| E2E Networks Limited | 43 |

Annexure - D
Form No. AOC-2
(Pursuant to clause (h) of sub-section (3) of section 134 of the Companies Act, 2013 and Rule 8(2) of the
Companies (Accounts) Rules, 2014)

Form for disclosure of particulars of contracts or arrangements entered by the company with related parties
referred to in sub-section (1)
of section 188 of the Companies Act, 2013 including certain arm’s length transactions under third proviso
thereto:

1. Details of contracts or arrangements or transactions not at arm’s length basis: The Company has not entered
any
contract/arrangement/transaction with its related parties which is not in ordinary course of business or at
arm’s length during FY 22-23.

i. Name(s) of the related party and nature of relationship – Not Applicable

ii. Nature of contracts/arrangements/transactions - Not Applicable

iii. Duration of the contracts / arrangements/transactions - Not Applicable

iv. Salient terms of the contracts or arrangements or transactions including the value, if any - Not
Applicable

v. Justification for entering such contracts or arrangements or transactions - Not Applicable

vi. Date(s) of approval by the Board – Not Applicable

vii. Amount paid as advances, if any: - Not Applicable

| viii. | Date on which the special resolution was passed in general meeting as required under first proviso to section 188 – Not Applicable |

2. Details of material contracts or arrangement or transactions at arm’s length basis: During the financial
year 2022-23, there were no
transactions with related parties which qualify as material transactions under the applicable provisions of
the Companies Act, 2013 and SEBI (LODR)
Regulations, 2015.

i. Name(s) of the related party and nature of relationship – Not Applicable

ii. Nature of contracts/arrangements/transactions – Not Applicable

| E2E Networks Limited | 44 |

iii. Duration of the contracts / arrangements/transactions – Not Applicable

iv. Salient terms of the contracts or arrangements or transactions including the value, if any: Not Applicable

v. Date(s) of approval by the Board, if any: - Not Applicable

vi. Amount paid as advances, if any: - Not Applicable.

On behalf of the Board of Directors

Place: New Delhi Sd/- Srishti Baweja
Tarun Dua Whole Time Director
```

### Chunk 56

_text · pages 47–48 · 161 words · 293 tokens · starts with overlap_

```text
## MANAGEMENT DISCUSSION AND ANALYSIS REPORT
Date(s) of approval by the Board, if any: - Not Applicable

vi. Amount paid as advances, if any: - Not Applicable. On behalf of the Board of Directors

Place: New Delhi Sd/- Srishti Baweja
Tarun Dua Whole Time Director

| Date: August 28, 2023 | Managing Director | DIN:08057000 | DIN: 02696789 |
| E2E Networks Limited | 45 |

## MANAGEMENT DISCUSSION AND ANALYSIS REPORT

Disclaimer: Certain Statements made herein describing the Company’s expectations or predictions are “forward
looking statements”. The Company’s
results, performance or achievements can significantly differ materially from those projected via such
statements. Important factors that could make a
difference to the Company’s operations include, among others, economic conditions affecting demand/supply,
changes in government regulations, tax
regimes, economic developments and other incidental factors. The Company assumes no responsibility in respect
of forward- looking statements that may
be amended or modified in future on the basis of subsequent developments, information or events.
```

### Chunk 57

_text · pages 48–48 · 212 words · 346 tokens_

```text
## INDUSTRY STRUCTURE AND DEVELOPMENTS
IAAS public cloud market continues to grow robustly in India. As per Statista.com
https://www.statista.com/outlook/tmo/
public-cloud/infrastructure-as-a-service/india the IAAS revenue in India is expected to be close to 2.9
billion USD and IAAS Revenue in India is
expected to show an annual growth rate (CAGR 2023-2027) of 24.21%, resulting in a market volume of US$7.0bn by
2027.

## OUR BUSINESS, OUTLOOK AND STRATEGY
Given the projections of the vast size of the Indian IAAS market by multiple credible industry reports your
company intends to follow an aggressive
growth strategy of investing massively into Cloud Infrastructure build out with increased capabilities from
the perspective of the maximum size of
workloads that can be deployed on its Cloud Platform. In an environment of highly competitive intensity, it is
important to establish trust of the
customers deploying their workloads in production with E2E Cloud. The customers should be able to try out the
platform at production scale in the
Proof-of-Concept stage of the relationship to allow them to experience the full scope of capabilities of E2E
Cloud Platform. The size of market dictates
that we aggressively rely on debt apart from internal cash generation to build out capacity based on the size
of the opportunity while continuing to
build a stable business.
```

### Chunk 58

_text · pages 48–49 · 224 words · 359 tokens_

```text
## OPPORTUNITIES AND THREATS
OPPORTUNITIES

As per the economic Potential of Generative AI - June, 2023, McKinsey, globally, across 63 use cases,
generative AI has the potential to generate $2.6
trillion to $4.4 trillion in value across industries.

Generative AI Growth Report - June, 2023, Bloomberg.

The generative AI market could grow to $1.3 trillion in 10 years, impacting numerous sectors. Generative AI
market to grow at a forecasted CAGR of

| E2E Networks Limited | 46 |

Generative AI models like Large Language Models, Diffusion models, Multi-Modal models can generate not just
text/voice outcomes based on reasoning
but also generate images, videos and rich multimedia. These are bigger workloads using much larger Cloud GPU
compute clusters requiring newer
investment thesis, the significant expense required to use these clusters makes for a compelling argument in
favor of cutting down the cost of compute
by exploring Cloud Platforms outside of the traditional large hyperscalers. The barriers to entry exist for
simple large hardware deployment vendors
with experience in only CPU based private cloud platforms to compete directly with hyperscalers without having
invested in multiple cycles of
investment into software product design, high throughput network, server infrastructure and scale out storage
capabilities in production for live
customers. The AI/ML/DL/NLP/LLMs/Diffusion Open Source based technologies is a significantly large sized niche
that your company can grow into.

THREATS
```

### Chunk 59

_text · pages 49–49 · 207 words · 318 tokens · starts with overlap_

```text
## OPPORTUNITIES AND THREATS
The AI/ML/DL/NLP/LLMs/Diffusion Open Source based technologies is a significantly large sized niche that your
company can grow into. THREATS

1. Significantly fast-moving markets like AI/ML/NLP/LLMs throws significant challenges in terms of the effort
just required to keep up with the
daily new developments.
2. Change in government regulations or their implementation could disrupt the operations and adversely affect
the business and results of the
Company, due to which Company may incur increased costs.
3. Increased competition from Global as well as Local players may impact our customer acquisition and future
growth.
4. Significant increases in market prices of Computer equipment and other hardware, energy or 39
transportations, as well as supply disruptions,
could adversely affect our results of operations.
5. Changes in the monetary and fiscal policies of India, unanticipated turbulence in interest rates, foreign
exchange rates, changes in domestic
and foreign laws, regulations, and taxes.
6. Change in technology may render our current technology obsolete and require us to make substantial
investments which could affect the
Company finances and operations.
7. General Technology related risks like Disclosures of new vulnerabilities in CPUs, Risks of becoming victims
of Cyber Crime, accidental data
disclosure etc.
8. Access to and retention of highly skilled professionals.
```

### Chunk 60

_text · pages 49–50 · 164 words · 241 tokens_

```text
## RISKS AND CONCERNS
The Company's business activities fall within a single primary business segment. Accordingly, disclosures
under Ind AS -108 "Operating Segments”
are not required to be made.

## RISKS AND CONCERNS

The Company understands that it operates in a competitive and challenging environment and its business and
operations are subject to a variety of
risks and uncertainties like operational risks, financial risks, hazard related risks, market-related risks
and strategic risks amongst others.

| E2E Networks Limited | 47 |

The Company has a well-defined system in place to reduce its operational risks and has a Risk Management
Policy in place that helps in the
identification, assessment and monitoring of risks and helps to mitigate and manage the identified risks.

The Company strives to promote a proactive approach in risks reporting and management. This involves reviewing
operations of the organization,
identifying potential threats to the organization and the likelihood of their occurrence, and then taking
appropriate actions to address the most likely
threats.
```

### Chunk 61

_text · pages 50–50 · 254 words · 350 tokens_

```text
## INTERNAL CONTROL SYSTEMS AND THEIR ADEQUACY
The Company has the internal control systems in place, adequate for the size of the Company and the nature of
its business. The primary function of
our internal control systems is to ensure efficiency in business operations, safeguarding of company’s assets,
adherence to policies and procedures,
protecting and detecting errors and frauds, strict compliance with applicable laws and ensuring the
reliability of financial statements and reporting.

The Company has in place the internal financial controls for the various processes of the Company such as
Revenue reporting and recognition, Fixed
assets, Finance and accounts, Taxation, Treasury, HR & Payroll and Procurement etc. The internal control
systems adopted by the Company ensures
that all transactions are executed with proper authorisation, are recorded and reported correctly, and assets
are safeguarded and protected against
loss from unauthorised use. In addition, the compliance of corporate policies is duly monitored.

The internal audits carried out by the Internal Auditor of the Company and management reviews supplements the
process of internal financial control
framework. Internal Audits are conducted at regular intervals to assure the management of fair transactions,
as per set policies and processes. Efficacy
of internal control systems are tested periodically by Internal Auditors and internal control over financial
reporting is tested and certified by Statutory
Auditors.

The Company also has an Audit Committee to interact with the Statutory Auditors, Internal Auditors and
Management in dealing with matters within
its terms of reference including the matters relating to financial reporting and internal controls.
```

### Chunk 62

_text · pages 50–51 · 219 words · 317 tokens_

```text
## MATERIAL DEVELOPMENTS IN HUMAN RESOURCES AND INDUSTRIAL RELATIONS
We believe in investing in our people and giving them opportunities to realize their full potential. We also
believe in treating the organization as an
extended family and standing by each member in their hour of need.

Our Company values its relationship with its employees and ensures that each employee feels connected to the
Company’s objectives and shares the
Company’s broader vision to create stakeholders’ value. Our Human Resource Team, guided by the Top Management
relentlessly undertakes various

| E2E Networks Limited | 48 |

people-centric activities to keep all our employees engaged and provide them with suitable opportunities. E2E
believes in inspiring the employees to
their highest potential.

Recognition and appreciation at the workplace go a long way in motivating the employees to work even harder
and better. Our performance appraisal
systems have been designed to recognise and reward exceptional performers.

The Company has made rigorous efforts to ensure that employees can handle challenges of the future, while
staying abreast with the knowledge in
relation to their respective functional domain. It also focuses on providing opportunities to each employee to
grow and utilise their complete potential.

As on 31st March 2023, 110 employees are on the rolls of the Company. The industrial relations have remained
harmonious throughout the year.
```

### Chunk 63

_text · pages 51–51 · 23 words · 57 tokens_

```text
## FINANCIAL PERFORMANCE AND HIGHLIGHTS
The ϐinancial performance during the Financial Year 2022-23 has been summarized below: (Amount in INR Lakhs)

Particulars Standalone
```

### Chunk 64

_table · pages 51–51 · 175 words · 459 tokens_

```text
## FINANCIAL PERFORMANCE AND HIGHLIGHTS
The ϐinancial performance during the Financial Year 2022-23 has been summarized below: (Amount in INR Lakhs)
Particulars Standalone

| FY 2022-23 | FY 2021-22 |
| Revenue from operations | 6620.18 | 5187.34 |
| Total Expenditure other than finance cost and depreciation | 3313.96 | 2893.01 |
| Earnings before Interest, Tax and Depreciation (EBITDA) | 3306.22 | 2294.33 |
| Other Income | 76.01 | 35.51 |
| Depreciation | 2011.15 | 1782.64 |
| Finance Costs | 47.46 | 18.60 |
| Profit/(Loss) before tax (PBT) | 1323.62 | 528.60 |
| Current Tax | 314.80 | - |
| Deferred Tax | 17.83 | (116.50) |
| Net Profit/(Loss) for the Year (PAT) | 990.99 | 645.10 |
| Other Comprehensive Income | 25.54 | 487.89 |
| Total comprehensive income for the period/year | 1016.53 | 1132.99 |
| Basic EPS (in INR) | 6.85 | 4.46 |
| Diluted EPS (in INR) | 6.77 | 4.44 |
| E2E Networks Limited | 49 |
```

### Chunk 65

_text · pages 52–52 · 136 words · 269 tokens_

```text
## FINANCIAL PERFORMANCE AND HIGHLIGHTS
The Company has reported total revenue from operations of INR 6620.18 Lakhs during the FY 2022-23 as against
revenue of INR 5187.34 Lakhs
during the FY 2021-22 witnessing an increase of 27.62% in its revenue as compared to last financial year.
Further, the Company has witnessed an
increase in its operating margins from 44% in FY 21-22 to in FY 22-23.The Company has reported Net Profit
after tax amounting51%to INR 990.99 Lakhs during the FY 2022-23 as against Net Profit after tax of INR 645.10
Lakhs for the FY 2021-22.

In fiscal year 2023, we have witnessed the increase in recurring revenue and increase in our customer base. We
have created a strong leadership
pipeline to work with trained and motivated employees to continue to work towards increasing our customer
base.
```

### Chunk 66

_text · pages 52–52 · 155 words · 251 tokens_

```text
## BASIS OF PREPARATION OF FINANCIAL STATEMENTS
The standalone financial statements have been prepared in compliance with Indian Accounting Standards (“Ind
AS”), the provisions of the Companies
Act, 2013 (“the Companies Act”), as applicable and guidelines issued by the Securities and Exchange Board of
India (“SEBI”). The Ind AS are prescribed
under Section 133 of the Companies Act read with Rule 3 of the Companies (Indian Accounting Standards) Rules,
2015 and amendments issued
thereafter. The Management accepts the responsibility for the integrity and objectivity of these ﬁnancial
statements, as well as for various estimates
and judgements used therein. The estimates and judgements relating to the ﬁnancial statements have been made
on a prudent and reasonable basis,
so that the ﬁnancial statements reﬂect in a true and fair manner the form and substance of transactions, and
reasonably present the state of aﬀairs,
proﬁt/loss and cash ﬂows for the year.

| E2E Networks Limited | 50 |
```

### Chunk 67

_table · pages 53–53 · 69 words · 134 tokens_

```text
## RATIO ANALYSIS
| Ratio | FY | FY | % Change as | Remarks/Reason for change where change is + 25% or more as |
| 2022- | 2021- | compared to | compared to Previous FY |
| 23 | 22 | previous FY |
| Debtors Turnover/Trade | 181.77 | 224.71 | -19.11% | The Trade receivable turnover ratio has decreased due to increase in |
```

### Chunk 68

_text · pages 53–53 · 165 words · 299 tokens_

```text
## RATIO ANALYSIS
Receivable Turnover debtors balance as the revenue has increased during the year.
Ratio

Inventory Turnover N.A N.A N.A Since the Company does not have any inventory, the Inventory
Turnover Ratio is not applicable.

| Debt Service Coverage | 13.69 | 105.09 | -86.97% | The Debt service coverage ratio has decreased during the year due to |

ratio decline in current borrowings of the Company on account of debt
repayment.

| Interest Coverage Ratio | 0.01 | 0.01 | Nil | N.A |
| Current Ratio | 1.86:1 | 1.36:1 | 36.76 % | The Current Ratio has increased during the year on account of increase |

in cash and cash equivalents and other bank balances with a
corresponding decline in current borrowings of the Company on
account of debt repayment.

| Debt Equity Ratio | 0.12 | 0.05 | 118.05% | The Debt Equity ratio has increased during the year on account of |

increase in lease liability of the Company.
```

### Chunk 69

_table · pages 53–53 · 109 words · 202 tokens_

```text
## RATIO ANALYSIS
in cash and cash equivalents and other bank balances with a
corresponding decline in current borrowings of the Company on
account of debt repayment.
| Debt Equity Ratio | 0.12 | 0.05 | 118.05% | The Debt Equity ratio has increased during the year on account of |
increase in lease liability of the Company.

| Operating Profit Margin | 51.05% | 44.88% | 13.75% | The operating Profit Margin has improved due to increase in revenue. |
| (%) |
| Net Profit Margin (%) | 14.97% | 12.44% | 20.34% | The Net profit ratio has increased during the year on accounts of |
```

### Chunk 70

_text · pages 53–54 · 240 words · 395 tokens_

```text
## RATIO ANALYSIS
improvement in overall profitability of the Company on account of
increase in revenue and improved operating margin during the year.

| Return on Net Worth | 34.78 % | 18.97% | 83.34% | The return on capital employed has increased during the year on |

/Return on Capital account of increase in revenue and improvement in overall profitability
Employed (%) of the Company during the year.

| E2E Networks Limited | 51 |

## COMPANY’S PHILOSOPHY ON CODE OF GOVERNANCE
E2E’s philosophy on Corporate Governance aims to achieve long term viability of the business by taking into
consideration the customers’ satisfaction
in terms of quality and cordial relationship with Shareholders. Corporate Governance is a continuous process
that aims to align interest of the Company
with its Shareholders and other Stakeholders. The primary characteristics of Corporate Governance are
transparency, independence, accountability,
fairness and responsibility. The Company has a strong legacy of fair, transparent and ethical governance
practices and compliance with statutory and
legal requirements. The Company has formulated, inter-alia, various policy documents and introduced best
practices of governance like Code of
Conduct, Prohibition of Insider Trading Policy, Whistle Blower Policy etc.
The Company’s Policies on Corporate Governance and Compliance thereof in respect of specific areas for the
year ended March 31, 2023, as per the
format prescribed by SEBI (LODR) Regulations, 2015 (“the Listing Regulations”) are set out below for the
information of the shareholders of the
Company.
```

### Chunk 71

_text · pages 54–54 · 122 words · 180 tokens_

```text
## BOARD STRUCTURE
The Board comprises of eminent persons with high credentials of considerable professional experience and
expertise, who effectively contribute to
the Company’s growth and policy formulation decisions. The composition of Board of Directors of the Company is
in conformity with the requirements
of Regulation 17 of Listing Regulations as well as provisions of the Companies Act, 2013 (“the Act”) and the
Articles of Association of the Company and
all other applicable laws and in accordance with best practices. The Chairperson of the Board of the Company
is a Promoter Executive Director.

The category wise composition of Board of Directors under Regulation 17 of SEBI Listing Regulations as on
March 31, 2023 is as under:

S. No. Category No. of Directors
```

### Chunk 72

_table · pages 54–54 · 64 words · 107 tokens_

```text
## BOARD STRUCTURE
The category wise composition of Board of Directors under Regulation 17 of SEBI Listing Regulations as on March 31, 2023 is as under:
S. No. Category No. of Directors

| 1 | Executive Director | 2 |
| 2 | Non-Executive, Independent Director | 4 |
| 3 | Other Non- Executive Director | 0 |
| Total | 6 |
```

### Chunk 73

_text · pages 54–55 · 75 words · 130 tokens_

```text
## KEY INFORMATION OF DIRECTORS
None of the Non-Executive Directors are and were responsible for the day-to-day affairs of the Company during
the year under review.

| E2E Networks Limited | 52 |

## KEY INFORMATION OF DIRECTORS

The details relating to composition and category of Directors as on March 31, 2023 are as follows:

| Name of the Director | DIN | Designation/ | Age | Shareholding as on 31st March 2023 |

Category
```

### Chunk 74

_table · pages 55–55 · 171 words · 352 tokens_

```text
## KEY INFORMATION OF DIRECTORS
| E2E Networks Limited | 52 |
## KEY INFORMATION OF DIRECTORS
The details relating to composition and category of Directors as on March 31, 2023 are as follows:
| Name of the Director | DIN | Designation/ | Age | Shareholding as on 31st March 2023 |
Category

| Mr. Tarun Dua* | 02696789 | Managing Director | 43 | 80,60,695 |
| Mrs. Srishti Baweja | 08057000 | Whole Time Director | 40 | 0 |
| Mr. Gaurav Munjal* | 02363421 | Non- Executive and Independent Director | 42 | 0 |
| Mr. Varun Pratap Rajda* | 07468016 | Non- Executive and Independent Director | 36 | 0 |
| Mr. Naman K. Sarawagi | 05295642 | Non- Executive and Independent Director | 36 | 10,500 |
| Mr. Aditya Bhushan | 01148272 | Non- Executive and Independent Director | 47 | 0 |
| * | Reappointed as Managing Director w.e.f. January 31, 2023 for a period of 3 years. |
```

### Chunk 75

_text · pages 55–56 · 169 words · 320 tokens_

```text
## KEY INFORMATION OF DIRECTORS
Reappointed as Whole Time Director w.e.f. January 31, 2023, for a period of 3 years.
* Re-appointed as Non-Executive Independent Director w.e.f. February 9, 2023, for a second term of 5
consecutive years.

| E2E Networks Limited | 53 |

INFORMATION OF CHAIRMANSHIP/DIRECTORSHIP AND POSITION HELD IN COMMITTEES OF OTHER COMPANIES AS ON 31ST MARCH
2023:

The details relating to directorships held by Directors in other companies and their membership and
chairpersonship in various Committees
of Board of other companies, as on March 31, 2023, are as follows:

Name of the Director Chairmanship/ Directorship in other Position held in
Indian Companies Committees
Name of other listed companies & (only Audit and
categories Stakeholders’
of directorship Relationship Committee)
of the Board of other
Public Limited Companies
As Chairperson As As As No. of Name of Category
Director Chairperson Member Directorship other listed
in other Listed Companies
Companies
Mr. Tarun Dua - - - - -

Mrs. Srishti Baweja - - - - - - -
```

### Chunk 76

_table · pages 56–56 · 102 words · 153 tokens_

```text
## KEY INFORMATION OF DIRECTORS
Mrs. Srishti Baweja - - - - - - -

| Mr. Gaurav Munjal | - | 1 | 2 | 3 | 1 | Infolian | Managing |
| Research Director |
| Service |
| Limited |
| Mr. Varun Pratap Rajda | - | 1 | - | 2 | - | - | - |
| Mr. Naman K. Sarawagi | - | 1 | - | 2 | - | - | - |
| Mr. Aditya | - | 2 | - | 2 | - | - | - |
```

### Chunk 77

_text · pages 56–57 · 383 words · 568 tokens_

```text
## KEY INFORMATION OF DIRECTORS
Bhushan

| E2E Networks Limited | 54 |

Notes:

1. The Independence of a Director is determined by the criteria stipulated under Regulation 16(1)(b) of the
Listing Regulations & Section 149 (6) of
the Act. All the Independent Directors have confirmed that they meet the criteria of Independence as mentioned
under the Regulation 16(1)(b) of
the Listing Regulations and are not aware of any circumstances or situation which exist or may be reasonably
anticipated, that could impair or
impact their ability to discharge duties with an objective independent judgment and without any external
influence. Further, in the opinion of the
Board, the Independent Directors fulfil the conditions specified in these regulations and are independent of
the management.

2. None of the Directors of the Company holds directorship in more than 20 companies. This includes alternate
directorship but does not include
the directorships held in foreign companies, dormant companies and companies under Section 8 of the Act.
Further, none of the Directors hold
directorship in more than 10 public companies. For the purpose of reckoning the directorships in listed
companies, only equity listed companies
have been considered.

3. None of the Directors of the Company is holding position of Director in more than seven listed companies.

4. None of the Directors of the Board is holding position of Independent Director in more than seven listed
companies:

5. None of the Directors on the Board is a Member of more than 10 Committees or Chairperson of more than 5
Committees (as specified in Regulation
26 of the Listing Regulations) across all the public limited companies in which the person is a Director.
Necessary disclosures regarding Committee
positions in other Public Limited Companies as on March 31, 2023, have been made by the Directors. For the
purpose of considering the limit of
committees in which a director can serve, all public limited companies, whether listed or not, have been
included; whereas all other companies
including private limited companies, foreign companies, high value debt listed entities and companies under
section 8 of the Act/section 25 of the
Companies Act, 1956 have been excluded. The Committees considered for the purpose are those prescribed under
Regulation 26 of the Listing
Regulations viz. Audit Committee and Stakeholders’ Relationship Committee of all Indian Public Limited
Companies.
```

### Chunk 78

_text · pages 57–58 · 380 words · 643 tokens · starts with overlap_

```text
## KEY INFORMATION OF DIRECTORS
The Committees considered for the purpose are those prescribed under Regulation 26 of the Listing
Regulations viz. Audit Committee and Stakeholders’ Relationship Committee of all Indian Public Limited
Companies.

6. All the Directors in their individual capacity have confirmed that they are not debarred or disqualified by
SEBI/Ministry of Corporate Affairs or
any other statutory authority to continue as Director of the Company. The Company has also obtained a
certificate from a Company Secretary, in
Whole Time Practice in this regard.

7. None of the Non-Executive Directors have any material pecuniary relationship or transactions with the
Company.

8. The Board of Directors periodically reviews the compliance report of all the laws applicable to the
Company.

| E2E Networks Limited | 55 |

9. As required under the Listing Regulations and second proviso to Section 149(1) of the Act, Mrs. Srishti
Baweja is the Woman Director on the
Board of the Company.

10. None of the Directors of the Company has attained the age of seventy-five years as on March 31, 2023.

11. None of the Directors on the Board of the Company has been restrained from holding position of Director in
any listed company by virtue of any
SEBI Order or any such authority.

12. There are no inter-se relationships between Board of Directors of the Company except that Mrs. Srishti
Baweja, the Whole Time Director of the
Company, is the wife of Mr. Tarun Dua, the Managing Director of the Company.

13. Based on the recommendation of the Nomination and Remuneration Committee and approved by the Shareholders
by the Resolutions passed
through Postal Ballot on 16th March 2023, Mr. Varun Pratap Rajda and Mr. Gaurav Munjal have been re-appointed
as the Non-Executive
Independent Directors for a second term of 5 consecutive years w.e.f February 9, 2023 till February 8, 2028.

14. Further, based on the recommendation of the Nomination and Remuneration Committee, the Board of Directors
has approved the re-appointment
of Mr. Naman K. Sarawagi as the Non-Executive Independent Director for a period of five years w.e.f. February
18, 2024 to February 17, 2029
subject to the approval of the Shareholders in the ensuing Annual General Meeting.

NUMBER OF BOARD MEETINGS, ATTENDANCE OF THE DIRECTORS AT MEETINGS OF THE BOARD AND ANNUAL GENERAL MEETING:
```

### Chunk 79

_text · pages 58–59 · 322 words · 529 tokens · starts with overlap_

```text
## KEY INFORMATION OF DIRECTORS
Sarawagi as the Non-Executive Independent Director for a period of five years w.e.f. February 18, 2024 to
February 17, 2029
subject to the approval of the Shareholders in the ensuing Annual General Meeting. NUMBER OF BOARD MEETINGS,
ATTENDANCE OF THE DIRECTORS AT MEETINGS OF THE BOARD AND ANNUAL GENERAL MEETING:

The Board meetings are held at regular intervals to consider, discuss and approve inter alia, the unaudited
and audited financial results of the Company,
to decide on business policy/strategy of the Company, risk management, competitive scenario, etc. Agenda
papers are circulated to Directors generally
one week before the meeting except for meetings which are held on shorter notice period. Each agenda item is
provided with sufficient background
and all material information is incorporated in the agenda papers for facilitating meaningful and focused
discussions at the meeting. Where it is not
practicable to attach any document to the agenda, it is tabled before the meeting with specific reference to
this effect in the agenda. In special and
exceptional circumstances, additional or supplementary item(s) on the agenda are permitted. Video conferencing
or other audio-visual facilities are
used to facilitate Directors who are unable to attend meetings physically and present at other locations, to
participate in the meetings. In case of
exigencies or urgencies, resolutions are considered by circulation as well.

During the financial year ended March 31, 2023, total 5 (five) Board Meetings were held on the following dates
- April 30, 2022, May 27, 2022, July 25,
2022, November 2, 2022, February 7, 2023. The gap between two meetings did not exceed 120 days. The last
Annual General Meeting was held on
August 24, 2022.

| E2E Networks Limited | 56 |

The details regarding attendance of Directors in the above-mentioned Board Meetings are as follows:

Name DIN Designation No. of Board Meetings No. of Board Meetings Whether attended last
held during the attended AGM or not
Tenure
```

### Chunk 80

_table · pages 59–59 · 146 words · 274 tokens_

```text
## KEY INFORMATION OF DIRECTORS
| E2E Networks Limited | 56 |
The details regarding attendance of Directors in the above-mentioned Board Meetings are as follows:
Name DIN Designation No. of Board Meetings No. of Board Meetings Whether attended last
held during the attended AGM or not
Tenure

| Mr. Tarun Dua | 02696789 | Managing Director | 5 | 4 | Yes |
| Mrs. Srishti Baweja | 08057000 | Whole-time Director | 5 | 5 | Yes |
| Mr. Varun Pratap Rajda | 07468016 | Independent Director | 5 | 3 | Yes |
| Mr. Gaurav Munjal | 02363421 | Independent Director | 5 | 5 | Yes |
| Mr. Naman K. Sarawagi | 05295642 | Independent Director | 5 | 4 | Yes |
| Mr. Aditya Bhushan | 01148272 | Independent Director | 5 | 5 | Yes |
```

### Chunk 81

_text · pages 59–60 · 100 words · 162 tokens_

```text
## INDEPENDENT DIRECTORS:
There was no change in the composition of the Board during FY 2022-23

## INDEPENDENT DIRECTORS:

The Board comprises of four Independent Directors as on March 31, 2023. The Company has issued formal letter
of appointment to its Independent
Directors. The terms and conditions of the appointment of the Independent Directors are published on the
website of the Company.

| E2E Networks Limited | 57 |

The tenure of Independent Directors in accordance with the Act and the Listing Regulations is as follows:

Name of the Independent Date of appointment Date of re-appointment for
Director second term
```

### Chunk 82

_table · pages 60–60 · 79 words · 192 tokens_

```text
## INDEPENDENT DIRECTORS:
| E2E Networks Limited | 57 |
The tenure of Independent Directors in accordance with the Act and the Listing Regulations is as follows:
Name of the Independent Date of appointment Date of re-appointment for
Director second term

| Mr. Gaurav Munjal | 09-02-2018 | 09-02-2023 |
| Mr. Varun Pratap Rajda | 09-02-2018 | 09-02-2023 |
| Mr. Naman K. Sarawagi | 18-02-2019 | N.A |
| Mr. Aditya Bhushan | 22-10-2021 | N.A |
```

### Chunk 83

_text · pages 60–60 · 204 words · 385 tokens_

```text
## SEPARATE MEETING OF INDEPENDENT DIRECTORS & FAMILIARIZATION PROGRAMME FOR THE INDEPENDENT DIRECTORS:
The Independent Directors fulfill the conditions specified in the Listing Regulations and that of Act and are
Independent of the Management.

## SEPARATE MEETING OF INDEPENDENT DIRECTORS & FAMILIARIZATION PROGRAMME FOR THE INDEPENDENT DIRECTORS:

During financial year 2022-23, separate meeting of the Independent Directors of the Company was held on March
29, 2023 without the presence of
Non-Independent Directors and members of management. Along with other matters, Independent Directors discussed
the matters specified in
Schedule IV of the Act and Regulation 25(4) of the Listing Regulations.

In compliance with the Regulation 25(7) of the Listing Regulations, the Company has put in place a
familiarization programme for the Independent
Directors to familiarize them with their roles, rights and responsibility as Directors, the working of the
Company, nature of the industry in which the
Company operates, business model etc.

The Independent Directors are familiarized with the Company’s business model through presentation in the Board
Meeting. The roles, rights and
responsibilities of Independent Directors are also updated through discussion in Board Meetings.

Details of familiarization programme imparted to the Independent Directors during FY 2022-2023 are available
on the website of the Company at
https://www.e2enetworks.com/investors/details-of-familiarization-program-held-for-independent-directors.
```

### Chunk 84

_text · pages 60–61 · 180 words · 273 tokens_

```text
## BOARD DIVERSITY AND SUCCESSION PLANNING:
In compliance with the provisions of the Listing Regulations, the Company has a policy on Board Diversity in
place. The Board comprises of eminent
persons with high credentials of considerable professional experience and expertise in diverse fields who
effectively contribute to the Company’s
growth and policy formulation. The directors are persons of eminence in areas of management and governance,
financial services, finance, law, etc.
and bring with them experience/skills which add value to the performance of the Board.

| E2E Networks Limited | 58 |

Further, one of the key functions of the Board of directors is selecting, compensating, monitoring, and when
necessary, replacing key managerial
personnel and overseeing succession planning. Accordingly, the Company strives to maintain an appropriate
balance of skills and experience within
the organization and the Board in an endeavour to introduce new perspectives while maintaining experience and
continuity. Further, pursuant to
regulation 17(4) of the Listing Regulations, the framework of succession planning for appointment of
Board/senior management has been adopted by
the Company and is reviewed from time to time.
```

### Chunk 85

_text · pages 61–61 · 164 words · 288 tokens_

```text
## SKILLS/EXPERTISE/COMPETENCE OF THE BOARD OF DIRECTORS:
The table below summarizes the skill/expertise/competencies of the Directors identified by the Board for
effective functioning of the Company and
which are available with the Board of the Company as on March 31, 2023.

Skills/Expertise/Competencies Details
Business/Domain Expertise Ability to understand the current drivers of innovation in the Information
Technology and the Cloud Computing
domain.

Leadership Leadership experience for a significant enterprise, resulting in a practical understanding of
organizations,
processes, strategic planning, and risk management.

Financial Knowledge Ability to analyse Financial Statements and contribute to strategic Financial Planning and
efficient use of
financial resource.

Board service and Governance Board Member of a Public Company to develop insights about maintaining Board and
Management
accountability, protecting Shareholder interests, and observing appropriate governance practices

Diversity Representation of gender, ethnic, geographic, cultural perspectives that expand the Board’s
understanding of
the needs and viewpoints of the Company’s Customers, Partners, Employees, Governments, and other
Stakeholders worldwide.

| E2E Networks Limited | 59 |
```

### Chunk 86

_text · pages 62–62 · 100 words · 233 tokens_

```text
## AREAS OF EXPERTISE OF BOARD MEMBERS:
Name of the Director Area of Expertise
Tarun Dua Business/Domain Expertise
Leadership
Financial Knowledge
Board service and Governance
Srishti Baweja Business/Domain Expertise
Leadership
Financial Knowledge
Board service and Governance
Diversity
Gaurav Munjal Leadership
Financial Knowledge
Board service and Governance
Diversity
Varun Pratap Rajda Leadership
Financial Knowledge
Board service and Governance
Diversity
Naman K. Sarawagi Leadership
Financial Knowledge
Board service and Governance
Diversity
Aditya Bhushan Leadership
Financial Knowledge
Board service and Governance
Diversity

Profile of Board Members are available on the website of the Company at
https://www.e2enetworks.com/investors/board-of-directors.

| E2E Networks Limited | 60 |
```

### Chunk 87

_text · pages 63–63 · 143 words · 209 tokens_

```text
## INFORMATION AVAILABLE TO THE BOARD
During the ϐinancial year 2022-23, minimum information as mentioned in Part A of Schedule II of the SEBI
Listing Regulations, wherever
applicable, has been placed before the Board for its consideration.

The aforesaid information is generally provided as a part of the agenda of the Board meeting and/or is placed
at the table during the course of the
meeting. Key Managerial Personnel and other senior management staff are also invited to the Board Meetings to
present reports on the Company’s
operations and internal control systems. The Company Secretary, in consultation with the executive directors
prepares the agenda. In special and
exceptional circumstances, additional or supplementary item(s) on the agenda are permitted to be taken up as
‘any other item’. Further, the Board
periodically reviews the Compliance Reports in respect of laws and regulations applicable to the Company.
```

### Chunk 88

_text · pages 63–63 · 119 words · 224 tokens_

```text
## DIRECTORS AND OFFICERS LIABILITY INSURANCE (‘D&O POLICY’)
The Company has procured an insurance policy for Directors and Ofϐicers Liability, offering coverage up to
Rupees Five Crores. This policy encompasses
the Company's directors, including independent directors, and senior ofϐicers.

POLICY ON APPOINTMENT AND REMUNERATION OF DIRECTORS AND KEY MANAGERIAL PERSONNEL AND OTHER EMPLOYEES:
The Nomination and Remuneration Committee (“NRC”) has determined the criteria to identify the Directors and
Key Managerial Personnel (KMP) in
accordance with the criteria laid down, and has recommended to the Board following policies relating to the
appointment and remuneration for the
Directors, Key Managerial Personnel and other employees which were approved by the Board:

Serial Name of the Policy Weblink
No.
1. Nomination and https://global-
```

### Chunk 89

_table · pages 63–63 · 62 words · 249 tokens_

```text
## DIRECTORS AND OFFICERS LIABILITY INSURANCE (‘D&O POLICY’)
The Company has procured an insurance policy for Directors and Ofϐicers Liability, offering coverage up to Rupees Five Crores. This policy encompasses
Serial Name of the Policy Weblink
No.
1. Nomination and https://global-

| Remuneration | uploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27893_Nomination-and- |
| Policy Remuneration-Policy.pdf |
| 2. Terms and https://global- |
| Conditions | for uploads.webϐlow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27a63_Terms-and- |
```

### Chunk 90

_text · pages 63–65 · 351 words · 692 tokens_

```text
## DIRECTORS AND OFFICERS LIABILITY INSURANCE (‘D&O POLICY’)
Appointment of Conditions-for-Appointment-of-Independent-Directors.pdf
Independent
Directors

| E2E Networks Limited | 61 |

1. Appointment
Nomination and Remuneration Committee ("NRC") determines the criteria of appointment to the Board and is
vested with the authority to identify
candidates for appointment to the Board of Directors. In evaluating the suitability of a person for
appointment / continuing to hold appointment as a
Director, the NRC takes into account among others, Board diversity, person's eligibility, qualification,
expertise, track record, general understanding
of the business, professional ethics, integrity and other fit and proper criteria. Based on recommendation of
the NRC, the Board evaluates the
candidate(s) and decide on the selection of the appropriate member.

2. Remuneration
The remuneration of Executive/Non-Executive Directors and Key Managerial Personnel is governed by the external
competitive environment, track
record, potential, individual performance and performance of the Company as well as industry standards and
decided by NRC in accordance with the
abovementioned policies.

i. Remuneration of Executive Directors
Remuneration of Executive Directors is decided by the Board based on recommendation of NRC within the ceiling
ϐixed by the Shareholders and
permissible under the Act and other relevant laws and regulations. Remuneration paid to the Executive
Directors during the year ended March 31,
2023, and the disclosures as per the requirement of Schedule V of the Act and Listing Regulations, are as
follows:

(Amount in Rs.)
Sr Name of MD and WTD Total Amount
No Tarun Dua Srishti Baweja Particulars Of Remuneration

| 1 | Gross Salary | ₹ 95,03,227 | ₹ 92,49,949/- | ₹ 18,753,176/- |

2 Stock Option Nil Nil Nil
3 Sweat Equity Nil Nil Nil
4 Commission
-as % of profit
Nil Nil Nil -others, specify

5 Others, please specify Nil Nil Nil

| Total (A) | ₹ 95,03,227/- | ₹ 92,49,949/- | ₹ 18,753,176/- |
| E2E Networks Limited | 62 |

Further the shares held by the Executive Directors as on March 31, 2023, are as follows:
Name No. of Shares held in the Company

| Mr. Tarun Dua | 80,60,695 |
| Mrs. Srishti Baweja | 0 |
```

### Chunk 91

_text · pages 65–65 · 131 words · 252 tokens · starts with overlap_

```text
## DIRECTORS AND OFFICERS LIABILITY INSURANCE (‘D&O POLICY’)
of Shares held in the Company

| Mr. Tarun Dua | 80,60,695 |
| Mrs. Srishti Baweja | 0 |

None of the Executive Directors have been granted ESOPs of the Company.
ii. Remuneration of Non-Executive Directors
Non-Executive Directors including Independent Directors do not have any pecuniary relationship or transactions
with the Company. They are
paid only the sitting fees for attending the meetings of the Board of Directors and Committees within the
limits as prescribed under the Act.
The remuneration and sitting fee paid to the Non-executive Directors during the ϐinancial year ended March 31,
2023, along with their
respective shareholdings in the Company are as under:
(Amount in Rs.)
Independent Directors Aditya Varun Gaurav Naman K.
Bhushan Pratap Rajda Munjal Sarawagi
```

### Chunk 92

_table · pages 65–65 · 182 words · 425 tokens_

```text
## DIRECTORS AND OFFICERS LIABILITY INSURANCE (‘D&O POLICY’)
(Amount in Rs.)

| DIN | 01148272 | 07468016 | 02363421 | 05295642 |
| Fee for attending Board Meeting | 50,000 | 30,000 | 50,000 | 40,000 |
| Fee for attending Audit Committee |
| 20,000 | 15,000 | 20,000 | 20,000 | Meetings |
| Fee for attending NRC Meeting | 15,000 | 10,000 | 15,000 | 15,000 |
| Fees for attending SRC Meeting | 5,000 | 5,000 | 5,000 | 5,000 |
| Fees for attending Borrowing Committee Meeting | 10,000 | - | - | - |
| Fees for attending CSR Meeting | - | 5000 | 5000 | 5000 |
| Commission - - - - |
| Benefits or Bonuses - - - - |
| Stock Options | 0 | 0 | 0 | 0 |
| Total | 1,00,000 | 65,000 | 95,000 | 85,000 |
| No. of Equity shares held as on March 31, 2023 | - | - | - | 10,500 |
| E2E Networks Limited | 63 |
```

### Chunk 93

_text · pages 66–66 · 62 words · 121 tokens_

```text
## DIRECTORS AND OFFICERS LIABILITY INSURANCE (‘D&O POLICY’)
iii. Senior Management:
The details of the Senior Management of the Company as on March 31, 2023 are as follows:

Name Designation Qualification Appointment

| Mohamed | Chief Technical Officer | Master of Science, Information and Communication Engineering from Anna | 16.03.2010 |

Imran University B.E, C Abdul Hakeem College of Engineering & Technology
```

### Chunk 94

_table · pages 66–66 · 113 words · 228 tokens_

```text
## DIRECTORS AND OFFICERS LIABILITY INSURANCE (‘D&O POLICY’)
(Amount in Rs.)
iii. Senior Management:
The details of the Senior Management of the Company as on March 31, 2023 are as follows:
Name Designation Qualification Appointment
| Mohamed | Chief Technical Officer | Master of Science, Information and Communication Engineering from Anna | 16.03.2010 |
Imran University B.E, C Abdul Hakeem College of Engineering & Technology

| Computer Science |
| Kesava | Chief Revenue Officer | B.E, AMIE | 01.04.2021 |
| Reddy M |
| Megha | Chief Financial Officer | Chartered Accountant | 20-07-2021 |
| Raheja |
| Richa Gupta | Company Secretary and | Company Secretary | 07-02-2023 |
```

### Chunk 95

_text · pages 66–67 · 196 words · 407 tokens_

```text
## EMPLOYEE STOCK OPTIONS SCHEMES
Compliance Officer
Note:
Ms. Neha Baid resigned as Company Secretary and Compliance Officer of the Company on February 7, 2023.

## EMPLOYEE STOCK OPTIONS SCHEMES

Nomination and Remuneration Committee of the Board of Directors of the Company, inter-alia, administers and
monitors the Employees’ Stock Option
Schemes of the Company in accordance with the Securities and Exchange Board of India (Share Based Employee
Benefits and Sweat Equity)
Regulations, 2021 (“SEBI SBEB Regulations”).

Details for the FY 2022-23 as required under the SEBI SBEB Regulations w.r.t. “E2E ESOS Scheme 2018” and “E2E
Networks Limited Employees Stock
Option Scheme – 2021” have been uploaded on the website of the Company and can be accessed through the
following link at
https://www.e2enetworks.com/investors/employee-stock-option-schemes

During the year under review, the Committee granted 1,44,000 stock options under the “E2E Networks Limited
Employees Stock Option Scheme –

There is no material change in the ESOP schemes of the Company during the year.

| E2E Networks Limited | 64 |

During the year, Ms. Sweeti Chouhan resigned as a trustee of the E2E Networks Employee Welfare Trust and Mr.
Soumyadeep Paul was appointed the
Trustee with effect from June 9, 2022.
```

### Chunk 96

_text · pages 67–67 · 288 words · 451 tokens_

```text
## ANNUAL PERFORMANCE EVALUATION
In terms of provisions of the Act and Regulation 17(10) read with Regulation 25(4) of the Listing Regulations,
the Board conducts an annual
performance evaluation of its own performance, the performance of the Directors individually as well as the
evaluation of the working of its
committees through questionnaire designed with qualitative parameters and feedback based on ratings.

The Board has adopted Board Evaluation Policy (“Policy”) for carrying out the evaluation of Board as whole,
the Board Committees and individual
Directors including Independent Directors. The Policy covers the performance evaluation criteria of all the
directors including independent directors.
The criteria covered to conduct the evaluation process includes contribution to and monitoring of corporate
governance practices, knowledge & update
of relevant areas, participation in the long-term strategic planning and fulfilment of Directors’ obligations
and fiduciary responsibilities, including but
not limited to, active/effective participation at the Board and Committee meetings, representation of
shareholders’ interest and enhancing
shareholders value etc.

Pursuant to the Policy, Board has carried out the annual performance evaluation of the Board as whole, all the
Board Committees and individual
Directors for the FY 2021-22 on April 30, 2022, as per the parameters prescribed in the evaluation forms
provided in the Policy for evaluation of Board
as whole, the Board Committees and individual Directors which include various aspects of Board’s functioning.

Further, Independent Directors have also carried out the performance evaluation of Board as a whole, Non-
Independent Directors and Chairperson of
the Company in their meetings held on March 22, 2022, for the FY 2021-22 and their meeting held on March 29,
2023 for the FY 2022-23.

The Board of Directors expressed their satisfaction with the Policy and Annual Performance Evaluation process
and evaluation results.
```

### Chunk 97

_text · pages 67–69 · 396 words · 659 tokens_

```text
## COMMITTEES OF THE BOARD OF DIRECTORS:
The Board has constituted 5 Committees viz. Audit Committee, Nomination and Remuneration Committee,
Stakeholders Relationship Committee,
Corporate Social Responsibility Committee and Borrowing Committee. Further, during the ϐinancial year ended
March 31, 2023, the Company was not
required to form the Risk Management Committee.

Details of the role and composition of Board Committees constituted as per requirements of the Act and the
Listing Regulations including number of
meetings held during the financial year and attendance thereat are provided hereunder:

| E2E Networks Limited | 65 |

1. Audit Committee:
The Company has constituted an Audit Committee in accordance with Section 177 of Act and the Listing
Regulations.

i. Composition

The Members of the Audit Committee as on March 31, 2023, are as follows:

Name Designation
Gaurav Munjal Chairperson
Varun Pratap Rajda Member

Naman K. Sarawagi Member

Aditya Bhushan Member

The Composition of the Committee as on March 31, 2023, and terms of reference are in compliance with Section
177 of the Act and Regulation 18
of the Listing Regulations. The Chairperson of the Committee is an Independent Director. The Company Secretary
of the Company acts as the
Secretary to the Committee. All the members of the Committee are financially literate and have accounting or
related financial management
expertise.

ii. Roles, responsibilities, and the terms of reference of the Audit Committee:

a. Oversight of the Company's financial reporting process and the disclosure of its financial information to
ensure that the financial
statement is correct, sufficient and credible.

b. Recommending to the Board, the appointment, re-appointment and, if required, the replacement or removal of
the statutory auditor and
the fixation of audit fees

c. Approval of payment to statutory auditors for any other services rendered by the statutory auditors.

d. To review the appointment, removal and terms of remuneration of the chief internal auditor

| E2E Networks Limited | 66 |

e. Reviewing, with the management, the annual financial statements before submission to the board for
approval, with particular reference

I. Matters required to be included in the Director's Responsibility Statement to be included in the Board's
report in terms of clause
(c) of sub-section 3 of section 134 of the Companies Act, 2013;

II. Changes, if any, in accounting policies and practices and reasons for the same;

III. Major accounting entries involving estimates based on the exercise of judgment by management;
```

### Chunk 98

_text · pages 69–70 · 387 words · 584 tokens · starts with overlap_

```text
## COMMITTEES OF THE BOARD OF DIRECTORS:
Changes, if any, in accounting policies and practices and reasons for the same;

III. Major accounting entries involving estimates based on the exercise of judgment by management;

IV. Significant adjustments made in the financial statements arising out of audit findings;

V. Compliance with listing and other legal requirements relating to financial statements

VI. Disclosure of any related party transactions;

VII. Modified Opinions in the draft audit report.

f. Reviewing, with the management, the quarterly financial statements before submission to the board for
approval.

g. Reviewing, with the management, the statement of uses / application of funds raised through an issue
(public issue, right issue, preferential
issue, etc.), the statement of funds utilized for purposes other than those stated in the offer document/Draft
Prospectus/ Prospectus /notice
and the report submitted by the monitoring agency monitoring the utilization of proceeds of a public or rights
issue, and making appropriate
recommendations to the Board to take up steps in this matter.

h. Review and monitor the auditor’s independence, performance and effectiveness of audit process.

i. Approval or any subsequent modification of transactions of the company with related parties;

j. Scrutiny of inter-corporate loans and investments;

k. Valuation of undertakings or assets of the company, wherever it is necessary;

| E2E Networks Limited | 67 |

l. Evaluation of internal financial controls and risk management systems;

m. Reviewing, with the management, performance of statutory and internal auditors, adequacy of the internal
control systems

n. Reviewing the adequacy of internal audit function, if any, including the structure of the Internal audit
department, staffing and seniority of
the official heading the department, reporting structure coverage and frequency of internal audit

o. Discussion with internal auditors any significant findings and follow up there on.

p. Reviewing the findings of any internal investigations by the internal auditors into matters where there is
suspected fraud or irregularity or a
failure of internal control systems of a material nature and reporting the matter to the board.

q. Discussion with statutory auditors before the audit commences, about the nature and scope of audit as well
as post-audit discussion to
ascertain any area of concern

r. To look into the reasons for substantial defaults in the payment to the depositors, debenture holders,
shareholders (in case of non-payment
of declared dividends) and creditors
```

### Chunk 99

_text · pages 70–71 · 303 words · 510 tokens · starts with overlap_

```text
## COMMITTEES OF THE BOARD OF DIRECTORS:
To look into the reasons for substantial defaults in the payment to the depositors, debenture holders,
shareholders (in case of non-payment
of declared dividends) and creditors

s. To oversee and review the functioning of the whistle blower/vigil mechanism which shall provide for
adequate safeguards against
victimization of employees and directors who avail of the vigil mechanism and also provide for direct access
to the Chairperson of the Audit
Committee in appropriate and exceptional cases.

t. Call for comments of the auditors about internal control systems, scope of audit including the observations
of the auditor and review of the
financial statements before submission to the Board;

u. Approval of appointment of CFO (i.e., the whole-time Finance Director or any other person heading the
finance function or discharging that
function) after assessing the qualifications, experience & background, etc. of the candidate.

v. To review utilisation of loans and/or advances from/ investment by holding company in the subsidiary
company exceeding INR 100 crores
or 10% of asset size of subsidiary, whichever is lower.

w. To consider and comment on rationale, cost-benefits and impact of schemes Involving merger, demerger,
amalgamation etc., on the Company
and its shareholders.

| E2E Networks Limited | 68 |

x. To investigate any other matters referred to by the Board of Directors.

iii. Meetings and attendance during the year

During the year under review, the Audit Committee (“Committee”) of the Company met 4 times viz. May 27, 2022;
July 25, 2022; November 2,
2022 and February 7, 2023. The Board has accepted all recommendations of the Committee made during the
financial year 2022-23.

The details regarding attendance of Members in the above Meetings are as follows:

S. Name of Member Designation No. of Meeting(s) which Member No. of Meeting(s) attended
No. was Entitled to attend
```

### Chunk 100

_table · pages 71–71 · 114 words · 188 tokens_

```text
## COMMITTEES OF THE BOARD OF DIRECTORS:
v. To review utilisation of loans and/or advances from/ investment by holding company in the subsidiary company exceeding INR 100 crores
The details regarding attendance of Members in the above Meetings are as follows:
S. Name of Member Designation No. of Meeting(s) which Member No. of Meeting(s) attended
No. was Entitled to attend

| 1 | Mr. Gaurav Munjal | Chairman | 4 | 4 |
| 2 | Mr. Varun Pratap Rajda | Member | 4 | 3 |
| 3 | Mr. Naman K. Sarawagi | Member | 4 | 4 |
| 4 | Mr Aditya Bhushan | Member | 4 | 4 |
```

### Chunk 101

_text · pages 71–72 · 405 words · 606 tokens_

```text
## COMMITTEES OF THE BOARD OF DIRECTORS:
2. Nomination and Remuneration Committee:
The Company has constituted Nomination and Remuneration Committee in accordance with the provision of Section
178 of the Act and
Regulation 19 of the Listing Regulations.

Composition
The Members of the Nomination and Remuneration Committee as on March 31, 2023 are as follows: i.
Name Designation
Gaurav Munjal Chairperson
Varun Pratap Rajda Member

Naman K. Sarawagi Member

Aditya Bhushan Member

The Composition of the Committee as on March 31, 2023, and terms of reference are in compliance with Section
178 of the Act and Regulation 19 of
the Listing Regulations. The Chairperson of the Committee is an Independent Director. The Company Secretary of
the Company acts as the Secretary
to the Committee.

| E2E Networks Limited | 69 |

ii. Roles, responsibilities, and the terms of reference of the Nomination and Remuneration Committee:
The terms of reference of the Nomination and Remuneration Committee are as under:-

a. Formulation of the criteria for determining qualifications, positive attributes and independence of a
director and recommend to the Board a
policy relating to, the remuneration of the directors, key managerial personnel and other employees;

b. For every appointment of an independent director, the Nomination and Remuneration Committee shall evaluate
the balance of skills,
knowledge and experience on the Board and on the basis of such evaluation, prepare a description of the role
and capabilities required of an
independent director. The person recommended to the Board for appointment as an independent director shall
have the capabilities identified
in such description. For the purpose of identifying suitable candidates, the Committee may:
I. use the services of an external agencies, if required;
II. consider candidates from a wide range of backgrounds, having due regard to diversity; and
III. consider the time commitments of the candidates;

c. Formulation of criteria for evaluation of performance of independent directors and the Board;

d. To ensure that the relationship of remuneration to performance is clear and meets appropriate performance
benchmarks; and

e. Devising a policy on diversity of Board of Directors;

f. Identifying persons who are qualified to become directors and who may be appointed in senior management in
accordance with the criteria
laid down and recommend to the Board their appointment and removal.

g. To recommend on whether to extend or continue the term of appointment of the independent director, on the
basis of the report of
performance evaluation of independent directors.
```

### Chunk 102

_text · pages 72–73 · 267 words · 431 tokens · starts with overlap_

```text
## COMMITTEES OF THE BOARD OF DIRECTORS:
g. To recommend on whether to extend or continue the term of appointment of the independent director, on the
basis of the report of
performance evaluation of independent directors.

h. To recommend to the board, all remuneration, in whatever form, payable to senior management.

i. Administering employee stock option schemes, employee stock purchase schemes, stock appreciation rights
schemes, general employee
benefits scheme and retirement benefit schemes (the “Schemes”);

j. Delegating the administration and superintendence of the Schemes to any trust set up with respect to the
Schemes;

| E2E Networks Limited | 70 |

k. Formulating detailed terms and conditions for the Schemes including provisions specified by the board of
directors of the Company in this
regard;

l. Determining the eligibility of employees to participate under the Schemes;

m. Granting options to eligible employees and determining the date of grant;

n. Determining the number of options to be granted to an employee;

o. Determining the exercise price under the Schemes; and

p. Construing and interpreting the Plan and any agreements defining the rights and obligations of the Company
and eligible employees under the
Schemes, and prescribing, amending and/or rescinding rules and regulations relating to the administration of
the Schemes.

iii. Meetings and attendance during the year
During the year under review, the Nomination and Remuneration Committee (“Committee”) of the Company met 3
times, viz. April 30,
2022; July 25, 2022 and February 7, 2023. The details regarding attendance of Members in the above Meetings
are as follows:

Name Designation No. of Meetings held during No. of Meetings attended
the Tenure
```

### Chunk 103

_table · pages 73–73 · 83 words · 142 tokens_

```text
## COMMITTEES OF THE BOARD OF DIRECTORS:
v. To review utilisation of loans and/or advances from/ investment by holding company in the subsidiary company exceeding INR 100 crores
Name Designation No. of Meetings held during No. of Meetings attended
the Tenure

| Gaurav Munjal | Chairperson | 3 | 3 |
| Varun Pratap Rajda | Member | 3 | 2 |
| Naman K. Sarawagi | Member | 3 | 3 |
| Aditya Bhushan | Member | 3 | 3 |
```

### Chunk 104

_text · pages 73–75 · 310 words · 526 tokens_

```text
## COMMITTEES OF THE BOARD OF DIRECTORS:
3. Stakeholders’ Relationship Committee:
The Stakeholders Relationship Committee has been constituted to specifically look into various aspects of
interest of Shareholders and
Investors complaints and other shareholders related issues.

| E2E Networks Limited | 71 |

i. Composition
The Members of the Stakeholder’s Relationship Committee as on March 31, 2023 are as follows:

Name Designation
Gaurav Munjal Chairperson
Varun Pratap Rajda Member

Naman K. Sarawagi Member

Aditya Bhushan Member

The Composition of the Committee as on March 31, 2023 and terms of reference are in compliance with Section
178 of the Act and Regulation 20 of
the Listing Regulations. The Chairperson of the Committee is an Independent Director. The Company Secretary of
the Company acts as the Secretary
to the Committee.

ii. Roles, responsibilities and the terms of reference of the Stakeholders’ Relationship Committee:

a. Resolving the grievances of the security holders of the listed entity including complaints related to
transfer/transmission of shares, non-
receipt of annual report, non-receipt of declared dividends, issue of new/duplicate certificates, general
meetings etc.

b. Review of measures taken for effective exercise of voting rights by shareholders.

c. Review of adherence to the service standards adopted by the listed entity in respect of various services
being rendered by the Registrar &
Share Transfer Agent.

d. Review of the various measures and initiatives taken by the listed entity for reducing the quantum of
unclaimed dividends and ensuring
timely receipt of dividend warrants/annual reports/statutory notices by the shareholders of the company.

iii. Meetings and attendance during the year

During the year under review, the Stakeholders Relationship Committee (“Committee”) of the Company met once
viz February 07, 2023.

| E2E Networks Limited | 72 |

The details regarding attendance of Members in the said meeting are as follows:

Name Designation No. of Meetings held during the No. of Meetings attended
Tenure
```

### Chunk 105

_table · pages 75–75 · 129 words · 217 tokens_

```text
## COMMITTEES OF THE BOARD OF DIRECTORS:
v. To review utilisation of loans and/or advances from/ investment by holding company in the subsidiary company exceeding INR 100 crores
iii. Meetings and attendance during the year
During the year under review, the Stakeholders Relationship Committee (“Committee”) of the Company met once viz February 07, 2023.
| E2E Networks Limited | 72 |
The details regarding attendance of Members in the said meeting are as follows:
Name Designation No. of Meetings held during the No. of Meetings attended
Tenure

| Gaurav Munjal | Chairperson | 1 | 1 |
| Varun Pratap Rajda | Member | 1 | 1 |
| Naman K. Sarawagi | Member | 1 | 1 |
| Aditya Bhushan | Member | 1 | 1 |
```

### Chunk 106

_text · pages 75–76 · 396 words · 635 tokens_

```text
## COMMITTEES OF THE BOARD OF DIRECTORS:
4. Corporate Social Responsibility Committee:

i. Composition

The Company has constituted Corporate Social Responsibility Committee in accordance with Section 135 of the
Act. The Members of the Corporate
Social Responsibility Committee as on March 31, 2023, are as follows:

Name Designation
Srishti Baweja Chairperson
Gaurav Munjal Member

Varun Pratap Rajda Member

Naman K. Sarawagi Member

The Composition of the Committee as on March 31, 2023 and terms of reference are in compliance with Section
135 of the Act. The Chairperson
of the Committee is the Whole-time Director. The Company Secretary of the Company acts as the Secretary to the
Committee.

| E2E Networks Limited | 73 |

ii. Roles, responsibilities, and the terms of reference of the Corporate Social Responsibility Committee:

a. To formulate and recommend to the Board, a CSR policy which shall indicate the activities to be undertaken
by the Company as per the
Companies Act, 2013 and rules made thereunder (as may be amended from time to time);

b. To review and recommend the amount of expenditure to be incurred on the CSR activities to be undertaken by
the company;

c. To monitor the CSR policy of the Company from time to time;

d. To monitor CSR projects, programs or activities undertaken by the Company;

e. To formulate and recommend to the Board an annual action plan which will include

I. the CSR project/programme which will be undertaken by the Company in the relevant financial year

II. the manner of execution of such CSR project/programme

III. the modalities of utilisation of funds and implementation schedules for such CSR project/programme

IV. monitoring and reporting mechanism for such CSR project/programme

V. details of impact assessment, if applicable, for the projects undertaken by the company.

f. To recommend to the Board the adoption of the CSR report and to review the effectiveness of the CSR Policy
and activities included in the
Policy.

g. Any other matter the CSR Committee may deem appropriate after approval of the Board of Directors or as may
be directed by the Board of
Directors from time to time.

iii. Meetings and attendance during the year

During the year under review, the Corporate Social Responsibility (“Committee”) of the Company met once viz
July 25, 2022. The details regarding
attendance of Members in the said meeting are as follows:

| E2E Networks Limited | 74 |
```

### Chunk 107

_text · pages 77–77 · 66 words · 115 tokens · starts with overlap_

```text
## COMMITTEES OF THE BOARD OF DIRECTORS:
iii. Meetings and attendance during the year

During the year under review, the Corporate Social Responsibility (“Committee”) of the Company met once viz
July 25, 2022. The details regarding
attendance of Members in the said meeting are as follows:

| E2E Networks Limited | 74 |

Name Designation No. of Meetings held during the No. of Meetings attended
Tenure
```

### Chunk 108

_table · pages 77–77 · 83 words · 143 tokens_

```text
## COMMITTEES OF THE BOARD OF DIRECTORS:
v. To review utilisation of loans and/or advances from/ investment by holding company in the subsidiary company exceeding INR 100 crores
Name Designation No. of Meetings held during the No. of Meetings attended
Tenure

| Srishti Baweja | Chairperson | 1 | 1 |
| Gaurav Munjal | Member | 1 | 1 |
| Varun Pratap Rajda | Member | 1 | 1 |
| Naman K. Sarawagi | Member | 1 | 1 |
```

### Chunk 109

_text · pages 77–78 · 382 words · 631 tokens_

```text
## COMMITTEES OF THE BOARD OF DIRECTORS:
5. Borrowing Committee:
The Company has constituted Borrowing Committee in accordance with of provisions of Section 179 of Act.

i. Composition
The Members of the Borrowing Committee as on March 31, 2023 are as follows:

Name Designation
Tarun Dua Chairperson
Srishti Baweja Member

Aditya Bhusan Member

The Composition of the Committee as on March 31, 2023, and terms of reference are in compliance with Section
179 of the Act. The Chairperson
of the Committee is the Managing Director. The Company Secretary of the Company acts as the Secretary to the
Committee.

ii. Roles, responsibilities and the terms of reference of the Borrowing Committee:

a. To avail financial facilities from financial institution(s)/bank(s) in form of term loan(s), guarantee(s)
or in any other forms (“facilities”)
other than by way of issuance of debentures, in connection with our Company’s business requirement.

b. To avail operating lease, financial lease, rental facility or financing facility in any from banks and/or
other financial institution.

c. To avail inter-corporate loan or deposits not exceeding the prescribed limit, as prescribed under the law;

d. To apply and avail cash management services with various banks.

| E2E Networks Limited | 75 |

e. To consider and approve availing of bank guarantees from various banks.

f. To provide security/ collateral or pledge / hypothecate FDRs as security towards Letter of Credit in favor
of third party(s).

g. To avail loan facilities and overdraft facilities from various banks.

h. To apply and avail corporate credit cards facility from various banks.

i. To consider and approve the list of authorized signatories to execute the documents required by various
banks for above activities.

j. To consider availing of credit card facility in the name of employees / officials of the Company.

k. Authorization to represent the Company in matters related to above.

l. Discharge such other role/functions as may be specifically referred to the Committee by the Board of
Directors from time to time.

iii. Meetings and attendance during the year
During the year under review, the Borrowing Committee(“Committee”) of the Company met twice viz September 17,
2022, and December 21,
2022. The details regarding attendance of Members in the above Meetings are as follows:

Name Designation No. of Meetings held during the No. of Meetings attended
Tenure
```

### Chunk 110

_table · pages 78–78 · 119 words · 209 tokens_

```text
## COMMITTEES OF THE BOARD OF DIRECTORS:
v. To review utilisation of loans and/or advances from/ investment by holding company in the subsidiary company exceeding INR 100 crores
iii. Meetings and attendance during the year
During the year under review, the Borrowing Committee(“Committee”) of the Company met twice viz September 17, 2022, and December 21,
2022. The details regarding attendance of Members in the above Meetings are as follows:
Name Designation No. of Meetings held during the No. of Meetings attended
Tenure

| Tarun Dua | Chairperson | 2 | 2 |
| Srishti Baweja | Member | 2 | 0 |
| Aditya Bhushan | Member | 2 | 2 |
| E2E Networks Limited | 76 |
```

### Chunk 111

_text · pages 79–79 · 21 words · 33 tokens_

```text
## GENERAL MEETINGS AND POSTAL BALLOT
The detail of the Annual General Meetings of the previous three years are as follows:
```

### Chunk 112

_table · pages 79–79 · 64 words · 155 tokens_

```text
## GENERAL MEETINGS AND POSTAL BALLOT
The detail of the Annual General Meetings of the previous three years are as follows:

| Financial | 2019-2020 | 2020-2021 | 2021-2022 |
| Year |
| Day, date & Tuesday, Wednesday, Wednesday, |
| time | 15th September,2020 at 4.00 P.M. | 22nd September 2021 at 4.00 P.M. | 24th August 2022 at 4.00 P.M. |
```

### Chunk 113

_text · pages 79–79 · 27 words · 61 tokens_

```text
## GENERAL MEETINGS AND POSTAL BALLOT
Venue Video Conferencing (“VC”)/ Video Conferencing (“VC”) / Video Conferencing (“VC”) /
Other Audio-Visual Means Other Audio-Visual Means Other Audio-Visual Means
```

### Chunk 114

_table · pages 79–79 · 79 words · 163 tokens_

```text
## GENERAL MEETINGS AND POSTAL BALLOT
Venue Video Conferencing (“VC”)/ Video Conferencing (“VC”) / Video Conferencing (“VC”) /
Other Audio-Visual Means Other Audio-Visual Means Other Audio-Visual Means

| (“OAVM”) (“OAVM”) (“OAVM”) |
| Details | of | 1. To authorise the Board to | 1. | To | consider, | approve | 1. To appoint Mr. Aditya Bhushan |
| Special | create/modify charge on | the | and ratify appointment of Mr. | (DIN: 01148272) as Non-Executive |
```

### Chunk 115

_text · pages 79–80 · 375 words · 739 tokens_

```text
## GENERAL MEETINGS AND POSTAL BALLOT
Resolution movable and immovable assets Tarun Dua, Managing Director of Independent Director of the
passed including undertakings of the the Company, and remuneration Company.
Company, both present and future, payable to him for the period from

| to secure the borrowings of the | April 1, 2021 till January 31, 2023. |

2. To consider and approve re- Company.

| appointment of Mr. Tarun Dua, |

2. To consider, approve and ratify Managing Director of the Company
appointment of Mrs. Srishti Baweja, and remuneration payable to him

| Whole Time Director | of the | for the period from January 31, |
| Company, | and | remuneration | 2023 till January 30, 2026. |

payable to her for the period from
April 1, 2021 till January 31, 2023

| 3. To consider and approve re- |

appointment of Mrs. Srishti Baweja
3. To approve and ratify the Whole time Director of the

| amendment | in E2E Networks | Company | and | remuneration |

Limited Employee Stock Option payable to her for the period from

| Scheme – 2021 | January 31, 2023 till January 30, |
| E2E Networks Limited | 77 |

1. Extra-ordinary General Meeting

During the financial year 2022-23 no Extra-Ordinary General Meeting was held.

2. Postal Ballot
During the FY 2022-23, the Company conducted one Postal Ballot in compliance with Regulation 44 of the Listing
Regulations and in pursuance of
Section 108 read with Section 110 and other applicable provisions of the Act read with Companies (Management
and Administration) Rules, 2014 to
obtain approval of Shareholders on the following matter as

Special Resolutions:
Serial No. Matter passed through Postal Ballot

| 1. | Re-appointment of Mr. Varun Pratap Rajda (07468016) as the Independent Director of the Company. |
| 2. | Re-appointment of Mr. Gaurav Munjal (02363421) as an Independent Director of the Company. |

Mr. Ankush Agarwal having (C.P. No- 14486) Partner of M/s. MAKS & CO., Company Secretaries (FRN :
P2018UP067700), was the scrutinizer for
conducting the Postal Ballot Activity.

The said resolutions were passed on March 16, 2023 with requisite majority, result of which was declared on
March 17, 2023.

i. Persons responsible for conducting the postal ballot exercise:
```

### Chunk 116

_text · pages 80–81 · 443 words · 942 tokens · starts with overlap_

```text
## GENERAL MEETINGS AND POSTAL BALLOT
MAKS & CO., Company Secretaries (FRN : P2018UP067700), was the scrutinizer for
conducting the Postal Ballot Activity. The said resolutions were passed on March 16, 2023 with requisite
majority, result of which was declared on March 17, 2023. i. Persons responsible for conducting the postal
ballot exercise:

Mr. Tarun Dua, Managing Director, Mrs. Srishti Baweja, Whole-Time Director, and Richa Gupta Company Secretary
cum Compliance Officer of the
Company, were appointed as persons responsible for conducting the postal ballot in a fair and transparent
manner. Mr. Ankush Agarwal
(C.P. No. 14486), Partner of M/s. MAKS & CO., Company Secretaries (FRN : P2018UP067700) was appointed as
Scrutinizer for conducting the Postal
Ballot process and services of M/s. Link Intime India Private Limited, (“Link Intime”) were engaged as an
Agency for the purpose of providing e-voting
facility. Mr. Ankush Agarwal conducted the process and submitted his report to the Chairperson.

| E2E Networks Limited | 78 |

ii. Procedure followed for postal ballot:

a. The Company issued the Postal Ballot Notice dated February 7, 2023, for the above-mentioned resolutions.
The draft resolutions together with
the explanatory statement setting out the material facts was sent through e-mail to all members of the Company
whose names appear on the
Register of Members/list of Beneϐicial Owners on the Cut-Off Date i.e. February 10, 2023 and who have
registered their email addresses with
the Company or Depository / Depository Participants. As per Section 108 and Section 110 read with Companies
(Management and
Administration) Rules, 2014 (“Rules”) read with the General Circular No.14/2020 dated 8th April 2020 read with
General Circular No.17/2020
dated 13th April 2020, General Circular No.03/2022 dated 5th May 2022 and General Circular No.11/2022 dated
28th December 2022 issued
by the Ministry of Corporate Affairs, Government of India (the “MCA Circulars”) and as per provisions of the
Listing Regulations, e-voting facility
was provided to the Shareholders to cast their votes electronically instead of physical mode. Further, the
Postal Ballot Notice was also placed
at the Company website on the following link:
https://global-uploads.webϐlow.com/6473d8d02a3cf26273f2787d/6473d8d02a3cf26273f28ac2_Postal%20Ballot_Final.pdf
was made
available on the website of https://instavote. linkintime.co.in and was also sent to the Stock Exchange (i.e.
NSE);

b. E-voting was provided from February 15, 2023 (9:00 A.M. IST) and ended on March 16, 2023 (5:00 P.M. IST).

c. The Company also published the Postal Ballot Notice in the newspaper i.e. Financial Express (English
Newspaper) and Jansatta (Hindi Newspaper)
declaring the details and requirements as mandated by the Act and Rules. Further the newspaper publication of
the Postal Ballot Notice was also

| placed | at the Company website on the | following | link https://www.e2enetworks.com/investors/newspaper-advertisement | . |
```

### Chunk 117

_text · pages 81–82 · 270 words · 561 tokens · starts with overlap_

```text
## GENERAL MEETINGS AND POSTAL BALLOT
Financial Express (English Newspaper) and Jansatta (Hindi Newspaper)
declaring the details and requirements as mandated by the Act and Rules. Further the newspaper publication of
the Postal Ballot Notice was also

| placed | at the Company website on the | following | link https://www.e2enetworks.com/investors/newspaper-advertisement | . |

d. Voting Rights were reckoned on the paid up value of the shares registered in the names of the
Members/Beneficial Owner as on the Cut-Off date;

e. Mr. Ankush Agarwal, scrutinizer, submitted his report on March 17, 2023;

f. The result of the Postal Ballot was declared on March 17, 2023 and displayed on the notice board at the
registered office of the Company. The date
of receipt of approval i.e. March 16, 2023 of the requisite majority of shareholders by means of e-voting has
been taken as the date of passing of
the resolution;
g. The result of the postal ballot was placed at the website of the Company on the following path
https://global-
uploads.webflow.com/6473d8d02a3cf26273f2787d/6473d8d02a3cf26273f28b0b_IntimationForVotingResultsfinal.pdf
besides being
communicated to the Stock Exchange (i.e. NSE) and Registrar and Share Transfer Agent.

| E2E Networks Limited | 79 |

iii. Details of Voting Pattern of Postal Ballot
The details of Voting Pattern of Postal ballot held on February 7, 2023, are as follows:

Resolution No. 1: Re-appointment of Mr. Varun Pratap Rajda (DIN: 07468016) as a Non-Executive Independent
Director of the Company for a term
of 5 consecutive years (Special Resolution) (E-voting mode only)

a. Details of voting through Remote e-voting:

Particulars Number of Valid Votes Percentage of total net
valid votes casted
Postal-Ballot Remote e-Votes Total
```

### Chunk 118

_table · pages 82–82 · 93 words · 224 tokens_

```text
## GENERAL MEETINGS AND POSTAL BALLOT
Resolution No. 1: Re-appointment of Mr. Varun Pratap Rajda (DIN: 07468016) as a Non-Executive Independent Director of the Company for a term
of 5 consecutive years (Special Resolution) (E-voting mode only)
a. Details of voting through Remote e-voting:
Particulars Number of Valid Votes Percentage of total net
valid votes casted
Postal-Ballot Remote e-Votes Total

| Assent | NA | 1,09,34,379 | 1,09,34,379 | 99.99 |
| Dissent | NA | 3 | 3 | Negligible |
| Total | NA | 1,09,34,382 | 1,09,34,382 | 100 |
```

### Chunk 119

_text · pages 82–82 · 35 words · 72 tokens_

```text
## GENERAL MEETINGS AND POSTAL BALLOT
b. Detailed summary of E-voting is as under:

Particulars No of shareholders No. of the Shares Paid-up value of the Shares % of Total
(In Rs.) Paid-up Capital
(Approx.)
```

### Chunk 120

_table · pages 82–82 · 111 words · 274 tokens_

```text
## GENERAL MEETINGS AND POSTAL BALLOT
b. Detailed summary of E-voting is as under:
Particulars No of shareholders No. of the Shares Paid-up value of the Shares % of Total
(In Rs.) Paid-up Capital
(Approx.)

| (a) Total votes received | 20 | 1,09,34,382 | 10,93,43,820 | 75.54 |
| (b) Less: Abstained | 0 | 0 | 0 | 0 |
| (c) Net Valid Votes | 20 | 1,09,34,382 | 10,93,43,820 | 75.54 |
| (d) Votes with Assent | 17 | 1,09,34,379 | 10,93,43,790 | 75.54 |
| (e) Votes with dissent | 3 | 3 | 30 | Negligible |
| E2E Networks Limited | 80 |
```

### Chunk 121

_text · pages 83–83 · 59 words · 131 tokens_

```text
## GENERAL MEETINGS AND POSTAL BALLOT
Resolution No. 2: Re-appointment of Mr. Gaurav Munjal (DIN: 02363421) as a Non-Executive Independent Director
of the Company for a term of 5
consecutive years (Special Resolution) (E-voting mode only)

a. Details of voting through Remote e-voting:

Particulars Number of Valid Votes Percentage of total net valid votes casted

Postal-Ballot Remote e-Votes Total
```

### Chunk 122

_table · pages 83–83 · 96 words · 233 tokens_

```text
## GENERAL MEETINGS AND POSTAL BALLOT
(In Rs.) Paid-up Capital
Resolution No. 2: Re-appointment of Mr. Gaurav Munjal (DIN: 02363421) as a Non-Executive Independent Director of the Company for a term of 5
consecutive years (Special Resolution) (E-voting mode only)
a. Details of voting through Remote e-voting:
Particulars Number of Valid Votes Percentage of total net valid votes casted
Postal-Ballot Remote e-Votes Total

| Assent | NA | 1,09,34,379 | 1,09,34,379 | 99.99 |
| Dissent | NA | 3 | 3 | Negligible |
| Total | NA | 1,09,34,382 | 1,09,34,382 | 100 |
```

### Chunk 123

_text · pages 83–83 · 35 words · 73 tokens_

```text
## GENERAL MEETINGS AND POSTAL BALLOT
b. Detailed summary of E-voting is as under:

Particulars No of shareholders No. of the Shares Paid-up value of the Shares
% of Total (In Rs.)
Paid-up Capital
(Approx.)
```

### Chunk 124

_table · pages 83–83 · 104 words · 262 tokens_

```text
## GENERAL MEETINGS AND POSTAL BALLOT
b. Detailed summary of E-voting is as under:
Particulars No of shareholders No. of the Shares Paid-up value of the Shares
% of Total (In Rs.)
Paid-up Capital
(Approx.)

| (a) Total votes received | 20 | 1,09,34,382 | 10,93,43,820 | 75.54 |
| (b) Less: Abstained | 0 | 0 | 0 | 0 |
| (c) Net Valid Votes | 20 | 1,09,34,382 | 10,93,43,820 | 75.54 |
| (d) Votes with Assent | 17 | 1,09,34,379 | 10,93,43,790 | 75.54 |
| (e) Votes with dissent | 3 | 3 | 30 | Negligible |
```

### Chunk 125

_text · pages 83–84 · 367 words · 680 tokens_

```text
## MEANS OF COMMUNICATION
No Special Resolution requiring Postal Ballot is being proposed to be conducted as on date of this Report.

| E2E Networks Limited | 81 |

## MEANS OF COMMUNICATION

1. Website:
The Company maintains an active website i.e. www.e2enetworks.com wherein all the information relevant for the
Shareholders are displayed. Copy
of the Press releases, Quarterly results, Presentations to Financial Analysts and Institutional Investors,
Policies of the Company, Shareholding pattern,
Stock Exchange disclosures as required under Regulation 46 of the Listing Regulations are made available on
the website. The Annual Report of the
Company and the quarterly/annual financial results of the Company are also placed on the Company’s website and
can be accessed from the link
https://www.e2enetworks.com/investors/financial-information and can further be downloaded.

Official news releases and official press releases are sent to NSE before sending the same to media and are
also displayed on the Company’s website
i.e. https://www.e2enetworks.com/investors/media-updates

There is a separate dedicated section under “Investors Relations” on the Company’s website i.e.
https://www.e2enetworks.com/investors/
which gives information on quarterly compliance reports / communications with the Stock Exchanges and other
relevant information of interest
to the investors / public. The presentations made to the Investors are available on the website.
All the corporate communication to the National Stock Exchange of India Limited are filed electronically with
NSE through NSE’s NSE Electronic
Application Processing System (NEAPS) portal. The Stock Exchange filings are also made available on the
website of the Company and can be accessed
at https://www.e2enetworks.com/investors/corporate-announcements .

2. Financial Results and Newspaper Publications
Quarterly Financial Results generally published in one of the leading newspapers of the country Financial
Express in English and in Jansatta in Regional
Newspapers in Hindi and are displayed on the website of the Company i.e.
https://www.e2enetworks.com/investors/newspaper-advertisement .

i. Stock Exchange Filings:
The Company also uploads its disclosures and announcements under the Listing Regulations at the link
https://neaps.nseindia.com/NEWLISTINGCORP/ to NSE Electronic Application Processing System (NEAPS). During the
year, the Company also
submits quarterly compliance report on Corporate Governance to the stock exchanges within 21 days from the
close of quarter as per the formats
given under the Listing Regulations.

ii. SEBI Complaints Redress System (SCORES)

| E2E Networks Limited | 82 |
```

### Chunk 126

_text · pages 85–85 · 114 words · 195 tokens · starts with overlap_

```text
## MEANS OF COMMUNICATION
During the year, the Company also
submits quarterly compliance report on Corporate Governance to the stock exchanges within 21 days from the
close of quarter as per the formats
given under the Listing Regulations. ii. SEBI Complaints Redress System (SCORES)

| E2E Networks Limited | 82 |

The Investors can raise complaints in a centralized web-based complaints redress system called “Scores”. The
Company uploads the action taken
report on the complaints raised by the Shareholders on “Scores”, which can be viewed by the Shareholder. The
complaints are closed to the
satisfaction of the shareholder and SEBI.

Details of complaints/requests etc., received and resolved during the FY 2022-2023 are as below:
```

### Chunk 127

_table · pages 85–85 · 103 words · 211 tokens_

```text
## MEANS OF COMMUNICATION
Details of complaints/requests etc., received and resolved during the FY 2022-2023 are as below:

| Source | Received during the period from | Resolved during the period from 01.04.2022 | Pending | as | on |
| 01.04.2022 to | to 31.03.2023 | 31.03.2023 |
| 31.03.2023 |
| SEBI | 0 | 0 | 0 |
| Stock Exchange(s) 0 | 0 | 0 |
| Investors’ | 0 | 0 | 0 |
| Associations/ |
| Others |
| Direct | 0 | 0 | 0 |
| Total | 0 | 0 | 0 |
```

### Chunk 128

_text · pages 85–85 · 117 words · 256 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
1. Annual General Meeting for the Financial Year 2022-23:

Ministry of Corporate Affairs vide its General Circular No.20/2020 dated 5th May 2020 read with General
Circular No.14/2020 dated 8th April 2020,
General Circular No.17/2020 dated 13th April 2020 and General Circular No.11/2022 dated 28th December 2022 has
allowed companies to conduct
their Annual General Meetings through video conference/other audio visual (VC/OAVM) means till September 30,
2023, without physical presence of
shareholders at a common venue subject to fulfilment of certain pre-requisite conditions.

Accordingly, in terms of the above MCA Circulars, it has been decided by the Company to hold its 14th Annual
General Meeting (AGM) through
VC/OAVM as per the details mentioned hereunder:
```

### Chunk 129

_table · pages 85–85 · 67 words · 130 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
Accordingly, in terms of the above MCA Circulars, it has been decided by the Company to hold its 14th Annual General Meeting (AGM) through
VC/OAVM as per the details mentioned hereunder:

| Date | : | September 29, 2023 |
| Time | : | 4:00 P.M (IST) |
| 2. Corporate Identity Number (CIN) |
| E2E Networks Limited | 83 |
```

### Chunk 130

_text · pages 86–86 · 76 words · 162 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
The Corporate Identity Number (CIN) allotted by the Ministry of Corporate Affairs, Government of India is
L72900DL2009PLC341980.

3. Financial Year

Financial Year of the Company is from April 1,2022 to March 31, 2023. The financial calendar of the Company is
reproduced below:

Tentative Calendar for the FY 2023-24 (subject to change)

Adoption of un-audited quarterly results and Annual Results For the Quarter ended on or before (actual &
tentative for future
quarters)
```

### Chunk 131

_table · pages 86–86 · 110 words · 231 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
3. Financial Year
Financial Year of the Company is from April 1,2022 to March 31, 2023. The financial calendar of the Company is reproduced below:
Tentative Calendar for the FY 2023-24 (subject to change)
Adoption of un-audited quarterly results and Annual Results For the Quarter ended on or before (actual & tentative for future
quarters)

| Unaudited 1st quarter results | August 14, 2023(Subject to Limited Review) |
| Unaudited 2nd quarter results | November 14, 2023(Subject to Limited Review) |
| Unaudited 3rd quarter results | February 14, 2024(Subject to Limited Review) |
| FY 2023-24 Audited Financial Results | May 30, 2024 (Audited) |
```

### Chunk 132

_text · pages 86–87 · 283 words · 550 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
4. Dividend Payment Date

The Company has not recommended/ paid any dividend for the period under review.

5. Listing on Stock Exchanges

Equity Shares of the Company are currently listed on National Stock Exchange of India Limited (NSE) Address:
“Exchange Plaza” C-1, Block G, Bandra
Kurla Complex, Bandra (East), Mumbai 400 051. National Securities Depository Limited (NSDL) and Central
Depository Services (India) Limited
(CDSL) are the depositories for the equity shares of the Company. The Annual Listing Fee for the financial
year 2023-24 has been paid by the Company
to the NSE where the Company’s equity shares are listed. The equity shares of the Company have not been
suspended from trading on the Stock
Exchange or by any Regulatory/Statutory Authority.

6. Payment of Depository Fees

Annual Custody/Issuer fee for the year 2023-24 has been paid by the Company to CDSL and NSDL.

7. Registered Address

| E2E Networks Limited | 84 |

Awfis, First Floor, A-24/9, Mohan Cooperative Industrial Estate, Mathura Road, New Delhi – 110044

8. Communication Address

Awfis, First Floor, A-24/9, Mohan Cooperative Industrial Estate, Mathura Road, New Delhi - 110044
Website: https://www.e2enetworks.com

9. International Securities Identification Number (ISIN)

ISIN is an Identification Number for traded Shares. This number needs to be quoted in each transaction
relating to the dematerialized Equity Shares
of the Company. The Company’s ISIN number for its Equity Shares is INE255Z01019.

10. Stock Code

The Company is listed on NSE having Stock Code – E2E

11. Market Price Data

The Company’s monthly high and low share price data as well as the total volume during each month in the FY
2022-23 on the NSE is as mentioned
below:

Month High Low Total Volume
```

### Chunk 133

_table · pages 87–87 · 183 words · 513 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
10. Stock Code
The Company is listed on NSE having Stock Code – E2E
11. Market Price Data
The Company’s monthly high and low share price data as well as the total volume during each month in the FY 2022-23 on the NSE is as mentioned
below:
Month High Low Total Volume

| April 2022 | 169.00 | 123.00 | 2,39,286 |
| May 2022 | 165.00 | 110.20 | 79,621 |
| June 2022 | 138.50 | 94.35 | 155,591 |
| July 2022 | 181.30 | 122.15 | 346,382 |
| August 2022 | 224.70 | 130.10 | 508,636 |
| September 2022 | 220.00 | 174.00 | 120,746 |
| October 2022 | 199.00 | 160.50 | 75,037 |
| November 2022 | 223.65 | 167.00 | 163,510 |
| December 2022 | 228.70 | 175.00 | 162,125 |
| January 2023 | 200.00 | 168.20 | 120,659 |
| February 2023 | 180.95 | 135.95 | 103,912 |
| March 2023 | 182.45 | 139.05 | 206,486 |
| E2E Networks Limited | 85 |
```

### Chunk 134

_text · pages 88–88 · 35 words · 76 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
12. Stock Market Data:

E2E Share Price Performance vs. Nifty

13. Distribution of Shareholding:

Sr. No. No. of Shares No. of % of Shares % of
Shareholders Shareholders Total Share Capital
```

### Chunk 135

_table · pages 88–88 · 173 words · 494 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
12. Stock Market Data:
E2E Share Price Performance vs. Nifty
13. Distribution of Shareholding:
Sr. No. No. of Shares No. of % of Shares % of
Shareholders Shareholders Total Share Capital

| 1 | 1 to 500 | 1305 | 76.0047 | 120,724 | 0.834 |
| 2 | 501 to 1000 | 96 | 5.5911 | 75,038 | 0.5184 |
| 3 | 1001 to 2000 | 154 | 8.9691 | 2,70,217 | 1.8668 |
| 4 | 2001 to 3000 | 36 | 2.0967 | 90,894 | 0.6279 |
| 5 | 3001 to 4000 | 30 | 1.7472 | 1,12,626 | 0.7781 |
| 6 | 4001 to 5000 | 11 | 0.6407 | 50,644 | 0.3499 |
| 7 | 5001 to 10000 | 39 | 2.2714 | 2,82,624 | 1.9525 |
| 8 | 10001 to above | 46 | 2.6791 | 1,34,72,359 | 93.0725 |
| Total | 1717 | 100% | 1,44,75,126 | 100.00% |
| E2E Networks Limited | 86 |
```

### Chunk 136

_text · pages 89–89 · 26 words · 64 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
14. Shareholding Pattern as on March 31, 2023:

Category No. of Shares Held Percentage of Shareholding
Shareholding of Promoter and Promoter Group
```

### Chunk 137

_table · pages 89–89 · 198 words · 478 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
14. Shareholding Pattern as on March 31, 2023:
Category No. of Shares Held Percentage of Shareholding
Shareholding of Promoter and Promoter Group

| Indian | 83,51,613 | 57.7 |
| Foreign | 2,90,918 | 2.01 |
| Total Shareholding of Promoter and Promoter Group | 86,42,531 | 59.71 |
| Public Shareholding |
| Institutions | 0 | 0 |
| Mutual Funds/Trusts | 0 | 0 |
| Venture Capital Fund | 11,96,760 | 8.27 |
| Alternate Investment Funds | 975,652 | 6.74 |
| Qualified Institutional Buyer | 0 | 0 |
| Financial Institutions/Banks | 0 | 0 |
| Foreign Portfolio Investors | 2,40,000 | 1.66 |
| Non-Institutions | 0 | 0 |
| Bodies Corporate | 87,847 | 0.61 |
| NBFC | 0 | 0 |
| NRI | 51,301 | 0.35 |
| Foreign National Individual Investors | 3,24,167 | 2.24 |
| Indian Public and Others | 28,87,868 | 19.94 |
| Total Public Shareholding | 57,63,595 | 39.81 |
| Employee ESOP Trust | 69,000 | 0.48 |
| Total Shareholding | 1,44,75,126 | 100.00 |
| E2E Networks Limited | 87 |
```

### Chunk 138

_text · pages 90–90 · 35 words · 67 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
15. List of Public Shareholders holding more than 1% shareholding of the Company as on March 31, 2023

Serial No. Name of Shareholder No. of Shares held % of Total Capital
```

### Chunk 139

_table · pages 90–90 · 124 words · 299 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
15. List of Public Shareholders holding more than 1% shareholding of the Company as on March 31, 2023
Serial No. Name of Shareholder No. of Shares held % of Total Capital

| 1. | Blume Ventures Fund I | 11,96,760 | 8.27 |
| 2. | Blume Ventures Fund Ia | 5,23,652 | 3.62 |
| 3. | Airavat Capital Trust | 4,52,000 | 3.12 |
| 4. | Mukesh Kumar Raheja | 4,48,000 | 3.09 |
| 5. | Freeman Murray | 324167 | 2.24 |
| 6. | Airavat Capital Holdings | 2,40,000 | 1.66 |
| 7. | Kotapalli Ravoof Mohamed Imran | 2,30,016 | 1.59 |
| 8. | Tripat Kaur | 2,16,999 | 1.5 |
```

### Chunk 140

_text · pages 90–91 · 94 words · 217 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
16. Dematerialization of Shares and Liquidity:

The Company’s Equity Shares are held with both the Depositories i.e. National Securities Depository Limited
(‘NSDL’) and Central Depository Services
(India) Limited (‘CDSL’). Further, out of total 1,44,75,126 Equity Shares of the Company, 1,41,50,959 Equity
Shares (97.76% of total share capital) are
held in electronic/ demat form as on March 31, 2023.

As on March 31, 2023, the number of Shares held in dematerialized and physical mode are as under:

| E2E Networks Limited | 88 |

Details No. of Shareholders No. of Shares
```

### Chunk 141

_table · pages 91–91 · 82 words · 183 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
As on March 31, 2023, the number of Shares held in dematerialized and physical mode are as under:
| E2E Networks Limited | 88 |
Details No. of Shareholders No. of Shares

| No. of shares in dematerialized form in CDSL | 1,173 | 98,95,322 |
| No. of shares in dematerialized form in NSDL | 543 | 42,55,637 |
| No. of shares in Physical | 1 | 3,24,167 |
| Total | 1,717 | 1,44,75,126 |
```

### Chunk 142

_text · pages 91–92 · 398 words · 745 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
17. Disclosure in respect of Equity Shares transferred in the Unclaimed Suspense Account
Not Applicable

18. Outstanding Global Depository Receipts (GDRs) / American Depository Receipts (ADRs) / Warrants or any
other Convertible
instruments, conversion date and likely impact on equity

Details of outstanding Stock Options are being uploaded on the website of the Company and same can be accessed
through following web link
https://www.e2enetworks.com/investors/employee-stock-option-schemes

Other than above, the Company has no outstanding ADR/GDR, options or rights to convert debentures, loans or
other instruments into the Equity
Shares as on March 31, 2023.

19. Registrar and Share Transfer Agent

All work related to Share Registry and Share Transfer, both in physical and electronic form, are handled by
the Company’s Registrar and Share Transfer
Agent, Link Intime India Private Limited.

Contact details of the Registrar and Share Transfer Agent are given hereunder:

Link Intime India Private Limited.
C-101, 247 Park, Lal Bahadur Shastri Marg,
Vikhroli (West), Mumbai - 400 083.
Website: www.linkintime.co.in

| E2E Networks Limited | 89 |

E-mail: delhi@linkintime.co.in
Investor Grievance Id: delhi@linkintime.co.in

20. Share Transfer System

The Company’s Registrar and Share Transfer Agent, process the share transfers and after completion of all
required formalities, return the shares in
the normal course within 15 days from the date of receipt if the documents are valid and complete in all
respects. Further, the RTA who is also the
Company’s Demat Registrars, requests for dematerialization of shares are processed and confirmation is given
by them to the respective depositories
i.e. National Securities Depository Limited (NSDL) and Central Depository Services India Limited (CDSL) within
15 days.

21. Plant Locations

Not Applicable.

22. Commodity Price Risk or Foreign Exchange Risk and Hedging Activities

The Company does not deal in any commodity risk or hedging activities and hence is not directly exposed to any
commodity price risk.
Foreign Currency risk is the risk that the fair value of future cash flows of an exposure will fluctuate
because of changes in foreign exchange rates.
The company does not have significant exposure in currency other than INR hence the foreign currency risk is
not material

23. Address for Correspondence with the Company

i. Details of Compliance Officer
Name : Richa Gupta
Official Address: Awfis, First Floor, A-24/9,Mohan Cooperative Industrial Estate, Mathura Road, Saidabad, New
Delhi-110044

ii. For Securities held in Physical form
Registrar And Transfer Agent

Link Intime India Pvt Ltd
```

### Chunk 143

_text · pages 92–94 · 405 words · 835 tokens · starts with overlap_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
Address for Correspondence with the Company

i. Details of Compliance Officer
Name : Richa Gupta
Official Address: Awfis, First Floor, A-24/9,Mohan Cooperative Industrial Estate, Mathura Road, Saidabad, New
Delhi-110044

ii. For Securities held in Physical form
Registrar And Transfer Agent

Link Intime India Pvt Ltd

Noble Heights, 1st Floor, Plot No. NH-2, TSC, C-1 Block, Near Savitri Market, Janakpuri, New Delhi-l10058
Registered Office Address: C-101, 1st Floor, 247 Park, Lal Bahadur Shastri Marg, Vikhroli (West), Mumbai 400
083

| E2E Networks Limited | 90 |

iii. For Securities held in Demat form
To the Investors' Depository Participant (s)
and/or
Registrar And Transfer Agent
Link Intime India Pvt Ltd
Noble Heights, 1st Floor, Plot No. NH-2, TSC, C-1 Block, Near Savitri Market, Janakpuri, New Delhi-l10058
Registered Office Address: C-101, 1st Floor, 247 Park, Lal Bahadur Shastri Marg, Vikhroli (West), Mumbai 400
083
iv. For Queries Relation to Retail Investors
Name : Richa Gupta
Official Address: Awfis, First Floor, A-24/9,Mohan Cooperative Industrial Estate, Mathura Road, Saidabad, New
Delhi-110044

v. For Queries related to Institutional Investors’ / Analysts’
Name : Richa Gupta
Official Address: Awfis, First Floor, A-24/9,Mohan Cooperative Industrial Estate, Mathura Road, Saidabad, New
Delhi-110044

| vi. | Credit Rating and Change /Revision in Credit Rating of the Company during the Financial Year 2022-23 |

The Company did not have any credit rating during the FY 2022-23.

24. Codes/ policies relating to corporate governance

The Board has laid down the following codes/ policies to ensure governance in an ethical manner:
Corporate Social Responsibility Policy

| Archival Policy on disclosure hosted on the Website of the Company | i. | Code of conduct for board members & senior management personnel | ii. | Code of conduct for Independent Directors | iii. | Nomination and Remuneration Policy | iv. | Terms and conditions of appointment of Independent Directors | v. | Policy for Preservation of Documents | vi. | Policy for Determination of Materiality of Information or Event | vii. | Key Managerial Personnel who are athorised for the purpose of determining materiality of an Event or Information as per | viii. | regulation 30 (5) of SEBI (Listing Obligations And Disclosure Requirements) Regulations, 2015 | ix. | Policy on determination of Material Subsidiary |

Policy on Familiarization Programmes for Independent Directors x. Policy on Succession Planning for the board
and Senior Management xi. xii.

| E2E Networks Limited | 91 |

Board Diversity Policy
```

### Chunk 144

_text · pages 94–95 · 426 words · 836 tokens · starts with overlap_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
| Policy on determination of Material Subsidiary |

Policy on Familiarization Programmes for Independent Directors x. Policy on Succession Planning for the board
and Senior Management xi. xii. | E2E Networks Limited | 91 |

Board Diversity Policy

| Policy On Related Party Transactions | xiii. | Code of Conduct for Prevention of Insider Trading | xiv. | Code of Practices and Procedures for Fair Discloures of Unpublsihed Price Sensitive | xv. | Information | xvi. | E2E’sWhistle Blower Policy/Vigil Mechanism Policy |

Policy on Sexual Harassment of Women at WorkplaceThe abovexvii.codes and policies are also available on the
website of the Company https://www.e2enetworks.com/investors/corporate-governance. xviii.
25. Disclosure on Materially Significant Related Party Transactions

All the contract/arrangements/transactions entered into with Related Parties as per the Act and Regulation 23
of the Listing Regulations during the
Financial Year 2022-23 were in ordinary course of business and on an arm’s length basis and do not attract
provisions of Section 188 of the Act.
Further, there was no materially significant related party transaction which required shareholder’s approval
and was required to be disclosed
quarterly along with the compliance report on Corporate Governance.

The required statements / disclosures with respect to the related party transactions are placed before the
Audit Committee on regular basis. Suitable
disclosures so required in accordance with the Indian Accounting Standards (Ind-AS) as notified under Section
133 of the Act have been made in notes
to the Financial Statements.

Further, the Company has not entered into any transaction of material nature with, the Directors or the
management, their subsidiaries or relatives
etc. that may have any potential conflict with the interest of the Company.

The Policy on Related Party Transactions may be accessed at the website of the Company on the following
link:26. Whistlehttps://global-uploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27895_Policy-
on-Related-Party-Transactions.pdf.Blower Policy / Vigil Mechanism

The Company promotes ethical behaviour in all its operations and has put in place a mechanism for reporting
illegal or unethical behaviour. The
Company has a Vigil Mechanism and Whistle Blower Policy in place under which the employees are free to report
fraudulent practices, corruption and
breaches of Code of Conduct in the most discreet manner. Employees may also report any matter of concern
directly to the Chairman of the Audit
Committee. During the year under review, no employee was denied access to the Audit Committee. The detail of
establishment of such
Policy/Mechanism is also uploaded on the website of the Company & can be accessed through the following link
https://globaluploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27a3c_Whistle-Blower-Policy.pdf

| E2E Networks Limited | 92 |

27. Compliance Certificate by CEO and CFO
```

### Chunk 145

_text · pages 95–96 · 412 words · 950 tokens · starts with overlap_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
The detail of establishment of such
Policy/Mechanism is also uploaded on the website of the Company & can be accessed through the following link
https://globaluploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27a3c_Whistle-Blower-Policy.pdf

| E2E Networks Limited | 92 |

27. Compliance Certificate by CEO and CFO

The Compliance Certificate by Chief Executive Officer and Chief Financial Officer are provided on a quarterly
basis. The Compliance Certificate as
required under the Regulation 17 of the Listing Regulations confirming compliance of Part B of Schedule II of
the Listing Regulations was placed before
the Board at its meeting and the same is annexed and forms part of this Report.

28. Code of Conduct

In compliance with Regulation 17 of the Listing Regulations, the Company has formulated and adopted a Code of
Conduct for its Board Members and
Senior Management and the same is available on our website
https://global-uploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27a5e_Code-of-Conduct-of-
directors-and-seniormanagement.pdf

The Code of Conduct inter-alia includes the duties of the Independent Directors as prescribed under the Act.
All the Board Members and the Senior
Management Personnel of the Company have affirmed compliance with the Code of Conduct as on March 31, 2023.

A declaration to this effect, duly signed by the Managing Director, is enclosed and forms part of this Report.

29. Procedures for Fair Disclosure of Unpublished Price Sensitive Information and Prevention of Insider
Trading

The Company has adopted the Code of Practices and Procedures for Fair Disclosure of Unpublished Price
Sensitive Information (“Fair Disclosure
Code”) and Code of Conduct for Prevention of Insider Trading (“Insider Code”) with a view to deal with
Unpublished Price Sensitive Information and
trading in securities by Directors, Employees of the Company / Designated Persons and Connected Persons. The
Company Secretary is Compliance
Officer for the purpose of Insider Code.

Both the Fair Practice Code and Insider Code have been posted on the website of the Company on the following
link
https://global-uploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27a64_Code-for-Fair-
Disclosure.pdf
https://global-uploads.webflow.com/6473d8d02a3cf26273f27856/6473d8d02a3cf26273f27890_Code-of-Conduct-for-
Prevention-of-Insider-
Trading.pdf

30. Risk Management

The Company has a Risk Management process which provides an integrated approach for managing the risks in
various aspects of the business. A
write-up on the above is provided in the Management Discussion and Analysis Report.

| E2E Networks Limited | 93 |

31. Details of Utilisation of Fund Raised through Preferential Allotment or Qualiϐied Institutions Placement
As Speciϐied Under Regulation

During the period under review, the Company has not raised any funds through preferential allotment or
qualiϐied institutions placement as speciϐied
under regulation 32(7A) of the Listing Regulations.

32. Business Responsibility and Sustainability Report (“BRSR”)
```

### Chunk 146

_text · pages 96–97 · 399 words · 660 tokens · starts with overlap_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
32. Business Responsibility and Sustainability Report (“BRSR”)

Regulation 34 of the Listing Regulations mandates the inclusion of the Business Responsibility and
Sustainability Report as part of the Annual Report
for the top 1000 listed entities based on market capitalization as at the end of immediate previous financial
year with effect from the financial year

Since, the Company does not fall under list of Top 1000 listed entities as on March 31, 2023, the report under
aforesaid provisions does not form part
of this Annual Report.

There was no instance during financial year 2022-23 when the Board had not accepted any recommendation of any
Committee of the Board.

33. Subsidiary Companies
During the period under review, the Company does not have any subsidiary and therefore provisions relating to
disclosures of subsidiaries are not
applicable to the Company.

34. Compliance with SEBI (Listing Obligations and Disclosure Requirements) Regulations, 2015

A Certiϐicate on Corporate Governance obtained from MAKS & Co., Practicing Company Secretaries for compliance
with SEBI (Listing Obligations and
Disclosure Requirements) Regulations, 2015, and is enclosed at the end of this Report.

Certiϐicate from practicing company secretary for Non-disqualiϐication of Directors:The35. Company has
obtained a certificate from a Company Secretary in Practice that none of the Directors on the Board of the
Company have been
debarred or disqualified from being appointed or continuing as Directors of companies by the SEBI/ Ministry of
Corporate Affairs or any such statutory
authority in accordance with Listing Regulations and is enclosed at the end of this Report.

| E2E Networks Limited | 94 |

36. Disclosure on accounting treatment in preparation of financial statements:

The Company has prepared financial statements in accordance with Indian Accounting Standards (“Ind AS”)
notified under the Companies (Indian
Accounting Standards) Rules, 2015 and relevant amendment rules issued thereafter.

The significant accounting policies which are consistently applied have been set out in the Notes to the
financial statements.

37. Management Discussion and Analysis Report

The Management Discussion and Analysis report forms part of the Annual Report.

38. Total Fees for all Services paid by the Company on consolidated basis to Statutory Auditors and all
entities in the Network Firm/
Network Entity of which the Statutory Auditor is a part

During the year under review, the total fees for all services paid by E2E Networks Limited to the statutory
auditors are as follows:
(INR in lakhs)
Fees Amount
```

### Chunk 147

_table · pages 97–97 · 72 words · 141 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
During the year under review, the total fees for all services paid by E2E Networks Limited to the statutory auditors are as follows:
(INR in lakhs)
Fees Amount

| Audit Fee | 2.50 |
| Advisory & Certification charges | 0 |
| Reimbursement of expenses | 0.38 |
| Tax Audit Fee | 0.50 |
| Total | 3.38 |
| E2E Networks Limited | 95 |
```

### Chunk 148

_text · pages 98–98 · 305 words · 541 tokens_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
39. Disclosures in Relation to the Sexual Harassment of Women at Workplace (Prevention, Prohibition and
Redressal) Act, 2013

As per the requirement of the Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal)
Act, 2013 and Rules made
thereunder, the details of the cases reported during the Financial Year 2022-23 are mentioned hereunder:

Details No. of Complaints
Number of Complaints at the beginning of the financial year Nil
Number of complaints filed during the financial year Nil
Number of complaints disposed of during the financial year Nil
Number of complaints pending as on end of the financial year Nil

40. Disclosure by Listed Entity and its Subsidiaries of ‘Loans and Advances’ in the nature of Loans to
Firms/Companies in which
Directors are interested by name and amount

The Company has not provided any Loans and Advances to Firms/Companies in which the Directors are interested
during FY 2022-23.

41. Details of Non-Compliance by the Company, Penalties, Strictures Imposed on the Company by the Stock
Exchange(s) or SEBI or
Any Statutory Authority, on any Matter Related to Capital Markets, During the last three years

No penalty or stricture has been imposed by the Stock Exchanges or SEBI or any other authority, during the
last 3 (three) years on the Company.

42. Disclosure of compliance with mandatory and adoption of discretionary requirements under SEBI (Listing
Obligations and Disclosure
Requirements) Regulations, 2015:

The Company has complied with Corporate Governance requirements specified in Regulation 17 to 27 and Clause
(b) to (i) of sub-regulation (2) of
Regulation 46 under the Listing Regulations.

The Company has adopted the non-mandatory requirements of Regulation 27 read with Part E of Schedule II of the
Listing Regulations in following
manner:

i. The Board
The Chairperson of the Company is Promoter Executive Director.

| E2E Networks Limited | 96 |
```

### Chunk 149

_text · pages 99–100 · 445 words · 770 tokens · starts with overlap_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
The Company has adopted the non-mandatory requirements of Regulation 27 read with Part E of Schedule II of the
Listing Regulations in following
manner:

i. The Board
The Chairperson of the Company is Promoter Executive Director. | E2E Networks Limited | 96 |

ii. Shareholders’ Rights
The quarterly results of the Company are published in English newspaper (Financial Express, All Edition) and a
Hindi newspaper (Jansatta,
Delhi Edition), having wide circulation. Further, the quarterly results are also posted on the website of the
Company and can be accessed on
https://www.e2enetworks.com/investors/financial-results In view of the forgoing, the half yearly results of
the Company are not sent to the
Shareholders individually. The complete copy of the Annual Report is sent to the shareholders of the Company.
Further, the Company also
publish the other important notices/information in English newspaper (Financial Express, All Edition) and a
Hindi newspaper (Jansatta, Delhi
Edition), having wide circulation besides uploading the same on the website of the Company.

iii. Modified/Un-Modified Opinion(s) in Audit Report
The Auditors have issued their reports on the Standalone Financial statements / results for financial year
ended March 31, 2023 with
unmodified opinion.

iv. Separate posts of Chairperson and the Managing Director or the Chief Executive Officer
The Chairperson of the Company is Promoter Executive Director who is also the Managing Director.

v. Reporting of Internal Auditor
The Internal Auditors of the Company reports directly to the Audit Committee of the Company.

43. Non-compliance of Regulations relating to Corporate Governance under SEBI (Listing Obligations And
Disclosure Requirements)
Regulations, 2015, if any:
The Company is fully compliant with Listing Regulations and there are no such non-compliances.

On behalf of the Board of Directors

Sd/-
Place: New Delhi Sd/- Srishti Baweja
Tarun Dua Whole Time Director

| Date: August 28, 2023 | Managing Director | DIN:08057000 | DIN: 02696789 |
| E2E Networks Limited | 97 |

CEO /CFO Certification

We, Tarun Dua, Managing Director and Megha Raheja, CFO of E2E Networks Limited (the Company) hereby certify
that:

i. We, have reviewed financial statements and the cash flow statement for the year ended March 31, 2023 and
that to the best of our knowledge and
belief:

(1) These statements do not contain any materially untrue statement or omit any material fact or contain
statements that might be misleading;

(2) These statements together present a true and fair view of the Company’s affairs and are in compliance with
existing accounting standards,
applicable laws and regulations.

B. There are, to the best of our knowledge and belief, no transactions entered into by the Company during the
year which are fraudulent, illegal or
violative of the Company’s code of conduct.
```

### Chunk 150

_text · pages 100–100 · 225 words · 322 tokens · starts with overlap_

```text
## GENERAL SHAREHOLDERS’ INFORMATION:
B. There are, to the best of our knowledge and belief, no transactions entered into by the Company during the
year which are fraudulent, illegal or
violative of the Company’s code of conduct.

C. We, accept responsibility for establishing and maintaining internal controls for financial reporting and
that we have evaluated the effectiveness
of internal control systems of the listed entity pertaining to financial reporting and we have disclosed to
the auditors and the audit committee,
deficiencies in the design or operation of such internal controls, if any, of which we are aware and the steps
we have taken or propose to take to
rectify these deficiencies.

D. We have indicated to the auditors and the Audit committee that:
1. There has not been any significant changes in internal control over financial reporting during the year
under reference;
2. There has not been any significant changes in accounting policies during the year under review; and
3. There has not been any instances of significant fraud of which we had become aware and the involvement
therein, if any, of the
management or an employee having a significant role in the Company’s internal control system over financial
reporting.

Place: New Delhi Tarun Dua Megha Raheja
Date: May 23, 2023 (Chairman and Managin director) (Chef Financial Officer)

| E2E Networks Limited | 98 |
```

### Chunk 151

_text · pages 101–102 · 113 words · 227 tokens_

```text
## DECLARATION BY CHAIRMAN & MANAGING DIRECTOR
This is to confirm that the Company has adopted a Code of Conduct for its Board Members and Senior Management
and the same is available on the
Company’s website https://www.e2enetworks.com.

It is further certified that the Directors and Senior Management have affirmed their compliance with the Code
for the year ended March 31, 2023.

For & on behalf of E2E Networks Limited
and its Board of Directors

Tarun Dua
Place: New Delhi Chairman & Managing Director

| Date: August 24, 2023 | DIN: 02696789 |
| E2E Networks Limited | 99 |

CERTIFICATE ON COMPLIANCE WITH THE CORPORATE GOVERNANCE REQUIREMENTS UNDER SEBI (LISTING OBLIGATIONS AND
DISCLOSURE
```

### Chunk 152

_text · pages 102–102 · 284 words · 491 tokens_

```text
## [CIN: L72900DL2009PLC341980]
The Members
Regd. Office: Awfis, First Floor, A-24/9, Mohan Cooperative Industrial Estate, Mathura Road, New Delhi – 110
044

## [CIN: L72900DL2009PLC341980]

We have examined the compliance of conditions of Corporate Governance by E2E Networks Limited (“the Company”,
for the financial year ended
March 31, 2023 as stipulated under Regulations 17 to 27, clauses (b to (i of Regulation 46(2 and Para C and D
of Schedule V to the SEBI (Listing
Obligations and Disclosure Requirements Regulations, 2015 (“SEBI LODR Regulations” pursuant to the Listing
Agreement of the Company with the
National Stock Exchange of India Ltd (“the NSE”.
The compliance of conditions of Corporate Governance as stipulated under the SEBI LODR Regulations is the
responsibility of the Management of the
Company including the preparation and maintenance of all the relevant records and documents. Our examination
was limited to procedures and
implementation thereof, adopted by the Company for ensuring the compliance of the conditions of Corporate
Governance. It is neither an audit nor an
expression of opinion on the financial statements of the Company.
In our opinion and to the best of our information and according to the explanations given to us, we certify
that the Company has complied with the
conditions of Corporate Governance as stipulated under Regulations 17 to 27, clauses (b to (i of Regulation
46(2 and Para C and D of Schedule V to
the SEBI LODR Regulations for the year ended on March 31, 2023.
We further state that such compliance is neither an assurance as to the future viability of the Company nor
the efficiency or effectiveness with which
the management has conducted the affairs of the Company.

For M/s. MAKS & Co.,
Company Secretaries
```

### Chunk 153

_text · pages 102–103 · 82 words · 256 tokens_

```text
## CERTIFICATE OF NON-DISQUALIFICATION OF DIRECTORS
Sd/-
Ankush Agarwal
Partner
Membership No: F9719
Certificate of Practice No: 14486
Peer Re/view Certificate No.: 2064/2022

## UDIN: F009719E000769302

Place: Noida, U.P

| E2E Networks Limited | 100 |

## CERTIFICATE OF NON-DISQUALIFICATION OF DIRECTORS

(Pursuant to Regulation 34(3) and Schedule V Para C clause (10)(i) of the SEBI (Listing

Obligations and Disclosure Requirements) Regulations, 2015)

The Members,
Regd. Office: Awfis, First Floor, A-24/9,
Mohan Cooperative Industrial Estate,
Mathura Road, New Delhi – 110 044
```

### Chunk 154

_text · pages 103–103 · 200 words · 374 tokens_

```text
## [CIN: L72900DL2009PLC341980]
We have examined the relevant registers, records, forms, returns and disclosures received from the Directors
of E2E Networks Limited, having
CIN: L72900DL2009PLC341980 and having registered office at, Awfis, First Floor, A-24/9, Mohan Cooperative
Industrial Estate, Mathura Road,
New Delhi - 110 044 (hereinafter referred to as ‘the Company’), produced before me by the Company for the
purpose of issuing this Certificate
in accordance with Regulation 34(3) read with Schedule V Para-C Sub clause 10(i) of the Securities and
Exchange Board of India (Listing
Obligations and Disclosure Requirements) Regulations, 2015.

In our opinion and to the best of our information and according to the verifications (including Director
Identification Number (DIN) status at
the portal www.mca.gov.in) as considered necessary and explanations furnished to us by the Company & its
officers, we hereby certify that
none of the Directors on the Board of the Company as stated below for the Financial Year ended on 31st March,
2023 have been debarred or
disqualified from being appointed or continuing as Directors of companies by the Securities and Exchange Board
of India, Ministry of Corporate
Affairs, or any such other Statutory Authority as applicable.

S. No. Name of Director DIN Date of Appointment
```

### Chunk 155

_table · pages 103–103 · 87 words · 276 tokens_

```text
## [CIN: L72900DL2009PLC341980]
S. No. Name of Director DIN Date of Appointment

| 1 | Mr. Tarun Dua | 02696789 | 20/08/2009 |
| 2 | Mrs. Srishti Baweja | 08057000 | 31/01/2018 |
| 3 | Mr. Gaurav Munjal | 02363421 | 09/02/2018 |
| 4 | Mr. Aditya Bhushan | 01148272 | 22/10/2021 |
| 5 | Mr. Naman Kailashprasad Sarawagi | 05295642 | 18/02/2019 |
| 6 | Ms. Varun Pratap Rajda | 07468016 | 09/02/2018 |
| E2E Networks Limited | 101 |
```

### Chunk 156

_text · pages 104–105 · 318 words · 567 tokens_

```text
## [CIN: L72900DL2009PLC341980]
Ensuring the eligibility for the appointment and continuity of every Director on the Board is the
responsibility of the management of the
Company. Our responsibility is to express an opinion on these based on our verification. This certificate is
neither an assurance as to the future
viability of the Company nor of the efficiency or effectiveness with which the management has conducted the
affairs of the Company.

For M/s. MAKS & Co.,
Company Secretaries

## INDEPENDENT AUDITOR’S REPORT
Ankush Agarwal
Partner
Membership No: F9719
Certificate of Practice No: 14486
Peer Review Certificate No.: 2064/2022

## UDIN: F009719E000769423

Place: Noida, U.P.

| E2E Networks Limited | 102 |

## INDEPENDENT AUDITOR’S REPORT

The Members of E2E Networks Limited

Report on the Financial Statements

OPINION

We have audited the accompanying financial statements of E2E Networks Limited (“the Company”), which comprise
the Balance Sheet
as at 31st March, 2023, the Statement of Profit and Loss (including other comprehensive income), Statement of
Changes in Equity and the
Statement of Cash Flow for the year ended, and the notes to financial statements including a summary of the
significant accounting policies
and other explanatory information (hereinafter referred to as “financial statement”).

In our opinion and to the best of our information and according to the explanations given to us, the aforesaid
financial statements gives
the information required by the Companies Act 2013 (the ‘Act’) in the manner so required and give a true and
fair view in conformity with
the accounting principles generally accepted in India including Indian Accounting standards (‘Ind AS’)
specified under section 133 of the
Act read with the Companies (Indian Accounting Standards) Rules, 2015, as amended, (“Ind AS”), of the state of
affairs of the Company
(financial position) as at 31st March, 2023, and its profit (financial performance including other
comprehensive income), the changes in
equity and its cash flows for the year ended on that date.
```

### Chunk 157

_text · pages 105–105 · 147 words · 204 tokens_

```text
## BASIS FOR OPINION
We conducted our audit of the financial statements in accordance with standard on auditing specified under
section 143(10) of the Act.
Our responsibilities under those standards are further described in the Auditor’s Responsibility for the audit
of the financial statements
section of our report. We are independent of the company in accordance with the Code of Ethics issued by the
institute of Chartered
Accountant of India (“ICAI”) together with the ethical requirements that are relevant to our audit of the
financial statements under the
provisions of the Act and the Rules made thereunder, and we have fulfilled our ethical responsibilities in
accordance with these
requirements and the ICAI’s Code of Ethics. We believe that the audit evidence obtained by us is sufficient
and appropriate to provide a
basis for our audit opinion on the financial statements.

| E2E Networks Limited | 103 |
```

### Chunk 158

_text · pages 106–107 · 371 words · 515 tokens_

```text
## KEY AUDIT MATTER
Key audit matters are those matters that, in our professional judgment, were of most significance in our audit
of the financial statements
of the current period. These matters were addressed in the context of our audit of the financial statements as
a whole, and in forming our
opinion thereon, and we do not provide a separate opinion on these matters.

Key Audit Matter Auditor’s Response

Revenue Recognition Our audit procedures included the following:

The Company recognizes revenue upon transfer of control of promised services Obtained an understanding of the
systems, processes and
to customers in an amount that reflects the consideration the Company expects to controls implemented by the
company for recording and
receive in exchange for those services. The Company provides cloud platform and computing revenue and the
associated contract assets, unearned
configuration services, including but not limited to smart dedicated servers, and deferred revenue balances.
graphics processing units,
object storage, content delivery network service and continuous data protection Our principal audit procedures
related to the Company's
back up services (“Services”) to its customers. revenue recognition for included the following:

Significant judgment is exercised by the Company in determining revenue • We tested the effectiveness of
controls related to the
recognition for these customers, and includes the following: - identification of distinct performance
obligations, the
determination of the timing of revenue recognition, and
a) The pattern of delivery (i.e., timing of when revenue is recognized) the estimation of variable
consideration.
for each distinct performance obligation. • We tested the mathematical accuracy of management's
b) Identification and treatment of contract terms that may impact the calculations of revenue and the
associated timing of
timing and amount of revenue recognized (e.g., variable revenue recognized in the financial statements.
consideration, optional purchases, and free services).
c) Determination of stand-alone selling prices for each distinct
performance obligation and for products and services that are not
sold separately.
Given these factors and due to the volume of transactions, the related audit effort
in evaluating management's judgments in determining revenue recognition for
these customer contracts was extensive and required a high degree of auditor
judgment.

| E2E Networks Limited | 104 |

Revaluation of Intangible assets Our audit procedures included the following:
```

### Chunk 159

_text · pages 107–107 · 217 words · 343 tokens · starts with overlap_

```text
## KEY AUDIT MATTER
| E2E Networks Limited | 104 |

Revaluation of Intangible assets Our audit procedures included the following:

Management has estimated the fair value of the certain class of Company’s Our procedures in relation to
management’s valuation of
intangible assets viz.IP addresses, to be INR 1,336.05 lakhs as at March 31, 2023 intangibles included:
with a revaluation gain for the year ended March 31, 2023 recorded in the
statement of profit or loss of INR 28 lakhs. Independent external valuations a) Evaluation of the independent
external valuers’
were obtained in respect of the value of intangible assets fair valued by the competence, capabilities and
objectivity;
Company in order to support management’s estimates. The valuations are b) Assessing the methodologies used and
the
dependent on certain key assumptions that require significant management appropriateness of the key
assumptions based on our
judgement including technological environment and availability of active knowledge of the technology industry,
discussion with
market. The increase in fair values mainly relates to movements in prices of management, discussion with
technology professionals;
intangibles in the active market. and
c) Checking, on a sample basis, the accuracy and relevance
of the input data used, including the visit of websites
where these intangibles are traded.

We found the key assumptions were supported by the available
evidence.
```

### Chunk 160

_text · pages 107–108 · 234 words · 351 tokens_

```text
## INFORMATION OTHER THAN THE FINANCIAL STATEMENTS AND AUDITOR’S REPORT THEREON
The company’s management and board of directors are responsible for the other information. The other
information comprises the
information included in Management Discussion and Analysis, Board’s Report including Annexures to Board’s
Report, Business
Responsibility Report and Corporate Governance Report, but does not include the financial statements and our
auditor’s report
thereon. The Management Discussion and Analysis, Board’s Report including Annexures to Board’s Report,
Business Responsibility
Report and Corporate Governance Report are expected to be made available to us after the date of this
auditor's report.

Our opinion on the financial statements does not cover the other information and we will not express any form
of assurance
conclusion thereon.

| E2E Networks Limited | 105 |

In connection with our audit report of the financial statements, our responsibility is to read the other
information identified above
when it becomes available and, in doing so, consider whether the other information is materially inconsistent
with the financial
statements or our knowledge obtained in the audit or otherwise appears to be materially misstated.

When we read the Management Discussion and Analysis, Board’s Report including Annexures to Board’s Report,
Business
Responsibility Report and Corporate Governance Report, if we conclude that there is material misstatement
therein, we are required
to communicate the matter to those charged with governance and if required issue a revised Audit report on
financial statement.
```

### Chunk 161

_text · pages 108–108 · 266 words · 365 tokens_

```text
## RESPONSIBILITY OF MANAGEMENT FOR FINANCIAL STATEMENTS
The Company’s Board of Directors is responsible for the matters stated in sub-section 5 of Section 134 of the
Companies Act, 2013
(“the Act”) with respect to the preparation of these financial statements that give a true and fair view of
the financial position,
financial performance including other comprehensive income, changes in equity and cash flows of the Company in
accordance with
the accounting principles generally accepted in India, including the Indian Accounting Standards specified
under Section 133 of the
Act read with relevant rules issued thereunder.

This responsibility also includes maintenance of adequate accounting records in accordance with the provisions
of the Act for
safeguarding the assets of the Company and for preventing and detecting frauds and other irregularities;
selection and application
of appropriate accounting policies; making judgments and estimates that are reasonable and prudent; and
design, implementation
and maintenance of adequate internal financial controls, that were operating effectively for ensuring the
accuracy and completeness
of the accounting records, relevant to the preparation and presentation of the financial statements that give
a true and fair view and
are free from material misstatement, whether due to fraud or error.

In preparing the financial statements, management is responsible for assessing the company’s ability to
continue as a going concern,
disclosing as applicable, matters related to going concern and using the going concern basis of accounting
unless management either
intend to liquidate the company or to cease operation, or has no realistic alternative but to do so.

The board of directors are also responsible for overseeing the Company’s financial reporting process.
```

### Chunk 162

_text · pages 108–109 · 299 words · 422 tokens_

```text
## AUDITORS’ RESPONSIBILITY FOR THE AUDIT OF FINANCIAL STATEMENTS
Our objectives are to obtain reasonable assurance about whether the financial statements as a whole are free
from material
misstatement, whether due to fraud or error, and to issue an auditor’s report that includes our opinion.
Reasonable assurance is a
high level of assurance but is not a guarantee that an audit conducted in accordance with Standards on
Auditing will always detect a

| E2E Networks Limited | 106 |

material misstatement when it exists. Misstatements can arise from fraud or error and are considered material
if, individually or in
the aggregate, they could reasonably be expected to influence the economic decisions of users taken on the
basis of these financial
statements.

As part of an audit in accordance with Standards on Auditing, we exercise professional judgment and maintain
professional
scepticism throughout the audit. We also:

• Identify and assess the risks of material misstatement of the financial statements, whether due to fraud or
error, design and
perform audit procedures responsive to those risks, and obtain audit evidence that is sufficient and
appropriate to provide a
basis for our opinion. The risk of not detecting a material misstatement resulting from fraud is higher than
for one resulting
from error, as fraud may involve collusion, forgery, intentional omissions, misrepresentations, or the
override of internal
control;

• Obtain an understanding of internal control relevant to the audit in order to design audit procedures that
are appropriate in
the circumstances. Under Section 143(3)(i) of the Act, we are also responsible for explaining our opinion on
whether the
company has adequate internal financial controls system in place and the operating effectiveness of such
controls;

• Evaluate the appropriateness of accounting policies used and the reasonableness of accounting estimates and
related
disclosures made by management;
```

### Chunk 163

_text · pages 109–110 · 320 words · 441 tokens_

```text
## AUDITORS’ RESPONSIBILITY FOR THE AUDIT OF FINANCIAL STATEMENTS
• Conclude on the appropriateness of management’s use of the going concern basis of accounting and, based on
the audit
evidence obtained, whether a material uncertainty exists related to events or conditions that may cast
significant doubt on
the Company’s ability to continue as a going concern. If we conclude that a material uncertainty exists, we
are required to
draw attention in our auditor’s report to the related disclosures in the financial statements or, if such
disclosures are
inadequate, to modify our opinion. Our conclusions are based on the audit evidence obtained up to the date of
our auditor’s
report. However, future events or conditions may cause the Company to cease to continue as a going concern and

• Evaluate the overall presentation, structure and content of the financial statements, including the
disclosures, and whether
the financial statements represent the underlying transactions and events in a manner that achieves fair
presentation.

| E2E Networks Limited | 107 |

Materiality is the magnitude of misstatements in the financial statements that, individually or in aggregate,
makes it probable that
the economic decisions of a reasonably knowledgeable user of the financial statements may be influenced. We
consider quantitative
materiality and qualitative factors in (i) planning the scope of our audit work and in evaluating the results
of our work; and (ii) to
evaluate the effect of any identified misstatements in the financial statements.

We communicate with those charged with governance regarding, among other matters, the planned scope and timing
of the audit
and significant audit findings, including any significant deficiencies in internal control that we identify
during our audit.

We also provide those charged with governance with a statement that we have complied with relevant ethical
requirements
regarding independence, and to communicate with them all relationships and other matters that may reasonably
be thought to bear
on our independence, and where applicable, related safeguards.
```

### Chunk 164

_text · pages 110–111 · 389 words · 588 tokens_

```text
## REPORT ON OTHER LEGAL AND REGULATORY REQUIREMENTS
1. As required by the Companies (Auditor’s Report) Order, 2020 (‘the Order’), issued by the Central Government
of India in exercise of
powers conferred by sub-section 11 of section 143 of the Act, we enclose in the “Annexure A” a statement on
the matters specified in
paragraphs 3 and 4 of the Order.

2. As required by sub-section 3 of Section 143 of the Act, we report that:

a) We have sought and obtained all the information and explanations which to the best of our knowledge and
belief were necessary
for the purposes of our audit.

b) In our opinion, proper books of account as required by law have been kept by the Company so far as it
appears from our
examination of those books.

c) The Balance Sheet, The Statement of Profit and Loss (including other comprehensive income), The Statement
of Changes in
Equity and The Statement of Cash Flows dealt with by this Report are in agreement with the books of account.

d) In our opinion, the aforesaid financial statements comply with the Indian Accounting Standards specified
under Section 133 of
the Act, as applicable, read with relevant rules issued thereunder.

| E2E Networks Limited | 108 |

e) On the basis of the written representation received from the Directors as on 31st March, 2023, taken on
record by the Board of
Directors, none of the Directors is disqualified as on 31st March, 2023 from being appointed as a Directors in
terms of section
164(2) of the Act.

f) With respect to the adequacy of the internal financial controls over financial reporting of the Company and
the operating
effectiveness of such controls, refer to our separate report in “Annexure B”. Our report expresses an
unmodified opinion on the
adequacy and operating effectiveness of the Company’s internal financial control over financial reporting.

g) With respect to the other matters to be included in the Auditors’ Report in accordance with Rule 11 of the
Companies (Audit and
Auditors) Rules, 2014, in our opinion and to the best of our information and according to the explanations
given to us:

i. The Company has disclosed the impact of pending litigations on its financial position in its financial
statement in
accordance with the generally accepted accounting practice. Refer Note 29 of the financial statements.
```

### Chunk 165

_text · pages 111–112 · 427 words · 645 tokens · starts with overlap_

```text
## REPORT ON OTHER LEGAL AND REGULATORY REQUIREMENTS
The Company has disclosed the impact of pending litigations on its financial position in its financial
statement in
accordance with the generally accepted accounting practice. Refer Note 29 of the financial statements.

ii. The Company did not have any long- term contracts including derivative contracts, other than those which
have already
been provided for which there were no material foreseeable losses.

iii. There has been no delay in transferring amounts, required to be transferred, to the Investor Education
and Protection
Fund by the Company.

| iv. | (a) The management has represented in Note 41(3) that, to the best of its knowledge and belief, no funds (which are |

material either individually or in the aggregate) have been advanced or loaned or invested (either from
borrowed funds
or share premium or any other sources or kind of funds) by the company to or in any other person(s) or
entity(ies),
including foreign entities (“Intermediaries”), with the understanding, whether recorded in writing or
otherwise, that the
Intermediary shall, whether, directly or indirectly lend or invest in other persons or entities identified in
any manner
whatsoever by or on behalf of the company (“Ultimate Beneficiaries”) or provide any guarantee, security or the
like on
behalf of the Ultimate Beneficiaries.

(b) The management has represented in Note 41(4), that, to the best of its knowledge and belief, other than as
disclosed
in the notes to the accounts, no funds (which are material either individually or in the aggregate) have been
received by

| E2E Networks Limited | 109 |

the company from any person(s) or entity(ies), including foreign entities (“Funding Parties”), with the
understanding,
whether recorded in writing or otherwise, that the company shall, whether, directly or indirectly, lend or
invest in other
persons or entities identified in any manner whatsoever by or on behalf of the Funding Party (“Ultimate
Beneficiaries”)
or provide any guarantee, security or the like on behalf of the Ultimate Beneficiaries; and

(c) Based on such audit procedures that have been considered reasonable and appropriate in the circumstances,
nothing
has come to our notice that has caused them to believe that the representations under sub-clause (i) and (ii)
of Rule
11(e), as provided under (a) and (b) above contain any material misstatement.”

v. Since, the Company has neither paid or declared any dividend during the year nor proposed any dividend for
the year,

| hence, | reporting requirement of clause (f) of rule 11 of the Companies (Audit and Auditors) Rules, 2014 are not |

applicable on the Company.
```

### Chunk 166

_text · pages 112–112 · 149 words · 288 tokens · starts with overlap_

```text
## REPORT ON OTHER LEGAL AND REGULATORY REQUIREMENTS
Since, the Company has neither paid or declared any dividend during the year nor proposed any dividend for the
year,

| hence, | reporting requirement of clause (f) of rule 11 of the Companies (Audit and Auditors) Rules, 2014 are not |

applicable on the Company.

| vi. | As proviso to rule 3(1) of the Companies (Accounts) Rules, 2014 is applicable for the company only w.e.f. April 1, 2023, |

reporting under this clause is not applicable.

h. As required by section 197(16) of the Act, we report that the company has paid remuneration to its
directors during the year in
accordance with the provisions and limits laid down under section 197 read with schedule V to the act.

For GSA & Associates LLP
Chartered Accountants
ICAI Firm Registration No.: 000257N/N500339

Tanuj Chaugh
Partner
Membership No.: 529619

Place: New Delhi
```

### Chunk 167

_text · pages 112–114 · 392 words · 616 tokens_

```text
## UDIN: 23529619BGTYAG4201
| E2E Networks Limited | 110 |

ANNEXURE - A To The Independent Auditor’s Report

(Referred to in paragraph 1 of ‘Report on Other Legal and Regulatory Requirements’ section of our report of
even date)

As required by the Companies (Auditor’s Report) Order, 2020 (“the Order”) issued by the Central Government in
terms of
Section 143(11) of the Act, we give in the Annexure as follows: -

i. In respect of Company’s Property, plant and equipment and intangible assets:

a) (A) The company has maintained proper records showing full particulars, including quantitative details and
situation of Property,
plant and equipment, ‘capital work-in- progress’, ‘investment property’’, and relevant details of right-of
-use- assets;

(B) The Company has maintained proper records showing full particulars of intangible assets.

b) The company has a program of physical verification of “Property, plant and equipment, and “right-of-use-of-
assets”, so to
reasonable cover all the assets once every three year which, in our opinion, is reasonable having regard to
the size of the company
and the nature of its assets. According to information explanation given to us, no material discrepancies were
noticed on such
verification.

c) According to the information and explanations given to us and on the basis of our examination of the
records of the Company, the
title deeds of immovable properties (other than immovable properties where the Company is the lessee and the
lease agreements
are duly executed in favour of the lessee) disclosed in the financial statements are held in the name of the
Company.

d) According to the information and explanations given to us and on the basis of our examination of the
records of the Company, the
Company has not revalued its property, plant and equipment (including Right-of-use assets) during the year.
The company has
obtained a report from a registered valuer. The aggregate of the net carrying value of the class of intangible
assets revalued by
the company has increased by INR 28 Lakhs during the year on account of such revaluation.

| E2E Networks Limited | 111 |

e) According to the information and explanations given to us and on the basis of our examination of the
records of the Company, there
are no proceedings initiated or pending against the Company for holding any benami property under the
Prohibition of Benami
Property Transactions Act, 1988 and rules made thereunder.
```

### Chunk 168

_text · pages 114–114 · 379 words · 557 tokens_

```text
## UDIN: 23529619BGTYAG4201
ii. With respect to clause ii), we state that: -
a) The company is a service company and does not have any inventory and hence reporting under clause 3(ii)(a)
of the order is not
applicable.
b) According to the information and explanations given to us and on the basis of our examination of the
records of the Company, the
Company has not sanctioned working capital limits in excess of five crore rupees, in aggregate, from banks on
the basis of security
of current assets. Accordingly clause 3(ii)(b) of the order is not applicable to the company.

iii. According to the information and explanations given to us and on the basis of our examination of the
records of the Company, the
Company has not made any investments in or provided security to companies, firms, limited liability
partnerships or any other parties
during the year. The Company has not provided guarantees, granted loans and advances in the nature of loans
during the year to
companies, firms, Limited Liability Partnerships or any other parties. Accordingly, clause 3(iii) of the Order
is not applicable to the
Company.

iv. According to the information and explanations given to us, the Company has not made loans, investments,
guarantees and has not
provided any security under the provisions of section 185 and 186 of the Companies Act, 2013 Accordingly
paragraph 3(iv) of the
Order is not applicable.

v. According to the information and explanations given to us, the Company has not accepted any deposits or
amounts which are
deemed to be deposits from the public within the meaning of the directives issued by the Reserve Bank of
India, provisions of Section
73 to 76 of the Act, any other relevant provisions of the Act and the relevant rules framed thereunder.
Accordingly, the Provisions of
clause 3(v) of the Order are not applicable to the company.

vi. In our opinion and according to the information and explanation given to us, the maintenance of the cost
records has not been specified
by the Central Government of India under Section 148(1) of the Companies Act 2013 for the business activities
carried out by the
company. According the Provisions of clause 3(vi) of the order are not applicable to the company.

| E2E Networks Limited | 112 |
```

### Chunk 169

_text · pages 115–116 · 425 words · 633 tokens · starts with overlap_

```text
## UDIN: 23529619BGTYAG4201
According the Provisions of clause 3(vi) of the order are not applicable to the company. | E2E Networks
Limited | 112 |

vii. According to the information and explanations given to us and according to the books and records as
produced and examined by us,
in our opinion:

a) The Company has been regular in depositing undisputed statutory dues including Goods and Services Tax,
Provident Fund,
Employees’ State Insurance, Income-tax, Customs Duty, Cess and other material statutory dues as applicable
with the appropriate
authorities.
According to the information and explanations given to us, no undisputed amounts payable in respect of
Provident Fund,
Employees’ State Insurance, Income-tax, Goods and Services Tax, Customs Duty, Cess and other material
statutory dues were in
arrears as at 31 March 2023 for a period of more than six months from the date they became payable.

b) According to the information and explanation given to us, there are no statutory dues referred in sub
clause (a) which have not
been deposited with appropriate authorities on account of any dispute.

viii. According to the information and explanations given to us and on the basis of our examination of the
records of the Company, the
Company has not surrendered or disclosed any transactions, previously unrecorded as income in the books of
account, in the tax
assessments under the Income Tax Act, 1961 as income during the year.

ix. With respect to the loans and borrowing obtained by the Company, we report that: -

a) According to the information and explanations given to us and on the basis of our examination of the
records of the Company,
the Company has not defaulted in repayment of loans or other borrowings or in the payment of interest thereon
to any lender.

b) According to the information and explanations given to us and on the basis of our examination of the
records of the Company,
the Company has not been declared a wilful defaulter by any bank or financial institution or government or
government
authority.

c) According to the information and explanations given to us and on the basis of our examination of the
records of the Company,
the company has not applied term loans for the purpose for which the loans obtained.

| E2E Networks Limited | 113 |

d) According to the information and explanations given to us and on the basis of our overall examination of
the financial statements
of the Company, we report that no funds raised on short- term basis have been used for long-term purposes by
the company.
```

### Chunk 170

_text · pages 116–117 · 393 words · 596 tokens_

```text
## UDIN: 23529619BGTYAG4201
e) The Company does not have any subsidiaries, associates or joint ventures. Accordingly reporting under
clause3(ix)(e) of the
Order is not applicable.

f) The Company does not have any subsidiaries, associates or joint ventures. Accordingly reporting under
clause3(ix)(e) of the
Order is not applicable.

| x. | With respect to Clause 3(x), we state that: - |

a) In our opinion and according to the information and explanations given to us and on the basis of
examination of records of the
company, the company has not raised moneys by way of initial public offer or further public offer (including
debt instruments)
during the year. Accordingly, the provision of clause 3(x)(a) of the Order are not applicable to the company.

b) During the year, the Company has not made any preferential allotment or private placement of shares or
convertible debentures
(fully or partly or optionally) and hence reporting under clause 3(x)(b) of the Order is not applicable.

| xi. | In respect of reporting under clause 3(xi), we state that: - |

a) In our opinion and according to the information and explanations given to us, no fraud by the company or no
fraud on the company
has been noticed or reported during the year. Based on examination of the books and records of the Company and
according to the
information and explanations given to us, considering the principles of materiality as outlined in the
Standards on Auditing, we
report that no fraud by the Company or on the Company has been noticed or reported during the course of the
audit.

b) According to the information and explanations given to us, no report under sub-section (12) of Section 143
of the Act has been filed
by the auditors in Form ADT-4 as prescribed under rule 13 of Companies (Audit and Auditors) Rules, 2014 with
the Central
Government.

| E2E Networks Limited | 114 |

c) As represented to us by the management, we have taken into consideration the whistle blower complaints
received by the Company
during the year while determining the nature, timing and extent of our audit procedures.

xii. In our opinion and according to the information and explanations given to us, according to the
information and explanations given to
us, the Company is not a Nidhi Company. Accordingly, clause 3(xii) of the Order are not applicable to the
Company.
```

### Chunk 171

_text · pages 117–118 · 442 words · 671 tokens · starts with overlap_

```text
## UDIN: 23529619BGTYAG4201
xii. In our opinion and according to the information and explanations given to us, according to the
information and explanations given to
us, the Company is not a Nidhi Company. Accordingly, clause 3(xii) of the Order are not applicable to the
Company.

xiii. In our opinion and according to the information and explanations given to us and on the basis of
examination of records of the company,
all transaction entered into with the Related Parties are in compliance with Sections 177 and 188 of the Act,
where applicable, and the
details of the related party transactions have been disclosed in the financial statements as required by the
applicable accounting
standards.

| xiv. | With respect to reporting under clause 3(xiv), we state that: - |

a) In our opinion and according to the information and explanations given to us, the Company has an internal
audit system
commensurate with the size and nature of its business.

b) We have considered, the internal audit reports for the year under audit, issued to the Company during the
year and till date, in
determining the nature, timing and extent of our audit procedures.

xv. In our opinion and according to the information and explanations given to us, the Company has not entered
into any non-cash
transactions with its directors or persons connected to its directors and hence, provisions of Section 192 of
the Companies Act, 2013
are not applicable to the Company.

| xvi. | With respect to reporting under clause 3(xvi), we state that: - |

a) In our opinion and according to the information and explanations given to us, the Company is not required
to be registered under
Section 45-IA of the Reserve Bank of India Act, 1934. Accordingly, the provision of clause 3(xvi)(a) of the
Order are not applicable
to the Company.

| E2E Networks Limited | 115 |

b) In our opinion and according to the information and explanations given to us, the Company is not required
to be registered under
Section 45-IA of the Reserve Bank of India Act, 1934. Accordingly, the provision of clause 3(xvi)(b) of the
Order are not applicable
to the Company.

c) In our opinion and according to the information and explanations given to us, the Company is not a Core
Investment Company (CIC)
as defined in the regulations made by the Reserve Bank of India. Accordingly, the provision of, clause
3(xvi)(c) of the Order are not
applicable to the company.

d) In our opinion and according to the information and explanations given to us, the Group does not have any
CIC. Accordingly, the
provision of clause 3(xvi)(d) are not applicable to the company.
```

### Chunk 172

_text · pages 118–119 · 440 words · 642 tokens · starts with overlap_

```text
## UDIN: 23529619BGTYAG4201
Accordingly, the provision of, clause 3(xvi)(c) of the Order are not
applicable to the company. d) In our opinion and according to the information and explanations given to us,
the Group does not have any CIC. Accordingly, the
provision of clause 3(xvi)(d) are not applicable to the company.

xvii. The Company has not incurred cash losses in the current and in the immediately preceding financial year.

xviii. There has been resignation of the statutory auditors during the period, and we have taken into
consideration the issues, objections or
concerns raised by the outgoing auditors.

xix. According to the information and explanation given to us and on the basis of the financial ratios, ageing
and expected dates of
realisation of financial assets and payment of financial liabilities, other information accompanying the
financial statements and our
knowledge of the Board of Directors and Management plans and based on our examination of the evidence
supporting the assumptions,
nothing has come to our attention, which causes us to believe that any material uncertainty exists as on the
date of the audit report
indicating that Company is not capable of meeting its liabilities existing at the date of balance sheet as and
when they fall due within a
period of one year from the balance sheet date. We, however, state that this is not an assurance as to the
future viability of the Company.
We further state that our reporting is based on the facts up to the date of the audit report and we neither
give any guarantee nor any
assurance that all liabilities falling due within a period of one year from the balance sheet date, will get
discharged by the Company as
and when they fall due.

xx. In our opinion and according to the information and explanations given to us, in respect of other than
ongoing projects, there are no
unspent amount that are required to be transferred to a fund specified in Schedule VII of the company Act
2013, in compliance with

| E2E Networks Limited | 116 |

second proviso to sub- section (5) of Section 135 of the Companies Act, 2013. This matter has been disclosed
in Note 39 to the Financial
Statements.

In our opinion and according to the information and explanations given to us, there are no unspent amount sub-
section (5) of Section
135 of the Companies Act, 2013 pursuant to any ongoing projects, those are required to be transferred to a
special account in in
compliance with second proviso to sub-section (6) of Section 135 of the Companies Act, 2013. This matter has
been disclosed in Note
39 to the Financial Statements.
```

### Chunk 173

_text · pages 119–120 · 142 words · 298 tokens · starts with overlap_

```text
## ANNEXURE - B TO THE INDEPENDENT AUDITOR’S REPORT
This matter has been disclosed in Note
39 to the Financial Statements.

For GSA & Associates LLP
Chartered Accountants
ICAI Firm Registration No.: 000257N/N500339

Tanuj Chaugh
Partner
Membership No.: 529619

Place: New Delhi

## UDIN: 23529619BGTYAG4201

| E2E Networks Limited | 117 |

## ANNEXURE - B TO THE INDEPENDENT AUDITOR’S REPORT

(Referred to in clause (f) of paragraph 2 under ‘Report on Other Legal and Regulatory Requirements’ section of
our report of even

Report on the Internal Financial Controls under Clause (i) of Sub-section 3 of Section 143 of the Companies
Act, 2013 (“the

We have audited the internal financial controls over financial reporting of E2E Networks Limited as of March
31, 2023 in conjunction
with our audit of the financial statements of the Company for the year ended on that date.
```

### Chunk 174

_text · pages 120–120 · 136 words · 202 tokens_

```text
## MANAGEMENT’S RESPONSIBILITY FOR INTERNAL FINANCIAL CONTROLS
The Board of Directors of the Company is responsible for establishing and maintaining internal financial
controls based on the internal
control over financial reporting criteria established by the Company considering the essential components of
internal control stated in
the Guidance Note on Audit of Internal Financial Controls over Financial Reporting issued by the Institute of
Chartered Accountants of
India (“The ICAI”). These responsibilities include the design, implementation and maintenance of adequate
internal financial controls that
were operating effectively for ensuring the orderly and efficient conduct of its business, including adherence
to company’s policies, the
safeguarding of its assets, the prevention and detection of frauds and errors, the accuracy and completeness
of the accounting records,
and the timely preparation of reliable financial information, as required under the Companies Act, 2013.
```

### Chunk 175

_text · pages 120–121 · 263 words · 356 tokens_

```text
## AUDITORS’ RESPONSIBILITY
Our responsibility is to express an opinion on the Company's internal financial controls over financial
reporting based on our audit. We
conducted our audit in accordance with the Guidance Note on Audit of Internal Financial Controls Over
Financial Reporting issued by the
ICAI and the Standards on Auditing, prescribed under section 143(10) of the Companies Act, 2013, to the extent
applicable to an audit of
internal financial controls, both applicable to an audit of Internal Financial Controls. Those Standards and
the Guidance Note require that
we comply with ethical requirements and plan and perform the audit to obtain reasonable assurance about
whether adequate internal
financial controls over financial reporting was established and maintained and if such controls operated
effectively in all material respects.

| E2E Networks Limited | 118 |

Our audit involves performing procedures to obtain audit evidence about the adequacy of the internal financial
controls system over
financial reporting and their operating effectiveness. Our audit of internal financial controls over financial
reporting included obtaining
an understanding of internal financial controls over financial reporting, assessing the risk that a material
weakness exists, and testing and
evaluating the design and operating effectiveness of internal control based on the assessed risk. The
procedures selected depend on the
auditor’s judgement, including the assessment of the risks of material misstatement of the financial
statements, whether due to fraud or
error.

We believe that the audit evidence we have obtained is sufficient and appropriate to provide a basis for our
audit opinion on the Company’s
internal financial controls system with reference to financial statements.
```

### Chunk 176

_text · pages 121–121 · 162 words · 224 tokens_

```text
## MEANING OF INTERNAL FINANCIAL CONTROLS OVER FINANCIAL REPORTING
A company's internal financial control over financial reporting is a process designed to provide reasonable
assurance regarding the
reliability of financial reporting and the preparation of financial statements for external purposes in
accordance with generally accepted
accounting principles. A company's internal financial control over financial reporting includes those policies
and procedures that

1. pertain to the maintenance of records that, in reasonable detail, accurately and fairly reflect the
transactions and dispositions of the
assets of the company;
2. provide reasonable assurance that transactions are recorded as necessary to permit preparation of financial
statements in accordance
with generally accepted accounting principles, and that receipts and expenditures of the company are being
made only in accordance
with authorizations of management and directors of the company; and
3. provide reasonable assurance regarding prevention or timely detection of unauthorized acquisition, use, or
disposition of the
company's assets that could have a material effect on the financial statements.
```

### Chunk 177

_text · pages 121–122 · 217 words · 352 tokens_

```text
## INHERENT LIMITATIONS OF INTERNAL FINANCIAL CONTROLS OVER FINANCIAL REPORTING
Because of the inherent limitations of internal financial controls over financial reporting, including the
possibility of collusion or improper
management override of controls, material misstatements due to error or fraud may occur and not be detected.
Also, projections of any
evaluation of the internal financial controls over financial reporting to future periods are subject to the
risk that the internal financial
control over financial reporting may become inadequate because of changes in conditions, or that the degree of
compliance with the
policies or procedures may deteriorate.

| E2E Networks Limited | 119 |

OPINION

In our opinion, to the best of our information and according to the explanations given to us, the Company has,
in all material respects, an
adequate internal financial controls system over financial reporting and such internal financial controls over
financial reporting were
operating effectively as at March 31, 2023, based on the internal control over financial reporting criteria
established by the Company
considering the essential components of internal control stated in the Guidance Note on Audit of Internal
Financial Controls Over Financial
Reporting issued by the Institute of Chartered Accountants of India.

For GSA & Associates LLP
Chartered Accountants
ICAI Firm Registration No.: 000257N/N500339

Tanuj Chaugh
Partner
Membership No.: 529619

Place: New Delhi
```

### Chunk 178

_text · pages 122–122 · 10 words · 36 tokens_

```text
## UDIN: 23529619BGTYAG4201
| E2E Networks Limited | 120 |
```
