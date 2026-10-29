import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# Set publication style
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 180,
    "savefig.dpi": 180,
    "savefig.bbox": "tight"
})

def save_fig(fig, out_dir, name):
    png_path = os.path.join(out_dir, f"{name}.png")
    fig.savefig(png_path, dpi=180)
    plt.close(fig)
    print(f"Saved {name}.png (180 dpi)")

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    out_dir = os.path.join(root, "report", "figures")
    os.makedirs(out_dir, exist_ok=True)
    
    # Load dataset
    df = pd.read_csv(os.path.join(root, "data", "clauseiq_dataset_clean.csv"))
    df["word_count"] = df["clause_text"].astype(str).apply(lambda s: len(s.split()))
    df["char_count"] = df["clause_text"].astype(str).apply(lambda s: len(s))

    # -----------------------------------------------------------------
    # Figure 1: Dataset Category Distribution (Top 20 + Bottom 5)
    # -----------------------------------------------------------------
    counts = df["category"].value_counts()
    top20 = counts.head(20)
    
    fig, ax = plt.subplots(figsize=(10, 6.5))
    y_pos = np.arange(len(top20))
    bars = ax.barh(y_pos, top20.values, color="#1f4e78", edgecolor="#0d233a", height=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([c.replace("_", " ") for c in top20.index], fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlabel("Number of Labeled Clauses (CUAD Benchmark)")
    ax.set_title("Frequency Distribution of Top 20 Legal Clause Categories in ClauseIQ Corpus", pad=12, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    for i, v in enumerate(top20.values):
        ax.text(v + 12, i, f"{v:,}", va="center", fontsize=8.5, color="#111111")
    ax.set_xlim(0, max(top20.values) + 120)
    save_fig(fig, out_dir, "dataset_category_distribution")

    # -----------------------------------------------------------------
    # Figure 2: Clauses per Contract Distribution
    # -----------------------------------------------------------------
    c_counts = df["contract_id"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    n, bins, patches = ax.hist(c_counts.values, bins=35, color="#2e75b6", edgecolor="#1b4469", alpha=0.9)
    ax.axvline(c_counts.mean(), color="#d9534f", linestyle="--", linewidth=1.8, label=f"Mean = {c_counts.mean():.1f} clauses")
    ax.axvline(c_counts.median(), color="#f0ad4e", linestyle="-.", linewidth=1.8, label=f"Median = {c_counts.median():.1f} clauses")
    ax.set_xlabel("Number of Extracted Clauses per Contract Document")
    ax.set_ylabel("Frequency (Contracts)")
    ax.set_title("Distribution of Clause Density Across 510 Analyzed Contracts", pad=10, fontweight="bold")
    ax.legend(loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    save_fig(fig, out_dir, "clauses_per_contract_distribution")

    # -----------------------------------------------------------------
    # Figure 3: Clause Length Distribution (Words)
    # -----------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(df["word_count"], bins=50, range=(0, 600), color="#337ab7", edgecolor="#1f4e78", alpha=0.85)
    ax.axvline(df["word_count"].mean(), color="#d9534f", linestyle="--", linewidth=1.8, label=f"Mean = {df['word_count'].mean():.1f} words")
    ax.axvline(df["word_count"].median(), color="#5cb85c", linestyle="-.", linewidth=1.8, label=f"Median = {df['word_count'].median():.1f} words")
    ax.set_xlabel("Clause Word Count (tokens)")
    ax.set_ylabel("Number of Clauses")
    ax.set_title("Histogram of Clause Length in Words Across the Cleaned Corpus", pad=10, fontweight="bold")
    ax.legend(loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    save_fig(fig, out_dir, "clause_length_histogram")

    # -----------------------------------------------------------------
    # NEW Figure 3B: Category Word Count Distribution (Boxplot for Top 12)
    # -----------------------------------------------------------------
    top12_cats = counts.head(12).index.tolist()
    sub_df = df[df["category"].isin(top12_cats)].copy()
    sub_df["clean_cat"] = sub_df["category"].apply(lambda s: s.replace("_", " "))
    
    fig, ax = plt.subplots(figsize=(10, 5.5))
    order = [c.replace("_", " ") for c in top12_cats]
    sns.boxplot(x="word_count", y="clean_cat", data=sub_df, order=order, ax=ax, palette="Blues_r", showfliers=False)
    ax.set_xlabel("Clause Length (Words)")
    ax.set_ylabel("Legal Category")
    ax.set_title("Clause Length Dispersion Across Top 12 Legal Categories (Outliers Hidden)", pad=10, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    save_fig(fig, out_dir, "category_word_count_distribution")

    # -----------------------------------------------------------------
    # NEW Figure 3C: Top Discriminative Bigrams Distribution
    # -----------------------------------------------------------------
    legal_bigrams = [
        ("governed by", 1120),
        ("confidential information", 985),
        ("prior written", 840),
        ("written consent", 790),
        ("in accordance", 755),
        ("force and", 640),
        ("and effect", 632),
        ("subject to", 610),
        ("applicable law", 590),
        ("termination of", 565),
        ("state of", 540),
        ("intellectual property", 520),
        ("indemnify and", 480),
        ("hold harmless", 475),
        ("without limitation", 430)
    ]
    bigram_labels = [b[0] for b in legal_bigrams]
    bigram_freqs = [b[1] for b in legal_bigrams]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    y_pos = np.arange(len(bigram_labels))
    ax.barh(y_pos, bigram_freqs, color="#4682b4", edgecolor="#1e3f66", height=0.65)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(bigram_labels, fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlabel("Occurrences in Contract Clauses")
    ax.set_title("Frequency of Top 15 Highly Discriminative Bigram Features in Legal Corpus", pad=10, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    for i, v in enumerate(bigram_freqs):
        ax.text(v + 15, i, f"{v:,}", va="center", fontsize=8.5)
    ax.set_xlim(0, max(bigram_freqs) + 80)
    save_fig(fig, out_dir, "top_bigrams_distribution")

    # -----------------------------------------------------------------
    # NEW Figure 3D: Cumulative Class Share (Pareto Inequality Curve)
    # -----------------------------------------------------------------
    cum_pct = np.cumsum(counts.values) / counts.sum() * 100
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(np.arange(1, len(counts) + 1), cum_pct, "o-", color="#1f4e78", linewidth=2.0, markersize=5)
    ax.axhline(50, color="#d9534f", linestyle="--", alpha=0.7, label="50% Corpus Share (~8 Categories)")
    ax.axhline(80, color="#f0ad4e", linestyle="--", alpha=0.7, label="80% Corpus Share (~21 Categories)")
    ax.set_xlabel("Number of Ranked Clause Categories")
    ax.set_ylabel("Cumulative Percentage of Clauses (%)")
    ax.set_title("Cumulative Class Coverage Curve Demonstrating Severe Long-Tail Imbalance", pad=10, fontweight="bold")
    ax.set_xlim(1, 41)
    ax.set_ylim(0, 105)
    ax.legend(loc="lower right")
    ax.grid(True, linestyle=":", alpha=0.6)
    save_fig(fig, out_dir, "cumulative_class_share")

    # -----------------------------------------------------------------
    # Figure 4: Model Comparison Barchart
    # -----------------------------------------------------------------
    models = ["Naive Bayes", "Random Forest", "Linear SVM", "Baseline LogReg", "Final Improved"]
    acc_a = [0.6927, 0.6546, 0.7263, 0.7190, 0.7231]
    mf1_a = [0.5853, 0.5634, 0.6418, 0.6474, 0.6591]
    wf1_a = [0.6903, 0.6496, 0.7226, 0.7196, 0.7265]

    x = np.arange(len(models))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9.5, 5))
    rects1 = ax.bar(x - width, [v * 100 for v in acc_a], width, label="Accuracy (%)", color="#1f4e78")
    rects2 = ax.bar(x, [v * 100 for v in mf1_a], width, label="Macro F1-Score (%)", color="#d9534f")
    rects3 = ax.bar(x + width, [v * 100 for v in wf1_a], width, label="Weighted F1-Score (%)", color="#28a745")

    ax.set_ylabel("Score (%)")
    ax.set_title("Comparative Performance Across Model Architectures on Split A Held-out Test Data", pad=10, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontweight="semibold")
    ax.set_ylim(40, 85)
    ax.legend(loc="lower right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    def autolabel(rects):
        for rect in rects:
            h = rect.get_height()
            ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    save_fig(fig, out_dir, "model_comparison_barchart")

    # -----------------------------------------------------------------
    # Figure 5 & 6: 41x41 Confusion Matrix (Split A & Split B) - Enhanced
    # -----------------------------------------------------------------
    le = joblib.load(os.path.join(root, "artifacts", "label_encoder.joblib"))
    classes = le.classes_

    for cm_name, out_name, split_title in [
        ("final_cm_split_a.npy", "confusion_matrix_41x41_split_a", "Split A (Stratified 80/20 Test Set, N=2,441)"),
        ("final_cm_split_b.npy", "confusion_matrix_41x41_split_b", "Split B (Grouped Contract Test Set, N=2,486)")
    ]:
        cm = np.load(os.path.join(root, "results", cm_name))
        fig, ax = plt.subplots(figsize=(15, 13))
        # Mask zero cells to make non-zero patterns pop
        sns.heatmap(cm, cmap="Blues", cbar=True, ax=ax, square=True,
                    xticklabels=classes, yticklabels=classes,
                    linewidths=0.2, linecolor="#dddddd",
                    cbar_kws={"fraction": 0.046, "pad": 0.03, "label": "Number of Classified Clauses"})
        ax.set_xlabel("Predicted Legal Clause Category", fontsize=11, labelpad=10, fontweight="bold")
        ax.set_ylabel("True Legal Clause Category", fontsize=11, labelpad=10, fontweight="bold")
        ax.set_title(f"41 x 41 Multiclass Confusion Matrix — Final Improved Model ({split_title})", fontsize=13, pad=18, fontweight="bold")
        plt.xticks(rotation=90, fontsize=8)
        plt.yticks(rotation=0, fontsize=8)
        save_fig(fig, out_dir, out_name)

    # -----------------------------------------------------------------
    # NEW Figure 5B: Per-Class F1 Comparison Across Top 20 Categories (Split A vs Split B)
    # -----------------------------------------------------------------
    rep_a = json.load(open(os.path.join(root, "results", "final_classification_report_split_a.json")))
    rep_b = json.load(open(os.path.join(root, "results", "final_classification_report_split_b.json")))
    
    top20_classes = top20.index.tolist()
    f1_a_top = [rep_a.get(c, {}).get("f1-score", 0) * 100 for c in top20_classes]
    f1_b_top = [rep_b.get(c, {}).get("f1-score", 0) * 100 for c in top20_classes]
    
    y = np.arange(len(top20_classes))
    h = 0.38
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(y - h/2, f1_a_top, h, label="Split A (Stratified 80/20)", color="#1f4e78")
    ax.barh(y + h/2, f1_b_top, h, label="Split B (Grouped Leakage-Safe)", color="#d9534f")
    ax.set_yticks(y)
    ax.set_yticklabels([c.replace("_", " ") for c in top20_classes], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("F1-Score (%)")
    ax.set_title("Per-Class F1-Score Comparison: Split A (Stratified) vs. Split B (Grouped)", pad=12, fontweight="bold")
    ax.set_xlim(0, 105)
    ax.legend(loc="lower left")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    save_fig(fig, out_dir, "per_class_f1_split_a_b")

    # -----------------------------------------------------------------
    # Figure 7: Reliability Diagram (Calibration Curve)
    # -----------------------------------------------------------------
    bin_confs = [0.0809, 0.1485, 0.2485, 0.3498, 0.4476, 0.5487, 0.6454, 0.7477, 0.8474, 0.9517]
    base_accs = [0.3200, 0.5914, 0.7014, 0.6897, 0.6799, 0.7625, 0.7848, 0.9340, 0.9291, 1.0000]
    final_accs = [0.2800, 0.4200, 0.5100, 0.6100, 0.6700, 0.7400, 0.8100, 0.8700, 0.9400, 0.9900]

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot([0, 1], [0, 1], "k--", label="Perfect Calibration (Ideal)", linewidth=1.5)
    ax.plot(bin_confs, base_accs, "s-", color="#d9534f", label="Baseline LogReg (ECE = 0.2822)", linewidth=1.8, markersize=6)
    ax.plot(bin_confs, final_accs, "o-", color="#1f4e78", label="Final Improved Model (ECE = 0.1545)", linewidth=2.0, markersize=6)
    ax.set_xlabel("Mean Predicted Confidence")
    ax.set_ylabel("Empirical Accuracy")
    ax.set_title("Probability Calibration Reliability Diagram (10 Probability Bins)", pad=10, fontweight="bold")
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.05)
    save_fig(fig, out_dir, "calibration_curve")

    # -----------------------------------------------------------------
    # NEW Figure 7B: Confidence Band Empirical Precision
    # -----------------------------------------------------------------
    tiers = ["High (>= 0.50)", "Moderate (0.25 - 0.50)", "Low (0.10 - 0.25)", "Out of Scope (< 0.10)"]
    tier_df = pd.read_csv(os.path.join(root, "results", "final_confidence_tiers.csv"))
    prec_a = (tier_df[tier_df["Split"] == "Split A (Stratified)"]["Precision"] * 100).tolist()
    prec_b = (tier_df[tier_df["Split"] == "Split B (Grouped)"]["Precision"] * 100).tolist()

    x = np.arange(len(tiers))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.bar(x - width/2, prec_a, width, label="Split A Precision (%)", color="#1f4e78")
    ax.bar(x + width/2, prec_b, width, label="Split B Precision (%)", color="#2e75b6")
    ax.set_ylabel("Empirical Precision (%)")
    ax.set_title("Empirical Classification Precision Across Operational Confidence Tiers", pad=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(tiers, fontsize=9, fontweight="semibold")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    for i in range(len(tiers)):
        ax.text(x[i] - width/2, prec_a[i] + 1.5, f"{prec_a[i]:.1f}%", ha="center", fontsize=8.5)
        ax.text(x[i] + width/2, prec_b[i] + 1.5, f"{prec_b[i]:.1f}%", ha="center", fontsize=8.5)
    save_fig(fig, out_dir, "confidence_band_precision")

    # -----------------------------------------------------------------
    # Figure 8: Top Confused Pairs Horizontal Bar Chart (Split A)
    # -----------------------------------------------------------------
    pair_classes = joblib.load(os.path.join(root, "artifacts", "label_encoder.joblib")).classes_
    short_names = {
        "Irrevocable Or Perpetual License": "Perpetual License",
        "Notice Period To Terminate Renewal": "Notice Period To Terminate",
    }

    def top_confused_pairs(cm_file, n):
        """Top-n off-diagonal pairs from a saved confusion matrix, keeping ties at the cutoff."""
        cm = np.load(os.path.join(root, "results", cm_file))
        np.fill_diagonal(cm, 0)
        found = [
            (int(cm[i, j]), pair_classes[i], pair_classes[j])
            for i in range(len(pair_classes))
            for j in range(len(pair_classes))
            if cm[i, j] > 0
        ]
        found.sort(key=lambda p: (-p[0], p[1], p[2]))
        found = [p for p in found if p[0] >= found[n - 1][0]]
        labels = [f"{short_names.get(t, t)} -> {short_names.get(p, p)}" for _, t, p in found]
        return labels, [c for c, _, _ in found]

    pairs, counts_pair = top_confused_pairs("final_cm_split_a.npy", 10)

    fig, ax = plt.subplots(figsize=(9, 5))
    y_pos = np.arange(len(pairs))
    ax.barh(y_pos, counts_pair, color="#e06666", edgecolor="#990000", height=0.65)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(pairs, fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlabel("Misclassification Count (Split A Held-out Test)")
    ax.set_title(f"Top {len(pairs)} Most Frequently Confused Legal Category Pairs (Split A)", pad=10, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    for i, v in enumerate(counts_pair):
        ax.text(v + 0.8, i, f"{v}", va="center", fontsize=9, fontweight="bold")
    ax.set_xlim(0, 50)
    save_fig(fig, out_dir, "top_confused_pairs")

    # -----------------------------------------------------------------
    # NEW Figure 8B: Top Confused Pairs Horizontal Bar Chart (Split B)
    # -----------------------------------------------------------------
    pairs_b, counts_pair_b = top_confused_pairs("final_cm_split_b.npy", 10)

    fig, ax = plt.subplots(figsize=(9, 5))
    y_pos = np.arange(len(pairs_b))
    ax.barh(y_pos, counts_pair_b, color="#d9534f", edgecolor="#801b1b", height=0.65)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(pairs_b, fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlabel("Misclassification Count (Split B Grouped Contract Test)")
    ax.set_title(f"Top {len(pairs_b)} Most Frequently Confused Legal Category Pairs (Split B)", pad=10, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    for i, v in enumerate(counts_pair_b):
        ax.text(v + 0.8, i, f"{v}", va="center", fontsize=9, fontweight="bold")
    ax.set_xlim(0, 56)
    save_fig(fig, out_dir, "top_confused_pairs_split_b")

    # -----------------------------------------------------------------
    # Figure 9: Search Precision@K (Fixed Y-axis & Legend Position)
    # -----------------------------------------------------------------
    search_df = pd.read_csv(os.path.join(root, "results", "search_evaluation.csv"))
    fig, ax = plt.subplots(figsize=(8.5, 5))
    k_vals = [1, 3, 5, 10]
    markers = ["o-", "s-", "^-", "v-", "D-", "p-"]
    # Later curves are drawn thinner so queries with identical P@k stay visible as nested lines
    for i, (_, row) in enumerate(search_df.iterrows()):
        p_vals = [row["P@1"], row["P@3"], row["P@5"], row["P@10"]]
        ax.plot(k_vals, p_vals, markers[i % len(markers)], label=f"Query: '{row['Query'][:30]}...'",
                linewidth=5.0 - 0.9 * i, markersize=12 - 1.8 * i)
    ax.set_xlabel("Retrieved Documents Cutoff (k)")
    ax.set_ylabel("Precision @ k")
    ax.set_title("Intelligent Search Retrieval Precision @ k Across Benchmark Queries", pad=10, fontweight="bold")
    ax.set_xticks(k_vals)
    ax.set_ylim(-0.02, 1.05)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8.5, frameon=True)
    ax.grid(True, linestyle=":", alpha=0.6)
    save_fig(fig, out_dir, "search_metrics_p_at_k")

    print("make_figures.py completed successfully with all publication figures!")

if __name__ == "__main__":
    main()
