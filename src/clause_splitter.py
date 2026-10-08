import re
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure src/ is in sys.path so sibling imports work from any cwd
src_dir = str(Path(__file__).resolve().parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Initialize NLP engine with graceful fallback for environments where spaCy DLLs are blocked
_nlp = None
try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
except Exception:
    _nlp = None


def split_into_clauses(text: str) -> list[str]:
    """Split input contract text into sentence-level clauses using spaCy or regex fallback."""
    if not text or not isinstance(text, str):
        return []
    
    clean_input = text.strip()
    if not clean_input:
        return []

    if _nlp is not None:
        try:
            doc = _nlp(clean_input)
            clauses = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 0]
            if clauses:
                return clauses
        except Exception:
            pass

    # High-precision fallback sentence tokenizer for legal text
    raw_clauses = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])", clean_input)
    if len(raw_clauses) <= 1:
        raw_clauses = re.split(r"(?<=[.!?])\s+", clean_input)

    return [c.strip() for c in raw_clauses if len(c.strip()) > 0]


if __name__ == "__main__":
    from pdf_extractor import extract_text_from_pdf

    sample_pdf = BASE_DIR / "data" / "raw_pdfs" / "sample_contract.pdf"
    text = extract_text_from_pdf(sample_pdf)
    clauses = split_into_clauses(text)
    print(f"Clause splitting successful: Found {len(clauses)} clauses")
    print("\n--- First 3 Sample Clauses ---")
    for i, c in enumerate(clauses[:3], 1):
        print(f"[{i}] {c}")
