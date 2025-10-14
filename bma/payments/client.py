from django.conf import settings
from razorpay import Client as rzpayClient

from bma.payments.models import Order
from bma.payments.serializers import OrderSerializer

api_key = settings.API_KEY
secrete = settings.API_SECRETE

class RazorPayClient:

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
        serializer = OrderSerializer(self.order)

        if serializer.is_valid:
            clean_data= serializer.data
        else:
            raise Exception("Error serialization your order")
        
        try:
            response = self.client.order.create(clean_data)
        except Exception as exc:
            response = str(exc)

        proc_response = self._save_response("create_order", response)
        if proc_response["is_success"]:
            self.order.order_id = proc_response["all_responses"].get("id", None)
            self.order.save(update_fields=["order_id"])
    
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