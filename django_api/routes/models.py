from django.contrib.gis.db import models
from users.models import ServiceUser


class Route(models.Model):
    user = models.ForeignKey(ServiceUser, on_delete=models.CASCADE)
    date_and_time = models.DateTimeField(null=True)
    start_point = models.PointField()
    finish_point = models.PointField()

    class Meta:
        indexes = [
            models.Index(fields=['user', 'date_and_time', 'start_point']),
        ]
