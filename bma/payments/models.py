from bma.base.utils import generate_random_uuid, BaseModel

from django.db import models
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import cached_property


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
    FAILURE = "failure"
    CAPTURE = "capture"
    
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

    # For Tracking your order
    order_state = models.CharField(
        verbose_name="State of order", 
        default=ORDER_STATES_CHOICES[0],
        choices=ORDER_STATES_CHOICES, 
        null=False, 
        blank=False
    )
    payment_state = models.CharField(
        verbose_name="State of payment", 
        default=PAYMENT_STATES_CHOICES[0],
        choices=PAYMENT_STATES_CHOICES,
        null=False, 
        blank=False
    )

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
    order_id = models.CharField(verbose_name="External Order id", null=True, blank=True)
    responses = models.JSONField(verbose_name="Order API responses", blank=True, default=dict, encoder=DjangoJSONEncoder)
    details = models.JSONField(blank=True, default=dict, encoder=DjangoJSONEncoder)

    @cached_property
    def notes(self):
        return {
            "description": self.description,
            "date": str(self.created.date())
        }


class Payment(BaseModel):
    amount = models.DecimalField("Payment Amount", decimal_places=2, max_digits=13)

    requested_by = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE, 
        default=None, 
        null=True, 
        blank=True, 
        related_name='payments'
    )
    description = models.TextField(verbose_name="Comment")
    details = models.JSONField(blank=True, default=dict, encoder=DjangoJSONEncoder)

    def save(self):
        super().save()