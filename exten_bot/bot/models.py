import secrets
import uuid
import os

from django.conf import settings
from django.db import models

from exten_bot.bot.tasks import manage_sip_user
from exten_bot.workflow.models import Dify


def function_default():
    return {
        "name": "get_time",
        "type": "function",
        "parameters": {
            "type": "object",
            "required": [],
            "properties": {},
        },
        "description": "If the user wants to know the time",
    }


# Create your models here.
PRIVACY = [
    ("private", "private"),
    ("public", "public"),
]


class Domain(models.Model):
    domain = models.CharField(max_length=255, default="exten.bot")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    privacy = models.CharField(max_length=50, choices=PRIVACY, default="public")

    def __str__(self):
        return self.domain


class Model(models.Model):
    name = models.CharField(max_length=255)
    max_completion_tokens = models.PositiveIntegerField(default=4096)

    def __str__(self):
        return self.name


class Function(models.Model):
    name = models.CharField(max_length=255, default="my function")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    description = models.JSONField(default=function_default)
    privacy = models.CharField(max_length=50, choices=PRIVACY, default="private")

    def __str__(self):
        return self.name


def generate_uuid():
    return uuid.uuid4().hex


class Voice(models.Model):
    voice = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.voice


class Bot(models.Model):
    username = models.CharField(max_length=32, default=generate_uuid)
    password = models.CharField(max_length=255, default=generate_uuid)
    expiration_date = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    token = models.CharField(max_length=500)
    domain = models.ForeignKey(
        "Domain", on_delete=models.SET_NULL, related_name="bots", null=True
    )
    model = models.ForeignKey(
        "Model", on_delete=models.SET_NULL, related_name="bots", null=True
    )
    voice = models.ForeignKey(
        "Voice", on_delete=models.SET_NULL, related_name="bots", null=True
    )
    dify = models.ForeignKey(
        Dify, on_delete=models.SET_NULL, related_name="bots", null=True, blank=True
    )
    instruction = models.TextField()
    welcome_msg = models.TextField(null=True, blank=True)
    transfer_uri = models.CharField(max_length=255, null=True, blank=True)
    functions = models.ManyToManyField(Function, related_name="bots", blank=True)
    temperature = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    max_tokens = models.PositiveIntegerField(default=4096)

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        if not self.password:
            self.password = secrets.token_urlsafe(25)

        if os.environ.get("DJANGO_SETTINGS_MODULE") == "config.settings.vendor":
            if self.owner and not self.owner.is_superuser:
                from exten_bot.billing.utils import get_date
                if not self.expiration_date:
                    self.expiration_date = get_date(self.owner)

        super().save(*args, **kwargs)

        if is_new:
            manage_sip_user.delay(
                "add", self.username, self.domain.domain, self.password
            )


    def __str__(self):
        return f"{self.username}: {self.id}"
