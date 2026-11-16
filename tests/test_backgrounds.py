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

import base64
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import ValidationError

from app import book_builder
from app.models import Article, BookImage, Project

PNG = base64.b64encode(b"\x89PNG\r\n\x1a\nfake").decode("ascii")
COVER = BookImage(title="couverture.png", mime_type="image/png", data_base64=PNG)
BACK = BookImage(title="dos.jpg", mime_type="image/jpeg", data_base64=PNG)
ARTICLE = Article(title="Saint-Pierre", language="fr", url="https://fr.wikipedia.org/wiki/Saint-Pierre")


class BookImageTest(unittest.TestCase):
    def test_accepts_supported_types(self):
        for mime in ("image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml"):
            BookImage(mime_type=mime, data_base64=PNG)

    def test_rejects_other_types_and_bad_base64(self):
        for mime, data in (("application/pdf", PNG), ("image/tiff", PNG), ("image/png", "pas du base64 !")):
            with self.subTest(mime=mime), self.assertRaises(ValidationError):
                BookImage(mime_type=mime, data_base64=data)

    def test_project_without_images_by_default(self):
        project = Project(name="Livre")
        self.assertIsNone(project.cover_image)
        self.assertIsNone(project.back_image)


class CoverBackgroundTest(unittest.TestCase):
    def test_cover_background_only_on_first_page(self):
        html = book_builder.build_cover_html(Project(name="Livre", cover_image=COVER, introduction="Bonjour"))
        self.assertIn(f'@page :first {{ background: url("data:image/png;base64,{PNG}") center / cover no-repeat; }}', html)
        self.assertEqual(html.count("background: url("), 1)

    def test_no_background_without_image(self):
        self.assertNotIn("background: url(", book_builder.build_cover_html(Project(name="Livre")))


class BackBackgroundTest(unittest.TestCase):
    def test_colophon_on_its_own_last_page_with_background(self):
        project = Project(name="Livre", back_image=BACK, conclusion="Fin.")
        html = book_builder.build_conclusion_page_html(project)
        self.assertIn(f'@page back-cover {{ background: url("data:image/jpeg;base64,{PNG}")', html)
        self.assertIn("page: back-cover", html)
        self.assertIn('<section class="back-cover"><footer class="colophon">', html)
        self.assertLess(html.index("Fin."), html.index('<section class="back-cover">'))

    def test_license_page_carries_back_page_without_conclusion(self):
        html = book_builder.build_license_page_html(Project(name="Livre", back_image=BACK), [ARTICLE], colophon=True)
        self.assertIn('<section class="back-cover">', html)
        self.assertNotIn('<section class="back-cover">', book_builder.build_license_page_html(Project(name="Livre", back_image=BACK), [ARTICLE]))

    def test_colophon_unchanged_without_image(self):
        html = book_builder.build_conclusion_page_html(Project(name="Livre", conclusion="Fin."))
        self.assertNotIn("back-cover", html)
        self.assertIn('<footer class="colophon">', html)


if __name__ == "__main__":
    unittest.main()
