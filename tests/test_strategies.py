import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resolution_strategies import (
    scheme_check,
    split_worlds_satisfiable,
    strategy_table,
)


class TestStrategies(unittest.TestCase):
    def test_strategy_table(self):
        table = strategy_table()
        # Unit, input, hyper, and both ordered orders close
        # everywhere (ordered wings-first by a different route).
        for name in (
            "unit", "input", "hyper",
            "ordered_bat_first", "ordered_wings_first",
        ):
            self.assertTrue(table[name]["kb_alone"], name)
            self.assertTrue(table[name]["kb_plus_not_h"], name)
            self.assertTrue(table[name]["kb_plus_h"], name)
        # Set of support: KB alone does not close, entailment does.
        self.assertFalse(table["set_of_support"]["kb_alone"])
        self.assertTrue(table["set_of_support"]["kb_plus_not_h"])
        self.assertFalse(table["set_of_support"]["kb_plus_h"])

    def test_split_worlds_satisfiable(self):
        worlds = split_worlds_satisfiable()
        self.assertFalse(worlds["world_mammal_empty"])
        self.assertFalse(worlds["world_baseball_empty"])

    def test_scheme(self):
        scheme = scheme_check()
        naive = scheme["naive_collapsed"]
        self.assertTrue(naive["entailment_test_closes"])
        self.assertTrue(naive["contradiction_test_closes"])
        self.assertFalse(naive["reads_as_neutral"])
        corrected = scheme["corrected_unresolved"]
        self.assertEqual(corrected["nli_label"], "Neutral")
        self.assertEqual(
            corrected["fol_verdict"], "logically inconclusive"
        )


if __name__ == "__main__":
    unittest.main()
