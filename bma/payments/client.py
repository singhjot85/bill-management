from django.conf import settings
from razorpay import Client as rzpayClient

from bma.payments.models import Order
from bma.payments.serializers import OrderAPISerializer, PaymentAPISerializer
from bma.base.constants import PaymentModeChoices

api_key = settings.API_KEY
secrete = settings.API_SECRETE
"""
TODO: UPI intent flow(mobile installed upi app - also requires webhook implementation)
https://razorpay.com/docs/payments/payment-gateway/s2s-integration/payment-methods/upi/intent/
currently only UPI Collect Flow is implemented
https://razorpay.com/docs/payments/payment-gateway/s2s-integration/payment-methods/upi/collect/
"""

class RazorPayClient:

    SUPPORTED_PAYMENT_METHODS=[
        "upi"
    ]

    def __init__(
        self, order: Order, create_order: bool = False, *args, **kwargs
    ):
        self.client: rzpayClient = rzpayClient(auth=(api_key, secrete))
        self.client.enable_retry(True)

        if order:
            self.order = order
        
        if create_order:
            self.order = Order.objects.create(
                order_amount = kwargs.pop("amount", 0),
                description = kwargs.get("description", "")
            )
        
        if not self.order:
            raise Exception("Order is required for a payment")
    
    def create_order(self):
        serializer = OrderAPISerializer(self.order)

        if serializer.is_valid:
            clean_data= serializer.data
        else:
            raise Exception("Error serialization your order")
        
        try:
            response = self.client.order.create(clean_data)
        except Exception as exc:
            response = str(exc)

        proccess_response = self._save_response("create_order", response)
        if proccess_response["is_success"]:
            self.order.order_id = proccess_response["all_responses"].get("id", None)
            self.order.save(update_fields=["order_id"])

        return proccess_response

    def create_payment_json(self, payment_mode: str, *args, **kwargs):
        """Create Payments API
        """
        if payment_mode not in self.SUPPORTED_PAYMENT_METHODS:
            raise Exception("Payment method not supported")
        
        if payment_mode == PaymentModeChoices.UPI:
            self.intiate_upi_payment_flow(*args, **kwargs)

        
    def intiate_upi_payment_flow(self, *args, **kwargs):
        serializer = PaymentAPISerializer()
        
        clean_data["browser"] = self._default_browser_data()
        try:
            response = self.client.payment.createPaymentJson(clean_data)
        except Exception as exc:
            response = str(exc)
        
        proccess_response = self._save_response("create_payment_json", response)
        

    def _save_response(self, key: str, response: dict | str):
        if isinstance(response, dict):
            all_responses = self.order.responses
            all_responses[key] = response
            self.order.save(update_fields=["responses"])
            return {
                "is_success": True,
                "all_responses": all_responses,
            }
        if isinstance(response, str):
            return {
                "is_success": False,
                "errors": response
            }


"""
    client.order.create({
    'amount':50000,
    'currency': 'INR',
    'receipt': 'rcptid_11',
    'payment': {
        'capture': 'automatic',
        'capture_options': {
        'automatic_expiry_period': 12,
        'manual_expiry_period': 7200,
        'refund_speed': 'optimum'
        }  
    }
    })
AUTOMATIC = "automatic"
MANUAL = "manual"
capture = 
manual_expiry_period =  
refund_speed = 
"""    
