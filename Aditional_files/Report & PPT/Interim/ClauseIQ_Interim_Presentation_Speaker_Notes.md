# ClauseIQ – Interim Project Presentation: Revised Speaker Notes & Defense Guide

**Project Title:** ClauseIQ – Machine Learning-Based Contract Clause Classification and Intelligent Search System  
**Student Name:** Mohammed Farhan K (Reg. No: MAC25MCA-2042)  
**Degree:** Master of Computer Applications (MCA)  
**Department:** Department of Computer Applications, Mar Athanasius College of Engineering (MACE), Kothamangalam  
**Project Guide:** Dr. Sonia Abraham (Associate Professor, Dept. of Computer Applications)  
**Milestone:** Interim Progress Review (September 2026)  
**Presentation Files:**  
- Primary File: [`ClauseIQ_Interim_Presentation_Revised.pptx`](file:///d:/SOFINS/Github/ClauseIQ/Aditional_files/Report%20&%20PPT/Interim/ClauseIQ_Interim_Presentation_Revised.pptx)  
- Backup File: [`ClauseIQ_Interim_Presentation_Revised.pptx`](file:///d:/SOFINS/Github/ClauseIQ/Aditional_files/Report%20&%20PPT/presentation/ClauseIQ_Interim_Presentation_Revised.pptx)

---

## Executive Presentation Strategy
- **Visual Design:** Less content, larger text (all body text $\ge$ 18–22 pt, titles 31 pt, stat numbers 38–46 pt).
- **Rule of Thumb:** The slide shows **only 3–4 concise bullet points or big visual numbers**; the **detailed technical explanation is delivered verbally via these speaker notes**.
- **Projector Legibility:** Every slide is readable from the back of the classroom without zooming.

---

## Slide 1 — Title Slide
- **Slide Content:**
  - Large Title: **ClauseIQ**
  - Subtitle: **Machine Learning-Based Contract Clause Classification and Intelligent Search System**
  - Phase: **Interim Project Presentation**
  - Metadata: **Mohammed Farhan K** | Reg No: **MAC25MCA-2042** | MCA, Department of Computer Applications, MACE
- **Speaker Notes (What to say):**
  > "Respected evaluators and my project guide Dr. Sonia Abraham, good morning. 
  > I am Mohammed Farhan K, presenting the Interim Project Presentation for my MCA mini project: 'ClauseIQ – Machine Learning-Based Contract Clause Classification and Intelligent Search System'.
  > During our first presentation, we proposed our system design and exploratory findings. Today, for this interim review, I am presenting the verified empirical results of our completed machine learning pipeline. This includes the training and hyperparameter tuning of four distinct classifiers, comprehensive multi-metric evaluations on our held-out test set, model selection based on our primary metric, error analysis using a full 41-by-41 confusion matrix, and our completed intelligent search prototype."

---

## Slide 2 — Problem & Motivation
- **Slide Content:**
  - Card 1: **MANUAL REVIEW** — Large contracts require time-consuming clause identification.
  - Card 2: **KEYWORD SEARCH** — Exact keyword search misses variations in legal wording.
  - Card 3: **CLASSIFICATION CHALLENGE** — 41 legal clause categories are highly imbalanced.
  - Bottom Banner: **GOAL: Automatically classify contract clauses and retrieve relevant clauses using classical ML.**
- **Speaker Notes (What to say):**
  > "Legal contract review is currently bottlenecked by three major challenges:
  > First, manual review across lengthy legal contracts is exhausting, slow, and prone to human error when locating specific risk provisions.
  > Second, standard keyword search tools fail because legal terminology varies widely across jurisdictions and drafters—for example, searching for 'limitation of liability' will completely miss clauses drafted as 'aggregate exposure'.
  > Third, automated clause classification is mathematically challenging because contract provisions span 41 distinct categories exhibiting severe statistical imbalance.
  > Our project goal is to build a practical, lightweight classical machine learning system that automatically classifies clauses into 41 categories and provides intelligent semantic clause retrieval."

---

## Slide 3 — Objectives & Current Scope
- **Slide Content:**
  - Left Section: **OBJECTIVES**
    - 1. Classify clauses into 41 categories
    - 2. Build TF-IDF based clause search
    - 3. Evaluate multiple ML models
  - Right Section: **CURRENTLY COMPLETED**
    - ✓ Dataset + preprocessing
    - ✓ TF-IDF feature extraction
    - ✓ 4 ML models trained & tuned
    - ✓ Model evaluation
    - ✓ Model selection
    - ✓ Search prototype
    - ✓ FastAPI prototype
- **Speaker Notes (What to say):**
  > "Slide 3 defines our interim project scope.
  > Our overarching engineering objectives are to classify contract clauses into 41 distinct legal categories, build a TF-IDF semantic clause retrieval engine, and systematically evaluate multiple machine learning models.
  > For this interim review milestone, we have completed the entire machine learning core: data validation, text preprocessing, 10,000-dimensional TF-IDF vectorization, training and tuning all four candidate classifiers, evaluating them on the held-out test set, selecting our model, building our search prototype, and implementing our FastAPI backend. The web interface and persistent database are scheduled for our upcoming final phase."

---

## Slide 4 — Dataset Specifications
- **Slide Content:**
  - 4 Big Number Stat Cards:
    - **510** CONTRACTS
    - **12,204** CLAUSE RECORDS
    - **41** CLAUSE CATEGORIES
    - **3** CORE FEATURES
  - Bottom Schema Box:
    - `contract_id  |  clause_text  |  category`
    - 100% Complete: 0 missing values • 0 empty strings • 0 duplicate rows
- **Speaker Notes (What to say):**
  > "Slide 4 shows our verified dataset specifications.
  > Our dataset is derived from the Contract Understanding Atticus Dataset (CUAD v1), curated by The Atticus Project.
  > It encompasses 510 commercial contracts containing exactly 12,204 labeled clause records across 41 categories.
  > The dataset schema consists of three columns: contract_id, clause_text, and category.
  > Through automated validation in `src/clean_dataset.py`, we confirmed 100% data integrity: zero missing values, zero empty strings, and zero duplicate records. The average clause length is 24 words, representing concise, high-density legal clauses."

---

## Slide 5 — Exploratory Data Analysis & Class Imbalance
- **Slide Content:**
  - Left Card:
    - Largest Category: **Parties — 1,251**
    - Smallest Category: **Price Restrictions — 27**
    - Imbalance Ratio: **46.33 : 1** (Large red typography)
    - Box: **Macro-F1 is more informative than Accuracy for this dataset.**
  - Right Card:
    - Embedded high-res [`class_distribution.png`](file:///d:/SOFINS/Github/ClauseIQ/reports/interim_report/figures/class_distribution.png)
- **Speaker Notes (What to say):**
  > "Slide 5 highlights our exploratory analysis of class distribution.
  > The dataset exhibits extreme class imbalance: 'Parties' is the largest category with 1,251 instances, while 'Price Restrictions' has only 27 instances.
  > This creates a severe imbalance ratio of 46.33 to 1.
  > Because of this skew, standard accuracy is misleading: a model could achieve over 70% accuracy simply by predicting common boilerplate like Parties while completely missing rare, high-consequence clauses like Price Restrictions. 
  > Therefore, Macro-F1—which weights all 41 classes equally—is established as our primary evaluation metric."

---

## Slide 6 — Data Preprocessing Pipeline
- **Slide Content:**
  - Horizontal Pipeline Flow:
    `RAW CLAUSE → LOWERCASE → REMOVE URL/EMAIL → CLEAN NOISE → NORMALIZE SPACES → CLEAN TEXT`
  - Example Card:
    - Before: `"This AGREEMENT shall be governed by Delaware! Contact legal@clauseiq.com or https://..."`
    - After: `"this agreement shall be governed by delaware contact for terms"`
- **Speaker Notes (What to say):**
  > "Slide 6 presents our text cleaning pipeline implemented in `src/text_cleaner.py`.
  > Raw clauses undergo case-folding, URL and email removal via regular expressions, noise filtering while preserving legal punctuation like dollar signs and percentages, and whitespace normalization.
  > The example shows how web links and irregular casing are cleaned into standardized tokens while preserving all substantive legal terms like 'governed by delaware'."

---

## Slide 7 — TF-IDF Feature Engineering
- **Slide Content:**
  - 5 Configuration Cards:
    - **10,000** FEATURES
    - **(1, 2)** N-GRAMS
    - **TRUE** SUBLINEAR TF
    - **2** MIN DF
    - **0.95** MAX DF
  - Bottom Anti-Leakage Card:
    - `TRAIN TEXT → FIT TF-IDF → TEST TEXT → TRANSFORM`
    - Vocabulary fitted only on training data to prevent data leakage.
    - Unigrams + Bigrams capture compound legal collocations ('governing law', 'audit rights').
- **Speaker Notes (What to say):**
  > "Slide 7 illustrates our feature extraction settings:
  > We configure 10,000 maximum features, unigrams and bigrams (1,2), sublinear TF scaling (1 + log(tf)), minimum document frequency of 2, and maximum document frequency of 0.95.
  > Bigrams are essential to capture two-word legal expressions like 'governing law' and 'prior written consent'.
  > Importantly, to prevent data leakage, the vectorizer was fitted strictly on the training partition and applied to the test partition via transform()."

---

## Slide 8 — Dataset Partitioning Strategy
- **Slide Content:**
  - Visual Partition Flow:
    - Top: **12,204 TOTAL CLAUSES**
    - Center Badge: **80 / 20 STRATIFIED SPLIT**
    - Left Card: **9,763 TRAIN SAMPLES (80%)**
    - Right Card: **2,441 TEST SAMPLES (20%)**
  - Bottom Note:
    - `41 classes preserved • random_state = 42 • Clause-level split — NOT contract-level`
- **Speaker Notes (What to say):**
  > "Slide 8 illustrates our dataset partition:
  > We performed an 80/20 stratified split with `random_state=42`, partitioning our 12,204 clauses into 9,763 training samples and 2,441 held-out test samples.
  > Stratification ensures all 41 categories maintain identical proportions in both splits.
  > Important clarification: this is a clause-level stratified split, not a contract-level split. All four models were evaluated on the exact same 2,441 held-out test instances."

---

## Slide 9 — Four Machine Learning Models
- **Slide Content:**
  - 4 Model Cards:
    - **LOGISTIC REGRESSION**: Linear classifier • Softmax decision surface with L2 regularization.
    - **LINEAR SVM**: Maximum-margin classifier • Separating hyperplane optimized for sparse text.
    - **NAIVE BAYES**: Probabilistic baseline • Fast generative word frequency baseline.
    - **RANDOM FOREST**: Tree ensemble • Decision tree ensemble evaluating non-linear bagging.
  - Bottom Bar:
    - `Same TF-IDF Features • Same Training Set • Same Held-Out Test Set`
- **Speaker Notes (What to say):**
  > "Slide 9 presents our four candidate models:
  > Logistic Regression: a multinomial linear model with L2 regularization.
  > Linear SVM: a maximum-margin hyperplane classifier well-suited for sparse text.
  > Naive Bayes: a fast probabilistic generative baseline.
  > Random Forest: an ensemble of decision trees to test non-linear bagging on text.
  > Crucially, all four models were trained on the same training set and evaluated on the exact same held-out test set."

---

## Slide 10 — Model Training & Hyperparameter Tuning
- **Slide Content:**
  - Compact Table (Font 21–22 pt):
    | MODEL | METHOD | BEST PARAMETER |
    | :--- | :---: | :---: |
    | **Naive Bayes** | GridSearchCV (5-Fold) | $\alpha = 0.01$ |
    | **Random Forest** | RandomizedSearchCV (3-Fold) | 200 trees, max_depth = 50 |
    | **Linear SVM** | GridSearchCV (3-Fold) | $C = 0.1$ |
    | **Logistic Regression** | L2 Regularization | $C = 1.0$ |
  - Bottom Card:
    - `Optimization Metric: Macro-F1 (Balances evaluation across all 41 categories)`
- **Speaker Notes (What to say):**
  > "Slide 10 summarizes the tuning parameters for all four classifiers.
  > All tuning was performed on the training partition using StratifiedKFold cross-validation optimizing for Macro-F1:
  > For Naive Bayes, GridSearchCV selected alpha = 0.01.
  > For Random Forest, RandomizedSearchCV selected 200 estimators and max_depth of 50.
  > For Linear SVM, grid search selected C = 0.1.
  > For Logistic Regression, L2 regularization with C = 1.0 and balanced class weights was utilized."

---

## Slide 11 — Implementation Code
- **Slide Content:**
  - Dark Code Box (Font 20 pt Consolas):
    ```python
    # TF-IDF Feature Extraction
    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
    X_train = vectorizer.fit_transform(X_train_text)
    X_test  = vectorizer.transform(X_test_text)

    # Model Training with Balanced Weights
    clf = LogisticRegression(max_iter=1000, class_weight="balanced")
    clf.fit(X_train, y_train)

    # Inference on Held-Out Test Set (N=2,441)
    y_pred = clf.predict(X_test)
    ```
  - Bottom Indicator:
    - `DATA → TF-IDF → MODEL → PREDICTION`
- **Speaker Notes (What to say):**
  > "Slide 11 shows the actual production code from our repository in `src/feature_extraction.py` and `src/train_baseline.py`.
  > First, we vectorize raw text using TfidfVectorizer with 10,000 features and unigram-bigram pairing. Notice that `fit_transform` is applied exclusively to `X_train_text`, while `X_test_text` is transformed using `transform()` to prevent data leakage.
  > Second, LogisticRegression is initialized with `class_weight='balanced'` to compensate for the 46:1 class imbalance.
  > Finally, the model fits on `X_train` and predicts on the 2,441 test samples."

---

## Slide 12 — Model Evaluation Results
- **Slide Content:**
  - Big Table (Font 22 pt bold):
    | Model | Accuracy | Precision | Recall | Macro-F1 |
    | :--- | :---: | :---: | :---: | :---: |
    | **Logistic Regression** | 71.90% | **64.81%** | 66.22% | **64.74%** |
    | **Linear SVM** | **72.63%** | 63.23% | **66.65%** | 64.18% |
    | **Naive Bayes** | 69.27% | 60.24% | 58.67% | 58.53% |
    | **Random Forest** | 65.46% | 55.27% | 59.04% | 56.34% |
  - Large Footer:
    - `TEST SET: 2,441 samples | 41 classes | Primary Metric: Macro-F1`
- **Speaker Notes (What to say):**
  > "Slide 12 is our core model evaluation table containing the verified results from `results/model_comparison.csv`:
  > Logistic Regression achieved 71.90% Accuracy, 64.81% Macro Precision, 66.22% Macro Recall, and 64.74% Macro-F1.
  > Linear SVM achieved 72.63% Accuracy, 63.23% Macro Precision, 66.65% Macro Recall, and 64.18% Macro-F1.
  > Naive Bayes achieved 69.27% Accuracy and 58.53% Macro-F1.
  > Random Forest achieved 65.46% Accuracy and 56.34% Macro-F1.
  > Notice that Linear SVM achieved the highest overall accuracy at 72.63%, but Logistic Regression achieved the highest Macro-F1 at 64.74%."

---

## Slide 13 — Model Comparison Visual Benchmark
- **Slide Content:**
  - Left: Large embedded chart [`model_comparison.png`](file:///d:/SOFINS/Github/ClauseIQ/results/model_comparison.png) (occupies 70% of slide area).
  - Right: Key Takeaways Card:
    - **SVM:** Highest Accuracy — **72.63%**
    - **Logistic Regression:** Highest Macro-F1 — **64.74%**
    - **NB / RF:** Lower Macro-F1 (58.53% / 56.34%)
- **Speaker Notes (What to say):**
  > "Slide 13 displays the model comparison bar chart generated at 300 DPI from `results/model_comparison.png`.
  > The chart visually shows the comparison across Accuracy, Macro-F1, and Weighted-F1:
  > Linear SVM leads in raw Accuracy with 72.63%.
  > Logistic Regression leads in Macro-F1 with 64.74%.
  > Both Naive Bayes and Random Forest lag significantly behind in Macro-F1, showing that linear models handle sparse high-dimensional TF-IDF vectors much better than tree ensembles."

---

## Slide 14 — Model Selection: Why Logistic Regression?
- **Slide Content:**
  - Left Card:
    - **LINEAR SVM**
    - Accuracy: **72.63%** (Highest Accuracy)
    - Macro-F1: **64.18%**
  - Right Card:
    - **LOGISTIC REGRESSION**
    - Accuracy: **71.90%**
    - Macro-F1: **64.74%** (Highest Macro-F1)
  - Center Banner:
    - **PRIMARY METRIC: MACRO-F1**
    - **SELECTED MODEL: LOGISTIC REGRESSION**
    - `Macro-F1 gives equal importance to all 41 classes regardless of sample frequency.`
- **Speaker Notes (What to say):**
  > "Slide 14 explains our model selection decision.
  > Our evaluation strategy defined Macro-F1 as the primary metric and Accuracy as the secondary metric.
  > Linear SVM achieved a higher raw accuracy of 72.63% compared to 71.90% for Logistic Regression.
  > However, Logistic Regression achieved a higher Macro-F1 of 64.74% compared to 64.18% for Linear SVM.
  > In an imbalanced 41-class dataset, Macro-F1 is essential because it gives equal importance to rare, high-consequence clauses like Price Restrictions and Non-Compete, rather than being dominated by frequent boilerplate.
  > Therefore, Logistic Regression was selected because Macro-F1 was defined as the primary evaluation metric."

---

## Slide 15 — Class-Level Performance
- **Slide Content:**
  - Clean Table with 6 Representative Categories (Font 21 pt):
    | Category | Precision | Recall | F1-Score |
    | :--- | :---: | :---: | :---: |
    | **Governing Law** | 100.00% | 96.74% | 98.34% |
    | **Parties** | 97.19% | 96.80% | 96.99% |
    | **Insurance** | 97.25% | 94.64% | 95.93% |
    | **Cap On Liability** | 79.46% | 65.93% | 72.06% |
    | **Affiliate License-Licensee** | 21.95% | 39.13% | 28.12% |
    | **Affiliate License-Licensor** | 11.11% | 21.43% | 14.63% |
  - Bottom Banner:
    - `Performance varies significantly across categories due to class imbalance and vocabulary overlap.`
- **Speaker Notes (What to say):**
  > "Slide 15 shows class-level results from our verified classification report in `results/classification_reports/logistic_regression_report.csv` across six representative categories:
  > Distinctive categories like Governing Law and Parties achieve near-perfect F1-scores of 98.34% and 96.99%.
  > Moderate provisions like Cap On Liability achieve 72.06% F1.
  > Challenging provisions such as Affiliate License-Licensee and Licensor achieve lower F1-scores (28.12% and 14.63%) because they share virtually identical vocabulary, differing only in who grants the license to whom."

---

## Slide 16 — Confusion Matrix Analysis
- **Slide Content:**
  - Left: Large embedded confusion matrix [`logistic_regression_cm.png`](file:///d:/SOFINS/Github/ClauseIQ/results/confusion_matrices/logistic_regression_cm.png) (occupies 70% of slide area).
  - Right Card:
    - **41 x 41 MATRIX**
    - • Rows = True Labels
    - • Columns = Predicted
    - • Diagonal = Correct
    - • Off-diagonal = Errors
    - Amber Note: `Most errors occur between classes with similar legal wording (e.g., Licensee vs. Licensor).`
- **Speaker Notes (What to say):**
  > "Slide 16 displays the full 41-by-41 confusion matrix for Logistic Regression on our held-out test set of 2,441 samples.
  > The vertical axis shows True Categories, and the horizontal axis shows Predicted Categories.
  > The bright diagonal confirms high accuracy on frequent provisions.
  > Off-diagonal errors are concentrated in specific pairs with similar wording, such as Affiliate License-Licensee versus Licensor, Cap On Liability versus Uncapped Liability, and Agreement Date versus Effective Date."

---

## Slide 17 — Search Prototype & Key Findings
- **Slide Content:**
  - Left Section: **SEARCH PROTOTYPE**
    - `TF-IDF + Cosine Similarity`
    - • **Precision@1 = 80%**
    - • **Precision@5 = 88%**
    - • **Precision@10 = 86%**
    - Alert Box: **BIGRAM ABLATION: Precision@1 drops 80% → 60% without bigrams**
  - Right Section: **KEY FINDINGS**
    - ✓ Linear models performed better on sparse TF-IDF features
    - ✓ Macro-F1 is essential for the imbalanced dataset
    - ✓ Similar legal vocabulary causes classification errors
    - ✓ Bigrams are critical for capturing legal collocations
- **Speaker Notes (What to say):**
  > "Slide 17 summarizes our search prototype and core machine learning insights.
  > In our search evaluation using TF-IDF and Cosine Similarity, the retrieval engine achieves 80% Precision@1, 88% Precision@5, and 86% Precision@10.
  > Our ablation experiment confirmed that bigrams are essential: without bigrams, Precision@1 drops by 20% (from 80% to 60%).
  > Our key machine learning takeaways are:
  > First, linear models handle sparse text spaces much better than tree ensembles;
  > Second, Macro-F1 is essential for an imbalanced legal dataset;
  > And third, vocabulary overlap is the primary source of classification confusion."

---

## Slide 18 — Current Status & Next Steps
- **Slide Content:**
  - Left Column: **COMPLETED ✓** (Light green card, font 21 pt)
    - • Dataset & EDA
    - • Preprocessing pipeline
    - • TF-IDF feature space
    - • 4 ML models trained & tuned
    - • Model evaluation
    - • Logistic Regression selected
    - • Confusion matrix analysis
    - • Search prototype + ablation
    - • FastAPI prototype
  - Right Column: **NEXT PHASE →** (Light blue card, font 22 pt)
    - • Supabase integration
    - • React.js user interface
    - • End-to-end integration
    - • Cloud deployment
    - • Final validation & testing
- **Speaker Notes (What to say):**
  > "Slide 18 provides an honest interim progress audit:
  > On the left, completed tasks include dataset validation, preprocessing, TF-IDF vectorization, training and tuning all four models, multi-metric evaluation, model selection of Logistic Regression, confusion matrix analysis, search prototype, and our FastAPI backend.
  > On the right, work scheduled for our final phase includes connecting the live Supabase database, building the React user interface, conducting end-to-end integration testing, and final cloud deployment."

---

## Slide 19 — Thank You
- **Slide Content:**
  - Large Title: **THANK YOU** (56 pt)
  - Subtitle: **Questions & Discussion** (28 pt)
  - Center Card:
    - **ClauseIQ** (30 pt)
    - **Machine Learning-Based Contract Clause Classification and Intelligent Search System** (20 pt)
    - **Mohammed Farhan K | MAC25MCA-2042 | MACE** (18 pt)
- **Speaker Notes (What to say):**
  > "Thank you very much, respected evaluators and guide, for your time and feedback. 
  > ClauseIQ has completed its core machine learning phase with verified empirical results, achieving 64.74% Macro-F1 with Logistic Regression across 41 imbalanced legal categories, alongside a verified search prototype.
  > I welcome your questions, feedback, and suggestions for our upcoming final phase."
