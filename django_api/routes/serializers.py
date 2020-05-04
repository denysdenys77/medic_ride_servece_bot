from rest_framework import serializers
from drf_extra_fields.geo_fields import PointField
from .models import Route
from users.serializers import ServiceUserSerializer


class RouteSerializer(serializers.ModelSerializer):
    user = serializers.CharField()
    start_point = PointField()
    finish_point = PointField()

    class Meta:
        model = Route
        fields = ['id', 'user', 'date_and_time', 'start_point', 'finish_point']


class GetSimilarRoutesSerializer(RouteSerializer):
    user = ServiceUserSerializer()
