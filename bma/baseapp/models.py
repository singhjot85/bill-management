from bma.base.utils import phone_number_validator

from django.contrib.auth.models import User
from django.db import models

from model_utils.models import (
    UUIDModel, 
    TimeStampedModel, 
    SoftDeletableModel
)

class BaseModel(
    UUIDModel, 
    TimeStampedModel, 
    SoftDeletableModel
):
    class Meta:
        abstract = True

class BaseUserModel(TimeStampedModel, SoftDeletableModel):
    IND = "+91"
    NYRK = "+1"

    COUNTRY_CODE_CHOICES = (
        (IND, "India - (+91)"),
        (NYRK, "New York - (+1)"),
        (NYRK, "CANADA - (+1)"),
    )

    user = models.ForeignKey(verbose_name="Assossiated User", to=User, on_delete=models.PROTECT, null=False, blank=False)
    contact_country_code = models.CharField(verbose_name="Conatact Country Code", default=IND, choices=COUNTRY_CODE_CHOICES)
    contact = models.CharField(verbose_name="Contact Number", validators=[phone_number_validator], null=False, blank=False)
    
    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cleaned_contact = self.contact.replace("-", "").replace(" ", "").strip()
        self.contact = cleaned_contact