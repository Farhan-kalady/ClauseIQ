from pathlib import Path
import sys
import json
import pandas as pd
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure src/ is in sys.path
src_dir = str(Path(__file__).resolve().parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from search import get_search_engine

# ==============================================================================
# DOCUMENTED QUERY-TO-CATEGORY RELEVANCE MAPPING
# ==============================================================================
# Each query is mapped strictly to official CUAD category names present in data/clauseiq_dataset_clean.csv.
# An item is relevant if and only if its dataset true_category is in the mapped list.
QUERY_MAPPING: Dict[str, List[str]] = {
    "termination for convenience": ["Termination For Convenience"],
    "governing law": ["Governing Law"],
    "non-compete": ["Non-Compete"],
    "limitation of liability": ["Cap On Liability", "Uncapped Liability"],
    "audit rights": ["Audit Rights"],
}


def evaluate_search_retrieval(
    results_dir: Path | str = BASE_DIR / "results",
    k_values: List[int] = [1, 3, 5, 10],
):
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    engine = get_search_engine()
    corpus_df = engine.df

    print("=" * 80)
    print("TASK 8: SEARCH RETRIEVAL EVALUATION (Precision@k & Recall@k)")
    print("=" * 80)

    # 1. Calculate total relevant corpus items for each query
    total_relevant_counts = {}
    for query, target_cats in QUERY_MAPPING.items():
        count = corpus_df["category"].isin(target_cats).sum()
        total_relevant_counts[query] = int(count)
        print(f"Query: '{query}' -> Target Categories: {target_cats} (Total in Corpus: {count})")

    print("-" * 80)

    eval_records = []

    for query, target_cats in QUERY_MAPPING.items():
        total_relevant_in_corpus = total_relevant_counts[query]
        # Retrieve maximum required k
        max_k = max(k_values)
        results = engine.search(query, top_k=max_k)

        query_row = {
            "Query": query,
            "Target Categories": ", ".join(target_cats),
            "Corpus Relevant Count": total_relevant_in_corpus,
        }

        for k in k_values:
            top_k_res = results[:k]
            # Check how many retrieved items have true_category in target_cats
            rel_count = sum(1 for r in top_k_res if r.get("true_category") in target_cats)
            prec_k = rel_count / k if k > 0 else 0.0
            rec_k = rel_count / total_relevant_in_corpus if total_relevant_in_corpus > 0 else 0.0

            query_row[f"P@{k}"] = round(prec_k, 4)
            query_row[f"R@{k}"] = round(rec_k, 4)
            query_row[f"Hits@{k}"] = rel_count

        eval_records.append(query_row)

    eval_df = pd.DataFrame(eval_records)

    # Display clean table
    display_cols = ["Query", "Corpus Relevant Count", "P@1", "R@1", "P@3", "R@3", "P@5", "R@5", "P@10", "R@10"]
    print("\n" + "=" * 80)
    print("SEARCH RETRIEVAL PERFORMANCE METRICS")
    print("=" * 80)
    print(eval_df[display_cols].to_string(index=False))
    print("=" * 80)

    # Compute Macro Average across queries
    macro_avg = {"Query": "MEAN / MACRO AVERAGE", "Corpus Relevant Count": "-"}
    for k in k_values:
        macro_avg[f"P@{k}"] = round(eval_df[f"P@{k}"].mean(), 4)
        macro_avg[f"R@{k}"] = round(eval_df[f"R@{k}"].mean(), 4)

    print("\nMACRO AVERAGES ACROSS ALL TEST QUERIES:")
    for k in k_values:
        print(f"  Mean Precision@{k}: {macro_avg[f'P@{k}']:.4f} ({macro_avg[f'P@{k}']*100:.1f}%) | Mean Recall@{k}: {macro_avg[f'R@{k}']:.4f} ({macro_avg[f'R@{k}']*100:.2f}%)")

    # Save to CSV and JSON
    csv_path = results_dir / "search_evaluation.csv"
    json_path = results_dir / "search_evaluation.json"

    eval_df.to_csv(csv_path, index=False)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(eval_records, f, indent=4)

    print(f"\nSaved search evaluation artifacts to:\n  - {csv_path}\n  - {json_path}")
    return eval_df


if __name__ == "__main__":
    evaluate_search_retrieval()
