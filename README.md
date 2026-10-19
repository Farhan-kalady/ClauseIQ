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
cd frontend
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

## 📈 Model Evaluation (Sprint 2 Complete 4-Model Benchmark)

All four classification algorithms were evaluated on the **exact same held-out stratified test set** (2,441 clauses) using the common TF-IDF representation strictly fit on training data ($N=9,763$).

| Model | Accuracy | Macro Precision | Macro Recall | Macro F1 (Primary) | Weighted Precision | Weighted Recall | Weighted F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Selected)** | 71.90% | **0.6481** | 0.6622 | **0.6474** | **0.7354** | 71.90% | 71.96% |
| **Linear SVM (Tuned C=0.1)** | **72.63%** | 0.6323 | **0.6665** | 0.6418 | 0.7331 | **72.63%** | **72.26%** |
| **Multinomial Naive Bayes (alpha=0.01)** | 69.27% | 0.6024 | 0.5867 | 0.5853 | 0.6996 | 69.27% | 69.03% |
| **Random Forest (200 trees, depth 50)** | 65.46% | 0.5527 | 0.5904 | 0.5634 | 0.6577 | 65.46% | 64.96% |

> **Selected Model**: **Logistic Regression** was chosen because it achieves the highest **Macro-F1 (0.6474)** across all 41 imbalanced legal categories, providing balanced protection on high-risk rare clauses while natively outputting well-calibrated confidence probabilities via softmax.
> Visual comparison charts and confusion matrices are saved in `results/model_comparison.png` and `results/confusion_matrices/`.

---

## 🔍 Intelligent Search System (TF-IDF + Cosine Similarity)

ClauseIQ implements high-speed, classical semantic clause retrieval without heavy neural dependencies:
- **Index**: 12,204 validated clauses pre-indexed in 10,000-dimensional TF-IDF space.
- **Scoring**: Cosine similarity between L2-normalized query vectors and corpus vectors.
- **Latency**: Sub-10ms query execution time.
- **Filtering**: Supports exact and fuzzy category filtering (`category_filter`) and score thresholds (`min_score`).

### Retrieval Benchmark ($P@k$ & $R@k$ on Realistic Queries)

| Query | Target Categories | P@1 | P@3 | P@5 | P@10 | R@5 | R@10 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `termination for convenience` | Termination For Convenience | 1.00 | 0.67 | 0.60 | 0.70 | 0.0122 | 0.0285 |
| `governing law` | Governing Law | 1.00 | 1.00 | 1.00 | 0.90 | 0.0108 | 0.0195 |
| `non-compete` | Non-Compete | 0.00 | 0.67 | 0.80 | 0.90 | 0.0156 | 0.0350 |
| `limitation of liability` | Cap On Liability, Uncapped Liability | 1.00 | 1.00 | 1.00 | 0.90 | 0.0060 | 0.0107 |
| `audit rights` | Audit Rights | 1.00 | 1.00 | 1.00 | 0.90 | 0.0078 | 0.0140 |
| **Macro Average** | **All Evaluated Queries** | **0.80** | **0.87** | **0.88** | **0.86** | **0.0105** | **0.0215** |

---

## ⚡ FastAPI Backend & API Endpoints

The backend is built with **FastAPI** and served with **Uvicorn**:

```bash
# Start FastAPI backend server
uvicorn main:app --reload --port 8000
```
Interactive Swagger documentation is available at: `http://localhost:8000/docs`

### 1. Clause Classification: `POST /classify`
**Request Body**:
```json
{
  "clause_text": "This Agreement and all disputes hereunder shall be governed by the laws of the State of New York."
}
```
**Response Body**:
```json
{
  "clause_text": "This Agreement and all disputes hereunder shall be governed by the laws of the State of New York.",
  "cleaned_text": "this agreement and all disputes hereunder shall be governed by the laws of the state of new york.",
  "predicted_category": "Governing Law",
  "confidence_score": 0.9886,
  "model_name": "LogisticRegression"
}
```

### 2. Intelligent Search: `POST /search`
**Request Body**:
```json
{
  "query": "termination for convenience",
  "top_k": 3,
  "category_filter": null,
  "min_score": 0.0
}
```
**Response Body**:
```json
{
  "query": "termination for convenience",
  "total_results": 3,
  "results": [
    {
      "rank": 1,
      "clause_text": "Termination for Convenience. [***].",
      "predicted_category": "Termination For Convenience",
      "true_category": "Termination For Convenience",
      "similarity_score": 1.0,
      "source_contract": "PHREESIA,INC_05_28_2019-EX-10.18-STRATEGIC ALLIANCE AGREEMENT"
    }
  ]
}
```

### 3. Document PDF & Text Upload: `POST /classify/file`
Upload a contract file (PDF or TXT) to automatically extract text, segment clauses, classify each clause, and persist the records into Supabase:
```powershell
curl -X POST "http://localhost:8000/classify/file" -F "file=@test_data/ClauseIQ_Synthetic_Company_Service_Agreement_Test.pdf"
```

---

## 🌐 Sprint 3: Full-Stack Web Application (React + Vite & Supabase)

ClauseIQ includes a modern, responsive React frontend integrated with the FastAPI backend and Supabase PostgreSQL database.

### 1. Environment Configuration (`.env`)
Create or edit `.env` in the project root:
```env
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_KEY=<your-publishable-anon-key>
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,*
```

### 2. Supabase Database Setup
Execute the DDL script in `database/schema.sql` via your Supabase SQL Editor:
- Creates `contracts`, `clauses`, `classification_logs`, and `search_logs` tables.
- Enables Row Level Security (RLS) with permissive read/write policies for the application.
- Configures B-tree indexes for fast queries.

### 3. Application Startup Instructions

#### Step 1: Start FastAPI Backend
```powershell
.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Health Status: `http://localhost:8000/health`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Alternative ReDoc: `http://localhost:8000/redoc`

#### Step 2: Start React Frontend
```powershell
cd frontend
npm run dev
```
- Web Application: `http://localhost:5173/`

### 4. How to Use the Web Application

#### A. Single Clause Classification
1. Open `http://localhost:5173/` in your browser.
2. Under **Contract Clause Classification**, select the **Paste Clause Text** tab.
3. Paste any contract clause (or click one of the quick sample chips: *Governing Law*, *Confidentiality*, *Termination*, *Non-Compete*).
4. Click **Classify Clause** to view the predicted category, calibrated confidence bar, and top-3 alternative classes.

#### B. Upload and Classify a PDF Document
1. In the **Contract Clause Classification** tab, click **Upload Contract Document (PDF / TXT)**.
2. Drag and drop or browse to select `test_data/ClauseIQ_Synthetic_Company_Service_Agreement_Test.pdf`.
3. Click **Extract & Classify Document**.
4. The system will extract the document text, segment the clauses, classify each clause, and store the metadata and clauses in Supabase.
5. Review the scrollable list of extracted and classified clauses directly in the interface.

#### C. Perform Intelligent Clause Search
1. Click the **Clause Search** tab in the navigation bar.
2. Enter your search query (e.g., `termination for convenience`, `limitation of liability`, `governing law`).
3. (Optional) Adjust the **Top Results (k)** slider (1 to 25) or select a specific category in the **Optional Category Filter** dropdown.
4. Click **Search** to view ranked matching clauses with Cosine Similarity percentages, predicted labels, and contract source identifiers.

---

## 🧪 Testing & Verification

Run the full automated test suite using `pytest`:
```bash
pytest tests/ -v
```
All **45 tests** across Sprint 1, Sprint 2, and Sprint 3 pass with 100% success covering:
- Text cleaning, NLTK lemmatization, and clause splitting
- Model artifact loading and inference
- Cosine similarity search, ranking order, and category filtering
- PDF extraction, upload limits (10 MB, 100 pages, `%PDF` magic bytes signature)
- Atomic database persistence, graceful fallback, and contract read endpoints (`/contracts`, `/contracts/{id}/clauses`)
- Scoped search over user-uploaded contracts

---

## 🎬 Running Artifact Generation & Model Evaluation

Rebuild artifacts reproducibly and evaluate final models:
```powershell
# Rebuild hybrid vectorizer and selected model
.venv\Scripts\python.exe src/build_artifacts.py

# Evaluate baseline protocol (Split A & Split B)
.venv\Scripts\python.exe src/evaluation_protocol.py

# Evaluate improved model vs. baseline
.venv\Scripts\python.exe src/evaluate_final_model.py
```

---

## 🚀 Machine Learning Pipeline & Results

### 1. Source Dataset
All statistics and models are derived from `data/clauseiq_dataset_clean.csv`:
- **Total Records**: 12,204 rows
- **Columns**: 3 (`contract_id`, `clause_text`, `category`)
- **Missing Values**: 0
- **Unique Contracts**: 510 commercial agreements
- **Unique Categories**: 41 legal clause categories
- **Top Categories**: *Parties* (1,251), *License Grant* (774), *Cap On Liability* (672), *Anti-Assignment* (652), *Audit Rights* (642)

### 2. Evaluated Splits
- **Split A (Comparable Stratified 80/20)**: $N=9,763$ train, $N=2,441$ test clauses (`random_state=42`).
- **Split B (Leakage-Safe Grouped 80/20 by `contract_id`)**: 408 train contracts ($N=9,718$), 102 test contracts ($N=2,486$). No contract appears in both partitions.

### 3. Final Production Model
- **Algorithm**: `LogisticRegression` ($C=1.0$, `class_weight='balanced'`)
- **Features**: 40,000 hybrid features (25,000 Word n-grams [1,2] + 15,000 Character n-grams `char_wb` [3,5]) with sublinear term frequency scaling and NLTK WordNet lemmatization.
- **Split B Test Results**: **0.7393 Accuracy**, **0.6947 Macro F1** (+2.56% over baseline), **0.8655 High Confidence Precision**.
- **Split A Test Results**: **0.7231 Accuracy**, **0.6591 Macro F1**, **0.1545 ECE** (calibrated down from 0.2822).

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
