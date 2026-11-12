"""The site follows the shared 12 languages (ipe_web_kit.languages): translations, pages, switcher, hreflang, sitemap."""
import json
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "vendor"))
from ipe_web_kit import languages  # noqa: E402

SUP = languages.SUPPORTED


def page_path(lang):
    base = "" if lang == languages.DEFAULT else lang + "/"
    return REPO / (base + "index.html")


class SharedLanguages(unittest.TestCase):
    def test_twelve_languages_from_kit(self):
        self.assertEqual(SUP, ("en", "ko", "ja", "zh-Hant", "es", "pt-BR", "fr", "de", "id", "th", "vi", "tr"))

    def test_every_language_has_a_translation_file_with_same_keys(self):
        en = json.loads((REPO / "content/i18n/en.json").read_text(encoding="utf-8"))
        for l in SUP:
            d = json.loads((REPO / f"content/i18n/{l}.json").read_text(encoding="utf-8"))
            self.assertEqual(set(d), set(en), l)
            for k in ("feats", "caps", "alts", "chips"):
                self.assertEqual(len(d[k]), len(en[k]), (l, k))

    def test_ended_languages_are_not_listed_and_files_are_not_deleted(self):
        for l in languages.ENDED:
            self.assertNotIn(l, SUP)
            self.assertFalse(page_path(l).exists(), l)

    def test_pages_hreflang_and_data_lang_are_exact(self):
        for l in SUP:
            html = page_path(l).read_text(encoding="utf-8")
            self.assertIn(f'<html lang="{l}">', html)
            hl = re.findall(r'<link rel="alternate" hreflang="([^"]+)"', html)
            self.assertEqual(hl, list(SUP) + ["x-default"], l)
            self.assertEqual(re.findall(r'data-lang="([^"]+)"', html), list(SUP), l)

    def test_sitemap_lists_every_page(self):
        sm = (REPO / "sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(sm.count("<loc>"), len(SUP))
        self.assertNotIn("release-notes", sm)
        for l in SUP:
            self.assertIn("https://duskblocks.ipe.rest" + ("/" if l == "en" else f"/{l}/") + "</loc>", sm)

    def test_build_script_does_not_list_languages_itself(self):
        src = (REPO / "scripts/build.py").read_text(encoding="utf-8")
        self.assertNotIn('"pt-BR"', src.split("OG_LOCALE")[0])
        self.assertIn("languages.SUPPORTED", src)


class AcceptLanguage(unittest.TestCase):
    def test_resolution_rules(self):
        r = languages.resolve
        self.assertEqual(r("zh-TW"), "zh-Hant")
        self.assertEqual(r("zh-CN"), "en")
        self.assertEqual(r("pt-PT"), "pt-BR")
        self.assertEqual(languages.resolve_accept_language("zh-CN,th;q=0.8"), "th")


if __name__ == "__main__":
    unittest.main()
