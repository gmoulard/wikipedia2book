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
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image
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
        self.assertIn(f'@page :first {{ background: url("data:image/png;base64,{PNG}") center / cover no-repeat fixed; }}', html)
        self.assertEqual(html.count("background: url("), 1)

    def test_no_background_without_image(self):
        self.assertNotIn("background: url(", book_builder.build_cover_html(Project(name="Livre")))


def png(color, size=(300, 400), mode="RGB", split=None):
    picture = Image.new(mode, size, color)
    if split:
        picture.paste(split, (0, 0, size[0] // 2, size[1]))
    buffer = io.BytesIO()
    picture.save(buffer, "PNG")
    return BookImage(title="fond.png", mime_type="image/png", data_base64=base64.b64encode(buffer.getvalue()).decode("ascii"))


class CoverTextStyleTest(unittest.TestCase):
    AREA = (16, 18, 192, 188)

    def test_text_color_follows_the_background(self):
        cases = {
            "dark": png("white"),
            "light": png("black"),
            "band": png("white", split=(0, 0, 0)),
        }
        for style, image in cases.items():
            with self.subTest(style=style):
                self.assertEqual(book_builder.cover_text_style(image, 210, 297, self.AREA), style)

    def test_transparent_image_is_read_on_white_paper(self):
        self.assertEqual(book_builder.cover_text_style(png((0, 0, 0, 0), mode="RGBA"), 210, 297, self.AREA), "dark")

    def test_only_the_visible_part_behind_the_text_counts(self):
        wide = png("white", size=(1200, 400), split=(0, 0, 0))
        self.assertEqual(book_builder.cover_text_style(wide, 210, 297, (120, 18, 192, 188)), "dark")

    def test_unreadable_image_gets_the_band(self):
        svg = BookImage(mime_type="image/svg+xml", data_base64=base64.b64encode(b'<svg xmlns="http://www.w3.org/2000/svg"/>').decode("ascii"))
        self.assertEqual(book_builder.cover_text_style(svg, 210, 297, self.AREA), "band")

    def test_cover_html_applies_the_style(self):
        dark = book_builder.build_cover_html(Project(name="Livre", cover_image=png("black")))
        self.assertIn(".cover, .cover .author, .cover .cover-note { color: #fff; }", dark)
        band = book_builder.build_cover_html(Project(name="Livre", cover_image=png("white", split=(0, 0, 0))))
        self.assertIn(".cover-text { padding:", band)
        plain = book_builder.build_cover_html(Project(name="Livre"))
        self.assertNotIn("color: #fff", plain)
        self.assertNotIn(".cover-text {", plain)


class BackBackgroundTest(unittest.TestCase):
    def test_back_cover_page_is_the_image_alone(self):
        html = book_builder.build_back_cover_html(Project(name="Livre", back_image=BACK, page_format="A5"))
        self.assertIn("@page { size: 148mm 210mm; margin: 0; }", html)
        self.assertIn(f'@page  {{ background: url("data:image/jpeg;base64,{PNG}") center / cover no-repeat fixed; }}', html)
        self.assertNotIn("colophon", html)

    def test_edition_date_follows_the_logo_not_the_cover(self):
        project = Project(name="Livre")
        license_html = book_builder.build_license_page_html(project, [ARTICLE], "en")
        self.assertLess(license_html.index('<img src="data:image/png;base64,'), license_html.index('<p class="edition">Edition of '))
        self.assertNotIn("Edition of", book_builder.build_cover_html(project, "en"))

    def test_colophon_follows_the_license_not_the_conclusion(self):
        project = Project(name="Livre", back_image=BACK, conclusion="Fin.")
        self.assertIn('<footer class="colophon">', book_builder.build_license_page_html(project, [ARTICLE]))
        self.assertNotIn("colophon", book_builder.build_conclusion_page_html(project))


if __name__ == "__main__":
    unittest.main()
