# ClauseIQ Model Card: Best Legal Clause Classification Model

## 1. Model Details
- **Model Name**: ClauseIQ Legal Clause Classifier (`LogisticRegression-HybridWordChar`)
- **Selected Architecture**: Multi-class Multinomial Logistic Regression (`sklearn.linear_model.LogisticRegression`) with L2 regularization and balanced class weighting.
- **Selection Criterion**: **Cross-Validated Macro-F1 on Grouped Splits (5-Fold StratifiedGroupKFold on Training Contracts)**. Macro-F1 was designated as the primary selection criterion because the contract clause dataset contains 41 highly imbalanced classes; Macro-F1 weights rare legal obligations equally without allowing high-frequency categories to dominate.
- **Artifact Locations**:
  - Model: `artifacts/best_model.joblib`
  - Feature Vectorizer: `artifacts/tfidf_vectorizer.joblib` (FeatureUnion: Word + Character n-grams)
  - Label Encoder: `artifacts/label_encoder.joblib`
  - Manifest: `artifacts/manifest.json`
- **Probability Support**: Supported natively via multinomial softmax (`predict_proba`).

---

## 2. Hyperparameters & Configuration
- **Penalty / Regularization**: L2 regularization
- **Inverse Regularization Strength ($C$)**: 1.0
- **Class Weight**: `"balanced"` (inversely proportional to class frequencies: $n\_samples / (n\_classes \times \text{bincount}(y))$)
- **Solver**: `"lbfgs"`
- **Maximum Iterations**: `2000` (converged without warnings)
- **Random State**: `42` (ensuring deterministic reproducibility)
- **Multi-Class Strategy**: Multinomial softmax (`predict_proba`)

---

## 3. Training & Feature Representation
- **Dataset**: Contract Understanding Atticus Dataset (CUAD v1 derived)
  - Total Validated Clauses: 12,204 rows
  - Source Contracts: 510 unique commercial contracts
  - Unique Classes: 41 legal clause categories
- **NLP Preprocessing**:
  - Lowercasing, URL/email removal, legal punctuation preservation
  - NLTK WordNet Lemmatization (`clean_text_lemmatized`)
- **Feature Extraction Pipeline (FeatureUnion)**:
  - **Sub-pipe 1 (Word n-grams)**: `TfidfVectorizer(max_features=25000, ngram_range=(1, 2), min_df=2, max_df=0.95, sublinear_tf=True)`
  - **Sub-pipe 2 (Character n-grams inside word boundaries)**: `TfidfVectorizer(max_features=15000, analyzer='char_wb', ngram_range=(3, 5), min_df=3, sublinear_tf=True)`
  - **Total Dimensionality**: 40,000 features
  - **Data Leakage Prevention**: Vectorizer fitted strictly on training partition ($N=9,763$ for Split A; $N=9,718$ for Split B); the test partition was strictly transformed.

---

## 4. Evaluation Metrics on Held-Out Test Partitions

All metrics were computed by scikit-learn from actual model predictions on the held-out test splits without manual adjustment:

### 4.1 Split A: Comparable Stratified 80/20 ($N=2,441$)

| Metric | Baseline Score | Improved Model Score | Improvement |
| :--- | :---: | :---: | :---: |
| **Accuracy** | 0.7190 (71.90%) | **0.7231 (72.31%)** | +0.41% |
| **Macro Precision** | 0.6481 (64.81%) | **0.6607 (66.07%)** | +1.26% |
| **Macro Recall** | 0.6622 (66.22%) | **0.6696 (66.96%)** | +0.74% |
| **Macro F1 (Primary Metric)** | 0.6474 (64.74%) | **0.6591 (65.91%)** | **+1.17%** |
| **Weighted Precision** | 0.7354 (73.54%) | **0.7381 (73.81%)** | +0.27% |
| **Weighted Recall** | 0.7190 (71.90%) | **0.7231 (72.31%)** | +0.41% |
| **Weighted F1** | 0.7196 (71.96%) | **0.7265 (72.65%)** | +0.69% |
| **Expected Calibration Error (ECE)** | 0.2822 | **0.1545** | **-0.1277** (improved calibration) |

### 4.2 Split B: Leakage-Safe Grouped Split by `contract_id` ($N=2,486$, 102 contracts)

| Metric | Baseline Score | Improved Model Score | Improvement |
| :--- | :---: | :---: | :---: |
| **Accuracy** | 0.7305 (73.05%) | **0.7393 (73.93%)** | +0.88% |
| **Macro Precision** | 0.6726 (67.26%) | **0.6976 (69.76%)** | +2.50% |
| **Macro Recall** | 0.6971 (69.71%) | **0.7123 (71.23%)** | +1.52% |
| **Macro F1 (Primary Metric)** | 0.6691 (66.91%) | **0.6947 (69.47%)** | **+2.56%** |
| **Weighted F1** | 0.7269 (72.69%) | **0.7371 (73.71%)** | +1.02% |
| **High Confidence Precision (≥ 0.50)** | 0.9024 | **0.8655** | Evaluated on 53.22% of all clauses |
| **Expected Calibration Error (ECE)** | 0.3115 | **0.2005** | **-0.1110** (improved calibration) |

---

## 5. Summary of Model Experimentation Rounds

Extensive cross-validation experiments were conducted on the training data only (recorded in `results/experiments.csv`):

| Round ID | Hypothesis / Change | CV Macro F1 | CV Accuracy | Key Takeaway |
| :--- | :--- | :---: | :---: | :--- |
| **EXP-00** | Baseline: regex cleaning + 10k word TF-IDF + LogReg | 0.6614 | 0.7430 | Initial baseline reference |
| **EXP-01C** | NLTK Stopword Removal | 0.6567 | 0.7388 | **Hurt** performance (-0.47% F1); legal modals ("shall", "may", "unless") are informative |
| **EXP-01D** | NLTK WordNet Lemmatization | 0.6662 | 0.7467 | **Helped** (+0.48% F1); normalizes inflected legal verbs |
| **EXP-02D** | Hybrid Word (25k) + Char_wb (15k) TF-IDF | **0.6865** | **0.7618** | **Major improvement** (+2.51% F1); character n-grams capture morphological subwords |
| **EXP-03A** | LinearSVC ($C=0.1$, balanced) | 0.6834 | 0.7624 | Strong accuracy, but no native probabilities |
| **EXP-03E** | ComplementNB ($\alpha=0.1$) | 0.5136 | 0.6968 | Poor performance on high-dimensional hybrid features |
| **EXP-04B** | Unweighted LogReg (`class_weight=None`) | 0.6213 | 0.7592 | Severe degradation (-6.52% F1) on rare categories |
| **EXP-05-SIG** | Post-hoc CalibratedClassifierCV | 0.6333 | 0.7561 | Platt scaling on 41 classes distorted multiclass argmax ranking |

**Chosen Model:** `LogisticRegression` ($C=1.0$, `class_weight='balanced'`) with Hybrid Word + Character TF-IDF (40,000 features) and NLTK Lemmatization.

---

## 6. Known Limitations & Error Boundaries

1. **Inherently Ambiguous Category Pairs**:
   - `Agreement Date` vs `Effective Date`: Frequently contained within the exact same introductory recitals.
   - `Cap On Liability` vs `Uncapped Liability`: Exception carve-outs inside limitation sections create co-occurrence noise.
2. **Extreme Class Imbalance**:
   - Categories with $<20$ total occurrences in CUAD (`Price Restrictions`, `Volume Restriction`, `Affiliate License-Licensor`) show lower F1 due to small support.
3. **Out-of-Scope Detection**:
   - Clauses with maximum predicted probability $<0.10$ exhibit lower precision (~28-32%) and are appropriately flagged by the API as "Out of supported category scope".
