import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from legal_agent.loop import resume_run, run_agent
from run import StubClient


class TestLoop(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        # Copy cases/ into the temp root so the loop can read them.
        src = Path(__file__).resolve().parents[1] / "cases"
        shutil.copytree(src, self.tmp / "cases")
        # Also copy the modules the loop imports via sys.path.
        # The loop imports cases, agent_kit, verification, fol, nli
        # from the project root, which is already on sys.path
        # in this test (see sys.path insert above), so only the
        # cases directory needs to live under the temp root.

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_run_agent_answers_with_stub(self):
        result = run_agent(root=self.tmp, client=StubClient(), turns=30)
        self.assertEqual(result["status"], "answered")
        self.assertEqual(result["memo"]["nli_label"], "Neutral")
        self.assertEqual(result["memo"]["fol_claim"], "inconclusive")
        progress_file = self.tmp / "workspace" / f"{result['run_id']}.json"
        self.assertTrue(progress_file.is_file())

    def test_resume_run_continues_paused_run(self):
        # A stub that never files a memo: run should pause at
        # the turn limit, then resume_run should continue it.
        class NeverFiles:
            class chat:
                class completions:
                    @staticmethod
                    def create(model=None, messages=None, tools=None, tool_choice=None):
                        class Msg:
                            content = "thinking"
                            tool_calls = []

                        class Resp:
                            choices = [type("C", (), {"message": Msg()})()]

                        return Resp()

        result = run_agent(root=self.tmp, client=NeverFiles(), turns=2)
        self.assertEqual(result["status"], "paused")
        resumed = resume_run(
            root=self.tmp, run_id=result["run_id"], client=StubClient(), turns=30
        )
        self.assertEqual(resumed["status"], "answered")

    def test_resume_unknown_run_raises(self):
        with self.assertRaises(FileNotFoundError):
            resume_run(root=self.tmp, run_id="doesnotexist", client=StubClient())


if __name__ == "__main__":
    unittest.main()
