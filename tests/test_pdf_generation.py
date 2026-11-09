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

from app.book_builder import build_book_html
from app.models import Article, Project
from app.pdf_generator import stamp_page_numbers


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


class TableOfContentsPageNumbersTest(unittest.TestCase):
    def test_page_numbers_appear_in_toc_when_provided(self):
        project = Project(name="Test")
        article = Article(title="Chat", language="fr", url="https://fr.wikipedia.org/wiki/Chat", selected=True)
        html = build_book_html(project, [article], article_pages={article.key: 5})
        self.assertIn('<span class="page-no">5</span>', html)

    def test_no_page_number_markup_when_not_provided(self):
        project = Project(name="Test")
        article = Article(title="Chat", language="fr", url="https://fr.wikipedia.org/wiki/Chat", selected=True)
        html = build_book_html(project, [article])
        self.assertNotIn('<span class="page-no">', html)


if __name__ == "__main__":
    unittest.main()
