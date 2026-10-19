import re
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure src/ is in sys.path
src_dir = str(Path(__file__).resolve().parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def split_into_clauses(text: str, filter_synthetic_artifacts: bool = True) -> list[str]:
    """Split input contract text into clause-level segments, protecting section numbers and legal headings.
    
    Pipeline:
    1. Filter generic page headers/footers, page numbers, and optional metadata banners.
    2. Re-attach standalone numbered section headers.
    3. Split on contractual section boundaries (e.g. 'PARTIES AND BACKGROUND', 'Section 1.', 'ARTICLE 1').
    4. Fall back to paragraph splitting (double newlines) if sections not found.
    5. Fall back to sentence tokenizer protecting section numbers.
    6. Merge isolated numbering prefixes with following clause.
    7. Filter fragments < 15 characters without alphabetic content.
    """
    if not text or not isinstance(text, str):
        return []

    clean_input = text.strip()
    if not clean_input:
        return []

    # 1. Filter running page headers/footers, page numbers, and metadata banners
    lines = clean_input.split("\n")
    filtered_lines = []
    skip_disclaimer = False

    for line in lines:
        stripped = line.strip()

        # Generic page numbers (e.g. "Page 1", "Page 1 of 5", "1 / 10", "- 1 -")
        if re.match(r"^(?:page\s+\d+(?:\s+of\s+\d+)?|\d+\s*/\s*\d+|[-–—]\s*\d+\s*[-–—])$", stripped, re.IGNORECASE):
            continue

        # Optional test/banner filter for evaluation documents
        if filter_synthetic_artifacts:
            if re.match(r"^(?:ClauseIQ Synthetic Test Document|IMPORTANT (?:TEST-DATA )?NOTICE:)", stripped, re.IGNORECASE):
                if "NOTICE:" in stripped.upper():
                    skip_disclaimer = True
                continue
            if skip_disclaimer:
                if stripped.endswith("relied upon.") or stripped.endswith("relied upon"):
                    skip_disclaimer = False
                continue
            if re.search(r"^(?:END OF (?:SYNTHETIC )?TEST DOCUMENT|ClauseIQ Test Document|SYNTHETIC COMPANY SERVICE AGREEMENT)", stripped, re.IGNORECASE):
                continue
            if re.search(r"^These names and signatures are fictional", stripped, re.IGNORECASE):
                continue

        filtered_lines.append(line)

    filtered_text = "\n".join(filtered_lines).strip()
    if not filtered_text:
        filtered_text = clean_input

    # 2. Re-attach standalone numbered section headers (e.g. "1.\nDEFINITIONS" -> "1. DEFINITIONS")
    filtered_text = re.sub(r"(?m)^(\d{1,2}\.)\s*\n\s*([A-Za-z])", r"\1 \2", filtered_text)

    # 3. Check for structured contractual section boundaries (e.g. 'PARTIES AND BACKGROUND', '1. DEFINITIONS', 'Section 1.', 'ARTICLE 1')
    section_pattern = r"(?m)(?=^(?:PARTIES AND BACKGROUND|\bSection\s+\d{1,2}\.|\bARTICLE\s+[IVXLCDM\d]+|\d{1,2}\.\s+[A-Z\s]{3,}))"
    sections = [s.strip() for s in re.split(section_pattern, filtered_text) if s.strip()]
    if len(sections) >= 3:
        clean_secs = [s for s in sections if len(s) >= 20 and re.search(r"[a-zA-Z]", s)]
        if len(clean_secs) >= 3:
            return clean_secs

    # 4. Paragraph splitting by double newlines if distinct paragraphs exist
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", filtered_text) if p.strip()]
    if len(paragraphs) >= 2:
        clean_paras = [p for p in paragraphs if len(p) >= 20 and re.search(r"[a-zA-Z]", p)]
        if len(clean_paras) >= 2:
            return clean_paras

    # 5. Sentence / clause tokenizer protecting section numbers (fallback for unstructured continuous text)
    raw_clauses = re.split(r"(?<!\b\d\.)(?<!\b\d{2}\.)(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])", filtered_text)
    if len(raw_clauses) <= 1:
        raw_clauses = re.split(r"(?<=[.!?])\s+", filtered_text)

    # 6. Merge any lingering isolated numbered prefixes (e.g. "1.", "2.", "Section 1.") with following clause
    merged_clauses = []
    prefix_buffer = ""
    for c in raw_clauses:
        c_str = c.strip()
        if not c_str:
            continue
        if re.match(r"^(\d{1,2}\.|\bSection\s+\d{1,2}\.?)$", c_str, re.IGNORECASE):
            prefix_buffer = (prefix_buffer + " " + c_str).strip()
            continue
        if prefix_buffer:
            merged_clauses.append(f"{prefix_buffer} {c_str}")
            prefix_buffer = ""
        else:
            merged_clauses.append(c_str)
    if prefix_buffer:
        if merged_clauses:
            merged_clauses[-1] = f"{merged_clauses[-1]} {prefix_buffer}"
        else:
            merged_clauses.append(prefix_buffer)

    # 7. Filter short meaningless fragments (< 15 chars without letters)
    final_clauses = [c for c in merged_clauses if len(c) >= 15 and re.search(r"[a-zA-Z]", c)]
    return final_clauses if final_clauses else merged_clauses


if __name__ == "__main__":
    from pdf_extractor import extract_text_from_pdf

    sample_pdf = BASE_DIR / "data" / "raw_pdfs" / "sample_contract.pdf"
    if sample_pdf.is_file():
        text = extract_text_from_pdf(sample_pdf)
        clauses = split_into_clauses(text)
        print(f"Clause splitting successful: Found {len(clauses)} clauses")
        print("\n--- First 3 Sample Clauses ---")
        for i, c in enumerate(clauses[:3], 1):
            print(f"[{i}] {c}")