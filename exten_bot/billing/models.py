from django.db import models
from django.conf import settings

# Create your models here.
class Tariff(models.Model):
    trial = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10, default="USD")
    duration = models.PositiveIntegerField(blank=True, null=True)
    period = models.CharField(max_length=10, default="day")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.price} - {self.duration}"


class Trial(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trials")

    def __str__(self):
        return str(self.id)