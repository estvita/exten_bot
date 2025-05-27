# Create your models here.
from django.conf import settings
from django.db import models


class Dify(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="dify",
        help_text="User who owns this Dify configuration"
    )
    base_url = models.URLField(
        default="https://api.dify.ai/v1",
        help_text="Base URL for the Dify API"
    )
    api_key = models.CharField(
        max_length=255,
        help_text="API key for accessing the Dify WorkFlow API"
    )

    def __str__(self):
        return f"{self.id} - {self.owner}"
