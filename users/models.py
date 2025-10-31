from django.contrib.auth.models import User
from django.db import models
from core.models import BaseModel, SoftDeleteMixin


class UserProfile(BaseModel, SoftDeleteMixin):
    """Extends Django User with restaurant-specific info."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        groups = ', '.join(self.user.groups.values_list('name', flat=True))
        return f'{self.user.username} [{groups}]' if groups else self.user.username
