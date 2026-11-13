import os
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import journal_md  # noqa: E402


class Md(unittest.TestCase):
    def test_front_matter_and_render(self):
        meta, body = journal_md.parse('---\ntitle: "A"\ndate: 2026-11-13\n---\n\n## H\n\ntext **b** `c`\n\n- x\n- y\n')
        self.assertEqual((meta["title"], meta["date"]), ("A", "2026-11-13"))
        out = journal_md.render(body)
        self.assertIn("<h2>H</h2>", out)
        self.assertIn("<strong>b</strong>", out)
        self.assertIn("<ul><li>x</li><li>y</li></ul>", out)

    def test_escapes_html(self):
        self.assertIn("&lt;script&gt;", journal_md.inline("<script>"))


class Posts(unittest.TestCase):
    def test_every_post_has_en_and_ko_with_matching_slug(self):
        posts = journal_md.load_posts(str(REPO))
        self.assertTrue(posts)
        for slug, v in posts.items():
            self.assertEqual(set(v), {"en", "ko"}, slug)
            for lang, (m, _) in v.items():
                self.assertEqual(m["slug"], slug)
                self.assertEqual(m["lang"], lang)
                self.assertTrue(m["title"] and m["description"] and m["date"])

    def test_internal_links_point_to_existing_posts(self):
        import re
        posts = journal_md.load_posts(str(REPO))
        for slug, v in posts.items():
            for lang, (_, body) in v.items():
                for u in re.findall(r"\]\((/(?:ko/)?journal/([^/)]+)/)\)", body):
                    self.assertIn(u[1], posts, f"{slug}/{lang} → {u[0]}")


if __name__ == "__main__":
    unittest.main()
