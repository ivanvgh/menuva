from django.db import models
from django.utils.translation import gettext_lazy as _


class TableStatus(models.TextChoices):
    """Status options for a restaurant table."""
    FREE = 'FREE', _('Free')
    OCCUPIED = 'OCCUPIED', _('Occupied')
    NEEDS_HELP = 'NEEDS_HELP', _('Needs Help')

    @classmethod
    def color(cls, value: str) -> str:
        """Return a color name (used in admin/templates) for a given status."""
        return {
            cls.FREE: '#28a745',        # green
            cls.OCCUPIED: '#ffc107',    # amber/yellow
            cls.NEEDS_HELP: '#dc3545',  # red
        }.get(value, '#6c757d')  # fallback = gray


class SessionStatus(models.TextChoices):
    """Status options for a table session."""
    OPEN = 'OPEN', _('Open')
    CLOSED = 'CLOSED', _('Closed')

    @classmethod
    def color(cls, value: str) -> str:
        """Return a color name (used in admin/templates) for a given session status."""
        return {
            cls.OPEN: '#28a745',    # green
            cls.CLOSED: '#6c757d',  # gray
        }.get(value, '#000000')  # fallback = black
