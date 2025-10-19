from django.conf import settings
from razorpay import Client as rzpayClient

from bma.payments.models import Order

api_key = settings.RAZORPAY_API_KEY
secrete = settings.RAZORPAY_API_SECRETE
"""
TODO: UPI intent flow(mobile installed upi app - also requires webhook implementation)
https://razorpay.com/docs/payments/payment-gateway/s2s-integration/payment-methods/upi/intent/
currently only UPI Collect Flow is implemented
https://razorpay.com/docs/payments/payment-gateway/s2s-integration/payment-methods/upi/collect/
"""

class RazorPayClient:

    def __init__(self, order: Order):
        self.client: rzpayClient = rzpayClient(auth=(api_key, secrete))
        self.order = order
        if not self.order:
            raise Exception("An order is required to make a request")