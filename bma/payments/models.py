from bma.base.models import BaseModel
from bma.requests.models import Bill

from django.db import models
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder


class Order(BaseModel):
    ORDER_STATES_CHOICES = (
        ("created", "Created"),
        ("attempted", "Attempted/ Under - processing"),
        ("paid", "Paid")
    )
    
    PAYMENT_STATES_CHOICES = (
        ("created", "Created")
        ("authorized", "Authorized")
        ("failed", "Authorized but Failed")
        ("captured", "Captured")
    )

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
    order_id = models.CharField(verbose_name="External Order id", null=True, blank=True)
    responses = models.JSONField(verbose_name="Order API responses", blank=True, default=dict, encoder=DjangoJSONEncoder)
    details = models.JSONField(blank=True, default=dict, encoder=DjangoJSONEncoder)


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
    bill = models.ForeignKey(
        to=Bill, 
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