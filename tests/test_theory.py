import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fol import check_collapsed, check_unresolved_worlds, fol_verdict, linear_resolve, collapsed_clauses, _lit
from nli import nli_label
from verification.verify_fol_theory import run_verification as verify_fol
from verification.verify_memo import run_verification as verify_memo
from verification.verify_nli_theory import run_verification as verify_nli


class TestTheory(unittest.TestCase):
    def test_collapsed_kb_unsatisfiable(self):
        result = check_collapsed()
        self.assertTrue(result["collapsed_kb_unsatisfiable"])
        self.assertTrue(result["kb_only_empty_clause"])

    def test_two_resolution_procedures_only(self):
        # Traditional (saturation) and linear both close the
        # collapsed KB on its own, without the negated query.
        result = check_collapsed()
        self.assertTrue(result["traditional_kb_only_empty_clause"])
        self.assertTrue(result["linear_kb_only_empty_clause"])
        self.assertEqual(result["linear_kb_only_chain_length"], 4)
        self.assertEqual(
            fol_verdict()["resolution_procedures_used"],
            ["traditional", "linear"],
        )
        # Linear chain, direct check from Bat.
        empty, chain = linear_resolve(
            collapsed_clauses(), frozenset([_lit("Bat")])
        )
        self.assertTrue(empty)
        self.assertEqual(len(chain), 4)

    def test_unresolved_worlds_inconclusive(self):
        result = check_unresolved_worlds()
        self.assertTrue(result["logically_inconclusive"])
        self.assertFalse(result["h_follows_from_unresolved"])
        self.assertFalse(result["not_h_follows_from_unresolved"])

    def test_nli_neutral(self):
        self.assertEqual(nli_label()["label"], "Neutral")

    def test_verifiers_refuse_entailment_overclaim(self):
        memo = {
            "nli_label": "Entailment",
            "nli_reason": "collapsed resolution",
            "fol_claim": "entailed",
            "fol_reason": "collapsed resolution",
        }
        self.assertFalse(verify_nli(memo)["passed"])
        self.assertFalse(verify_fol(memo)["passed"])

    def test_verifiers_pass_corrected_memo(self):
        memo = {
            "nli_label": "Neutral",
            "nli_reason": "readings disagree",
            "fol_claim": "inconclusive",
            "fol_reason": "unresolved worlds disagree",
        }
        self.assertTrue(verify_nli(memo)["passed"])
        self.assertTrue(verify_fol(memo)["passed"])
        self.assertTrue(verify_memo(memo)["passed"])

    def test_memo_rules_refuse_signed_overclaim(self):
        memo = {
            "nli_label": "Neutral",
            "nli_reason": "readings disagree",
            "fol_claim": "inconclusive",
            "fol_reason": "signed statement proves it",
        }
        self.assertFalse(verify_memo(memo)["passed"])


if __name__ == "__main__":
    unittest.main()
