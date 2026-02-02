from __future__ import annotations

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def markdown_to_pdf(markdown: str) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    lines = markdown.splitlines()
    y = height - 40
    for line in lines:
        if line.strip() == "========================":
            pdf.showPage()
            y = height - 40
            continue
        if y < 40:
            pdf.showPage()
            y = height - 40
        pdf.drawString(40, y, line[:120])
        y -= 14

    pdf.save()
    return buffer.getvalue()
