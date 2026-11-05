import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    abstract_pdf_interpretation,
    baseball_model,
    evaluate_pdf_rules,
    mammal_model,
    pdf_interpretation,
    prove_no_collapsed_model,
)


class TestModels(unittest.TestCase):
    def test_pdf_interpretation_rules(self):
        # Sketch's I0: rules 1 and 4 true, 2 and 3 false.
        rules = evaluate_pdf_rules(pdf_interpretation())
        self.assertTrue(rules["rule1_wings_not_barrels"])
        self.assertFalse(rules["rule2_bats_have_wings"])
        self.assertFalse(rules["rule3_bats_have_barrel"])
        self.assertTrue(rules["rule4_barrels_not_wings"])

    def test_abstract_pdf_rules_identical(self):
        rules = evaluate_pdf_rules(
            abstract_pdf_interpretation(), keyword="A"
        )
        self.assertEqual(rules, evaluate_pdf_rules(pdf_interpretation()))

    def test_reading_models_disagree_on_h(self):
        self.assertTrue(mammal_model()["h_true"])
        self.assertFalse(baseball_model()["h_true"])

    def test_no_collapsed_model_proof(self):
        proof = prove_no_collapsed_model()
        self.assertIn("unsatisfiable", proof["conclusion"])


if __name__ == "__main__":
    unittest.main()
