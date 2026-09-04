from pathlib import Path
import sys
import spacy

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure src/ is in sys.path so sibling imports work from any cwd
src_dir = str(Path(__file__).resolve().parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

nlp = spacy.load("en_core_web_sm")


def split_into_clauses(text: str) -> list[str]:
    """Split input contract text into sentence-level clauses using spaCy."""
    if not text or not isinstance(text, str):
        return []
    doc = nlp(text)
    clauses = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 0]
    return clauses


if __name__ == "__main__":
    from pdf_extractor import extract_text_from_pdf

    sample_pdf = BASE_DIR / "data" / "raw_pdfs" / "sample_contract.pdf"
    text = extract_text_from_pdf(sample_pdf)
    clauses = split_into_clauses(text)
    print(f"Clause splitting successful: Found {len(clauses)} clauses")
    print("\n--- First 3 Sample Clauses ---")
    for i, c in enumerate(clauses[:3], 1):
        print(f"[{i}] {c}")