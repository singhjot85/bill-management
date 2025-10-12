from bma.requests.models import Bill
from rest_framework.serializers import ModelSerializer

class BillSerializer(ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'