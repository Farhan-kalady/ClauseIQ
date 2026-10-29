from collections import Counter
from pathlib import Path
import re
import pymupdf

BASE_DIR = Path(__file__).resolve().parent.parent

_PAGE_NUMBER_RE = re.compile(r"^(page\s*)?\d+(\s*(of|/)\s*\d+)?$", re.IGNORECASE)


def strip_headers_footers(pages: list[str], edge_lines: int = 3) -> list[str]:
    """Remove page-number lines and header/footer lines repeated across pages.

    Only the first and last `edge_lines` lines of each page are considered, so
    repeated phrases in the contract body are never touched.
    """
    split_pages = [p.splitlines() for p in pages]

    edge_counts = Counter()
    for lines in split_pages:
        edges = {l.strip() for l in lines[:edge_lines] + lines[-edge_lines:] if l.strip()}
        edge_counts.update(edges)
    repeated = {line for line, n in edge_counts.items() if len(pages) > 1 and n > 1}

    cleaned = []
    for lines in split_pages:
        kept = []
        for i, line in enumerate(lines):
            s = line.strip()
            at_edge = i < edge_lines or i >= len(lines) - edge_lines
            if at_edge and (s in repeated or _PAGE_NUMBER_RE.match(s)):
                continue
            kept.append(line)
        cleaned.append("\n".join(kept))
    return cleaned


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    path = Path(pdf_path)
    if not path.is_file():
        # Fallback to checking relative to the project root directory
        candidate = BASE_DIR / pdf_path
        if candidate.is_file():
            path = candidate
        else:
            raise FileNotFoundError(f"PDF file not found at '{pdf_path}' or '{candidate}'")

    with pymupdf.open(path) as doc:
        pages = [page.get_text() for page in doc]

    return "\n".join(strip_headers_footers(pages))


if __name__ == "__main__":
    sample_pdf = BASE_DIR / "data" / "raw_pdfs" / "sample_contract.pdf"
    text = extract_text_from_pdf(sample_pdf)
    print("PDF extraction successful")
    print(f"Extracted {len(text)} characters")
    print("\n--- Preview (First 500 characters) ---")
    print(text[:500])
