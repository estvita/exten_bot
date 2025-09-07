from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Bot
from .tasks import manage_sip_user, manage_registrant


@receiver(post_delete, sender=Bot)
def delete_opensips_record(sender, instance, **kwargs):
    """Удаляем запись из OpenSIPS перед удалением бота"""
    if instance.type == "registrar":
        manage_sip_user(
            "delete", instance.username, instance.domain
        )
    elif instance.type == "registrant":
        manage_registrant(
            "delete", instance.username, instance.domain
        )