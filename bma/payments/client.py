import uuid
from django.conf import settings
from razorpay import Client as rzpayClient

from bma.payments.models import Order

api_key = settings.API_KEY
secrete = settings.API_SECRETE

class RazorPayClient:

    def __init__(self, order: Order, create_order: bool = False):
        self.client: rzpayClient = rzpayClient(auth=(self.api_key, self.secrete))
        self.client.enable_retry(True)
        if order:
            self.order = order
        elif create_order:
            self.order = Order.objects.create()
        else:
            raise Exception("Order is required for a payment")
        
    
    def create_order(self, *args, **kwargs):

        kwargs.get("amount", 0)
        kwargs.get("description", {})


    
    
    def _get_create_order_payload(
        self,
        reciept_number: uuid,
        amount: float = None,
        currency: str = "INR",
        description: dict = {},
        partial_payment: bool = False,
        first_payment_min_amount: float = None
    ):
        """
            "amount": 50000,
            "currency": "INR",
            "receipt": "receipt#1",
            "notes": {
                "key1": "value3",
                "key2": "value2"
            }
            "partial_payment": False,
            "first_payment_min_amount": None
        """
        return {
            "amount": amount, # User
            "currency": currency, # Default
            "receipt": reciept_number, # Random
            "notes": description, # User
            "partial_payment": partial_payment,
            "first_payment_min_amount": first_payment_min_amount
        }