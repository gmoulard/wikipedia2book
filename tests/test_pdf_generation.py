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


class TableOfContentsPageNumbersTest(unittest.TestCase):
    def test_page_numbers_appear_in_toc_when_provided(self):
        project = Project(name="Test")
        article = Article(title="Chat", language="fr", url="https://fr.wikipedia.org/wiki/Chat", selected=True)
        html = build_toc_html(project, [article], article_pages={article.key: 5})
        self.assertIn('<span class="page-no">5</span>', html)

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


if __name__ == "__main__":
    unittest.main()
