from weasyprint import HTML


def generate_pdf(html_document: str) -> bytes:
    return HTML(string=html_document).write_pdf()
