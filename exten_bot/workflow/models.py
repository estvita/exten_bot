# Create your models here.
from django.conf import settings
from django.db import models

class Mcp(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="mcp",
        help_text="User who owns this Mcp configuration"
    )
    base_url = models.URLField(
        default="http://localhost:8000",
        help_text="Base URL for the Mcp server"
    )
    api_key = models.CharField(
        max_length=255,
        help_text="API key for accessing the Mcp server",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.id} - {self.owner}"