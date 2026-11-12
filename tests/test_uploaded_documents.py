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

from PIL import Image
from pypdf import PdfReader

from app.book_builder import build_toc_html, ordered_article_groups
from app.models import Article, BookChapter, Project, UploadedDocument
from app.pdf_generator import image_to_pdf


def _make_png(width=300, height=200):
    buffer = BytesIO()
    Image.new("RGB", (width, height), color=(10, 20, 30)).save(buffer, format="PNG")
    return buffer.getvalue()


class ImageToPdfTest(unittest.TestCase):
    def test_produces_one_page_sized_to_the_book_format(self):
        pdf_bytes = image_to_pdf(_make_png(), page_width_mm=210, page_height_mm=297)
        reader = PdfReader(BytesIO(pdf_bytes))
        self.assertEqual(len(reader.pages), 1)
        page = reader.pages[0]
        # 210mm/297mm converted to points (1mm = 2.8346pt), with a tolerance for rounding.
        self.assertAlmostEqual(float(page.mediabox.width), 210 * 2.8346456693, delta=1)
        self.assertAlmostEqual(float(page.mediabox.height), 297 * 2.8346456693, delta=1)


class MixedBookItemsTest(unittest.TestCase):
    def test_grouping_and_toc_handle_articles_and_documents_together(self):
        project = Project(name="Test", chapters=[BookChapter(title="Chapitre A")])
        article = Article(title="Chat", language="fr", url="https://fr.wikipedia.org/wiki/Chat", selected=True)
        document = UploadedDocument(title="Photo.png", kind="image", mime_type="image/png", data_base64="QQ==")
        project.chapters[0].article_keys = [article.key, document.key]

        groups = ordered_article_groups(project, [article, document])
        self.assertEqual(groups, [("Chapitre A", [article, document])])

        html = build_toc_html(project, [article, document], article_pages={document.key: 7})
        self.assertIn("Photo.png", html)
        self.assertIn('<span class="page-no">7</span>', html)

    def test_unassigned_items_go_first_without_heading_when_requested(self):
        chat = Article(title="Chat", language="fr", url="https://fr.wikipedia.org/wiki/Chat", selected=True)
        loup = Article(title="Loup", language="fr", url="https://fr.wikipedia.org/wiki/Loup", selected=True)
        chapters = [BookChapter(title="Félidés", article_keys=[chat.key])]
        last = ordered_article_groups(Project(name="Test", chapters=chapters), [loup, chat])
        self.assertEqual(last, [("Félidés", [chat]), ("Sans chapitre", [loup])])
        first = ordered_article_groups(Project(name="Test", chapters=chapters, unassigned_first=True), [loup, chat])
        self.assertEqual(first, [("", [loup]), ("Félidés", [chat])])


if __name__ == "__main__":
    unittest.main()
