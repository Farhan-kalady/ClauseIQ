from pathlib import Path
import sys
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure src/ is in sys.path so sibling imports work from any cwd
src_dir = str(Path(__file__).resolve().parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from text_cleaner import clean_text


def clean_dataset(
    input_path: Path | str = BASE_DIR / "data" / "clauseiq_dataset.csv",
    output_path: Path | str = BASE_DIR / "data" / "clauseiq_dataset_clean.csv",
) -> pd.DataFrame:
    input_path = Path(input_path)
    output_path = Path(output_path)

    print(f"Loading raw dataset from {input_path}...")
    df = pd.read_csv(input_path)
    print(f"Dataset shape: {df.shape}")

    # Determine text column
    text_col = "clause_text" if "clause_text" in df.columns else df.columns[1]
    print(f"Applying clean_text on column: '{text_col}'...")
    df["clean_text"] = df[text_col].fillna("").astype(str).apply(clean_text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Done. Cleaned dataset saved to {output_path}")
    print(f"Total rows: {len(df)}")
    return df


if __name__ == "__main__":
    df = clean_dataset()
    print("\nSample cleaned rows:")
    print(df[["clause_text", "clean_text"]].head(3))