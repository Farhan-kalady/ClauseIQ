"""Systematic classical ML experimentation harness for ClauseIQ.

Executes numbered experiment rounds using StratifiedGroupKFold on training data only.
Prevents leakage: test set is never evaluated during rounds.
Logs every round to results/experiments.csv.
"""

from datetime import datetime, timezone
import os
from pathlib import Path
import re
import sys
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import VotingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold
from sklearn.naive_bayes import ComplementNB, MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from text_cleaner import clean_text

# Optional NLTK tools
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    _nltk_available = True
    _lemmatizer = WordNetLemmatizer()
    _stopwords = set(stopwords.words("english"))
    # Protect critical contractual/modal words
    _legal_keep_words = {"shall", "may", "not", "no", "unless", "except", "without", "against", "under", "all", "any", "each", "every", "both"}
    _filtered_stopwords = _stopwords - _legal_keep_words
except Exception:
    _nltk_available = False
    _lemmatizer = None
    _filtered_stopwords = set()


# Alternative cleaning functions
def clean_text_preserve_sections(text: str) -> str:
    """Cleaner that explicitly preserves section references and alphanumeric numbering."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " ", text)
    # Retain section markers, numbers, dots, hyphens, and legal punctuation
    text = re.sub(r"[^a-z0-9.,;:()\-\/§# ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_text_stopwords(text: str) -> str:
    """Cleaner applying NLTK stopword filtering while preserving legal keywords."""
    base = clean_text(text)
    if not _nltk_available or not base:
        return base
    tokens = [w for w in base.split() if w not in _filtered_stopwords]
    return " ".join(tokens)


def clean_text_lemmatized(text: str) -> str:
    """Cleaner applying NLTK WordNet lemmatization."""
    base = clean_text(text)
    if not _nltk_available or not base:
        return base
    tokens = [_lemmatizer.lemmatize(w) for w in base.split()]
    return " ".join(tokens)


def get_cv_folds(df_train, n_splits=5, random_state=42):
    sgkf = StratifiedGroupKFold(n_splits=n_splits)
    folds = list(sgkf.split(df_train, df_train["category_encoded"], groups=df_train["contract_id"]))
    return folds


def evaluate_cv(
    df_train,
    folds,
    text_preprocessor=None,
    feature_builder=None,
    model_factory=None,
    oversample_minority=False,
    min_samples_threshold=30,
):
    """Run CV across folds on training data only. Returns mean macro F1, accuracy, and weighted F1."""
    macro_f1s = []
    accuracies = []
    weighted_f1s = []

    # Pre-extract text column
    texts_raw = df_train["clause_text"].fillna("").astype(str).tolist()
    if text_preprocessor is not None:
        texts = [text_preprocessor(t) for t in texts_raw]
    else:
        # Default existing clean_text
        texts = df_train["clean_text"].fillna("").astype(str).tolist()

    y_all = df_train["category_encoded"].to_numpy()

    for fold_idx, (tr_idx, val_idx) in enumerate(folds):
        tr_texts = [texts[i] for i in tr_idx]
        val_texts = [texts[i] for i in val_idx]
        y_tr = y_all[tr_idx]
        y_val = y_all[val_idx]

        # In-fold oversampling of minority categories if requested
        if oversample_minority:
            # Count class frequencies in y_tr
            unique, counts = np.unique(y_tr, return_counts=True)
            class_counts = dict(zip(unique, counts))
            extra_texts = []
            extra_y = []
            rng = np.random.RandomState(42 + fold_idx)
            for c_label, count in class_counts.items():
                if count < min_samples_threshold:
                    c_indices = [i for i, label in enumerate(y_tr) if label == c_label]
                    needed = min_samples_threshold - count
                    sampled = rng.choice(c_indices, size=needed, replace=True)
                    for s_i in sampled:
                        extra_texts.append(tr_texts[s_i])
                        extra_y.append(y_tr[s_i])
            if extra_texts:
                tr_texts = tr_texts + extra_texts
                y_tr = np.concatenate([y_tr, np.array(extra_y)])

        # Feature extraction in-fold
        X_tr, X_val = feature_builder(tr_texts, val_texts)

        # Model fit & evaluate
        model = model_factory()
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_val)

        macro_f1s.append(f1_score(y_val, y_pred, average="macro", zero_division=0))
        accuracies.append(accuracy_score(y_val, y_pred))
        weighted_f1s.append(f1_score(y_val, y_pred, average="weighted", zero_division=0))

    return {
        "cv_macro_f1": round(float(np.mean(macro_f1s)), 4),
        "cv_accuracy": round(float(np.mean(accuracies)), 4),
        "cv_weighted_f1": round(float(np.mean(weighted_f1s)), 4),
        "macro_f1_std": round(float(np.std(macro_f1s)), 4),
    }


def log_experiment(csv_path: Path, round_id: str, hypothesis_and_change: str, metrics: dict, notes: str):
    file_exists = csv_path.is_file()
    row = {
        "round_id": round_id,
        "hypothesis_and_change": hypothesis_and_change,
        "cv_macro_f1": metrics["cv_macro_f1"],
        "cv_accuracy": metrics["cv_accuracy"],
        "cv_weighted_f1": metrics["cv_weighted_f1"],
        "macro_f1_std": metrics["macro_f1_std"],
        "notes": notes,
        "logged_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }
    df_row = pd.DataFrame([row])
    df_row.to_csv(csv_path, mode="a", index=False, header=not file_exists)
    print(f"[{round_id}] {hypothesis_and_change}")
    print(f"      CV Macro F1: {metrics['cv_macro_f1']:.4f} (±{metrics['macro_f1_std']:.4f}) | CV Acc: {metrics['cv_accuracy']:.4f} | {notes}\n")


def run_all_experiments():
    exp_csv = RESULTS_DIR / "experiments.csv"
    if exp_csv.is_file():
        # Keep backup before re-running
        exp_csv.rename(RESULTS_DIR / "experiments_backup.csv")

    data_path = BASE_DIR / "data" / "clauseiq_dataset_clean.csv"
    df = pd.read_csv(data_path)

    # Encode labels
    le = LabelEncoder()
    df["category_encoded"] = le.fit_transform(df["category"])

    # Split into Train (80%) and Test (20%) strictly by contract_id
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_idx, test_idx = next(gss.split(df, groups=df["contract_id"]))
    df_train = df.iloc[train_idx].copy().reset_index(drop=True)
    df_test = df.iloc[test_idx].copy().reset_index(drop=True)

    print(f"Dataset split strictly by contract_id:")
    print(f"  Training clauses: {len(df_train)} (408 contracts)")
    print(f"  Held-out test clauses: {len(df_test)} (102 contracts - LOCKED)")

    folds = get_cv_folds(df_train, n_splits=5, random_state=42)

    # Default baseline feature builder
    def make_baseline_features(max_features=10000, ngram_range=(1, 2)):
        def builder(tr_texts, val_texts):
            vec = TfidfVectorizer(
                max_features=max_features,
                ngram_range=ngram_range,
                min_df=2,
                max_df=0.95,
                sublinear_tf=True,
            )
            return vec.fit_transform(tr_texts), vec.transform(val_texts)
        return builder

    # --- ROUND 0: Baseline ---
    m0 = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=None,
        feature_builder=make_baseline_features(10000, (1, 2)),
        model_factory=lambda: LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    )
    log_experiment(exp_csv, "EXP-00", "Baseline: regex clean_text + word TF-IDF 10k (1,2) + LogReg balanced", m0, "Reference baseline on 5-fold grouped CV")

    # --- SERIES 1: Text variants (ablations) ---
    # EXP-01A: No cleaning (raw text lowercased only)
    m1a = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=lambda t: t.lower().strip(),
        feature_builder=make_baseline_features(10000, (1, 2)),
        model_factory=lambda: LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    )
    log_experiment(exp_csv, "EXP-01A", "Text Ablation: Raw text lowercased without regex cleaning", m1a, "Checks if regex cleaning helps or hurts")

    # EXP-01B: Preserve section numbers and legal symbols
    m1b = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=clean_text_preserve_sections,
        feature_builder=make_baseline_features(10000, (1, 2)),
        model_factory=lambda: LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    )
    log_experiment(exp_csv, "EXP-01B", "Text Ablation: Preserve section numbers (§, #, /, -) and clauses", m1b, "Tests if keeping numbering tokens aids legal boundary distinction")

    # EXP-01C: NLTK Stopword filtering (with legal protections)
    m1c = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=clean_text_stopwords,
        feature_builder=make_baseline_features(10000, (1, 2)),
        model_factory=lambda: LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    )
    log_experiment(exp_csv, "EXP-01C", "Text Ablation: NLTK stopwords removed (preserving shall, may, not, unless)", m1c, "Checks if standard stopword removal aids legal classification")

    # EXP-01D: NLTK WordNet Lemmatization
    m1d = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=clean_text_lemmatized,
        feature_builder=make_baseline_features(10000, (1, 2)),
        model_factory=lambda: LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    )
    log_experiment(exp_csv, "EXP-01D", "Text Ablation: NLTK WordNet Lemmatization", m1d, "Checks if lemmatizing inflected forms improves generalization")

    # Determine best text cleaner so far
    cleaner_scores = [("default", m0["cv_macro_f1"]), ("raw", m1a["cv_macro_f1"]), ("preserve_sections", m1b["cv_macro_f1"]), ("stopwords", m1c["cv_macro_f1"]), ("lemmatized", m1d["cv_macro_f1"])]
    cleaner_scores.sort(key=lambda x: x[1], reverse=True)
    best_cleaner_name = cleaner_scores[0][0]
    print(f"--> Best text representation from Series 1: '{best_cleaner_name}' with Macro F1 {cleaner_scores[0][1]}")

    chosen_preprocessor = None
    if best_cleaner_name == "preserve_sections":
        chosen_preprocessor = clean_text_preserve_sections
    elif best_cleaner_name == "raw":
        chosen_preprocessor = lambda t: t.lower().strip()
    elif best_cleaner_name == "stopwords":
        chosen_preprocessor = clean_text_stopwords
    elif best_cleaner_name == "lemmatized":
        chosen_preprocessor = clean_text_lemmatized

    # --- SERIES 2: Features (Vocabulary, n-grams, character n-grams) ---
    # EXP-02A: Vocabulary 25k (1, 2)
    m2a = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=chosen_preprocessor,
        feature_builder=make_baseline_features(25000, (1, 2)),
        model_factory=lambda: LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    )
    log_experiment(exp_csv, "EXP-02A", "Features: Vocab size expanded to 25,000 unigrams+bigrams", m2a, "Tests if larger legal vocabulary captures specific terminology")

    # EXP-02B: Vocabulary 50k (1, 2)
    m2b = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=chosen_preprocessor,
        feature_builder=make_baseline_features(50000, (1, 2)),
        model_factory=lambda: LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    )
    log_experiment(exp_csv, "EXP-02B", "Features: Vocab size expanded to 50,000 unigrams+bigrams", m2b, "Tests if 50k vocabulary improves rare clause recognition")

    # EXP-02C: N-gram range (1, 3) unigram, bigram, trigram
    def make_trigram_features(max_features=35000):
        def builder(tr_texts, val_texts):
            vec = TfidfVectorizer(
                max_features=max_features,
                ngram_range=(1, 3),
                min_df=2,
                max_df=0.95,
                sublinear_tf=True,
            )
            return vec.fit_transform(tr_texts), vec.transform(val_texts)
        return builder

    m2c = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=chosen_preprocessor,
        feature_builder=make_trigram_features(35000),
        model_factory=lambda: LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    )
    log_experiment(exp_csv, "EXP-02C", "Features: Trigram extension (1, 3) with 35,000 features", m2c, "Tests multi-word legal boilerplate matching (e.g. 'governed by laws of')")

    # EXP-02D: Word TF-IDF + Character n-grams (char_wb 3-5) via hstack
    def make_word_char_features(word_max=25000, char_max=15000):
        def builder(tr_texts, val_texts):
            vec_word = TfidfVectorizer(
                max_features=word_max,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
                sublinear_tf=True,
            )
            vec_char = TfidfVectorizer(
                max_features=char_max,
                analyzer="char_wb",
                ngram_range=(3, 5),
                min_df=3,
                sublinear_tf=True,
            )
            X_tr_w = vec_word.fit_transform(tr_texts)
            X_val_w = vec_word.transform(val_texts)
            X_tr_c = vec_char.fit_transform(tr_texts)
            X_val_c = vec_char.transform(val_texts)
            return hstack([X_tr_w, X_tr_c]).tocsr(), hstack([X_val_w, X_val_c]).tocsr()
        return builder

    m2d = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=chosen_preprocessor,
        feature_builder=make_word_char_features(25000, 15000),
        model_factory=lambda: LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    )
    log_experiment(exp_csv, "EXP-02D", "Features: Hybrid Word TF-IDF (25k) + Char_wb (3-5, 15k)", m2d, "Tests character n-gram robustness on subwords, prefixes, and punctuation patterns")

    # Determine best feature set
    feature_scores = [("10k_word", m0["cv_macro_f1"]), ("25k_word", m2a["cv_macro_f1"]), ("50k_word", m2b["cv_macro_f1"]), ("trigram_35k", m2c["cv_macro_f1"]), ("hybrid_word_char", m2d["cv_macro_f1"])]
    feature_scores.sort(key=lambda x: x[1], reverse=True)
    best_feat_name = feature_scores[0][0]
    print(f"--> Best feature set from Series 2: '{best_feat_name}' with Macro F1 {feature_scores[0][1]}")

    if best_feat_name == "hybrid_word_char":
        chosen_feature_builder = make_word_char_features(25000, 15000)
    elif best_feat_name == "trigram_35k":
        chosen_feature_builder = make_trigram_features(35000)
    elif best_feat_name == "50k_word":
        chosen_feature_builder = make_baseline_features(50000, (1, 2))
    elif best_feat_name == "25k_word":
        chosen_feature_builder = make_baseline_features(25000, (1, 2))
    else:
        chosen_feature_builder = make_baseline_features(10000, (1, 2))

    # --- SERIES 3: Classical ML Models Comparison & Tuning ---
    # EXP-03A: LinearSVC (C=0.1)
    m3a = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=chosen_preprocessor,
        feature_builder=chosen_feature_builder,
        model_factory=lambda: LinearSVC(C=0.1, class_weight="balanced", random_state=42),
    )
    log_experiment(exp_csv, "EXP-03A", f"Model: LinearSVC (C=0.1, balanced) with {best_feat_name}", m3a, "Evaluates margin-based linear separation on improved features")

    # EXP-03B: LinearSVC (C=0.5)
    m3b = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=chosen_preprocessor,
        feature_builder=chosen_feature_builder,
        model_factory=lambda: LinearSVC(C=0.5, class_weight="balanced", random_state=42),
    )
    log_experiment(exp_csv, "EXP-03B", f"Model: LinearSVC (C=0.5, balanced) with {best_feat_name}", m3b, "Tests higher margin penalty for tighter boundaries")

    # EXP-03C: Logistic Regression (C=2.0)
    m3c = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=chosen_preprocessor,
        feature_builder=chosen_feature_builder,
        model_factory=lambda: LogisticRegression(C=2.0, max_iter=2000, class_weight="balanced", random_state=42),
    )
    log_experiment(exp_csv, "EXP-03C", f"Model: LogisticRegression (C=2.0, balanced) with {best_feat_name}", m3c, "Tests lower L2 penalty to let strong weights activate")

    # EXP-03D: Logistic Regression (C=5.0)
    m3d = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=chosen_preprocessor,
        feature_builder=chosen_feature_builder,
        model_factory=lambda: LogisticRegression(C=5.0, max_iter=2000, class_weight="balanced", random_state=42),
    )
    log_experiment(exp_csv, "EXP-03D", f"Model: LogisticRegression (C=5.0, balanced) with {best_feat_name}", m3d, "Tests C=5.0 for high fidelity on sparse legal vocabulary")

    # EXP-03E: ComplementNB (specifically for imbalanced text)
    m3e = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=chosen_preprocessor,
        feature_builder=chosen_feature_builder,
        model_factory=lambda: ComplementNB(alpha=0.1),
    )
    log_experiment(exp_csv, "EXP-03E", f"Model: ComplementNB (alpha=0.1) with {best_feat_name}", m3e, "Naive Bayes variant designed specifically for imbalanced class distributions")

    # EXP-03F: SGDClassifier with modified_huber loss (produces probabilities and fast linear margins)
    m3f = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=chosen_preprocessor,
        feature_builder=chosen_feature_builder,
        model_factory=lambda: SGDClassifier(loss="modified_huber", alpha=1e-4, penalty="l2", class_weight="balanced", random_state=42),
    )
    log_experiment(exp_csv, "EXP-03F", f"Model: SGDClassifier (modified_huber, alpha=1e-4, balanced) with {best_feat_name}", m3f, "Smooth hinge loss that outputs calibrated margin probabilities")

    # EXP-03G: Classical Soft Ensemble (Voting of Tuned LogReg + Calibrated LinearSVC + SGD)
    def make_ensemble():
        clf1 = LogisticRegression(C=2.0, max_iter=2000, class_weight="balanced", random_state=42)
        clf2 = CalibratedClassifierCV(LinearSVC(C=0.2, class_weight="balanced", random_state=42), cv=3)
        clf3 = SGDClassifier(loss="modified_huber", alpha=1e-4, penalty="l2", class_weight="balanced", random_state=42)
        return VotingClassifier(estimators=[("lr", clf1), ("svc", clf2), ("sgd", clf3)], voting="soft")

    m3g = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=chosen_preprocessor,
        feature_builder=chosen_feature_builder,
        model_factory=make_ensemble,
    )
    log_experiment(exp_csv, "EXP-03G", f"Model: Soft Voting Ensemble (LogReg C=2 + Calibrated SVC + SGD)", m3g, "Combines diverse linear models using soft probability averaging")

    # --- SERIES 4: Class Imbalance Treatments ---
    # EXP-04A: Random Oversampling of rare classes (<30 samples) in training folds
    m4a = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=chosen_preprocessor,
        feature_builder=chosen_feature_builder,
        model_factory=lambda: LogisticRegression(C=2.0, max_iter=2000, class_weight="balanced", random_state=42),
        oversample_minority=True,
        min_samples_threshold=30,
    )
    log_experiment(exp_csv, "EXP-04A", "Imbalance: In-fold random oversampling of classes < 30 samples", m4a, "Assesses if synthesizing rare-class instances within training folds boosts macro recall")

    # EXP-04B: No class weights (unweighted baseline on same features)
    m4b = evaluate_cv(
        df_train,
        folds,
        text_preprocessor=chosen_preprocessor,
        feature_builder=chosen_feature_builder,
        model_factory=lambda: LogisticRegression(C=2.0, max_iter=2000, class_weight=None, random_state=42),
    )
    log_experiment(exp_csv, "EXP-04B", "Imbalance: Unweighted Logistic Regression (class_weight=None)", m4b, "Ablation verifying that class_weight='balanced' is necessary for macro F1")

    # --- SERIES 5: Calibration & Threshold Optimization on Validation Data ---
    # Compare raw probabilities vs Sigmoid vs Isotonic CalibratedClassifierCV on training data
    print("Evaluating probability calibration methods...")
    cal_res = {}
    for cal_method in ["sigmoid", "isotonic"]:
        def make_calibrated():
            base = LogisticRegression(C=2.0, max_iter=2000, class_weight="balanced", random_state=42)
            return CalibratedClassifierCV(base, method=cal_method, cv=3)

        m_cal = evaluate_cv(
            df_train,
            folds,
            text_preprocessor=chosen_preprocessor,
            feature_builder=chosen_feature_builder,
            model_factory=make_calibrated,
        )
        log_experiment(exp_csv, f"EXP-05-{cal_method[:3].upper()}", f"Calibration: CalibratedClassifierCV ({cal_method}) on LogReg C=2.0", m_cal, f"Tests post-hoc probability calibration ({cal_method}) across validation folds")
        cal_res[cal_method] = m_cal

    print("Experiment suite complete. All rounds recorded in results/experiments.csv.")


if __name__ == "__main__":
    run_all_experiments()
