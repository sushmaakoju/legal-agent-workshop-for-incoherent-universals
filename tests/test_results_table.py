import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from results_table import build_table, combined_label, unresolved_table


class TestResultsTable(unittest.TestCase):
    def test_brown_bat_table(self):
        table = build_table("brown_bat")
        # Every strategy except Set of Support: both empty.
        for name, row in table.items():
            if name == "Set of Support":
                self.assertTrue(row["kb_and_not_query_empty"])
                self.assertFalse(row["kb_and_query_empty"])
                self.assertEqual(
                    row["combined_label"],
                    "inconclusive inference (cannot decide)",
                )
            else:
                self.assertTrue(row["kb_and_not_query_empty"], name)
                self.assertTrue(row["kb_and_query_empty"], name)
                self.assertTrue(
                    row["combined_label"].startswith("cannot decide"),
                    name,
                )
            self.assertEqual(row["nli_label"], "Neutral")

    def test_brown_a_table_identical(self):
        # Abstract case, run by renaming, not copy-pasted.
        self.assertEqual(build_table("brown_a"), build_table("brown_bat"))

    def test_combined_labels(self):
        self.assertEqual(combined_label(False, False), "Neutral")
        self.assertEqual(
            combined_label(True, False),
            "inconclusive inference (cannot decide)",
        )
        self.assertEqual(
            combined_label(False, True),
            "inconclusive inference (cannot decide)",
        )
        self.assertTrue(
            combined_label(True, True).startswith("cannot decide")
        )

    def test_unresolved_is_neutral_and_logically_inconclusive(self):
        table = unresolved_table()
        self.assertEqual(table["combined_label"], "Neutral")
        self.assertEqual(
            table["fol_verdict"], "logically inconclusive"
        )


if __name__ == "__main__":
    unittest.main()
