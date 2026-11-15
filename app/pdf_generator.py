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

import pikepdf
from pypdf import PageObject, PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from weasyprint import HTML


def generate_pdf(html_document: str) -> bytes:
    return HTML(string=html_document).write_pdf()


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
    image = ImageReader(BytesIO(image_bytes))
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


# NE PAS copier les pages dans un PdfWriter pypdf ni lire les fichiers en mémoire : qpdf (pikepdf) garde le contenu des pages dans les fichiers temporaires jusqu'à l'écriture, c'est ce qui permet les très gros livres sans manquer de mémoire.
class BookAssembly:
    def __init__(self) -> None:
        self.book = pikepdf.new()
        self.sources: list[pikepdf.Pdf] = []

    def append(self, path: Path) -> None:
        source = pikepdf.open(path)
        self.sources.append(source)
        self.book.pages.extend(source.pages)

    def add_outline(self, entries: list[OutlineEntry]) -> None:
        def item(entry: OutlineEntry) -> pikepdf.OutlineItem:
            node = pikepdf.OutlineItem(entry.title, entry.page)
            node.children.extend(item(child) for child in entry.children)
            return node

        with self.book.open_outline() as outline:
            outline.root.extend(item(entry) for entry in entries)

    def link_toc(
        self,
        first_page: int,
        page_count: int,
        prefix: str,
        links: list[tuple[int, list[float], str]],
        targets: dict[str, int],
    ) -> None:
        pages = self.book.pages
        for page in pages[first_page:first_page + page_count]:
            annotations = page.obj.get("/Annots")
            if annotations is None:
                continue
            kept = [
                annotation
                for annotation in annotations
                if not str((annotation.get("/A") or {}).get("/URI", "")).startswith(prefix)
            ]
            page.obj.Annots = pikepdf.Array(kept)
        for offset, rect, key in links:
            if key not in targets:
                continue
            page = pages[first_page + offset].obj
            annotation = self.book.make_indirect(pikepdf.Dictionary(
                Type=pikepdf.Name.Annot,
                Subtype=pikepdf.Name.Link,
                Rect=pikepdf.Array(rect),
                Border=pikepdf.Array([0, 0, 0]),
                Dest=pikepdf.Array([pages[targets[key]].obj, pikepdf.Name.Fit]),
            ))
            if "/Annots" not in page:
                page.Annots = pikepdf.Array()
            page.Annots.append(annotation)

    # NE PAS appeler avant d'avoir ajouté toutes les pages, toutes déjà passées par fit_pdf_to_format : chaque page doit avoir une origine (0,0) propre.
    def stamp_page_numbers(self) -> None:
        buffer = BytesIO()
        overlay = canvas.Canvas(buffer)
        for index, page in enumerate(self.book.pages):
            width, height = float(page.mediabox[2]), float(page.mediabox[3])
            overlay.setPageSize((width, height))
            overlay.setFont("Helvetica", 8)
            overlay.setFillColorRGB(0.33, 0.33, 0.33)
            overlay.drawCentredString(width / 2, 24, str(index + 1))
            overlay.showPage()
        overlay.save()
        numbers = pikepdf.open(BytesIO(buffer.getvalue()))
        self.sources.append(numbers)
        for index, page in enumerate(self.book.pages):
            if index == 0:
                continue
            page.add_overlay(numbers.pages[index])

    def save(self, path: Path) -> int:
        # NE PAS laisser les options par défaut : qpdf décompresserait puis recompresserait chaque flux (images comprises), ce qui multiplie le temps d'écriture pour un gain de taille faible.
        self.book.save(path, stream_decode_level=pikepdf.StreamDecodeLevel.none, compress_streams=False)
        return path.stat().st_size

    def close(self) -> None:
        self.book.close()
        for source in self.sources:
            source.close()
