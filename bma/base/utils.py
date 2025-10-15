import uuid
from io import BytesIO

from django.template.loader import render_to_string
from django.core.exceptions import ValidationError

from weasyprint import HTML

"""
brew install cairo pango gdk-pixbuf libffi
"""

def render_to_pdf(template: str, data: dict) -> BytesIO:
    """This method will be used to render PDF 
    from a given html template string and data.
    """

    complete_template = render_to_string(template, context={"invoice": data} )

    pdf_file = BytesIO()
    HTML(string=complete_template).write_pdf(pdf_file)

    return pdf_file

def generate_random_uuid():
    return uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid4()))

def phone_number_validator(number: str):
    cleaned_number = number.replace("-", "").replace(" ", "").strip()
    if len(cleaned_number) != 10:
        raise ValidationError("Phone number must have exactly 10 digits.")
    if not cleaned_number.isdigit():
        raise ValidationError("Phone number must contain only digits.")