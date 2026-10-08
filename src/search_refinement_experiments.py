from pathlib import Path
import sys
import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure src/ is in sys.path
src_dir = str(Path(__file__).resolve().parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from text_cleaner import clean_text
from evaluate_search import QUERY_MAPPING


def run_search_refinement_experiments(
    data_path: Path | str = BASE_DIR / "data" / "clauseiq_dataset_clean.csv",
    results_dir: Path | str = BASE_DIR / "results",
):
    data_path = Path(data_path)
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading corpus from {data_path}...")
    df = pd.read_csv(data_path)
    texts = df["clean_text"].fillna("").astype(str).tolist()

    # Total relevant counts for each query
    total_relevant_counts = {
        q: int(df["category"].isin(cats).sum())
        for q, cats in QUERY_MAPPING.items()
    }

    # Define experimental configurations
    configs = {
        "Baseline (Unigram+Bigram, Sublinear TF=True)": {
            "ngram_range": (1, 2),
            "sublinear_tf": True,
            "stop_words": None,
            "min_score": 0.0,
        },
        "Exp 1: Unigram Only (ngram_range=(1,1))": {
            "ngram_range": (1, 1),
            "sublinear_tf": True,
            "stop_words": None,
            "min_score": 0.0,
        },
        "Exp 2: Linear TF (sublinear_tf=False)": {
            "ngram_range": (1, 2),
            "sublinear_tf": False,
            "stop_words": None,
            "min_score": 0.0,
        },
        "Exp 3: Standard English Stopwords Stripped": {
            "ngram_range": (1, 2),
            "sublinear_tf": True,
            "stop_words": "english",
            "min_score": 0.0,
        },
        "Exp 4: Score Threshold Filtering (min_score=0.20)": {
            "ngram_range": (1, 2),
            "sublinear_tf": True,
            "stop_words": None,
            "min_score": 0.20,
        },
    }

    print("=" * 85)
    print("TASK 9: SYSTEMATIC SEARCH REFINEMENT EXPERIMENTS")
    print("=" * 85)

    summary_rows = []
    detailed_results = {}

    for exp_name, params in configs.items():
        print(f"\nEvaluating Configuration: {exp_name}...")
        # Fit vectorizer on corpus for this experiment
        vec = TfidfVectorizer(
            max_features=10000,
            ngram_range=params["ngram_range"],
            sublinear_tf=params["sublinear_tf"],
            stop_words=params["stop_words"],
            min_df=2,
            max_df=0.95,
        )
        corpus_mat = vec.fit_transform(texts)
        min_score = params["min_score"]

        exp_query_metrics = []

        for query, target_cats in QUERY_MAPPING.items():
            tot_rel = total_relevant_counts[query]
            cleaned_q = clean_text(query)
            q_vec = vec.transform([cleaned_q])

            if q_vec.nnz == 0:
                prec_1 = prec_3 = prec_5 = prec_10 = 0.0
                rec_1 = rec_3 = rec_5 = rec_10 = 0.0
            else:
                sims = cosine_similarity(q_vec, corpus_mat).flatten()
                # Apply score threshold
                valid_mask = sims >= min_score
                valid_indices = np.where(valid_mask)[0]
                valid_scores = sims[valid_indices]

                # Sort top 10
                if len(valid_scores) > 10:
                    top_part = np.argpartition(-valid_scores, 10)[:10]
                    sort_idx = top_part[np.argsort(-valid_scores[top_part])]
                else:
                    sort_idx = np.argsort(-valid_scores)

                top_indices = valid_indices[sort_idx] if len(valid_indices) > 0 else []

                def get_metrics_at_k(k):
                    if len(top_indices) == 0:
                        return 0.0, 0.0
                    sub = top_indices[:k]
                    # Count hits
                    hits = sum(1 for idx in sub if df.iloc[idx]["category"] in target_cats)
                    p = hits / k
                    r = hits / tot_rel if tot_rel > 0 else 0.0
                    return p, r

                prec_1, rec_1 = get_metrics_at_k(1)
                prec_3, rec_3 = get_metrics_at_k(3)
                prec_5, rec_5 = get_metrics_at_k(5)
                prec_10, rec_10 = get_metrics_at_k(10)

            exp_query_metrics.append({
                "query": query,
                "p@1": prec_1, "r@1": rec_1,
                "p@3": prec_3, "r@3": rec_3,
                "p@5": prec_5, "r@5": rec_5,
                "p@10": prec_10, "r@10": rec_10,
            })

        detailed_results[exp_name] = exp_query_metrics

        # Calculate macro averages
        mean_p1 = np.mean([m["p@1"] for m in exp_query_metrics])
        mean_p3 = np.mean([m["p@3"] for m in exp_query_metrics])
        mean_p5 = np.mean([m["p@5"] for m in exp_query_metrics])
        mean_p10 = np.mean([m["p@10"] for m in exp_query_metrics])
        mean_r5 = np.mean([m["r@5"] for m in exp_query_metrics])
        mean_r10 = np.mean([m["r@10"] for m in exp_query_metrics])

        summary_rows.append({
            "Experiment": exp_name,
            "Mean P@1": round(float(mean_p1), 4),
            "Mean P@3": round(float(mean_p3), 4),
            "Mean P@5": round(float(mean_p5), 4),
            "Mean P@10": round(float(mean_p10), 4),
            "Mean R@5": round(float(mean_r5), 4),
            "Mean R@10": round(float(mean_r10), 4),
        })

    summary_df = pd.DataFrame(summary_rows)
    print("\n" + "=" * 90)
    print("SEARCH REFINEMENT EXPERIMENTS COMPARISON")
    print("=" * 90)
    print(summary_df.to_string(index=False))
    print("=" * 90)

    # Save to CSV and JSON
    csv_path = results_dir / "search_refinement_experiments.csv"
    json_path = results_dir / "search_refinement_experiments.json"

    summary_df.to_csv(csv_path, index=False)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": summary_rows,
            "detailed": detailed_results,
        }, f, indent=4)

    print(f"\nSaved refinement artifacts to:\n  - {csv_path}\n  - {json_path}")
    return summary_df


if __name__ == "__main__":
    run_search_refinement_experiments()
