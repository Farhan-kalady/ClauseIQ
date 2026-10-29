"""Classify every clause of a contract PDF and print the Table 5.7 view.

Usage:
    .venv\\Scripts\\python show_document_predictions.py [path/to/contract.pdf]

Defaults to data/raw_pdfs/sample_contract.pdf (the document in Table 5.7).
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path[:0] = [str(BASE_DIR), str(BASE_DIR / "src")]
sys.stdout.reconfigure(encoding="utf-8")

from api.services.ml_service import classify_document

pdf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE_DIR / "data" / "raw_pdfs" / "sample_contract.pdf"
result = classify_document(pdf_path.read_bytes(), pdf_path.name)
clauses = result["clauses"]

print(f"\n{pdf_path.name}: {len(clauses)} clauses extracted\n")
print(f"{'#':>3}  {'Predicted Category':<30} {'Conf':>6}  {'Assigned Tier':<34} Clause snippet")
print("-" * 120)
for c in clauses:
    snippet = " ".join(c["clause_text"].split())[:45]
    print(f"{c['clause_index']:>3}  {c['predicted_category']:<30} {c['confidence'] * 100:5.1f}%  {c['confidence_status']:<34} {snippet}")

tiers = {}
for c in clauses:
    tiers[c["confidence_status"]] = tiers.get(c["confidence_status"], 0) + 1
print("\nTier summary:", ", ".join(f"{t}: {n}" for t, n in tiers.items()))
