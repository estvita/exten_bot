from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def add_user_to_default_group(sender, instance, created, **kwargs):
    if created:
        group, create = Group.objects.get_or_create(name="users")
        if create:
            perms = Permission.objects.filter(
                codename__in=[
                    "add_bot",
                    "change_bot",
                    "view_bot",
                    "add_workflow",
                    "change_workflow",
                    "view_workflow",
                    "add_function",
                    "change_function",
                    "view_function",
                ]
            )
            group.permissions.set(perms)
        instance.groups.add(group)
        instance.is_staff = True
        instance.save()
