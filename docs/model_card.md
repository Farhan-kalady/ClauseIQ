# ClauseIQ Model Card: Best Clause Classification Model

## 1. Model Details
- **Model Name**: ClauseIQ Legal Clause Classifier
- **Selected Architecture**: Logistic Regression (`sklearn.linear_model.LogisticRegression`)
- **Selection Criterion**: **Macro-F1** (Primary: 0.6474) and **Accuracy** (Secondary: 0.7190). Macro-F1 was designated as the primary selection criterion because the contract clause dataset contains 41 highly imbalanced classes; Macro-F1 assigns equal weight to rare legal obligations without allowing high-frequency categories to dominate.
- **Artifact Locations**:
  - Model: `artifacts/best_model.joblib` (and `models/logistic_regression.pkl`)
  - Feature Vectorizer: `artifacts/tfidf_vectorizer.joblib` (and `models/tfidf_vectorizer.pkl`)
  - Label Encoder: `artifacts/label_encoder.joblib` (and `models/label_encoder.pkl`)
- **Probability Support**: Supported natively via multinomial softmax (`predict_proba`).

---

## 2. Hyperparameters & Configuration
- **Penalty / Regularization**: L2 regularization
- **Inverse Regularization Strength ($C$)**: 1.0 (default)
- **Class Weight**: `"balanced"` (inversely proportional to class frequencies $n\_samples / (n\_classes \times \text{bincount}(y))$)
- **Solver**: `"lbfgs"`
- **Maximum Iterations**: `2000` (converged without convergence warnings)
- **Random State**: `42` (ensuring deterministic reproducibility)
- **Multi-Class Strategy**: Multinomial (`multinomial` / softmax formulation)

---

## 3. Training & Feature Representation
- **Dataset**: Contract Understanding Atticus Dataset (CUAD v1)
- **Corpus Dimension**:
  - Total Validated Clauses: 12,204 rows
  - Source Contracts: 510 unique commercial contracts
  - Unique Classes: 41 legal clause categories
- **Train/Test Split Methodology**:
  - Split: Stratified 80% train / 20% test split (`random_state=42`, `stratify=y`)
  - Training Set Size: **9,763 samples**
  - Held-out Test Set Size: **2,441 samples**
- **Feature Extraction Pipeline**:
  - Vectorizer: `TfidfVectorizer` (scikit-learn)
  - Vocabulary Size: 10,000 features
  - N-gram Range: `(1, 2)` (unigrams and bigrams)
  - Document Frequency Bounds: `min_df=2`, `max_df=0.95`
  - Sublinear TF Scaling: Enabled (`sublinear_tf=True`, using $1 + \log(\text{tf})$)
  - Data Leakage Prevention: Fitted strictly on the training partition ($N=9,763$); the test partition ($N=2,441$) was strictly transformed.

---

## 4. Evaluation Metrics on Held-Out Test Set (N=2,441)

All metrics were computed by scikit-learn from actual model predictions on the held-out test split:

| Metric | Score (Decimal) | Score (Percentage) |
| :--- | :---: | :---: |
| **Accuracy** | 0.7190 | 71.90% |
| **Macro Precision** | 0.6481 | 64.81% |
| **Macro Recall** | 0.6622 | 66.22% |
| **Macro F1 (Primary Metric)** | **0.6474** | **64.74%** |
| **Weighted Precision** | 0.7354 | 73.54% |
| **Weighted Recall** | 0.7190 | 71.90% |
| **Weighted F1** | 0.7196 | 71.96% |

### Benchmark Comparison Against Other Evaluated Models

| Rank | Model | Macro F1 | Accuracy | Weighted F1 | Selection Rationale |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | **Logistic Regression** | **0.6474** | **0.7190** | **0.7196** | **Selected**: Highest Macro-F1 across 41 classes; natively outputs calibrated confidence probabilities. |
| 2 | Linear SVM (C=0.1) | 0.6418 | 0.7263 | 0.7226 | Slightly higher accuracy (+0.73%), but lower Macro-F1 (-0.56%) and no native calibrated probabilities. |
| 3 | Multinomial Naive Bayes (alpha=0.01) | 0.5853 | 0.6927 | 0.6903 | Fast inference, but lacks class weighting; suppressed recall on rare categories. |
| 4 | Random Forest (200 trees, depth 50) | 0.5634 | 0.6546 | 0.6496 | Sub-optimal partitioning on high-dimensional sparse TF-IDF (10,000 features). |

---

## 5. Per-Class Performance Highlights

- **High-Performing Classes (F1 > 0.85)**:
  - *Audit Rights*: Precision 0.88, Recall 0.94, F1 0.91
  - *Anti-Assignment*: Precision 0.81, Recall 0.88, F1 0.84
  - *Governing Law*: Precision 0.86, Recall 0.93, F1 0.89
  - *Termination For Convenience*: Precision 0.83, Recall 0.87, F1 0.85
  - *Insurance*: Precision 0.85, Recall 0.90, F1 0.87
- **Challenging Classes (Low Support, F1 < 0.40)**:
  - *Price Restrictions* (Support: 5 in test): Precision 0.33, Recall 0.40, F1 0.36
  - *Most Favored Nation* (Support: 8 in test): Precision 0.44, Recall 0.50, F1 0.47
  - *Affiliate License-Licensor* (Support: 14 in test): Precision 0.38, Recall 0.36, F1 0.37

---

## 6. Limitations & Known Class Imbalance Issues
1. **Extreme Class Imbalance**:
   The CUAD dataset spans from 1,251 clauses for majority categories (*Parties*) down to only 27 clauses for minority categories (*Price Restrictions*). Although `class_weight='balanced'` boosts gradient updates for minority classes, rare categories still suffer from high variance due to small sample size.
2. **Contract-Level Overlap**:
   Because the dataset is partitioned via clause-level stratified splitting, clauses from the same parent contract may appear in both train and test partitions. Real-world contract drafting styles may have slight stylistic correlation across clauses within a single agreement.
3. **Lexical Boundary Sensitivity**:
   Classification relies on classical n-gram TF-IDF representations. Novel paraphrasing, unconventional legal vocabulary, or heavily obfuscated clauses not captured in the 10,000 feature vocabulary may see reduced confidence.
