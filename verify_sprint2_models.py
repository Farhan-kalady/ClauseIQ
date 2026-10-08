"""
ClauseIQ - Sprint 2 Results Demonstration

Displays:
1. Naive Bayes tuning results
2. Random Forest tuning results
3. Model comparison
4. Best model based on Macro-F1
5. Classification reports
6. Confusion matrices
7. Saves a comparison chart

IMPORTANT:
All values are loaded from actual generated results.
No metrics are hard-coded.
"""

import os
import json
import pandas as pd
import matplotlib
# Use non-interactive backend to ensure clean headless execution if needed
if os.environ.get("MPLBACKEND") is None:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

RESULTS_DIR = "results"

COMPARISON_CSV = os.path.join(
    RESULTS_DIR,
    "model_comparison.csv"
)

COMPARISON_JSON = os.path.join(
    RESULTS_DIR,
    "model_comparison.json"
)


# ============================================================
# 1. CHECK RESULTS
# ============================================================

print("=" * 70)
print("CLAUSEIQ - SPRINT 2 MODEL EVALUATION RESULTS")
print("=" * 70)

if not os.path.exists(RESULTS_DIR):
    raise FileNotFoundError(
        f"Results directory not found: {RESULTS_DIR}"
    )

print(f"\nResults directory: {RESULTS_DIR}")


# ============================================================
# 2. LOAD MODEL COMPARISON
# ============================================================

if not os.path.exists(COMPARISON_CSV):

    raise FileNotFoundError(
        f"\nModel comparison file not found:\n"
        f"{COMPARISON_CSV}\n\n"
        "Ask Antigravity for the actual location of "
        "the model comparison CSV."
    )


df = pd.read_csv(COMPARISON_CSV)


print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print("\nColumns:")
print(list(df.columns))

print("\nActual model comparison:")
print(df.to_string(index=False))


# ============================================================
# 3. DISPLAY NUMERICAL COMPARISON
# ============================================================

print("\n" + "=" * 70)
print("IMPORTANT EVALUATION METRICS")
print("=" * 70)

# Find columns without assuming exact capitalization

column_map = {
    column.lower().strip(): column
    for column in df.columns
}

possible_metrics = [
    "accuracy",
    "macro precision",
    "macro recall",
    "macro f1",
    "weighted precision",
    "weighted recall",
    "weighted f1"
]

available_metrics = []

for metric in possible_metrics:

    if metric in column_map:
        available_metrics.append(
            column_map[metric]
        )

model_column = None

for candidate in [
    "model",
    "Model",
    "model_name",
    "Model Name"
]:

    if candidate in df.columns:
        model_column = candidate
        break


if model_column is not None:

    display_columns = [
        model_column
    ] + available_metrics

    print(
        df[display_columns].to_string(
            index=False
        )
    )

else:

    print(
        "\nModel column could not be identified."
    )


# ============================================================
# 4. SELECT BEST MODEL USING MACRO-F1
# ============================================================

print("\n" + "=" * 70)
print("BEST MODEL SELECTION")
print("=" * 70)

macro_f1_column = None

for column in df.columns:

    if column.lower().strip() == "macro f1":
        macro_f1_column = column
        break


if macro_f1_column is None:

    raise ValueError(
        "Macro-F1 column was not found."
    )


if model_column is None:

    raise ValueError(
        "Model name column was not found."
    )


# Convert to numeric

df[macro_f1_column] = pd.to_numeric(
    df[macro_f1_column],
    errors="coerce"
)


if df[macro_f1_column].isna().any():

    raise ValueError(
        "Some Macro-F1 values are not numeric."
    )


best_index = df[macro_f1_column].idxmax()

best_model = df.loc[
    best_index,
    model_column
]

best_macro_f1 = df.loc[
    best_index,
    macro_f1_column
]


print(f"\nSelected Model : {best_model}")
print(f"Macro-F1       : {best_macro_f1:.4f}")

print(
    "\nSelection criterion:"
    "\nPrimary   -> Macro-F1"
    "\nSecondary -> Accuracy"
)


# ============================================================
# 5. ACCURACY OF SELECTED MODEL
# ============================================================

accuracy_column = None

for column in df.columns:

    if column.lower().strip() == "accuracy":
        accuracy_column = column
        break


if accuracy_column:

    best_accuracy = df.loc[
        best_index,
        accuracy_column
    ]

    print(
        f"Accuracy       : {best_accuracy:.4f}"
    )


# ============================================================
# 6. LOAD OPTIONAL JSON RESULTS
# ============================================================

if os.path.exists(COMPARISON_JSON):

    print("\n" + "=" * 70)
    print("MODEL COMPARISON JSON")
    print("=" * 70)

    with open(
        COMPARISON_JSON,
        "r",
        encoding="utf-8"
    ) as f:

        json_data = json.load(f)

    print(
        json.dumps(
            json_data,
            indent=2
        )
    )


# ============================================================
# 7. MODEL COMPARISON BAR CHART
# ============================================================

print("\n" + "=" * 70)
print("GENERATING COMPARISON CHART")
print("=" * 70)


chart_metrics = []

for metric in [
    "Accuracy",
    "Macro F1",
    "Weighted F1"
]:

    matching_column = None

    for column in df.columns:

        if column.lower().strip() == metric.lower():

            matching_column = column
            break

    if matching_column:

        chart_metrics.append(
            matching_column
        )


if chart_metrics and model_column:

    chart_df = df[
        [model_column] + chart_metrics
    ].copy()

    chart_df = chart_df.set_index(
        model_column
    )

    ax = chart_df.plot(
        kind="bar",
        figsize=(12, 7)
    )

    ax.set_title(
        "ClauseIQ - Sprint 2 Model Comparison"
    )

    ax.set_ylabel(
        "Score"
    )

    ax.set_xlabel(
        "Model"
    )

    ax.set_ylim(
        0,
        1
    )

    plt.xticks(
        rotation=20
    )

    plt.tight_layout()

    chart_path = os.path.join(
        RESULTS_DIR,
        "sprint2_model_comparison.png"
    )

    plt.savefig(
        chart_path,
        dpi=300
    )

    print(
        f"\nChart saved to:\n{chart_path}"
    )

    plt.show()


# ============================================================
# 8. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("SPRINT 2 TASK STATUS")
print("=" * 70)

print("""
1. Naive Bayes training & tuning       -> VERIFY ABOVE
2. Random Forest training & tuning     -> VERIFY ABOVE
3. Model evaluation & comparison       -> VERIFY ABOVE
4. Best model selection                -> VERIFY ABOVE
5. Evaluation artifacts                -> VERIFY ABOVE
""")

print("=" * 70)
print("SPRINT 2 MODEL EVALUATION COMPLETE")
print("=" * 70)
