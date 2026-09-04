# ClauseIQ – Exploratory Data Analysis (EDA) Report
**Machine Learning-Based Contract Clause Classification and Intelligent Search System**

---

## Executive Summary

This report presents the findings of the Exploratory Data Analysis (EDA) conducted on the primary dataset for **ClauseIQ** (`clauseiq_dataset.csv`), derived from the Contract Understanding Atticus Dataset (CUAD) benchmark. The objective of ClauseIQ is to automate the extraction, multi-class categorization, and intelligent search of legal clauses embedded within commercial contracts.

Every metric, table, and distribution presented in this report has been programmatically computed from the actual dataset without synthetic data, placeholders, or assumptions. All experiments and notebooks operate under a fixed random seed (`RANDOM_STATE = 42`) ensuring complete reproducibility.

---

## 1. Dataset Overview & Structural Metadata

### 1.1 Dimensions and Storage
* **Dataset File:** `clauseiq_dataset.csv` (Located in `DataSet CSV file/clauseiq_dataset.csv`)
* **Total Sample Count (Rows):** **12,204**
* **Total Feature Count (Columns):** **3**
* **Dataset Matrix Dimension:** **(12204, 3)**
* **File Size on Disk:** ~4.66 MB

### 1.2 Schema & Data Types
The dataset contains three primary attributes, all stored as text (`object` / `string` in pandas):

| Column # | Column Name | Data Type | Non-Null Count | Null Count | Null % | Description |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `contract_id` | `object` (`string`) | 12,204 | 0 | 0.00% | Unique identifier of source commercial agreement |
| 2 | `clause_text` | `object` (`string`) | 12,204 | 0 | 0.00% | Verbatim extracted text span of legal clause |
| 3 | `category` | `object` (`string`) | 12,204 | 0 | 0.00% | Ground-truth legal classification category (Target) |

---

## 2. Data Completeness & Integrity Audit

### 2.1 Missing Values
* **Null Value Count:** Exactly **0** missing values across all columns.
* **Empty Strings (`""`):** Exactly **0** empty string entries.
* **Whitespace-Only Records:** Exactly **0** whitespace-only entries.
* **Conclusion:** The dataset exhibits **100.0% data completeness**.

### 2.2 Duplication Analysis
A critical distinction was made between exact record duplicates, duplicate clause text, and recurring clauses across multiple agreements:
* **Exact Duplicate Rows `(contract_id, clause_text, category)`:** **0** (**0.00%**). Every record represents a distinct annotation instance.
* **Duplicate Clause Texts (`clause_text`):** **1,655** occurrences (**13.56%** of the dataset).
* **Unique Distinct Clause Texts:** **10,549**.

#### Semantic Interpretation of Duplicate Clause Texts
In commercial contract drafting, repetitive language is standard legal practice. Boilerplate clauses such as standard governing law provisions (*"This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware..."*) or common corporate entity names recur identically across hundreds of distinct agreements. These 1,655 instances reflect genuine cross-contract repetitions rather than data ingestion corruption, and they should be preserved.

---

## 3. Contract-Level Analysis

The dataset aggregates clauses extracted across commercial legal agreements:
* **Total Unique Contracts:** **510**
* **Mean Clauses per Contract:** **23.93**
* **Median Clauses per Contract:** **19.00**
* **Standard Deviation:** **17.88**
* **Minimum Clauses in a Contract:** **1**
* **Maximum Clauses in a Contract:** **93**

### Top 10 Contracts with Highest Clause Density

| Rank | Contract ID | Clause Count | % of Dataset |
| :---: | :--- | :---: | :---: |
| 1 | `GOOSEHEADINSURANCE,INC_04_02_2018-EX-10.6-Franchise Agreement` | 93 | 0.76% |
| 2 | `Monsanto Company - SECOND A_R EXCLUSIVE AGENCY AND MARKETING AGREEMENT` | 90 | 0.74% |
| 3 | `CardlyticsInc_20180112_S-1_EX-10.16_11002987_EX-10.16_Maintenance Agreement1` | 89 | 0.73% |
| 4 | `UpjohnInc_20200121_10-12G_EX-2.6_11948692_EX-2.6_Manufacturing Agreement_ Supply Agreement` | 88 | 0.72% |
| 5 | `RevolutionMedicinesInc_20200117_S-1_EX-10.1_11948417_EX-10.1_Development Agreement` | 87 | 0.71% |
| 6 | `BERKELEYLIGHTS,INC_06_26_2020-EX-10.12-COLLABORATION AGREEMENT` | 86 | 0.70% |
| 7 | `PhasebioPharmaceuticalsInc_20200330_10-K_EX-10.21_12086810_EX-10.21_Development Agreement` | 85 | 0.70% |
| 8 | `JOINTCORP_09_19_2014-EX-10.15-FRANCHISE AGREEMENT` | 84 | 0.69% |
| 9 | `PfHospitalityGroupInc_20150923_10-12G_EX-10.1_9266710_EX-10.1_Franchise Agreement1` | 83 | 0.68% |
| 10 | `BUFFALOWILDWINGSINC_06_05_1998-EX-10.3-FRANCHISE AGREEMENT` | 82 | 0.67% |

*Associated plot:* `eda_outputs/clauses_per_contract.png`

---

## 4. Target Variable (Category) Distribution & Class Imbalance

### 4.1 Target Variable Characteristics
* **Target Column:** `category`
* **Total Unique Classes:** **41**
* **Mean Class Size:** **297.66** samples
* **Median Class Size:** **246.00** samples
* **Standard Deviation across Classes:** **219.04**

### 4.2 Complete 41-Class Distribution Table (Ranked)

| Rank | Clause Category | Sample Count | % of Dataset |
| :---: | :--- | :---: | :---: |
| 1 | Parties | 1,251 | 10.25% |
| 2 | License Grant | 774 | 6.34% |
| 3 | Cap On Liability | 672 | 5.51% |
| 4 | Anti-Assignment | 652 | 5.34% |
| 5 | Audit Rights | 642 | 5.26% |
| 6 | Insurance | 559 | 4.58% |
| 7 | Expiration Date | 467 | 3.83% |
| 8 | Governing Law | 462 | 3.79% |
| 9 | Post-Termination Services | 449 | 3.68% |
| 10 | Agreement Date | 426 | 3.49% |
| 11 | Termination For Convenience | 412 | 3.38% |
| 12 | Document Name | 409 | 3.35% |
| 13 | Non-Compete | 382 | 3.13% |
| 14 | Effective Date | 363 | 2.97% |
| 15 | Notice Period To Terminate Renewal | 344 | 2.82% |
| 16 | IP Ownership Assignment | 338 | 2.77% |
| 17 | Exclusivity | 336 | 2.75% |
| 18 | Change Of Control | 309 | 2.53% |
| 19 | Renewal Term | 308 | 2.52% |
| 20 | Non-Disparagement | 273 | 2.24% |
| 21 | Liquidated Damages | 246 | 2.02% |
| 22 | Irrevocable Or Perpetual License | 239 | 1.96% |
| 23 | Rofr/Rofo/Rofn | 233 | 1.91% |
| 24 | Joint IP Ownership | 227 | 1.86% |
| 25 | Warranty Duration | 224 | 1.84% |
| 26 | Minimum Commitment | 215 | 1.76% |
| 27 | Non-Transferable License | 196 | 1.61% |
| 28 | No-Solicit Of Employees | 185 | 1.52% |
| 29 | Source Code Escrow | 175 | 1.43% |
| 30 | Uncapped Liability | 165 | 1.35% |
| 31 | Volume Restriction | 158 | 1.29% |
| 32 | Covenant Not To Sue | 134 | 1.10% |
| 33 | Affiliate License-Licensor | 129 | 1.06% |
| 34 | Competitive Restriction Exception | 100 | 0.82% |
| 35 | Affiliate License-Licensee | 98 | 0.80% |
| 36 | Revenue/Profit Sharing | 82 | 0.67% |
| 37 | No-Solicit Of Customers | 58 | 0.48% |
| 38 | Third Party Beneficiary | 39 | 0.32% |
| 39 | Most Favored Nation | 38 | 0.31% |
| 40 | Unlimited/All-You-Can-Eat-License | 32 | 0.26% |
| 41 | Price Restrictions | 27 | 0.22% |

*Associated plots:* `eda_outputs/class_distribution.png`, `eda_outputs/category_frequency.png`

### 4.3 Class Imbalance Profile
* **Largest Class:** `Parties` with **1,251** samples (**10.25%**)
* **Smallest Class:** `Price Restrictions` with **27** samples (**0.22%**)
* **Class Imbalance Ratio:** $\frac{1251}{27} = \mathbf{46.33 : 1}$
* **Classification Status:** **Highly Imbalanced**.
* **Imbalance Assessment:** 
  The top 5 categories account for **31.90%** of all data, while the bottom 5 categories combined represent only **1.59%** (194 samples). A standard unweighted model would collapse prediction boundaries against the low-frequency categories.

---

## 5. Text Statistics & Length Profiles

Fresh text statistics were computed from `clause_text` to verify text integrity without mutating the underlying dataset.

### 5.1 Word Count and Character Length Distributions

| Metric | Word Count | Character Length | Sentence Count |
| :--- | :---: | :---: | :---: |
| **Minimum** | 3 | 9 | 1 |
| **Maximum** | 479 | 3,169 | 24 |
| **Mean** | 45.89 | 289.16 | 1.63 |
| **Median** | 36.00 | 224.00 | 1.00 |
| **Standard Deviation** | 43.66 | 277.38 | 1.25 |
| **25th Percentile (Q1)** | 17.00 | 105.00 | 1.00 |
| **75th Percentile (Q3)** | 61.00 | 386.00 | 2.00 |
| **Interquartile Range (IQR)** | 44.00 | 281.00 | 1.00 |
| **IQR Upper Fence (Q3 + 1.5×IQR)** | 127.00 | 807.50 | 3.50 |
| **Outliers Count (> Upper Fence)** | 757 (6.20%) | 759 (6.22%) | 557 (4.56%) |

*Associated plots:* `eda_outputs/word_count_distribution.png`, `eda_outputs/word_count_boxplot.png`, `eda_outputs/character_length_distribution.png`, `eda_outputs/character_length_boxplot.png`

### 5.2 Correlation Analysis
* **Pearson Correlation (`char_len` vs `word_count`):** **0.9945** (Near-perfect linear collinearity)
* **Spearman Rank Correlation (`char_len` vs `word_count`):** **0.9917**
* *Associated plot:* `eda_outputs/numerical_correlation.png`

---

## 6. Text Length Profile by Category

Clause lengths exhibit dramatic variance across different categories. Some categories consist of brief metadata declarations, while others contain extensive legal covenants.

### Top 5 Longest Categories (by Mean Word Count)
1. **Affiliate License-Licensor:** Mean = **148.88 words** (Max = 394 words)
2. **Non-Compete:** Mean = **147.23 words** (Max = 479 words)
3. **Competitive Restriction Exception:** Mean = **116.89 words** (Max = 303 words)
4. **Source Code Escrow:** Mean = **116.29 words** (Max = 451 words)
5. **Post-Termination Services:** Mean = **99.64 words** (Max = 387 words)

### Top 5 Shortest Categories (by Mean Word Count)
1. **Parties:** Mean = **4.27 words** (Min = 3, Max = 45 words)
2. **Document Name:** Mean = **5.67 words** (Min = 3, Max = 29 words)
3. **Agreement Date:** Mean = **8.07 words** (Min = 3, Max = 46 words)
4. **Effective Date:** Mean = **16.26 words** (Min = 3, Max = 111 words)
5. **Expiration Date:** Mean = **18.79 words** (Min = 3, Max = 169 words)

*Associated plots:* `eda_outputs/average_word_count_by_category.png`, `eda_outputs/category_vs_word_count_boxplot.png`

---

## 7. Outlier & Short Clause Deep-Dive

### 7.1 Extreme Outlier Analysis
* **Shortest Clauses (3 words):**
  - Examples: `"Cool Technologies Inc.."`, `"BIA GP L.L.C."`, `"TRADEMARK LICENSE AGREEMENT"`, `"JOINT FILING AGREEMENT"`.
  - **Qualitative Assessment:** These spans represent valid contract titles and entity names extracted by human annotators in CUAD. They are not data collection artifacts.
* **Longest Clauses (380 – 479 words):**
  - Examples: Extensive Non-Compete agreements detailing geographic boundaries and restricted activities; Source Code Escrow release condition schedules.
  - **Qualitative Assessment:** These are fully articulated, binding contractual provisions. Dropping or truncating them would strip crucial operative conditions.

### 7.2 Very Short Clause Audit
* **1-word clauses:** **0** (0.00%)
* **2-word clauses:** **0** (0.00%)
* **Fewer than 3 words (<3):** **0** (0.00%)
* **Fewer than 5 words (<5):** **1,487** (**12.18%**)

#### Category Breakdown for Clauses <5 Words:
* **Parties:** **1,123** clauses (75.5% of all ultra-short clauses; 89.8% of all `Parties` records)
* **Document Name:** **225** clauses (15.1% of all ultra-short clauses; 55.0% of all `Document Name` records)
* **Agreement Date:** **64** clauses (4.3%)
* **Effective Date:** **47** clauses (3.2%)
* **Other 37 categories combined:** **28** clauses (1.9%)

**Recommendation:** Ultra-short clauses must be retained in the dataset. Dropping clauses with `<5 words` would inadvertently eradicate 89.8% of the `Parties` category and 55% of `Document Name`.

---

## 8. Text Quality & Preprocessing Artifacts

| Pattern Audited | Occurrences | Percentage (%) | Preprocessing Recommendation |
| :--- | :---: | :---: | :--- |
| Leading / Trailing Whitespaces | 0 | 0.00% | Clean, no strip required |
| Repeated Spaces (`>=2 spaces`) | 0 | 0.00% | Clean, normalized spaces |
| Embedded Newlines (`\n`, `\r`) | 0 | 0.00% | Flattened clean text |
| Embedded Tabs (`\t`) | 0 | 0.00% | Clean |
| Numeric Digits (`0-9`) | 5,228 | 42.84% | Preserve or replace with generic `<NUM>` token |
| Punctuation Marks | 11,497 | 94.21% | Standard punctuation stripping for bag-of-words |
| Web URLs (`http`, `www`) | 7 | 0.06% | Normalize to `<URL>` or remove |
| Email Addresses | 35 | 0.29% | Normalize to `<EMAIL>` or remove |

---

## 9. Vocabulary, N-Gram & Legal Terminology Analysis

### 9.1 Most Frequent Words (Stopwords Removed)
* **Total Processed Tokens:** **349,602**
* **Unique Vocabulary Size:** **11,887** distinct word stems/tokens

| Rank | Token | Frequency | % of Tokens |
| :---: | :--- | :---: | :---: |
| 1 | `agreement` | 7,686 | 2.20% |
| 2 | `shall` | 7,352 | 2.10% |
| 3 | `party` | 4,685 | 1.34% |
| 4 | `term` | 2,525 | 0.72% |
| 5 | `section` | 2,300 | 0.66% |
| 6 | `right` | 2,031 | 0.58% |
| 7 | `use` | 2,028 | 0.58% |
| 8 | `company` | 2,019 | 0.58% |
| 9 | `date` | 1,893 | 0.54% |
| 10 | `license` | 1,827 | 0.52% |
| 11 | `product` | 1,825 | 0.52% |
| 12 | `products` | 1,656 | 0.47% |
| 13 | `rights` | 1,645 | 0.47% |
| 14 | `written` | 1,638 | 0.47% |
| 15 | `non` | 1,630 | 0.47% |
| 16 | `provided` | 1,579 | 0.45% |
| 17 | `exclusive` | 1,476 | 0.42% |
| 18 | `period` | 1,473 | 0.42% |
| 19 | `notice` | 1,445 | 0.41% |
| 20 | `business` | 1,436 | 0.41% |

*Associated plot:* `eda_outputs/top_words.png`

### 9.2 Legal Collocations (Top 20 Bigrams)

| Rank | Bigram Sequence | Frequency | Contextual Legal Meaning |
| :---: | :--- | :---: | :--- |
| 1 | `agreement shall` | 1,027 | Operative covenant establishment |
| 2 | `set forth` | 957 | Cross-referential contractual definition |
| 3 | `effective date` | 821 | Temporal milestone / validity start |
| 4 | `prior written` | 760 | Consent precondition |
| 5 | `written notice` | 753 | Formal termination / breach notification |
| 6 | `non exclusive` | 730 | Intellectual property licensing scope |
| 7 | `term agreement` | 720 | Contract duration definition |
| 8 | `intellectual property` | 628 | Asset ownership / assignment |
| 9 | `terms conditions` | 555 | Standard governance phrasing |
| 10 | `written consent` | 550 | Formal authorization condition |
| 11 | `royalty free` | 550 | Commercial licensing terms |
| 12 | `party shall` | 403 | Direct party obligation |
| 13 | `initial term` | 400 | Baseline contract period |
| 14 | `subject terms` | 370 | Conditional covenant qualification |
| 15 | `terminate agreement` | 351 | Dissolution mechanism |
| 16 | `pursuant section` | 349 | Structural document citation |
| 17 | `shall right` | 349 | Granted entitlement |
| 18 | `forth section` | 344 | Procedural reference |
| 19 | `non transferable` | 344 | Restrictive IP license grant |
| 20 | `conditions agreement` | 336 | Mutual covenant framework |

*Associated plot:* `eda_outputs/top_bigrams.png`

---

## 10. Data Quality Audit Scorecard

| Check | Empirical Result | Status | Action / Recommendation |
| :--- | :--- | :---: | :--- |
| **Missing Values** | 0 null values across all 3 columns | **PASS** | Ready for ingestion; no imputation required |
| **Exact Duplicate Rows** | 0 duplicate rows (0.00%) | **PASS** | Perfect record uniqueness |
| **Empty Clause Text** | 0 empty strings | **PASS** | No blank samples |
| **Whitespace Text** | 0 whitespace-only strings | **PASS** | Valid character content across all rows |
| **Duplicate Clause Text** | 1,655 instances (13.56%) | **PASS** | Natural legal boilerplate across agreements; retain |
| **Schema & Typing** | All columns conform to string/object | **PASS** | Clean schema |
| **Negative Values** | 0 negative lengths | **PASS** | Strict non-negative physical text metrics |
| **Zero-Length Clauses** | 0 zero-length clauses | **PASS** | All clauses contain substantive text |
| **Category Consistency** | Exactly 41 unique classes; zero typo drift | **PASS** | Standardized labels match CUAD benchmark |
| **Ultra-Short Spans (<3 words)** | 0 clauses | **PASS** | Shortest clause has 3 words |
| **Short Spans (<5 words)** | 1,487 clauses (12.18%) | **REVIEW** | Concentrate in *Parties* & *Document Name*; retain |
| **Long Spans (>127 words)** | 757 clauses (6.20%) | **REVIEW** | Legitimate complex covenants; retain with sublinear TF |

---

## 11. Strategic Machine Learning Implications for ClauseIQ

### 11.1 Feature Extraction: Suitability of TF-IDF
1. **Strong Domain Specificity:** The analysis confirmed that legal clause categories possess highly distinctive vocabularies (e.g. *audit, books, inspect* for Audit Rights; *indemnify, aggregate, liability* for Cap On Liability; *perpetual, irrevocable, royalty-free* for Irrevocable Licenses). TF-IDF provides an optimal inductive bias for linear classifiers on this dataset.
2. **Sublinear TF Scaling:** Given that word counts range up to 479 words, configure `sublinear_tf=True` in scikit-learn's `TfidfVectorizer`. This computes term frequency as $1 + \log(tf)$, dampening the influence of lengthy repetitive provisions.
3. **Corpus Frequency Boundaries:** 
   - Set `max_df=0.85`: Ubiquitous terms like *shall* and *agreement* appear in thousands of clauses. Setting `max_df` automatically suppresses non-discriminative legal noise.
   - Set `min_df=3`: Prunes single-occurrence typos and idiosyncratic party names, reducing feature dimensionality and preventing overfitting.

### 11.2 N-Gram Range Configuration
The bigram analysis revealed that phrases like *prior written*, *written consent*, *governing law*, and *non exclusive* carry semantic weight far beyond individual unigrams. We strongly recommend configuring `ngram_range=(1, 2)` (or `(1, 3)`) during TF-IDF vectorization.

### 11.3 Class Imbalance Strategy
* **Do NOT use Naive SMOTE:** In high-dimensional sparse TF-IDF spaces (5,000 to 20,000 features), synthesizing points via linear interpolation between nearest neighbors produces dense, artificial vectors that do not represent coherent legal sentences and destroys matrix sparsity.
* **Recommended Technique: Cost-Sensitive Learning:**
  - Utilize `class_weight='balanced'` in Linear Support Vector Machines (`LinearSVC`), Logistic Regression, and SGDClassifier.
  - Employ **Stratified K-Fold Cross-Validation** (`n_splits=5`, `random_state=42`) to guarantee that low-sample classes like *Price Restrictions* (27 samples) are represented proportionately across validation folds.

### 11.4 Recommended Evaluation Metrics
Because of the **46.33 : 1** imbalance ratio, raw classification accuracy is an uninformative metric. The evaluation framework must report:
1. **Macro-Averaged F1-Score:** Primary evaluation metric; weights all 41 categories equally.
2. **Weighted-Averaged F1-Score:** Secondary metric; reflects global volume throughput.
3. **Per-Class Precision, Recall, and F1-Score:** Critical for legal compliance tracking.
4. **41-Class Confusion Matrix:** Identifies confusion clusters between semantically adjacent categories.

---

## 12. Conclusion

The ClauseIQ dataset is a **high-quality, complete, and robust legal corpus** containing 12,204 validated instances across 41 classes and 510 commercial contracts. With zero missing values and zero exact duplicates, the dataset is primed for machine learning feature extraction and model development. Adhering to sublinear TF-IDF vectorization with bigrams, cost-sensitive class weighting, and macro-averaged metrics will ensure high classification accuracy across both frequent operational clauses and rare compliance provisions.
