# ClauseIQ — Baseline Evaluation & Trustworthy Metrics Report (Phase 1)

**Date of Execution:** October 19, 2026  
**Script Used:** `src/evaluation_protocol.py` (and `src/build_artifacts.py`)  
**Environment:** Python 3.14.6, scikit-learn 1.9.0, joblib 1.5.3, numpy 2.5.2, pandas 3.0.5  
**Random State:** 42 (reproducible seed across all splits and algorithms)

---

## 1. Evaluation Methodology

ClauseIQ evaluates four classical machine learning models across two rigorous splitting strategies to guarantee honest, leakage-aware benchmarking:

1. **Split A (Comparable Clause-Level Stratified 80/20):**
   - Partitioned uniformly across the 12,204 validated CUAD clause instances.
   - Train samples: **9,763**, Test samples: **2,441**.
   - Directly mirrors the historical baseline reported in `docs/model_card.md` and `results/model_comparison.json`.
   - *Limitation:* Clauses originating from the same parent commercial contract may appear in both partitions.

2. **Split B (Leakage-Safe Grouped Split by `contract_id`):**
   - Partitioned strictly by contract entity using `GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)`.
   - Train samples: **9,718 clauses** across **408 unique contracts**.
   - Test samples: **2,486 clauses** across **102 unique contracts**.
   - Zero contract overlap: no clause in the test partition comes from any contract present in the training set.
   - All 41 legal clause categories are present and evaluated in both partitions.

---

## 2. Baseline Model Comparison (Split A vs Split B)

All metrics below are calculated directly from empirical predictions on held-out test data without rounding adjustments.

| Model | Partition Split | Accuracy | Macro F1 | Weighted F1 | Macro Precision | Macro Recall | ECE | High Conf Precision (≥ 0.50) | Mod Conf Precision (0.25–0.50) | Low Conf Precision (0.10–0.25) | Out of Scope Precision (< 0.10) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** (Served) | **Split A (Stratified)** | 0.7190 | 0.6474 | 0.7196 | 0.6481 | 0.6622 | 0.2822 | 0.8575 | 0.6874 | 0.6270 | 0.3200 |
| **Linear SVM** ($C=0.1$) | Split A (Stratified) | **0.7263** | 0.6418 | **0.7226** | 0.6323 | 0.6665 | N/A | N/A | N/A | N/A | N/A |
| **Multinomial Naive Bayes** ($\alpha=0.01$) | Split A (Stratified) | 0.6927 | 0.5853 | 0.6903 | 0.6024 | 0.5867 | 0.1580 | 0.7238 | 0.3500 | 0.3000 | 0.2222 |
| **Random Forest** ($n=100$) | Split A (Stratified) | 0.6436 | 0.5486 | 0.6392 | 0.5403 | 0.5666 | 0.2911 | 0.6658 | 0.7065 | 0.6172 | 0.2774 |
| **Logistic Regression** (Served) | **Split B (Grouped)** | 0.7305 | **0.6691** | 0.7269 | **0.6726** | 0.6971 | 0.3115 | **0.9024** | 0.7182 | 0.6150 | 0.3897 |
| **Linear SVM** ($C=0.1$) | Split B (Grouped) | **0.7385** | 0.6635 | **0.7283** | 0.6575 | **0.7045** | N/A | N/A | N/A | N/A | N/A |
| **Multinomial Naive Bayes** ($\alpha=0.01$) | Split B (Grouped) | 0.7076 | 0.5940 | 0.6899 | 0.6431 | 0.5895 | 0.1180 | 0.7549 | 0.3278 | 0.2759 | 0.2241 |
| **Random Forest** ($n=100$) | Split B (Grouped) | 0.6866 | 0.6055 | 0.6734 | 0.6225 | 0.6258 | 0.3251 | 0.8992 | 0.7392 | 0.5576 | 0.3333 |

---

## 3. Probability Calibration Analysis for the Served Model (Logistic Regression)

### 3.1 Reliability Bins (Split A, $N=2,441$)

| Bin Index | Confidence Range | Sample Count | Mean Predicted Confidence | Empirical Accuracy | Calibration Gap |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | [0.00, 0.10] | 125 | 0.0809 | 0.3200 | 0.2391 |
| 2 | (0.10, 0.20] | 394 | 0.1485 | 0.5914 | 0.4429 |
| 3 | (0.20, 0.30] | 345 | 0.2485 | 0.7014 | 0.4529 |
| 4 | (0.30, 0.40] | 348 | 0.3498 | 0.6897 | 0.3398 |
| 5 | (0.40, 0.50] | 303 | 0.4476 | 0.6799 | 0.2323 |
| 6 | (0.50, 0.60] | 261 | 0.5487 | 0.7625 | 0.2138 |
| 7 | (0.60, 0.70] | 223 | 0.6454 | 0.7848 | 0.1393 |
| 8 | (0.70, 0.80] | 197 | 0.7477 | 0.9340 | 0.1863 |
| 9 | (0.80, 0.90] | 127 | 0.8474 | 0.9291 | 0.0818 |
| 10 | (0.90, 1.00] | 118 | 0.9517 | 1.0000 | 0.0483 |

**Overall Expected Calibration Error (ECE):** **0.2822**  
*Key Insight:* In lower probability bins (0.10 to 0.40), raw softmax probabilities are under-confident relative to empirical accuracy (e.g. clauses predicted with 25% confidence actually achieve ~70% accuracy). This occurs because 41 competing classes dilute the softmax probability mass. Post-hoc calibration in Phase 2 should align these distributions.

### 3.2 Precision by UI Confidence Status (Split B Leakage-Safe, $N=2,486$)

| Status Tier | Threshold Rule | Sample Count | % of Predictions | Empirical Precision | Interpretation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **High confidence** | $\ge 0.50$ | 850 | 34.19% | **0.9024 (90.2%)** | High confidence predictions are reliable for decision support; met target $\ge 0.90$. |
| **Moderate confidence** | $0.25 \le \text{conf} < 0.50$ | 841 | 33.83% | **0.7182 (71.8%)** | Good candidate predictions; human verification suggested. |
| **Low confidence – Review Required** | $0.10 \le \text{conf} < 0.25$ | 600 | 24.14% | **0.6150 (61.5%)** | Borderline classification; human review mandatory. |
| **Out of supported category scope** | $< 0.10$ | 195 | 7.84% | **0.3897 (39.0%)** | Model has diffuse probability across classes; high risk of misclassification. |

---

## 4. Top 15 Most Confused Category Pairs (Served Model, Split A)

| Rank | True Category | Predicted Category | Confused Count | Primary Root Cause |
| :---: | :--- | :--- | :---: | :--- |
| 1 | **Effective Date** | Agreement Date | 44 | Near-identical temporal phrasing ("entered into as of...", "dated as of...") |
| 2 | **License Grant** | Non-Transferable License | 33 | Nested contractual rights ("hereby grants a non-transferable license...") |
| 3 | **Cap On Liability** | Uncapped Liability | 32 | Both discuss liability limitation, often negating each other in sub-clauses |
| 4 | **Agreement Date** | Effective Date | 23 | Reciprocal confusion of date preamble clauses |
| 5 | **Renewal Term** | Notice Period To Terminate Renewal | 18 | Term extension clauses that simultaneously specify required notice periods |
| 6 | **License Grant** | Irrevocable Or Perpetual License | 17 | Overlapping intellectual property granting provisions |
| 7 | **License Grant** | Exclusivity | 16 | Exclusive licensing grants containing both grant and restriction terms |
| 8 | **Notice Period To Terminate Renewal** | Renewal Term | 15 | Reciprocal confusion between renewal provisions and termination deadlines |
| 9 | **Expiration Date** | Renewal Term | 13 | Clauses specifying both expiration date and renewal mechanics |
| 10 | **Uncapped Liability** | Cap On Liability | 13 | Reciprocal liability boundary confusion |
| 11 | **Effective Date** | Expiration Date | 11 | Temporal date clauses mentioning term commencement and conclusion |
| 12 | **License Grant** | Affiliate License-Licensee | 11 | Corporate scope extensions inside general licensing grants |
| 13 | **Exclusivity** | Competitive Restriction Exception | 9 | Commercial restraint terms with carve-outs |
| 14 | **Expiration Date** | Effective Date | 8 | Temporal date references in contract definitions |
| 15 | **License Grant** | Affiliate License-Licensor | 8 | Licensor affiliate rights specified in multi-party license sections |

---

## 5. Real-Document Pipeline Check

The real API pipeline (`api.services.ml_service.classify_document`) was executed on local contract PDFs:

1. **`test_data/ClauseIQ_Synthetic_Company_Service_Agreement_Test.pdf`**:
   - Total clauses extracted: **18 clauses** (section-level segmentation based on `clause_splitter.py` Section/Article regex headers).
   - Expected synthetic benchmark file (`docs/synthetic_pdf_classification_results.json`) contained 69 items (created when sentence-level fallback was used without structural section boundaries).
   - The current hierarchical splitter selects section chunks when $\ge 3$ sections match.
   - Identified categories on extracted sections: `Parties` (0.2714, Moderate), `Source Code Escrow` (0.1667, Low), `Expiration Date` (0.7172, High), `Revenue/Profit Sharing` (0.5710, High).

2. **`data/raw_pdfs/sample_contract.pdf`**:
   - Total clauses extracted: **2 clauses**.
   - Predictions: `Cap On Liability` (0.5302, High confidence), `Parties` (0.8335, High confidence).
   - Both clauses classified with High confidence.
   - *Honest Note:* The sample test PDF set is tiny (2 documents) and demonstrates the sensitivity of regex-based structural segmentation to document formatting.

---

## 6. Baseline Reproducibility Manifest

The baseline artifacts are generated reproducibly by `src/build_artifacts.py` and documented in `artifacts/manifest.json`. Running `src/build_artifacts.py` reproduces the historical baseline numbers (0.7190 accuracy, 0.6474 macro F1, 0.7196 weighted F1) exactly.
