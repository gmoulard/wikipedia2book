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

from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote

import pymupdf
from pypdf import PageObject, PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import weasyprint
from PIL import Image
from weasyprint import HTML

from app.models import SAFE_IMAGE_FORMATS

RENDER_PROTOCOLS = frozenset({"data"})


# NE PAS laisser WeasyPrint charger autre chose que des URI data: : une image de fond SVG (envoyée par l'utilisateur ou téléchargée) peut référencer file:///etc/passwd ou une adresse interne, que le rendu irait lire et imprimerait dans le livre.
def generate_pdf(html_document: str) -> bytes:
    return HTML(string=html_document, url_fetcher=weasyprint.URLFetcher(allowed_protocols=RENDER_PROTOCOLS)).write_pdf()


FORMAT_TOLERANCE_PT = 1.0


def fit_page_to_format(source_page, width_pt: float, height_pt: float) -> PageObject:
    # NE PAS déplacer ce test après transfer_rotation_to_content : cet appel réécrit tout le contenu de la page, c'est lui qui coûte cher.
    if (
        source_page.rotation % 360 == 0
        and abs(float(source_page.mediabox.width) - width_pt) <= FORMAT_TOLERANCE_PT
        and abs(float(source_page.mediabox.height) - height_pt) <= FORMAT_TOLERANCE_PT
        and float(source_page.mediabox.left) == 0
        and float(source_page.mediabox.bottom) == 0
    ):
        box = RectangleObject([0, 0, width_pt, height_pt])
        source_page.mediabox = box
        source_page.cropbox = box
        for name in ("/TrimBox", "/BleedBox", "/ArtBox"):
            if name in source_page:
                del source_page[name]
        return source_page
    # NE PAS corriger le DeprecationWarning pypdf de cette ligne : attendu avec pypdf<7 (voir CLAUDE.md).
    source_page.transfer_rotation_to_content()
    source_width = float(source_page.mediabox.width)
    source_height = float(source_page.mediabox.height)
    scale = min(width_pt / source_width, height_pt / source_height)
    tx = (width_pt - source_width * scale) / 2
    ty = (height_pt - source_height * scale) / 2
    transformation = Transformation().scale(scale, scale).translate(tx, ty)
    target = PageObject.create_blank_page(width=width_pt, height=height_pt)
    target.merge_transformed_page(source_page, transformation)
    return target


def fit_pdf_to_format(pdf_data: bytes, width_mm: float, height_mm: float) -> bytes:
    width_pt, height_pt = width_mm * mm, height_mm * mm
    reader = PdfReader(BytesIO(pdf_data))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(fit_page_to_format(page, width_pt, height_pt))
    buffer = BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return buffer.read()


def internal_links(pdf_data: bytes, prefix: str, width_mm: float, height_mm: float) -> list[tuple[int, list[float], str]]:
    width_pt, height_pt = width_mm * mm, height_mm * mm
    links: list[tuple[int, list[float], str]] = []
    for index, page in enumerate(PdfReader(BytesIO(pdf_data)).pages):
        source_width = float(page.mediabox.width)
        source_height = float(page.mediabox.height)
        scale = min(width_pt / source_width, height_pt / source_height)
        tx = (width_pt - source_width * scale) / 2
        ty = (height_pt - source_height * scale) / 2
        left, bottom = float(page.mediabox.left), float(page.mediabox.bottom)
        for reference in page.get("/Annots") or []:
            annotation = reference.get_object()
            uri = str((annotation.get("/A") or {}).get("/URI") or "")
            if annotation.get("/Subtype") != "/Link" or not uri.startswith(prefix):
                continue
            x1, y1, x2, y2 = (float(value) for value in annotation["/Rect"])
            rect = [tx + (x1 - left) * scale, ty + (y1 - bottom) * scale, tx + (x2 - left) * scale, ty + (y2 - bottom) * scale]
            links.append((index, rect, unquote(uri[len(prefix):])))
    return links


def image_to_pdf(image_bytes: bytes, page_width_mm: float, page_height_mm: float) -> bytes:
    width_pt, height_pt = page_width_mm * mm, page_height_mm * mm
    image = ImageReader(Image.open(BytesIO(image_bytes), formats=SAFE_IMAGE_FORMATS))
    image_width, image_height = image.getSize()
    scale = min(width_pt / image_width, height_pt / image_height)
    drawn_width, drawn_height = image_width * scale, image_height * scale

    buffer = BytesIO()
    pdf_canvas = canvas.Canvas(buffer, pagesize=(width_pt, height_pt))
    pdf_canvas.drawImage(
        image,
        (width_pt - drawn_width) / 2,
        (height_pt - drawn_height) / 2,
        width=drawn_width,
        height=drawn_height,
    )
    pdf_canvas.showPage()
    pdf_canvas.save()
    buffer.seek(0)
    return buffer.read()


@dataclass
class OutlineEntry:
    title: str
    page: int
    children: list["OutlineEntry"] = field(default_factory=list)


PAGE_NUMBER_SIZE = 8
PAGE_NUMBER_COLOR = (0.33, 0.33, 0.33)
MERGE_BATCH = 20


# NE PAS revenir à qpdf (pikepdf.Job --pages) ni à pdf.pages.extend : ils gardent en mémoire tous les objets de toutes les pages, environ 10 fois la taille du livre (938 Mo pour 100 articles, mesuré en local) ; PyMuPDF par lots de MERGE_BATCH parties, écrits en mise à jour incrémentale, tient en 130 Mo.
def merge_files(parts: list[Path], merged: Path) -> None:
    for start in range(0, len(parts), MERGE_BATCH):
        book = pymupdf.open(merged) if start else pymupdf.open()
        try:
            for path in parts[start:start + MERGE_BATCH]:
                with pymupdf.open(path) as part:
                    book.insert_pdf(part)
            if start:
                book.save(merged, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
            else:
                book.save(merged)
        finally:
            book.close()
    # NE PAS garder les fichiers des parties après la fusion : avec le fichier fusionné et le PDF final, l'espace temporaire monterait à trois fois la taille du livre, ce qui dépasse vite le quota d'espace temporaire d'un hébergeur.
    # NE PAS parcourir parts tel quel : une même partie peut y figurer plusieurs fois (deux titres de même clé d'article, « France Info » et « France info »), et sa seconde suppression échouerait.
    for path in dict.fromkeys(parts):
        path.unlink()


class BookAssembly:
    def __init__(self, merged: Path) -> None:
        self.book = pymupdf.open(merged)

    def add_outline(self, entries: list[OutlineEntry]) -> None:
        toc: list[list] = []

        def walk(entry: OutlineEntry, level: int) -> None:
            toc.append([level, entry.title, entry.page + 1])
            for child in entry.children:
                walk(child, level + 1)

        for entry in entries:
            walk(entry, 1)
        self.book.set_toc(toc)

    def link_toc(
        self,
        first_page: int,
        page_count: int,
        prefix: str,
        links: list[tuple[int, list[float], str]],
        targets: dict[str, int],
    ) -> None:
        for number in range(first_page, first_page + page_count):
            page = self.book[number]
            for link in page.get_links():
                if str(link.get("uri", "")).startswith(prefix):
                    page.delete_link(link)
        for offset, (x1, y1, x2, y2), key in links:
            if key not in targets:
                continue
            page = self.book[first_page + offset]
            height = page.rect.height
            page.insert_link({
                "kind": pymupdf.LINK_GOTO,
                "from": pymupdf.Rect(x1, height - y2, x2, height - y1),
                "page": targets[key],
                "to": pymupdf.Point(0, 0),
            })

    # NE PAS appeler avant d'avoir ajouté toutes les pages, toutes déjà passées par fit_pdf_to_format : chaque page doit avoir une origine (0,0) propre.
    # NE PAS revenir à une superposition de page (add_overlay, show_pdf_page) : elle réécrit le contenu de chaque page sans le compresser, ce qui faisait presque doubler la taille du livre (173 Mo au lieu de 96 pour 100 articles).
    def stamp_page_numbers(self, skip_last: bool = False) -> None:
        for index in range(1, self.book.page_count - (1 if skip_last else 0)):
            page = self.book[index]
            label = str(index + 1)
            width = pymupdf.get_text_length(label, fontname="helv", fontsize=PAGE_NUMBER_SIZE)
            page.insert_text(
                (page.rect.width / 2 - width / 2, page.rect.height - 24),
                label,
                fontname="helv",
                fontsize=PAGE_NUMBER_SIZE,
                color=PAGE_NUMBER_COLOR,
            )

    def save(self, path: Path) -> int:
        # NE PAS demander de compression ni de nettoyage (deflate, garbage, clean) : MuPDF décompresserait et réécrirait chaque flux, images comprises, ce qui multiplie le temps d'écriture et la mémoire pour un gain de taille faible.
        self.book.save(path)
        return path.stat().st_size

    def close(self) -> None:
        self.book.close()
