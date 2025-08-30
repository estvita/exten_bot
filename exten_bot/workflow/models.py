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


class Function(models.Model):
    name = models.CharField(max_length=255, default="my function", help_text="Name of the function")
    url = models.URLField(help_text="URL of the function")
    token = models.CharField(max_length=1000, help_text="Bearer Token of the url", blank=True, null=True)
    json_schema = models.JSONField(help_text="JSON schema of the function")
    input_schema = models.JSONField(help_text="Input schema of the function", blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.name}"