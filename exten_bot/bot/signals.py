from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Bot
from .tasks import manage_sip_user


@receiver(post_delete, sender=Bot)
def bot_sip_post_delete(sender, instance, **kwargs):
    if instance.username and instance.domain:
        manage_sip_user.delay("delete", instance.username, instance.domain.domain)
