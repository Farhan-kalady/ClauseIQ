from pathlib import Path
import pymupdf

BASE_DIR = Path(__file__).resolve().parent.parent


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    path = Path(pdf_path)
    if not path.is_file():
        # Fallback to checking relative to the project root directory
        candidate = BASE_DIR / pdf_path
        if candidate.is_file():
            path = candidate
        else:
            raise FileNotFoundError(f"PDF file not found at '{pdf_path}' or '{candidate}'")

    full_text = []
    with pymupdf.open(path) as doc:
        for page in doc:
            full_text.append(page.get_text())

    return "".join(full_text)


if __name__ == "__main__":
    sample_pdf = BASE_DIR / "data" / "raw_pdfs" / "sample_contract.pdf"
    text = extract_text_from_pdf(sample_pdf)
    print("PDF extraction successful")
    print(f"Extracted {len(text)} characters")
    print("\n--- Preview (First 500 characters) ---")
    print(text[:500])
