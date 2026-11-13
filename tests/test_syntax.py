# This file is part of Wikipedia2Book
# <https://github.com/gmoulard/wikipedia2book>.
# Copyright (c) 2026 Guillaume Moulard.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
