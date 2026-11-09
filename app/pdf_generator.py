from io import BytesIO

from pypdf import PdfReader, PdfWriter
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from weasyprint import HTML


def generate_pdf(html_document: str) -> bytes:
    return HTML(string=html_document).write_pdf()


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
