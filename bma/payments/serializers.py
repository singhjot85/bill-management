from rest_framework import serializers

from django.contrib.contenttypes.models import ContentType

from bma.payments.models import Order, Payment
from bma.core.serializers import BaseUserSerializer

class PaymentSerializer(serializers.ModelSerializer):
    requested_by = BaseUserSerializer()
    class Meta:
        model = Payment
        fields = [
            "id",
            "details",
            "payment_state",
            "requested_by",
            "payment_mode",
            "external_payment_id"
        ]

class OrderSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_state",
            "currency",
            "amount",
            "description",
            "exteranal_order_id",
            "external_reciept_number",
            "responses",
            "details",
            "payments"
        ]