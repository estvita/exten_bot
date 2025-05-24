import contextlib

from django.apps import AppConfig


class BotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "exten_bot.bot"

    def ready(self):
        with contextlib.suppress(ImportError):
            import exten_bot.bot.signals  # noqa: F401
