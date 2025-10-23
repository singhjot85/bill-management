import jq
import uuid
from io import BytesIO

from bma.base.constants import PAYMENTS_TYPE_CHOICE_TO_MODEL_MAP as payment_model_map

from django.apps import apps
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

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

def jq_transform_payload(input_payload: dict, jq_path: str):
    try:
        with open(jq_path, 'r') as f:
            jq_program = f.read()
        output_payload = jq.compile(jq_program).input(input_payload).first()
    except Exception as exc:
        return str(f"Error in jq tranformation [{str(exc)}]")

    return output_payload

def jq_transform_with_config(input_payload: dict, config: dict, jq_path: str):
    try:
        with open(jq_path, 'r') as f:
            jq_program = f.read()    
        output_payload = jq.compile(jq_program, config).input(input_payload).first()
    except Exception as exc:
        return str(f"Error in jq tranformation [{str(exc)}]")

    return output_payload

def get_contenttype_for_payment(payment_mode: str):
    """
    Give a payment mode choice and this will return 
    ContentType for that choice's corresponding model
    Args:
        payment_mode (str): Mode of payment from payment mode choices
    Returns:
        content_type : Content Type for that model
        Model : Model of the app
    """
    model_name = payment_model_map.get(payment_mode, None)
    if not model_name:
        raise Exception("Payment mode not supported yet.")
    Model = apps.get_model('payments', model_name)
    return ContentType.objects.get_for_model(Model), Model