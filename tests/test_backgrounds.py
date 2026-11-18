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
from app.models import Article, BookImage, Project, UploadedDocument

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

    def test_an_image_is_either_an_address_or_its_content(self):
        image = BookImage(title="Phare", url="https://upload.wikimedia.org/phare.jpg")
        self.assertIsNone(image.data_base64)
        for fields in ({}, {"url": "http://example.org/a.png"}, {"data_base64": PNG},
                       {"url": "https://example.org/a.png", "mime_type": "image/png", "data_base64": PNG}):
            with self.subTest(fields=fields), self.assertRaises(ValidationError):
                BookImage(**fields)

    def test_a_document_is_either_an_address_or_its_content(self):
        UploadedDocument(title="Notice", kind="pdf", url="https://example.org/notice.pdf")
        UploadedDocument(title="Notice", kind="pdf", mime_type="application/pdf", data_base64=PNG)
        for fields in ({}, {"url": "ftp://example.org/a.pdf"}, {"data_base64": PNG},
                       {"url": "https://example.org/a.pdf", "mime_type": "application/pdf", "data_base64": PNG}):
            with self.subTest(fields=fields), self.assertRaises(ValidationError):
                UploadedDocument(title="Notice", kind="pdf", **fields)

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
        plain = book_builder.build_cover_html(Project(name="Livre", cover_color=None))
        self.assertNotIn("color: #fff", plain)
        self.assertNotIn(".cover-text {", plain)


def encoded(picture, fmt, **options):
    buffer = io.BytesIO()
    picture.save(buffer, fmt, **options)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def decoded(image):
    return Image.open(io.BytesIO(base64.b64decode(image.data_base64)))


class FitBackgroundTest(unittest.TestCase):
    A4 = (2480, 3508)

    def test_large_photo_is_reduced_to_the_page_at_300_dpi(self):
        photo = BookImage(title="Photo", mime_type="image/jpeg", data_base64=encoded(Image.new("RGB", (5616, 3744), "navy"), "JPEG"))
        fitted = book_builder.fit_background(photo, 210, 297)
        self.assertEqual((fitted.title, fitted.mime_type), ("Photo", "image/jpeg"))
        self.assertEqual(decoded(fitted).size, self.A4)
        self.assertLess(len(fitted.data_base64), len(photo.data_base64))

    def test_crop_keeps_the_center(self):
        picture = Image.new("RGB", (9000, 3508), "white")
        picture.paste((0, 0, 0), (3000, 0, 6000, 3508))
        fitted = decoded(book_builder.fit_background(BookImage(mime_type="image/png", data_base64=encoded(picture, "PNG")), 210, 297))
        self.assertEqual(fitted.size, self.A4)
        self.assertLess(sum(fitted.getpixel((1240, 1754))), 30)

    def test_transparency_is_kept_as_png(self):
        picture = Image.new("RGBA", (5000, 7000), (255, 0, 0, 0))
        fitted = book_builder.fit_background(BookImage(mime_type="image/png", data_base64=encoded(picture, "PNG")), 210, 297)
        self.assertEqual(fitted.mime_type, "image/png")
        self.assertEqual(decoded(fitted).mode, "RGBA")

    def test_exif_rotation_is_applied_before_cropping(self):
        picture = Image.new("RGB", (7000, 5000), "green")
        exif = picture.getexif()
        exif[0x0112] = 6
        fitted = book_builder.fit_background(BookImage(mime_type="image/jpeg", data_base64=encoded(picture, "JPEG", exif=exif)), 210, 297)
        self.assertEqual(decoded(fitted).size, self.A4)

    def test_small_svg_and_unreadable_images_are_left_alone(self):
        small = BookImage(mime_type="image/png", data_base64=encoded(Image.new("RGB", (800, 600), "red"), "PNG"))
        svg = BookImage(mime_type="image/svg+xml", data_base64=base64.b64encode(b'<svg xmlns="http://www.w3.org/2000/svg"/>').decode("ascii"))
        broken = BookImage(mime_type="image/png", data_base64=PNG)
        for image in (small, svg, broken):
            with self.subTest(mime=image.mime_type):
                self.assertIs(book_builder.fit_background(image, 210, 297), image)


class ColorAndLogoTest(unittest.TestCase):
    def test_colors_are_checked(self):
        self.assertEqual(Project(name="Livre", cover_color="#1D2927").cover_color, "#1D2927")
        for color in ("red", "#12345", "#1234567", "#gggggg", "url(x)"):
            with self.subTest(color=color), self.assertRaises(ValidationError):
                Project(name="Livre", back_color=color)
        project = Project(name="Livre")
        self.assertEqual((project.cover_color, project.back_color, project.cover_logo, project.back_logo), ("#273c75", None, False, False))
        self.assertIsNone(Project(name="Livre", cover_color=None).cover_color)

    def test_default_cover_is_blue_with_white_text(self):
        html = book_builder.build_cover_html(Project(name="Livre"))
        self.assertIn("#273c75", html)
        self.assertEqual(book_builder.color_text_style("#273c75"), "light")
        self.assertNotIn("#273c75", book_builder.build_cover_html(Project(name="Livre", cover_color=None)))

    def test_cover_color_sets_the_background_and_the_text(self):
        dark = book_builder.build_cover_html(Project(name="Livre", cover_color="#1d2927"))
        self.assertIn("@page :first { background-color: #1d2927; }", dark)
        self.assertIn(book_builder.COVER_TEXT_CSS["light"], dark)
        light = book_builder.build_cover_html(Project(name="Livre", cover_color="#f4e9c8"))
        self.assertNotIn(book_builder.COVER_TEXT_CSS["light"], light)
        self.assertEqual(book_builder.color_text_style("#000000"), "light")
        self.assertEqual(book_builder.color_text_style("#ffffff"), "dark")

    def test_image_keeps_its_text_style_over_a_color(self):
        html = book_builder.build_cover_html(Project(name="Livre", cover_color="#000000", cover_image=COVER))
        self.assertLess(html.index("background-color: #000000"), html.index("background: url("))

    def test_logo_on_the_cover_and_the_last_page(self):
        self.assertNotIn('class="cover-logo"', book_builder.build_cover_html(Project(name="Livre")))
        wikipedia = base64.b64encode(book_builder.WIKIPEDIA_LOGO.read_bytes()).decode("ascii")
        cover = book_builder.build_cover_html(Project(name="Livre", cover_logo=True))
        self.assertIn(f'<div class="cover-logo"><img src="data:image/png;base64,{wikipedia}" alt="Wikipedia"></div>', cover)
        self.assertIn(".cover-logo { position: absolute; right: 0; bottom: 0; }", cover)
        self.assertNotIn("Wikipedia2Book", cover)
        old_file = Project.model_validate({"name": "Livre", "cover_app_logo": True, "back_app_logo": True})
        self.assertFalse(book_builder.has_back_cover(old_file))
        self.assertNotIn('class="cover-logo"', book_builder.build_cover_html(old_file))
        back = book_builder.build_back_cover_html(Project(name="Livre", back_logo=True, back_color="#336699"))
        self.assertIn(f'<div class="back-logo"><img src="data:image/png;base64,{wikipedia}" alt="Wikipedia"></div>', back)
        self.assertIn(".back-logo { position: absolute; right: 15mm; bottom: 15mm; }", back)
        self.assertIn(".back-logo img { width: 25mm; margin-left: 4mm; vertical-align: bottom; }", back)
        self.assertIn("@page  { background-color: #336699; }", back)

    def test_a_last_page_needs_an_image_a_color_or_the_logo(self):
        self.assertFalse(book_builder.has_back_cover(Project(name="Livre")))
        for fields in ({"back_image": BACK}, {"back_color": "#336699"}, {"back_logo": True}):
            with self.subTest(fields=fields):
                self.assertTrue(book_builder.has_back_cover(Project(name="Livre", **fields)))


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
