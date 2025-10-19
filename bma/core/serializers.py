from rest_framework import serializers

from bma.core.models import BaseUserModel

class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseUserModel
        fields = [
            "id",
            "username",
            "email",
            "country_code",
            "phonenumber"
        ]