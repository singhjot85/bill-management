from rest_framework import serializers

from bma.payments.models import Order, Payment, Customer
from bma.core.serializers import BaseUserSerializer
from bma.base.utils import get_contenttype_for_payment

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

class ExternalOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "currency",
            "amount",
            "description"   
        ]


class ExternalCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "name",
            "email",
            "country_code",
            "phone_number"
        ]


class ExternalPaymentSerializer(serializers.ModelSerializer):
    requested_by = ExternalCustomerSerializer()

    class Meta:
        model = Payment
        fields = [
            "payment_mode",
            "requested_by"
        ]

    # def validate(self, attrs):
    #     validated_data = super().validate(attrs)

    #     content_type, object_id = self._make_foreign_key(validated_data)

    #     self.instance : Payment
    #     self.instance.content_type = content_type
    #     self.instance.object_id = object_id
    #     self.instance.save(update_fields=["content_type", "object_id"])

    # def _make_foreign_key(self, validated_data):
    #     payment_mode = validated_data.pop("payment_mode", None)
    #     content_type, Model = get_contenttype_for_payment(payment_mode)
    #     object_id = Model.objects.create().id

    #     return content_type, object_id