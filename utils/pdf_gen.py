from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
import io

TEMPLATE_PATH = "templates/warranty_template.pdf"

def create_pdf(model, serial, price, warranty, output_path="garantiyny_talon.pdf"):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica", 12)  # стандартний шрифт

    can.drawString(165, 690, model)
    can.drawString(165, 650, serial)
    can.drawString(430, 690, str(price))  # Ціну без "грн"
    can.drawString(165, 670, datetime.now().strftime("%d.%m.%Y"))
    can.drawString(430, 670, warranty)  # Наприклад, "3"

    can.save()
    packet.seek(0)

    template_pdf = PdfReader(TEMPLATE_PATH)
    overlay_pdf = PdfReader(packet)
    output = PdfWriter()

    page = template_pdf.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    output.add_page(page)

    with open(output_path, "wb") as f:
        output.write(f)

    return output_path
