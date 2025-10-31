from django.db import migrations


def seed_default_roles(apps, schema_editor):
    """Seed the global default Groups (roles) once."""
    Group = apps.get_model('auth', 'Group')
    default_roles = ['guest', 'admin', 'waiter', 'kitchen', 'bartender', 'host']
    for name in default_roles:
        Group.objects.get_or_create(name=name)


def unseed_default_roles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(
        name__in=['guest', 'admin', 'waiter', 'kitchen', 'bartender', 'host']
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_default_roles, unseed_default_roles),
    ]
