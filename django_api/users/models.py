from django.db import models

# Create your models here.


class ServiceUser(models.Model):
    telegram_id = models.IntegerField()
    type = models.CharField(max_length=10)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)

    class Meta:
        indexes = [models.Index(fields=['first_name'])]

    def __str__(self):
        return f'{self.first_name} {self.last_name} -- {self.type}'
