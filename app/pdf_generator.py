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

from io import BytesIO
from urllib.parse import unquote

from pypdf import PageObject, PdfReader, PdfWriter, Transformation
from pypdf.annotations import Link
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from weasyprint import HTML


def generate_pdf(html_document: str) -> bytes:
    return HTML(string=html_document).write_pdf()


def fit_page_to_format(source_page, width_pt: float, height_pt: float) -> PageObject:
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


def add_internal_links(
    writer: PdfWriter,
    first_page: int,
    page_count: int,
    prefix: str,
    links: list[tuple[int, list[float], str]],
    targets: dict[str, int],
) -> None:
    for page in writer.pages[first_page:first_page + page_count]:
        annotations = page.get("/Annots")
        if annotations is None:
            continue
        kept = [
            reference
            for reference in annotations
            if not str((reference.get_object().get("/A") or {}).get("/URI") or "").startswith(prefix)
        ]
        annotations.clear()
        annotations.extend(kept)
    for offset, rect, key in links:
        if key in targets:
            writer.add_annotation(first_page + offset, Link(rect=rect, target_page_index=targets[key]))


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


# NE PAS appeler avant fit_pdf_to_format : chaque page doit déjà avoir une origine (0,0) propre.
def stamp_page_numbers(writer: PdfWriter, skip_first: bool = True) -> None:
    for index, page in enumerate(writer.pages):
        if skip_first and index == 0:
            continue
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        buffer = BytesIO()
        overlay = canvas.Canvas(buffer, pagesize=(width, height))
        overlay.setFont("Helvetica", 8)
        overlay.setFillColorRGB(0.33, 0.33, 0.33)
        overlay.drawCentredString(width / 2, 24, str(index + 1))
        overlay.save()
        buffer.seek(0)
        page.merge_page(PdfReader(buffer).pages[0])
