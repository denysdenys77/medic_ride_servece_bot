from rest_framework import serializers
from .models import ServiceUser


class ServiceUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceUser
        fields = ['id', 'telegram_id', 'type', 'first_name', 'last_name', 'phone_number']
