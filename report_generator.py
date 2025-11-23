# backend/report_generator.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import base64
from PIL import Image
import io

def generate_pdf_report(scan, out_path):
    c = canvas.Canvas(out_path, pagesize=letter)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 750, "Crop Disease Detection Report")

    c.setFont("Helvetica", 12)

    c.drawString(50, 720, f"Scan ID: {scan.id}")
    c.drawString(50, 700, f"Crop: {scan.crop}")
    c.drawString(50, 680, f"Disease: {scan.top_label}")
    c.drawString(50, 660, f"Confidence: {round(scan.confidence*100, 2)}%")
    c.drawString(50, 640, f"Treatment: {scan.treatment}")
    c.drawString(50, 620, f"Notes: {scan.notes}")
    c.drawString(50, 600, f"Location: {scan.geo}")

    # Decode stored base64 image
    img_data = base64.b64decode(scan.image_base64)
    img = Image.open(io.BytesIO(img_data))
    img = img.resize((250, 250))

    img_path = out_path.replace(".pdf", ".jpg")
    img.save(img_path)

    c.drawImage(img_path, 50, 330, width=250, height=250)

    c.save()
