from rest_framework import serializers

from bma.payments.models import Order, Payment


class OrderSerializer(serializers.ModelSerializer):
    # response = serializers.SerializerMethodField(write_only=True)
    first_payment_min_amount = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "amount",
            "currency",
            "notes",
            "partial_payment",
            "first_payment_min_amount"
        ]
        read_only_fields = [
            "amount",
            "currency",
            "notes",
            "partial_payment",
            "first_payment_min_amount"
        ]
    
    def get_first_payment_min_amount(self, obj):
        # TODO
        return None
    
    def get_amount(self, obj):
        return int(obj.amount)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

