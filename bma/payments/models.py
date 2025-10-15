from bma.base.utils import generate_random_uuid
from bma.base.constants import (
    PaymentModeChoices,
    CardNetworkChoices,
    CardlessEMIProviderChoices
)
from bma.baseapp.models import BaseModel, BaseUserModel

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import cached_property


def create_paymentmode(obj: BaseModel):
    """TODO: Make it a post_commit hook"""
    PaymentMode.objects.create(
        object_id = obj.id,
        content_type = ContentType.objects.get_for_model(obj.__class__)
    )


class Order(BaseModel):
    
    CREATED = "created"
    ATTEMPTED = "attempted"
    PAID = "paid"

    ORDER_STATES_CHOICES = (
        ("created", "Created"),
        ("attempted", "Attempted/ Under - processing"),
        ("paid", "Paid")
    )

    CREATED = "created"
    AUTHORIZED = "authorized"
    FAILURE = "failed"
    CAPTURE = "captured"
    
    PAYMENT_STATES_CHOICES = (
        ("created", "Created"),
        ("authorized", "Authorized"),
        ("failed", "Authorized but Failed"),
        ("captured", "Captured")
    )

    INR = "INR"
    USD = "USD"

    CURRENCY_CHOICES = (
        (INR, "Indian Rupee"),
        (USD, "US Dollar")
    )

    # Tracking your order
    order_state = models.CharField(
        verbose_name="State of order", 
        default=ORDER_STATES_CHOICES[0],
        choices=ORDER_STATES_CHOICES, 
        null=False, 
        blank=False
    )
    payment_state = models.CharField(verbose_name="State of payment", default=PAYMENT_STATES_CHOICES[0], choices=PAYMENT_STATES_CHOICES, null=False, blank=False)

    # Payload Data
    amount = models.DecimalField(verbose_name="Order Amount", decimal_places=2, max_digits=13)
    currency = models.CharField(verbose_name="Currency", default=INR, choices=CURRENCY_CHOICES)
    reciept_number = models.UUIDField(
        default= generate_random_uuid,
        editable=False,
        primary_key=False,
        unique=True
    )
    partial_payment = models.BooleanField(verbose_name="Is Partial Payment", default=False)
    description = models.CharField(verbose_name="Order Description", blank=True, null=True) 

    # Response data
    order_id = models.CharField(verbose_name="External Order id", null=True, blank=True, editable=False)
    responses = models.JSONField(verbose_name="Order API responses", blank=True, default=dict, encoder=DjangoJSONEncoder)
    details = models.JSONField(blank=True, default=dict, encoder=DjangoJSONEncoder)

    @cached_property
    def notes(self):
        return {
            "description": self.description,
            "date": str(self.created.date())
        }


class PaymentMode(BaseModel):
    content_type = models.ForeignKey(verbose_name="Content Type", to='contenttypes.ContentType', on_delete=models.CASCADE, null=True, blank=True, related_name="paymentmodes")
    object_id = models.UUIDField(verbose_name="Object Id", editable=False)
    payment_object = GenericForeignKey('content_type', 'object_id')


class Payment(BaseModel):

    requested_by = models.ForeignKey(verbose_name="Requested by", to=BaseUserModel, on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='payments')
    order = models.ForeignKey(verbose_name="Order", to='payments.Order', on_delete=models.CASCADE, null=False, related_name="payments")
    method = models.CharField(verbose_name="Payment method", default=PaymentModeChoices.UPI, choices=PaymentModeChoices)
    
    payment_mode = models.ForeignKey(verbose_name="Payment Mode", to=PaymentMode, on_delete=models.CASCADE, null=False, blank=False, related_name="payments")

    external_payment_id = models.CharField(verbose_name="External Payment Id", null=True, blank=True, editable=False,  max_length=15)
    details = models.JSONField(verbose_name="Details of Payment", blank=True, default=dict, encoder=DjangoJSONEncoder)

    def save(self):
        super().save()


class CardDetails(BaseModel):
    card_network = models.CharField(verbose_name="Card Network", choices=CardNetworkChoices)
    
    number = models.CharField(verbose_name="Card Number", null=False, blank=False)
    name = models.CharField(verbose_name="Card User Name", null=False, blank=False)
    
    expiry_month = models.CharField(verbose_name="Expiry Month", editable=False)
    expiry_year = models.CharField(verbose_name="Expiry Month", editable=False)
    cvv = models.IntegerField(verbose_name="CVV/CVC")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        create_paymentmode(self)

class InternetBankingDetails(BaseModel):
    bank = models.CharField(verbose_name="Internet Banking Provider", null=False, blank=False)
    
    details = models.JSONField(verbose_name="Internet Banking Details", default=dict, encoder=DjangoJSONEncoder)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        create_paymentmode(self)

class EMIDetails(BaseModel):
    emi_duration = models.IntegerField(verbose_name="EMI duration", null=False, blank=False)
    
    card = models.ForeignKey(verbose_name="EMI card", to='payments.CardDetails', on_delete=models.CASCADE, null=True, blank=True, related_name="emidetails")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        create_paymentmode(self)

class CardlessEMIDetails(BaseModel):
    bank = models.CharField(verbose_name="Cardless EMI Provider", null=False, blank=False, choices=CardlessEMIProviderChoices)

    details = models.JSONField(verbose_name="Internet Banking Details", default=dict, encoder=DjangoJSONEncoder)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        create_paymentmode(self)

class WalletDetails(BaseModel):
    bank = models.CharField(verbose_name="Wallet Provider", null=False, blank=False)

    details = models.JSONField(verbose_name="Wallet Details", default=dict, encoder=DjangoJSONEncoder)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        create_paymentmode(self)

class PayLaterDetails(BaseModel):
    provider = models.CharField(verbose_name="Pay Later Provider", null=False, blank=False)

    details = models.JSONField(verbose_name="Pay Later Details", default=dict, encoder=DjangoJSONEncoder)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        create_paymentmode(self)
