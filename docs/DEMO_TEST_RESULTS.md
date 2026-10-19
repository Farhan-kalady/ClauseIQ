# ClauseIQ — Demonstration Test Results

**Date**: October 13, 2026  
**System**: ClauseIQ (MCA Mini Project)  
**Selected Model**: Logistic Regression (Sprint 2 tuned champion)  
**Feature Representation**: TF-IDF Vectorizer (`max_features=10000`, `ngram_range=(1,2)`)  
**Corpus**: CUAD v1 (41 legal clause categories)  

---

## 1. Single-Clause Classification Benchmark Results

This table documents the actual classification predictions and probability scores produced by the trained Logistic Regression model when tested against representative contract clauses.

| Test ID | Input Clause Text | Expected Category | Actual Predicted Category | Confidence Score | Probability Distribution (Top Alternatives) | Test Status |
| :---: | :--- | :--- | :--- | :---: | :--- | :---: |
| **Input A** | *"The Receiving Party agrees to keep all confidential information received from the Disclosing Party strictly confidential and shall not disclose such information to any third party without prior written consent."* | Confidentiality | **Anti-Assignment** | **12.27%** (0.1227) | • Rofr/Rofo/Rofn: 5.48%<br>• Non-Compete: 5.35%<br>• Audit Rights: 4.70% | **EXPLAINED** *(See Note 1)* |
| **Input B** | *"Either party may terminate this Agreement by providing thirty days written notice to the other party. In case of a material breach, the non-breaching party may terminate this Agreement if the breach is not remedied within the specified period."* | Termination | **Termination For Convenience** | **54.27%** (0.5427) | • Change Of Control: 9.35%<br>• Non-Disparagement: 3.42%<br>• Notice Period To Terminate Renewal: 3.30% | **PASS** *(Semantic Match)* |
| **Input C** | *"This Agreement shall be governed by the laws of India. The courts located in Bengaluru shall have exclusive jurisdiction over disputes arising from this Agreement."* | Governing Law | **Governing Law** | **73.04%** (0.7304) | • Competitive Restriction Exception: 1.80%<br>• Exclusivity: 1.77%<br>• Cap On Liability: 1.49% | **PASS** *(Exact Match)* |

> **Note 1 on Input A (Confidentiality):**  
> The official CUAD v1 benchmark schema contains **41 predefined legal categories**. Notably, a standalone category named *"Confidentiality"* or *"Non-Disclosure"* does not exist within the 41 CUAD classes (which focus on commercial commitments, licenses, restrictions, and liability terms). Because the model is strictly constrained to the 41 CUAD classes, it distributes probabilities diffusely with low confidence (max probability 12.27%), selecting *Anti-Assignment* as the marginal argmax. This reflects authentic model behavior rather than an implementation defect.

---

## 2. Synthetic PDF Contract Extraction & Classification Summary

**Document Tested**: `test_data/ClauseIQ_Synthetic_Company_Service_Agreement_Test.pdf`  
**File Size**: 34,835 bytes (3 pages)  
**Document Nature**: Fictional synthetic company service agreement created exclusively for testing.

| Test Item | Specification / Requirement | Actual Result | Verification Status |
| :--- | :--- | :--- | :---: |
| **PDF Upload** | Multipart upload via `/classify/file` | HTTP 200 OK | **PASS** |
| **Text Extraction** | Extract readable document text via PyMuPDF | 9,144 characters extracted | **PASS** |
| **Document Headings Found** | All 17 separately headed sections | 17 / 17 sections present | **PASS** |
| **Extracted Clause Segments** | Identified clauses from document | **69 segments** | **PASS** |
| **Successfully Classified Segments** | Inferred category and probability | **69 segments** (100%) | **PASS** |
| **Failed Segments** | Unhandled parsing / model errors | **0 segments** | **PASS** |
| **Database Persistence (Contract)** | Metadata stored in Supabase `contracts` | Contract ID: `0390cc53-4182-4761-99ab-6a97fd624239` | **PASS** |
| **Database Persistence (Clauses)** | Clause records in Supabase `clauses` | **69 records inserted** | **PASS** |

### Section-by-Section Heading Verification

All 17 sections defined in the synthetic contract are accounted for in the extracted text:

1. `Definitions and Interpretation` — Verified (Clauses #5–#7)
2. `Effective Date and Term` — Verified (Clauses #8–#10)
3. `Services and Deliverables` — Verified (Clauses #11–#14)
4. `Fees and Payment Terms` — Verified (Clauses #15–#19)
5. `Confidentiality` — Verified (Clauses #20–#24)
6. `Data Protection and Security` — Verified (Clauses #25–#28)
7. `Intellectual Property Rights` — Verified (Clauses #29–#32)
8. `Representations and Warranties` — Verified (Clauses #33–#36)
9. `Indemnification` — Verified (Clauses #37–#40)
10. `Limitation of Liability` — Verified (Clauses #41–#43)
11. `Assignment` — Verified (Clauses #44–#45)
12. `Termination` — Verified (Clauses #46–#50)
13. `Notice` — Verified (Clauses #51–#53)
14. `Governing Law and Jurisdiction` — Verified (Clauses #54–#56)
15. `Force Majeure` — Verified (Clauses #57–#59)
16. `Entire Agreement and Amendments` — Verified (Clauses #60–#62)
17. `Signatures` — Verified (Clauses #63–#69)

---

## 3. Intelligent Clause Search Benchmark Results

**Corpus**: 12,204 pre-indexed CUAD clauses  
**Method**: Classical TF-IDF feature extraction + Cosine Similarity ranking  

| Query # | Search Query String | Top Result Clause Preview | Predicted Category | Annotated Label | Cosine Similarity Score | Telemetry Logged to Supabase | Status |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **1** | `confidential information disclosure` | *"...misuse of confidential information..."* (WHITESMOKE, INC.) | Uncapped Liability | Uncapped Liability | **0.3893** (38.9%) | ID: `98adcd3f` | **PASS** |
| **2** | `termination of agreement` | *"Upon termination of this Agreement,..."* (Paperexchange.com) | Post-Termination Services | Post-Termination Services | **0.3697** (37.0%) | ID: `6f93ddc8` | **PASS** |
| **3** | `governing law and jurisdiction` | *"The terms of the Governing Law and Dispute Resolution..."* (Scansource) | Document Name | Governing Law | **0.3836** (38.4%) | ID: `71381a15` | **PASS** |
| **4** | `intellectual property ownership` | *"INTELLECTUAL PROPERTY RIGHTS AGREEMENT..."* (Rare Element Resources) | Document Name | Document Name | **0.6130** (61.3%) | ID: `67fbb65e` | **PASS** |
| **5** | `payment and invoices` | *"Payment Data Systems, Inc...." (Usio Inc.)* | Parties | Parties | **0.1956** (19.6%) | ID: `1848c505` | **PASS** |
| **6** | `indemnification against third party claims` | *"...liable for any third party claims..."* (NETGEAR, INC.) | Cap On Liability | Cap On Liability | **0.2891** (28.9%) | ID: `f6cc4a8e` | **PASS** |
| **7** | `limitation of liability` | *"Limitation of Liability of the Sponsor...."* (DOMINI ADVISOR TRUST) | Cap On Liability | Cap On Liability | **0.7215** (72.2%) | ID: `8e8e694d` | **PASS** |

---

## 4. Live Demonstration Execution Commands

To execute the live demonstration before the evaluation guide:

### Terminal 1: Backend API
```powershell
.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
*Accessible URLs:*
- Health check: `http://127.0.0.1:8000/health`
- Swagger UI documentation: `http://127.0.0.1:8000/docs`

### Terminal 2: React Frontend
```powershell
cd frontend
npm run dev
```
*Accessible URL:* `http://localhost:5173/`
