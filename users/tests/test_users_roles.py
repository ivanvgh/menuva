import pytest
from django.contrib.auth.models import User, Group
from users.models import UserProfile
from users.permissions import user_has_role


@pytest.mark.django_db
def test_roles_seeded_by_migration():
    """Ensure roles exist after applying migration."""
    roles = ['guest', 'admin', 'waiter', 'kitchen', 'bartender', 'host']
    for name in roles:
        assert Group.objects.filter(name=name).exists()


@pytest.mark.django_db
def test_profile_created_and_guest_assigned():
    """Ensure new users get a profile and default guest role."""
    user = User.objects.create_user(username='john', password='1234')
    assert hasattr(user, 'profile')
    assert UserProfile.objects.filter(user=user).exists()
    assert user.groups.filter(name='guest').exists()
    assert user_has_role(user, 'guest')
