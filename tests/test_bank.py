import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import bank  # noqa: E402
import common  # noqa: E402


class TestBank(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = bank.Bank()

    def test_check_passes(self):
        err, _ = bank.check(self.b)
        self.assertEqual(err, [], "\n".join(err[:20]))

    def test_every_answered_question_resolves(self):
        for q in self.b.questions:
            if q.get("status") != "todo":
                ans = common.full_answer(q, self.b.cards, self.b.compares)
                self.assertTrue(ans.strip(), q["id"])
                self.assertNotIn("引用失效", ans, q["id"])

    def test_ref_forms(self):
        t, body = common.resolve_ref("first_pass", self.b.cards, self.b.compares)
        self.assertIn("首过", t)
        t, body = common.resolve_ref("raas#ACEI降压机制", self.b.cards, self.b.compares)
        self.assertIn("缓激肽", body)
        t, body = common.resolve_ref("cmp:heparin_vs_warfarin", self.b.cards, self.b.compares)
        self.assertIn("鱼精蛋白", body)
        with self.assertRaises(KeyError):
            common.resolve_ref("raas#不存在的小节", self.b.cards, self.b.compares)

    def test_raw_matches_exams(self):
        exams = {f.stem for f in common.exam_files()}
        raws = {f.stem for f in common.RAW.glob("*.md")}
        self.assertEqual(exams, raws)

    def test_yaml_roundtrip_is_stable(self):
        f = common.exam_files()[0]
        before = f.read_text(encoding="utf-8")
        common.write_exam(f, common.load_yaml(f))
        self.assertEqual(before, f.read_text(encoding="utf-8"), "bank.py fmt 应当是幂等的")

    def test_stems(self):
        stems = common.load_stems()
        self.assertEqual(common.stems_for("metoprolol", stems), ["olol"])
        self.assertIn("micin", common.stems_for("gentamicin", stems))
        self.assertNotIn("mycin", common.stems_for("gentamicin", stems))
        self.assertEqual(common.stems_for("magnesium sulfate", stems), [])
        self.assertIn("apine", common.stems_for("clozapine", stems))
        self.assertNotIn("apine", common.stems_for("nifedipine", stems))


if __name__ == "__main__":
    unittest.main()
