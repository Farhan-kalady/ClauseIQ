# ClauseIQ Final Project Report — User Action Items (TODO & Status)

This document records the verification status of the revised final report for **ClauseIQ – Machine Learning-Based Contract Clause Classification and Intelligent Search System**.

---

## 1. UI Screenshots Status: 100% Real & Verified (Zero Missing)

All eight requested user interface screenshots have been captured directly from the live running application (FastAPI backend + React/Vite frontend) and compiled directly into `report/figures/ui/` and the final PDF report:

| Target File | Status | Description |
| :--- | :---: | :--- |
| `report/figures/ui/ui_01_classify_text_result.png` | **REAL** | Single clause classification with animated ConfidenceRing (53.4%), green StatusBadge (High confidence), and candidate alternative predictions. |
| `report/figures/ui/ui_02_classify_upload_dropzone.png` | **REAL** | Document upload mode dropzone with drag-and-drop file ingestion support for PDF/TXT commercial agreements. |
| `report/figures/ui/ui_03_classify_document_results.png` | **REAL** | Extracted clause table showing all 29 clauses from `sample_contract.pdf`, confidence breakdown summary, and category filter chips. |
| `report/figures/ui/ui_04_search_results.png` | **REAL** | Semantic search console executing a query with active category filter (*Cap On Liability*) and highlighted keyword matches. |
| `report/figures/ui/ui_05_dark_mode.png` | **REAL** | High-contrast dark theme view optimized for extended contract review sessions. |
| `report/figures/ui/ui_06_mobile_view.png` | **REAL** | Responsive mobile viewport (390 px width) showing vertically stacked controls and mobile bottom tab navigation. |
| `report/figures/ui/ui_07_offline_banner.png` | **REAL** | Amber warning alert banner displayed when the backend server is stopped. |
| `report/figures/ui/ui_08_api_docs.png` | **REAL** | Interactive FastAPI OpenAPI Swagger UI (`/docs`) documenting all 7 verified REST endpoints. |

---

## 2. Compilation and Packaging

The report compiles cleanly with zero errors using Tectonic and is 100% compatible with Overleaf (pdfLaTeX):
- **Source Directory:** `report/`
- **Synchronized Directory:** `Aditional_files/Report & PPT/Final_Report/`
- **Overleaf Archive:** `ClauseIQ_Report.zip` (in workspace root)
- **Primary Document:** `main.tex`
- **Total Page Count:** 74 pages (strictly exceeding the 60-page requirement, within the target 62–74 range).
- **Introduction:** Pages 1–3 (ends exactly on page 3).

---

## 3. Items To Be Confirmed (TBC) by User

All technical data, software versions, and performance latencies have been measured and verified directly on the active machine. The only remaining items for the user are college-specific administrative pages:
1. **Institutional Cover Page:** The college usually supplies an official cover page with the university seal, department header, and student registration numbers.
2. **Certificates & Declaration:** Standard college certificate of authenticity, guide approval form, and student declaration of original work.
3. **External Examiner Signatures:** Blank signature blocks for the final project defense committee.
