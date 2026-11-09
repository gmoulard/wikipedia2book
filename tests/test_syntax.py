import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class SyntaxTest(unittest.TestCase):
    def test_all_python_files_parse(self):
        files = sorted((ROOT / "app").rglob("*.py"))
        self.assertTrue(files, "no .py files found under app/")
        for path in files:
            with self.subTest(file=str(path.relative_to(ROOT))):
                source = path.read_text(encoding="utf-8")
                ast.parse(source, filename=str(path))


if __name__ == "__main__":
    unittest.main()
