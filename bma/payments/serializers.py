from rest_framework.serializers import ModelSerializer

from bma.payments.models import Payment


class PaymentSerializer(ModelSerializer):


    class Meta:
        model = Payment
        fields = [
            "id",
            "amount",
            "description",
            "requested_by"
        ]

"""
payment = Payment.objects.first()
serializer = PaymentSerializer(payment)
serializer.data ={
        "id": ,
        "amount": ,
        "description": ,
        "requested_by": 56789-98765
    }
"""