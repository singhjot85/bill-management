from io import BytesIO

from django.template.loader import render_to_string
from weasyprint import HTML

"""
brew install cairo pango gdk-pixbuf libffi
"""

def render_to_pdf(template: str, data: dict) -> BytesIO:
    """
    This method will be used to render PDF 
    from a given html template string and data.
    """

    complete_template = render_to_string(template, context={"invoice": data} )

    pdf_file = BytesIO()
    HTML(string=complete_template).write_pdf(pdf_file)

    return pdf_file