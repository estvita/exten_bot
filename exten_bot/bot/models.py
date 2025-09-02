import secrets
import uuid
import os

from django.conf import settings
from django.db import models

from exten_bot.bot.tasks import manage_sip_user, manage_registrant
from exten_bot.workflow.models import Function, Mcp


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

BOT_TYPES = [
    ("registrant", "registrant"),
    ("registrar", "registrar"),
]


class Model(models.Model):
    name = models.CharField(max_length=255)
    max_completion_tokens = models.PositiveIntegerField(default=4096)

    def __str__(self):
        return self.name


def generate_uuid():
    return uuid.uuid4().hex


class Voice(models.Model):
    voice = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.voice


class Bot(models.Model):
    username = models.CharField(
        max_length=32,
        default=generate_uuid,
        help_text="Bot's username"
    )
    password = models.CharField(
        max_length=255,
        default=generate_uuid,
        help_text="Bot's password"
    )
    expiration_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Expiration date for the bot"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Owner of the bot"
    )
    type = models.CharField(
        max_length=50,
        choices=BOT_TYPES,
        default="registrar",
        help_text="Type of bot"
    )
    token = models.CharField(
        max_length=500,
        help_text="OpenAI token"
    )
    domain = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default="exten.bot",
        help_text="SIP Server associated with the bot"
    )
    model = models.ForeignKey(
        "Model",
        on_delete=models.SET_NULL,
        related_name="bots",
        null=True,
        help_text="Model used by the bot"
    )
    voice = models.ForeignKey(
        "Voice",
        on_delete=models.SET_NULL,
        related_name="bots",
        null=True,
        help_text="Voice configuration for the bot"
    )

    instruction = models.TextField(
        help_text="Instructions for the bot"
    )
    welcome_msg = models.TextField(
        null=True,
        blank=True,
        help_text="The message that the bot will say upon connecting."
    )
    transfer_uri = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="URI to transfer the conversation (optional)"
    )
    temperature = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.0,
        help_text="Sampling temperature (0.0-1.0)"
    )
    max_tokens = models.PositiveIntegerField(
        default=4096,
        help_text="Maximum number of tokens"
    )
    functions = models.ManyToManyField(
        Function,
        related_name="bots",
        blank=True,
        help_text="Functions available to this bot"
    )
    mcp_servers = models.ManyToManyField(
        Mcp,
        related_name="bot_servers",
        blank=True,
        help_text="MCP servers available to this bot"
    )

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
            if self.type == "registrar":
                manage_sip_user.delay(
                    "add", self.username, self.domain, self.password
                )
            elif self.type == "registrant":
                manage_registrant.delay(
                    "add", self.username, self.domain, self.password
                )


    def __str__(self):
        return f"{self.username}: {self.id}"