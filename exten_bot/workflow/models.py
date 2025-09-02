# Create your models here.
from django.conf import settings
from django.db import models

class Mcp(models.Model):
    APPROVAL_CHOICES = [
        ("never", "Never"),
        ("always", "Always"),
    ]
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="mcp",
        help_text="User who owns this Mcp configuration"
    )
    server_url = models.URLField(
        default="http://localhost:8000",
        help_text="Base URL for the Mcp server"
    )
    api_key = models.CharField(
        max_length=255,
        help_text="API key for accessing the Mcp server",
        blank=True,
        null=True
    )
    server_label = models.CharField(
        max_length=255, 
        help_text="Label of the server", 
        unique=True,
        blank=True
    )
    require_approval = models.CharField(max_length=255, choices=APPROVAL_CHOICES, default="never")

    def __str__(self):
        return f"{self.id} - {self.server_label}"

    def save(self, *args, **kwargs):
        if not self.server_label:
            # Генерируем уникальный label
            base_label = "mcp_server"
            counter = 1
            while True:
                new_label = f"{base_label}_{counter}"
                if not Mcp.objects.filter(server_label=new_label).exists():
                    self.server_label = new_label
                    break
                counter += 1
        super().save(*args, **kwargs)


class Function(models.Model):
    name = models.CharField(max_length=255, default="my function", help_text="Name of the function")
    url = models.URLField(help_text="URL of the function")
    token = models.CharField(max_length=1000, help_text="Bearer Token of the url", blank=True, null=True)
    json_schema = models.JSONField(help_text="JSON schema of the function")
    input_schema = models.JSONField(help_text="Input schema of the function", blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.name}"