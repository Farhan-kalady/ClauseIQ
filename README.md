# ClauseIQ

### Machine Learning-Based Contract Clause Classification & Intelligent Search System

ClauseIQ is a **Classical Machine Learning-based legal document analysis system** that automatically classifies clauses in commercial contracts and helps users quickly find relevant clauses through similarity-based search.

The system is designed to reduce the time and manual effort required to review lengthy legal contracts.

---

## 📌 Project Overview

Organizations handle a large number of contracts such as:

* Employment agreements
* Vendor contracts
* Non-disclosure agreements
* Service agreements
* Commercial agreements

Finding a particular clause manually can be time-consuming and error-prone. Traditional keyword search can also fail when the exact wording of a clause is unknown.

**ClauseIQ** addresses this problem by:

1. Extracting text from uploaded PDF contracts
2. Splitting the document into individual clauses
3. Converting clause text into numerical features using **TF-IDF**
4. Classifying clauses using Classical Machine Learning
5. Storing classified clauses in a database
6. Searching and ranking relevant clauses using **Cosine Similarity**

---

## 🎯 Objectives

* Automatically classify contract clauses into predefined legal categories.
* Reduce the manual effort required for contract review.
* Provide fast and relevance-ranked clause search.
* Compare different Classical Machine Learning algorithms.
* Identify the best-performing classification model.
* Provide an easy-to-use web interface for contract analysis.

---

## 🔄 System Workflow

```text
                ┌──────────────────┐
                │  Upload Contract │
                │       (PDF)      │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │  Text Extraction │
                │    PyMuPDF       │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ Clause Splitting │
                │  & Preprocessing │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │     TF-IDF       │
                │ Feature Extraction│
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │  ML Classification│
                │ LR / SVM / NB / RF│
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ Supabase/Postgres│
                │    Database      │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │  Clause Search   │
                │ Cosine Similarity│
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ Search Results & │
                │ Classification   │
                └──────────────────┘
```

---

## 📊 Dataset

ClauseIQ uses the **Contract Understanding Atticus Dataset (CUAD)**.

### Dataset Details

| Property          | Details                                 |
| ----------------- | --------------------------------------- |
| Dataset           | CUAD                                    |
| Full Name         | Contract Understanding Atticus Dataset  |
| Contracts         | 510 commercial contracts                |
| Annotated Clauses | 13,000+                                 |
| Categories        | 41 legal categories                     |
| Dataset Type      | Expert-annotated legal contract dataset |

### Example Categories

* Confidentiality
* Termination
* Payment Terms
* Liability
* Governing Law
* And other legal clause categories

Dataset source:

https://www.atticusprojectai.org/cuad

---

## 🤖 Machine Learning

ClauseIQ uses **Classical Machine Learning** rather than Deep Learning.

### Feature Extraction

**TF-IDF (Term Frequency–Inverse Document Frequency)** is used to convert textual clauses into numerical feature vectors.

### Classification Algorithms

The project compares the following algorithms:

* Logistic Regression
* Support Vector Machine (SVM)
* Naive Bayes
* Random Forest

The models are evaluated and the best-performing model is selected for the final system.

### Evaluation Metrics

The models are compared using:

* Accuracy
* Precision
* Recall
* F1-Score

---

## 🔎 Intelligent Clause Search

ClauseIQ provides similarity-based clause retrieval using **Cosine Similarity**.

Instead of depending only on exact keyword matching, the system converts the user's search query and contract clauses into TF-IDF vectors and calculates their similarity.

The clauses are then ranked according to their relevance to the query.

### Example

**Search Query:**

```text
What happens if the agreement is terminated?
```

The system can retrieve clauses related to:

```text
Termination
Early Termination
Agreement Termination
Termination Conditions
```

and rank them according to their similarity score.

---

## 🏗️ System Architecture

```text
User
  │
  ▼
React Frontend
  │
  ▼
FastAPI Backend
  │
  ├──────────────► PDF Text Extraction
  │
  ├──────────────► Clause Preprocessing
  │
  ├──────────────► TF-IDF
  │
  ├──────────────► ML Classification
  │
  └──────────────► Cosine Similarity Search
                         │
                         ▼
                 Supabase PostgreSQL
                         │
                         ▼
                    Results
```

---

## 🛠️ Technology Stack

### Frontend

* React.js

### Backend

* Python
* FastAPI

### Machine Learning

* Scikit-learn
* TF-IDF
* Logistic Regression
* Support Vector Machine
* Naive Bayes
* Random Forest

### NLP & Document Processing

* spaCy
* PyMuPDF

### Database

* Supabase
* PostgreSQL

### Development Tools

* VS Code
* Google Colab
* Jupyter Notebook
* Git
* GitHub

---

## 📁 Project Structure

```text
ClauseIQ/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
├── ml/
│   ├── preprocessing/
│   ├── training/
│   ├── models/
│   └── evaluation/
│
├── data/
│   └── README.md
│
├── notebooks/
│   └── experiments/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ClauseIQ.git
cd ClauseIQ
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Do **not** commit your `.env` file to GitHub.

---

## ▶️ Running the Project

### Start the FastAPI Backend

```bash
uvicorn main:app --reload
```

The API will be available locally through the FastAPI server.

### Start the React Frontend

```bash
npm install
npm run dev
```

The frontend will then be available through the local development server.

---

## 🧪 Machine Learning Pipeline

The ML pipeline consists of the following stages:

```text
Raw Contract Text
       ↓
Text Preprocessing
       ↓
Clause Extraction
       ↓
TF-IDF Feature Extraction
       ↓
Train/Test Split
       ↓
Model Training
       ↓
Model Evaluation
       ↓
Best Model Selection
       ↓
Clause Classification
```

---

## 📈 Model Evaluation (Sprint 1 Results)

Each classification algorithm is evaluated on the identical held-out stratified test set (2,441 clauses) using TF-IDF features strictly fit on training data.

| Model | Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted F1 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Baseline)** | 71.90% | 0.6481 | 0.6622 | 64.74% | 71.96% |
| **Linear SVM (Tuned C=0.1)** | **72.63%** | 0.6323 | **0.6665** | 64.18% | **72.26%** |
| Naive Bayes | Sprint 2 | Sprint 2 | Sprint 2 | Sprint 2 | Sprint 2 |
| Random Forest | Sprint 2 | Sprint 2 | Sprint 2 | Sprint 2 | Sprint 2 |

---

## 🚀 Sprint 1: Core ML Pipeline

Sprint 1 delivers the fully functional, reproducible Core Machine Learning Pipeline for ClauseIQ.

### 1. Sprint Objective
Build and verify the complete core ML pipeline for classifying contract clauses into CUAD clause categories using Classical Machine Learning, from raw PDF ingestion to tuned model evaluation.

### 2. Dataset Information (Source of Truth)
All statistics and models are derived from `data/clauseiq_dataset.csv`:
- **Total Records**: 12,204 rows
- **Columns**: 3 (`contract_id`, `clause_text`, `category`)
- **Missing Values**: 0
- **Unique Contracts**: 510 commercial agreements
- **Unique Categories**: 41 legal clause categories
- **Top Categories**: *Parties* (1,251), *License Grant* (774), *Cap On Liability* (672), *Anti-Assignment* (652), *Audit Rights* (642)
- **Bottom Categories**: *Unlimited/All-You-Can-Eat-License* (32), *Price Restrictions* (27)
- *Note on row count discrepancy*: An earlier raw extract noted 13,823 rows; the active verified dataset contains exactly 12,204 clean rows after deduplication.

### 3. Pipeline Components
- **PDF Text Extraction (`src/pdf_extractor.py`)**: Uses PyMuPDF (`pymupdf`) to extract text from text-based contract PDFs, handling path resolution dynamically.
- **Clause Splitting (`src/clause_splitter.py`)**: Uses spaCy's `en_core_web_sm` model for sentence/clause boundary detection via `doc.sents`.
- **Text Cleaning (`src/text_cleaner.py`, `src/clean_dataset.py`)**: Normalizes whitespace, strips URLs and emails, removes non-alphanumeric noise while preserving essential legal terms (*shall*, *may*, *not*, *unless*, *provided*, *agreement*, *party*).
- **TF-IDF Vectorization (`src/feature_extraction.py`)**: Extracts unigram and bigram features (`ngram_range=(1,2)`, `max_features=10000`, `sublinear_tf=True`). Strict train-only fitting prevents data leakage.
- **Stratified Train/Test Split**: 80/20 split (`random_state=42`) producing 9,763 training samples and 2,441 test samples across 41 classes.
- **Baseline Logistic Regression (`src/train_baseline.py`)**: Balanced class-weighted baseline achieving 71.90% accuracy and 64.74% macro F1.
- **Tuned Linear SVM (`src/train_svm.py`)**: Balanced `LinearSVC` tuned using 3-fold cross-validation (`C=0.1`), achieving 72.63% accuracy and 72.26% weighted F1.
- **Model Comparison (`src/model_comparison.py`)**: Generates comparative benchmark across models on the test partition.
- **End-to-End Demo (`src/demo_pipeline.py`)**: Ingests `sample_contract.pdf`, segments clauses, and classifies them into legal categories.

### 4. Serialized Model Artifacts (`models/`)
- `tfidf_vectorizer.pkl`: Fitted TF-IDF vectorizer (10,000 features)
- `label_encoder.pkl`: Label encoder mapping 41 classes
- `train_test_split.pkl`: Tuple of `(X_train, X_test, y_train, y_test)`
- `logistic_regression.pkl`: Trained Logistic Regression model
- `svm_classifier.pkl`: Tuned Linear SVM classifier

### 5. How to Run the Sprint 1 Pipeline
From the project root:
```powershell
# 1. Clean the raw dataset
.venv\Scripts\python.exe src\clean_dataset.py

# 2. Extract TF-IDF features and create stratified train/test split
.venv\Scripts\python.exe src\feature_extraction.py

# 3. Train and evaluate Logistic Regression baseline
.venv\Scripts\python.exe src\train_baseline.py

# 4. Tune and evaluate Linear SVM
.venv\Scripts\python.exe src\train_svm.py

# 5. Run model comparison
.venv\Scripts\python.exe src\model_comparison.py

# 6. Run end-to-end PDF-to-classification demonstration
.venv\Scripts\python.exe src\demo_pipeline.py

# 7. Run automated test suite
.venv\Scripts\python.exe -m unittest tests\test_sprint1.py -v
```

### 6. Limitations & Notes
- **Contract-Level Overlap**: The clause-level stratified split results in 99.8% of test contracts having clauses in the training set. Contract-grouped splits (`GroupShuffleSplit`) will be evaluated in future sprints to test cross-contract generalization.

---

## 🔐 Privacy & Security

Legal contracts may contain confidential information.

The project therefore aims to:

* Avoid exposing confidential documents publicly.
* Store sensitive configuration values using environment variables.
* Avoid committing API keys and database credentials to GitHub.
* Consider privacy-preserving NLP techniques as a future enhancement.

---

## ☁️ Cloud Deployment

The current mini-project version is designed to run on **local/self-hosted infrastructure**.

No external cloud deployment platform is required for the current implementation.

Cloud deployment can be considered in future versions.

---

## 🚀 Future Scope

The current project focuses on Classical Machine Learning.

Future enhancements may include:

* Hybrid Retrieval-Augmented Generation (RAG)
* Large Language Model integration
* Contract summarization
* Conversational legal assistant
* Multilingual contract processing
* OCR for scanned contracts
* Voice-based search
* Privacy-aware NLP preprocessing
* Enterprise-scale deployment

> RAG and LLM technologies are **not part of the current mini-project scope**.

---

## 📚 Research References

1. E. Quevedo, T. Cerny, A. Rodriguez, P. Rivas, J. Yero, K. Sooksatra, A. Zhakubayev, and D. Taibi, "Legal Natural Language Processing From 2015 to 2022: A Comprehensive Systematic Mapping Study of Advances and Applications," *IEEE Access*, vol. 12, pp. 145286–145317, 2024.

2. M. Siino, M. Falco, D. Croce, and P. Rosso, "Exploring LLMs Applications in Law: A Literature Review on Current Legal NLP Approaches," *IEEE Access*, vol. 13, pp. 18253–18276, 2025.

3. M. Kutbi, "Named Entity Recognition Utilized to Enhance Text Classification While Preserving Privacy," *IEEE Access*, vol. 11, pp. 117576–117581, 2023.

4. D. Hendrycks, C. Burns, A. Chen, and S. Ball, "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review," *NeurIPS Datasets and Benchmarks Track*, 2021.

---

## 🎓 Academic Project

**Project:** ClauseIQ
**Type:** MCA Mini Project
**Domain:** Machine Learning / Natural Language Processing / Legal Document Analysis
**Department:** MCA – AI & Data Science
**Institution:** Mar Athanasius College of Engineering

---

## ⭐ Project Highlights

* 📄 Automated contract clause extraction
* 🤖 Classical Machine Learning classification
* 🔎 TF-IDF + Cosine Similarity search
* 📊 Multiple ML model comparison
* 🗂️ Legal clause categorization
* 🗄️ PostgreSQL-based data storage
* 🌐 React + FastAPI web application
* 🔐 Privacy-conscious document processing

---

## 📜 License

This project is developed for **academic and educational purposes** as part of an MCA Mini Project.
