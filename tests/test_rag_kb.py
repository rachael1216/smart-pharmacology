import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import kb  # noqa: E402
import rag  # noqa: E402


class TestKB(unittest.TestCase):
    def test_cn2int(self):
        self.assertEqual(kb.cn2int("十二"), 12)
        self.assertEqual(kb.cn2int("二十五"), 25)
        self.assertEqual(kb.cn2int("47"), 47)

    def test_split_chapters_skips_toc_and_offsets(self):
        pages = ["前言", "目录\n第一章 绪言 ........ 1\n第二章 药物代谢动力学 ........ 3",
                 "第一章 绪言\n药理学是……", "续", "第二章 药物代谢动力学\n首过消除……", "生物利用度……"]
        chs = kb.split_chapters(pages, offset=2)
        self.assertEqual([c["num"] for c in chs], [1, 2])
        self.assertEqual((chs[0]["start"], chs[0]["end"]), (1, 2))
        self.assertEqual((chs[1]["start"], chs[1]["end"]), (3, 4))

    def test_clean_joins_wrapped_cjk(self):
        self.assertIn("首过消除", kb.clean("称为首过消\n除。"))


class TestRAG(unittest.TestCase):
    def test_tokens(self):
        self.assertEqual(rag.tokens("首过消除 AUC"), ["首过", "过消", "消除", "auc"])

    def test_bm25_ranks_relevant_first(self):
        docs = [dict(corpus="textbook", text="口服药物首过消除使生物利用度降低"), dict(corpus="textbook", text="强心苷抑制钠泵")]
        from collections import Counter
        df = Counter()
        for d in docs:
            d["tok"] = dict(Counter(rag.tokens(d["text"])))
            d["len"] = sum(d["tok"].values())
            df.update(d["tok"].keys())
        idx = dict(n=2, avg=sum(d["len"] for d in docs) / 2, df=df, docs=docs)
        res = rag.search("首过消除", 2, idx=idx)
        self.assertEqual(res[0][1]["text"], docs[0]["text"])
        self.assertEqual(len(res), 1)


if __name__ == "__main__":
    unittest.main()
