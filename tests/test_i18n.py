import re
import unittest
from pathlib import Path

I18N_PATH = Path(__file__).resolve().parent.parent / "app" / "static" / "i18n.js"
LANGUAGES = ["fr", "en", "es", "pt", "it", "de", "nl", "tr", "zh", "ja", "fa"]


def _extract_blocks(source):
    blocks = {}
    for lang in LANGUAGES:
        match = re.search(rf"\b{lang}:\s*\{{(.*?)\n  \}},", source, re.DOTALL)
        assert match, f"block not found for {lang}"
        keys = re.findall(r'"([a-zA-Z0-9_.]+)":', match.group(1))
        blocks[lang] = keys
    return blocks


class I18nParityTest(unittest.TestCase):
    def test_every_language_defines_the_same_keys_once(self):
        source = I18N_PATH.read_text(encoding="utf-8")
        blocks = _extract_blocks(source)
        reference = set(blocks["fr"])
        self.assertTrue(reference, "no keys found in fr block")
        for lang, keys in blocks.items():
            with self.subTest(lang=lang):
                self.assertEqual(set(keys), reference, f"{lang} keys differ from fr")
                self.assertEqual(len(keys), len(set(keys)), f"{lang} has duplicate keys")

    def test_placeholders_match_across_languages(self):
        source = I18N_PATH.read_text(encoding="utf-8")
        blocks = {}
        for lang in LANGUAGES:
            match = re.search(rf"\b{lang}:\s*\{{(.*?)\n  \}},", source, re.DOTALL)
            pairs = re.findall(r'"([a-zA-Z0-9_.]+)":\s*"((?:[^"\\]|\\.)*)"', match.group(1))
            blocks[lang] = dict(pairs)
        for key, fr_value in blocks["fr"].items():
            fr_placeholders = set(re.findall(r"\{(\w+)\}", fr_value))
            for lang in LANGUAGES:
                with self.subTest(lang=lang, key=key):
                    other_placeholders = set(re.findall(r"\{(\w+)\}", blocks[lang][key]))
                    self.assertEqual(other_placeholders, fr_placeholders)


if __name__ == "__main__":
    unittest.main()
