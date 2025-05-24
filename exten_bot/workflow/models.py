# Create your models here.
from django.conf import settings
from django.db import models


class Dify(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dify"
    )
    base_url = models.URLField(default="https://api.dify.ai/v1")
    api_key = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.id} - {self.owner}"
