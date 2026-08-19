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

## 📈 Model Evaluation

Each classification algorithm will be evaluated using the same dataset split and evaluation metrics.

Example comparison:

| Model               | Accuracy | Precision | Recall | F1-Score |
| ------------------- | -------: | --------: | -----: | -------: |
| Logistic Regression |      TBD |       TBD |    TBD |      TBD |
| SVM                 |      TBD |       TBD |    TBD |      TBD |
| Naive Bayes         |      TBD |       TBD |    TBD |      TBD |
| Random Forest       |      TBD |       TBD |    TBD |      TBD |

> **Note:** Actual values will be added after model training and evaluation.

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
