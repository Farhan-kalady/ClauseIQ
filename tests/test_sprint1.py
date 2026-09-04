import unittest
from pathlib import Path
import sys

# Setup project root and src/ in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from text_cleaner import clean_text
from clause_splitter import split_into_clauses
from pdf_extractor import extract_text_from_pdf


class TestSprint1Pipeline(unittest.TestCase):
    """Test suite for ClauseIQ Sprint 1 Core ML Pipeline."""

    # 1. Text Cleaning Tests
    def test_text_cleaning_basic(self):
        sample = "  This Agreement   shall be GOVERNED by the Laws of Delaware.  "
        cleaned = clean_text(sample)
        self.assertEqual(cleaned, "this agreement shall be governed by the laws of delaware.")
        # Ensure legal keywords remain intact
        for keyword in ["shall", "agreement", "governed"]:
            self.assertIn(keyword, cleaned)

    def test_text_cleaning_urls_and_emails(self):
        sample = "Contact us at legal@company.com or visit https://www.company.com/terms for details."
        cleaned = clean_text(sample)
        self.assertNotIn("https", cleaned)
        self.assertNotIn("company.com", cleaned)
        self.assertNotIn("legal@", cleaned)
        self.assertIn("contact us at", cleaned)
        self.assertIn("details", cleaned)

    def test_text_cleaning_empty_and_invalid_input(self):
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text("   "), "")
        self.assertEqual(clean_text(None), "")
        self.assertEqual(clean_text(12345), "")

    # 2. Clause Splitting Tests
    def test_clause_splitting_basic(self):
        sample_doc = (
            "This Agreement is entered into as of January 1, 2026. "
            "The Service Provider shall maintain confidentiality. "
            "Payment shall be made within 30 days."
        )
        clauses = split_into_clauses(sample_doc)
        self.assertIsInstance(clauses, list)
        self.assertEqual(len(clauses), 3)
        self.assertTrue(all(len(c) > 0 for c in clauses))

    def test_clause_splitting_empty_and_invalid_input(self):
        self.assertEqual(split_into_clauses(""), [])
        self.assertEqual(split_into_clauses("   "), [])
        self.assertEqual(split_into_clauses(None), [])
        self.assertEqual(split_into_clauses(100), [])

    # 3. PDF Extraction Tests
    def test_pdf_extraction_sample_contract(self):
        pdf_path = PROJECT_ROOT / "data" / "raw_pdfs" / "sample_contract.pdf"
        self.assertTrue(pdf_path.is_file(), f"Sample PDF missing at {pdf_path}")
        text = extract_text_from_pdf(pdf_path)
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 500)
        self.assertIn("Confidentiality", text)

    def test_pdf_extraction_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            extract_text_from_pdf("non_existent_file_xyz.pdf")

    # 4. Model Artifact Existence Tests
    def test_model_artifacts_exist(self):
        models_dir = PROJECT_ROOT / "models"
        required_artifacts = [
            "tfidf_vectorizer.pkl",
            "label_encoder.pkl",
            "train_test_split.pkl",
            "logistic_regression.pkl",
            "svm_classifier.pkl",
        ]
        for artifact in required_artifacts:
            artifact_path = models_dir / artifact
            self.assertTrue(artifact_path.is_file(), f"Expected artifact {artifact} not found at {artifact_path}")

    # 5. End-to-End Prediction Test with Saved Model
    def test_saved_model_inference(self):
        import joblib

        models_dir = PROJECT_ROOT / "models"
        vectorizer = joblib.load(models_dir / "tfidf_vectorizer.pkl")
        svm_model = joblib.load(models_dir / "svm_classifier.pkl")
        le = joblib.load(models_dir / "label_encoder.pkl")

        raw_clause = "This Agreement and all disputes arising out of it shall be governed by the laws of New York."
        cleaned = clean_text(raw_clause)
        vec = vectorizer.transform([cleaned])
        pred_idx = svm_model.predict(vec)[0]
        predicted_category = le.inverse_transform([pred_idx])[0]

        self.assertIsInstance(predicted_category, str)
        self.assertEqual(predicted_category, "Governing Law")


if __name__ == "__main__":
    unittest.main(verbosity=2)
