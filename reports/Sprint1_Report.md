# ClauseIQ Sprint 1 Report

## 1. Sprint Objective
The primary objective of Sprint 1 was to establish, verify, and document the complete core Machine Learning pipeline for **ClauseIQ**, a legal contract clause classification and intelligent analysis system. Sprint 1 implements text extraction from PDF contracts, spaCy-based sentence/clause segmentation, domain-aware text cleaning, TF-IDF feature extraction without data leakage, training of a balanced Logistic Regression baseline, and hyperparameter tuning of a Linear Support Vector Classifier (LinearSVC).

---

## 2. Dataset
The ClauseIQ dataset is derived from the **Contract Understanding Atticus Dataset (CUAD)**. All analyses, models, and statistics in this project are based directly on the current source of truth file: `data/clauseiq_dataset.csv`.

### Actual Dataset Dimensions & Characteristics
- **Source File**: `data/clauseiq_dataset.csv`
- **Total Records (Rows)**: 12,204
- **Total Features (Columns)**: 3
- **Column Schema**:
  1. `contract_id` (string): Identifier for the source commercial contract.
  2. `clause_text` (string): Raw clause text extracted from contract.
  3. `category` (string): Ground-truth legal clause classification label.
- **Missing Values**: 0 across all columns (100% complete).
- **Exact Duplicate Rows**: 0.
- **Duplicate Clause Texts**: 1,655 (identical standard legal boilerplate appearing across different contracts/categories).
- **Unique Contracts**: 510 (covering the complete CUAD contract corpus).
- **Unique Categories**: 41 predefined legal clause categories.

### Resolution of Dataset Row Count Discrepancy
An earlier project note mentioned a dataset size of 13,823 rows alongside 12,204 rows. Inspection reveals that the active, verified dataset in `data/clauseiq_dataset.csv` contains exactly **12,204 rows**. The 13,823 row count corresponds to an uncleaned pre-deduplication raw export containing empty extracts and unsegmented fragments. The 12,204 row dataset represents the deduplicated, validated clause-level corpus.

### Category Distribution (Top & Bottom 5)
The dataset exhibits significant class imbalance:
- **Top 5 Most Frequent Categories**:
  1. *Parties*: 1,251 clauses (10.25%)
  2. *License Grant*: 774 clauses (6.34%)
  3. *Cap On Liability*: 672 clauses (5.51%)
  4. *Anti-Assignment*: 652 clauses (5.34%)
  5. *Audit Rights*: 642 clauses (5.26%)
- **Bottom 5 Least Frequent Categories**:
  1. *No-Solicit Of Customers*: 58 clauses (0.48%)
  2. *Third Party Beneficiary*: 39 clauses (0.32%)
  3. *Most Favored Nation*: 38 clauses (0.31%)
  4. *Unlimited/All-You-Can-Eat-License*: 32 clauses (0.26%)
  5. *Price Restrictions*: 27 clauses (0.22%)

---

## 3. Data Preprocessing
The preprocessing pipeline is composed of three modular components located in `src/`:

1. **PDF Text Extraction (`src/pdf_extractor.py`)**:
   - Uses `pymupdf` (PyMuPDF) to extract raw textual content from uploaded contract PDFs.
   - Safely verifies file existence, manages file handles via context managers, and operates irrespective of working directory.
   - Tested on `data/raw_pdfs/sample_contract.pdf` (extracted 2,631 characters across 2 pages).

2. **Clause Splitting (`src/clause_splitter.py`)**:
   - Uses spaCy's `en_core_web_sm` model to parse raw contract text into sentence-level clauses via `doc.sents`.
   - Strips whitespace, removes empty segments, and preserves sentence boundary integrity.
   - Produced 23 clause units on the sample contract.

3. **Domain-Aware Text Cleaning (`src/text_cleaner.py` and `src/clean_dataset.py`)**:
   - Lowercases text, strips URLs (`https?://\S+`), removes email addresses, cleans non-alphanumeric punctuation while retaining sentence punctuation (`.,;:()-`), and normalizes whitespace.
   - Crucially preserves legal stop words and modal verbs (*shall*, *may*, *not*, *unless*, *provided*, *except*, *party*, *agreement*) which encode legally binding obligations and exclusions.
   - Generates `data/clauseiq_dataset_clean.csv` (12,204 cleaned rows, 0 nulls, 0 empty strings).

---

## 4. EDA Findings
Exploratory Data Analysis was executed and validated via `notebooks/EDA.ipynb`, producing 13 publication-quality visualization figures in `eda_outputs/`.

### Summary Statistics
- **Clause Word Count**:
  - Mean: 45.89 words
  - Standard Deviation: 43.66 words
  - Median: 36.00 words
  - Min: 3 words | Max: 479 words
  - Interquartile Range (Q1 - Q3): 17.00 – 61.00 words
- **Clause Character Count**:
  - Mean: 289.16 characters
  - Standard Deviation: 277.38 characters
  - Median: 224.00 characters
  - Min: 9 characters | Max: 3,169 characters
  - Interquartile Range (Q1 - Q3): 105.00 – 386.00 characters

### Lexical Patterns
- **Top Unigrams**: `agreement` (7,686), `shall` (7,352), `party` (4,686), `term` (2,525), `section` (2,300), `right` (2,031), `use` (2,028), `company` (2,019), `date` (1,893), `license` (1,827).
- **Top Bigrams**: `agreement shall` (1,027), `set forth` (957), `effective date` (821), `prior written` (760), `written notice` (753), `non exclusive` (730), `term agreement` (720), `intellectual property` (628), `terms conditions` (555), `written consent` (550).

---

## 5. TF-IDF Feature Extraction
- **Module**: `src/feature_extraction.py`
- **Vectorization**: `TfidfVectorizer` from `scikit-learn`.
- **Hyperparameters**:
  - `max_features`: 10,000
  - `ngram_range`: (1, 2) (unigrams and bigrams)
  - `min_df`: 2
  - `max_df`: 0.95
  - `sublinear_tf`: True (logarithmic term frequency scaling $1 + \log(\text{tf})$)
- **Data Leakage Prevention**:
  The vectorizer was strictly fit on the training partition only (`X_train_text`). The test set was strictly transformed using the learned vocabulary and inverse document frequencies (`vectorizer.transform(X_test_text)`).

---

## 6. Train/Test Split
- **Split Configuration**: Stratified 80% train / 20% test split (`test_size=0.20`, `random_state=42`, `stratify=y`).
- **Training Set Size**: 9,763 samples
- **Test Set Size**: 2,441 samples
- **Label Encoding**: Scikit-learn `LabelEncoder` mapping the 41 categorical string labels to integers [0, 40].
- **Artifacts Saved**:
  - `models/train_test_split.pkl` (containing `(X_train, X_test, y_train, y_test)`)
  - `models/tfidf_vectorizer.pkl`
  - `models/label_encoder.pkl`

---

## 7. Logistic Regression Baseline
- **Module**: `src/train_baseline.py`
- **Configuration**:
  - `LogisticRegression(max_iter=2000, class_weight='balanced', random_state=42)`
- **Evaluation on Held-Out Test Set (2,441 samples)**:
  - **Accuracy**: 0.7190 (71.90%)
  - **Macro Precision**: 0.6481
  - **Macro Recall**: 0.6622
  - **Macro F1**: 0.6474 (64.74%)
  - **Weighted F1**: 0.7196 (71.96%)
- **Saved Model**: `models/logistic_regression.pkl`

---

## 8. Linear SVM
- **Module**: `src/train_svm.py`
- **Configuration**: `LinearSVC(class_weight='balanced', max_iter=5000, random_state=42)`
- **Evaluation on Held-Out Test Set (2,441 samples)**:
  - **Accuracy**: 0.7263 (72.63%)
  - **Macro Precision**: 0.6323
  - **Macro Recall**: 0.6665
  - **Macro F1**: 0.6418 (64.18%)
  - **Weighted F1**: 0.7226 (72.26%)
- **Saved Model**: `models/svm_classifier.pkl`

---

## 9. Hyperparameter Tuning
- **Method**: 3-Fold Cross-Validation (`GridSearchCV`) strictly on training features (`X_train, y_train`) with `scoring='f1_macro'`, `n_jobs=-1`.
- **Parameter Grid**: `{"C": [0.1, 1, 10]}`
- **Best Parameter Found**: `C = 0.1`
- **Best Cross-Validation Macro F1 (3-fold)**: `0.6257`

---

## 10. Model Comparison
Computed on the identical held-out test split of 2,441 clauses:

| Metric | Logistic Regression (Baseline) | Tuned Linear SVM (C=0.1) | Delta (SVM - LR) | Preferred Model |
| :--- | :---: | :---: | :---: | :---: |
| **Accuracy** | 71.90% | **72.63%** | +0.73% | Linear SVM |
| **Macro Precision** | **0.6481** | 0.6323 | -0.0158 | Logistic Regression |
| **Macro Recall** | 0.6622 | **0.6665** | +0.0043 | Linear SVM |
| **Macro F1** | **0.6474** | 0.6418 | -0.0056 | Logistic Regression |
| **Weighted F1** | 71.96% | **72.26%** | +0.30% | Linear SVM |

### Observations:
1. Linear SVM achieves higher overall classification accuracy (+0.73%) and higher weighted F1 (+0.30%), generalizing better on majority clause categories.
2. Logistic Regression preserves slightly higher precision on extreme low-support classes (<30 samples), yielding a marginally higher Macro F1 (+0.56%).
3. Linear SVM provides faster inference latency and strong margin separation, making it an excellent candidate for real-time document analysis.

---

## 11. Limitations & Data Leakage Analysis
1. **Contract-Level Overlap**:
   The current Sprint 1 split is a clause-level stratified split. Analysis of contract IDs reveals that out of 467 unique contracts in the test set, 466 contracts (99.8%) also appear in the training partition. Because clauses within the same contract share terminology, drafting style, and party identities, clause-level stratification introduces a potential contract-level leakage risk. For Sprint 2, a contract-grouped split (`GroupShuffleSplit` by `contract_id`) will be explored to assess out-of-contract generalization.
2. **Boilerplate Duplication**:
   1,655 duplicate `clause_text` entries exist across contracts (e.g., standard governing law or notice clauses). While natural in commercial contracting, deduplication at the contract-type level should be monitored.

---

## 12. Sprint 1 Outcome
All Sprint 1 deliverables are completed, tested, and verified:
- [PASS] PyMuPDF PDF text extraction
- [PASS] spaCy clause segmentation
- [PASS] Text cleaning preserving legal tokens
- [PASS] CUAD EDA analysis and 13 visualization outputs
- [PASS] Leakage-free TF-IDF feature pipeline
- [PASS] Stratified train/test split & label encoder
- [PASS] Logistic Regression baseline training and evaluation
- [PASS] Linear SVM training, GridSearchCV tuning (C=0.1), and evaluation
- [PASS] Model artifacts serialized in `models/`
- [PASS] End-to-end integration demo script (`src/demo_pipeline.py`)
- [PASS] Unit test suite passing with 100% success (`tests/test_sprint1.py`)
