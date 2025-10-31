from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver

from users.models import UserProfile

DEFAULT_ROLE_FOR_NEW_USERS = 'guest'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Ensure a profile exists and assign the default role group."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
        try:
            guest_group = Group.objects.get(name=DEFAULT_ROLE_FOR_NEW_USERS)
            instance.groups.add(guest_group)
        except Group.DoesNotExist:
            # roles not yet seeded (e.g. during initial migration)
            pass
