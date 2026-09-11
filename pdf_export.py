from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf(itemized, sources, disclaimer="Planning estimate, not certified QS quote"):
    filename = "estimate_report.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, "BuildCost GH Estimate Report")
    y = 700
    for k, v in itemized.items():
        c.drawString(100, y, f"{k}: {v}")
        y -= 20
    c.drawString(100, y-20, f"Sources: {sources}")
    c.drawString(100, y-40, f"Disclaimer: {disclaimer}")
    c.save()
    return filename
