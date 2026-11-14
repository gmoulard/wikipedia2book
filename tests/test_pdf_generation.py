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

import sys
import types
import unittest
from io import BytesIO

try:
    import weasyprint  # noqa: F401
except Exception:
    fake = types.ModuleType("weasyprint")
    fake.HTML = lambda *a, **k: None
    sys.modules["weasyprint"] = fake

from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

from app.book_builder import build_license_page_html, build_toc_html
from app.models import Article, Project
from app.pdf_generator import fit_pdf_to_format, stamp_page_numbers


def _make_pdf(num_pages, size):
    buffer = BytesIO()
    pdf_canvas = canvas.Canvas(buffer, pagesize=size)
    for _ in range(num_pages):
        pdf_canvas.drawString(50, 500, "page body")
        pdf_canvas.showPage()
    pdf_canvas.save()
    buffer.seek(0)
    return buffer.read()


class StampPageNumbersTest(unittest.TestCase):
    def test_skips_first_page_and_respects_each_page_size(self):
        writer = PdfWriter()
        writer.append(BytesIO(_make_pdf(1, size=(400, 600))))
        writer.append(BytesIO(_make_pdf(2, size=(300, 500))))
        stamp_page_numbers(writer)

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        reader = PdfReader(output)

        self.assertEqual(len(reader.pages), 3)
        self.assertNotIn("1", reader.pages[0].extract_text())
        self.assertIn("2", reader.pages[1].extract_text())
        self.assertIn("3", reader.pages[2].extract_text())


class FitPdfToFormatTest(unittest.TestCase):
    def test_every_page_matches_the_target_format_regardless_of_source_shape(self):
        from reportlab.lib.units import mm

        source = BytesIO()
        pdf_canvas = canvas.Canvas(source, pagesize=(400, 600))
        pdf_canvas.drawString(50, 500, "portrait page")
        pdf_canvas.showPage()
        pdf_canvas.setPageSize((600, 300))
        pdf_canvas.drawString(50, 250, "landscape page")
        pdf_canvas.showPage()
        pdf_canvas.save()
        source.seek(0)

        fitted = fit_pdf_to_format(source.read(), width_mm=148, height_mm=210)
        reader = PdfReader(BytesIO(fitted))
        self.assertEqual(len(reader.pages), 2)
        expected = (round(148 * mm, 3), round(210 * mm, 3))
        for page in reader.pages:
            actual = (round(float(page.mediabox.width), 3), round(float(page.mediabox.height), 3))
            self.assertEqual(actual, expected)
        self.assertIn("portrait page", reader.pages[0].extract_text())
        self.assertIn("landscape page", reader.pages[1].extract_text())


class FitFastPathTest(unittest.TestCase):
    def _pdf(self, width, height):
        buffer = BytesIO()
        pdf_canvas = canvas.Canvas(buffer, pagesize=(width, height))
        pdf_canvas.drawString(50, 50, "content")
        pdf_canvas.showPage()
        pdf_canvas.save()
        return buffer.getvalue()

    def test_page_within_one_point_keeps_its_content_and_gets_the_exact_format(self):
        from reportlab.lib.units import mm
        source = self._pdf(595.92, 841.92)
        original = PdfReader(BytesIO(source)).pages[0].get_contents().get_data()
        page = PdfReader(BytesIO(fit_pdf_to_format(source, 210, 297))).pages[0]
        self.assertEqual((round(float(page.mediabox.width), 3), round(float(page.mediabox.height), 3)), (round(210 * mm, 3), round(297 * mm, 3)))
        self.assertEqual(page.get_contents().get_data(), original)

    def test_page_with_another_size_is_still_recomposed(self):
        source = self._pdf(612, 792)
        original = PdfReader(BytesIO(source)).pages[0].get_contents().get_data()
        page = PdfReader(BytesIO(fit_pdf_to_format(source, 210, 297))).pages[0]
        self.assertNotEqual(page.get_contents().get_data(), original)


class TableOfContentsPageNumbersTest(unittest.TestCase):
    def test_page_numbers_appear_in_toc_when_provided(self):
        project = Project(name="Test")
        article = Article(title="Chat", language="fr", url="https://fr.wikipedia.org/wiki/Chat", selected=True)
        html = build_toc_html(project, [article], article_pages={article.key: 5})
        self.assertIn('<span class="page-no">5</span>', html)

    def test_chapters_are_blocks_with_their_articles_below_and_every_line_is_a_link(self):
        from app.book_builder import TOC_LINK_PREFIX
        from app.models import BookChapter
        chat = Article(title="Chat", language="fr", url="https://fr.wikipedia.org/wiki/Chat", selected=True)
        chien = Article(title="Chien", language="fr", url="https://fr.wikipedia.org/wiki/Chien", selected=True)
        project = Project(name="Test", chapters=[BookChapter(title="Félins", article_keys=[chat.key])])
        html = build_toc_html(project, [chat, chien], {chat.key: 4, chien.key: 9}, [3, 8])
        self.assertIn(f'<li class="toc-chapter"><a class="toc-line" href="{TOC_LINK_PREFIX}chapter%3A0"><span class="toc-title">Félins</span><span class="page-no">3</span></a><ol>', html)
        self.assertIn(f'href="{TOC_LINK_PREFIX}fr%3Atitle%3Achat"><span class="toc-title">Chat</span><span class="page-no">4</span>', html)
        self.assertNotIn("nav li { display: flex", html)

    def test_no_page_number_markup_when_not_provided(self):
        project = Project(name="Test")
        article = Article(title="Chat", language="fr", url="https://fr.wikipedia.org/wiki/Chat", selected=True)
        html = build_toc_html(project, [article])
        self.assertNotIn('<span class="page-no">', html)


class LicensePageTest(unittest.TestCase):
    def test_license_page_names_cc_by_sa_and_lists_sources_in_book_order(self):
        from app.models import UploadedDocument
        first = Article(title="Chien", language="fr", url="https://fr.wikipedia.org/wiki/Chien", selected=True)
        second = Article(title="Chat", language="fr", url="https://fr.wikipedia.org/wiki/Chat", selected=True)
        document = UploadedDocument(title="Carte.png", kind="image", mime_type="image/png", data_base64="AA==", selected=True)
        project = Project(name="T", article_order=[first.key, second.key])
        html = build_license_page_html(project, [second, first, document])
        self.assertIn("CC BY-SA 4.0", html)
        self.assertIn("https://creativecommons.org/licenses/by-sa/4.0/deed.fr", html)
        self.assertLess(html.index("Chien"), html.index("Chat"))
        self.assertIn("https://fr.wikipedia.org/w/index.php?title=Chat&amp;action=history", html)
        self.assertIn("Carte.png", html)


class TranslatedTitlesTest(unittest.TestCase):
    def test_generated_pages_use_the_requested_language(self):
        from app.book_builder import build_chapter_page_html, build_cover_html
        article = Article(title="Chat", language="fr", url="https://fr.wikipedia.org/wiki/Chat", selected=True)
        project = Project(name="T", introduction="Bonjour")
        self.assertIn("Table of contents", build_toc_html(project, [article], language="en"))
        self.assertIn("<h2>Einleitung</h2>", build_cover_html(project, "de"))
        arabic = build_chapter_page_html(project, "Chapitre", "ar")
        self.assertIn('lang="ar" dir="rtl"', arabic)
        self.assertIn("الفصل", arabic)
        self.assertIn("الترخيص", build_license_page_html(project, [article], "ar"))

    def test_license_explanation_is_translated(self):
        article = Article(title="Hund", language="de", url="https://de.wikipedia.org/wiki/Hund", selected=True)
        html = build_license_page_html(Project(name="T"), [article], "de")
        self.assertIn("Namensnennung – Weitergabe unter gleichen Bedingungen 4.0 International (CC BY-SA 4.0)", html)
        self.assertIn("https://creativecommons.org/licenses/by-sa/4.0/deed.de", html)
        self.assertIn("keine offizielle Veröffentlichung", html)
        self.assertNotIn("Les textes", html)
        self.assertIn("deed.zh-hans", build_license_page_html(Project(name="T"), [article], "zh"))


if __name__ == "__main__":
    unittest.main()
