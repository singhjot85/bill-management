from rest_framework import serializers

from bma.payments.models import (
    Order, 
    Payment,
    CardDetails,
)


class OrderAPISerializer(serializers.ModelSerializer):
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

class PaymentAPISerializer(serializers.ModelSerializer):
    OrderAPISerializer()

    class Meta:
        model = Payment
        read_only_fields = [
            "amount",
            "currency",
            "order_id",
            "email",
            "contact",
            "method",
            "description"
        ]
    
    # def to_representation(self, obj: BaseModel):
    #     data = super().to_representation(obj)
    #     payment: BasePaymentMode = BasePaymentMode.objects.get(
    #         content_type = ContentType.objects.get_for_model(obj.__class__),
    #         object_id = obj.id
    #     )
    #     if choice not in PaymentModeChoices:
    #         raise Exception(f"Payment Mode [{obj.method}] not supported.")
    #     for choice in PaymentModeChoices:
    #         if choice != obj.method:
    #             data.pop(choice, None)
    #     return data


class UPIPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = CardDetails
        read_only_fields = [
            "customer_id",
            "browser"
        ]
    



class CardPaymentSerializer(PaymentAPISerializer):

    class Meta:
        model = CardDetails
        read_only_fields = [
            "customer_id",
            "browser"
        ]

    authentication = serializers.SerializerMethodField()
    browser = serializers.SerializerMethodField()    

    def get_browser(self, obj):
        return {
            "java_enabled": False,
            "javascript_enabled": False,
            "timezone_offset": 11,
            "color_depth": 23,
            "screen_width": 23,
            "screen_height": 100
        }

    def get_authentication(self, obj):
        return {
            "authentication_channel": "browser"
        }

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

