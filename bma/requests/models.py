import uuid

from bma.base.models import BaseModel
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

def generate_bill_number():
    return uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid4()))

class Bill(BaseModel):

    CATEGORY_CHOICES = (
        ("1", "Category 1"),
        ("2", "Category 2")
    )
    number = models.UUIDField(
        default= generate_bill_number,
        editable=False,
        primary_key=False,
        unique=True
    )

    name = models.CharField("Bill Name", blank=True)
    category = models.CharField("Category", max_length=255, default=CATEGORY_CHOICES[0], choices=CATEGORY_CHOICES)
    amount = models.DecimalField("Bill Amount", decimal_places=2, max_digits=13)
    description = models.TextField("Bill Description", null=True, blank=True)
    razorpay_id = models.CharField("Payment Id", default=None, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'
    
    def __repr__(self):
        return f'Bill<{self.id}>'
    
    class Meta:
        verbose_name = "Bill"
        verbose_name_plural = "Bills"

def upload_file_path():
    return r'media/invoices'

class Document(BaseModel):
    name = models.CharField("Document Name", blank=True)
    template_used = models.TextField("Template used to render", null=True, blank=True)
    file = models.FileField('Document', upload_to=upload_file_path, max_length=255)
    details = models.JSONField("Details of Document", default=dict, encoder=DjangoJSONEncoder)

    def __str__(self):
        return f"{self.file.name}"