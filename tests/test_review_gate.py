import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "ops"))
import journal_md  # noqa: E402
import publish_next  # noqa: E402

FM = "---\ntitle: T\ndate: 2026-11-14\nslug: s\nlang: %s\ndescription: d\n%s---\n\nbody\n"


class Review(unittest.TestCase):
    def test_originals_need_no_review(self):
        for l in ("en", "ko"):
            self.assertTrue(journal_md.is_reviewed({}, l))

    def test_translation_needs_iris_review(self):
        self.assertFalse(journal_md.is_reviewed({}, "ja"))
        self.assertFalse(journal_md.is_reviewed({"copy_review": "pending"}, "ja"))
        self.assertFalse(journal_md.is_reviewed({"copy_review": "iris"}, "ja"))
        self.assertTrue(journal_md.is_reviewed({"copy_review": "iris 2026-11-14"}, "ja"))
        self.assertTrue(journal_md.is_reviewed({"copy_review": "iris", "copy_review_date": "2026-11-14"}, "ja"))

    def test_publish_skips_unreviewed_editions(self):
        with tempfile.TemporaryDirectory() as d:
            for lang, extra in (("en", ""), ("ko", ""), ("ja", ""), ("fr", "copy_review: iris 2026-11-14\n"), ("xx", "copy_review: iris 2026-11-14\n")):
                Path(d, lang + ".md").write_text(FM % (lang, extra), encoding="utf-8")
            got = [l for l, _ in publish_next.editions(d)]
        self.assertEqual(got, ["en", "ko", "fr"])  # ja: 검수 없음 · xx: 지원 언어 아님

    def test_loader_drops_unreviewed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d, "content", "journal", "s")
            p.mkdir(parents=True)
            (p / "en.md").write_text(FM % ("en", ""), encoding="utf-8")
            (p / "de.md").write_text(FM % ("de", ""), encoding="utf-8")
            self.assertEqual(set(journal_md.load_posts(d)["s"]), {"en"})
            self.assertEqual(set(journal_md.load_posts(d, only_reviewed=False)["s"]), {"en", "de"})


if __name__ == "__main__":
    unittest.main()
