import os
import uuid
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings

def save_pdf(params:dict):
    try:
        template = get_template('pdfs/invoice.html')
        html = template.render(params)

        # Ensure HTML is valid before proceeding
        if not html.strip():
            print("Rendered HTML is empty!")
            return None, False

        file_name = f"{uuid.uuid4()}.pdf"
        file_path = os.path.join(settings.BASE_DIR, "public", "static", file_name)

        # Use a file instead of BytesIO for pisaDocument output
        with open(file_path, "wb+") as output:
            pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), output)

        if pdf.err:
            print("Error while generating PDF")
            return None, False

        return file_name, True

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None, False
