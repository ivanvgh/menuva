import uuid
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel, SoftDeleteMixin
from table.enum import TableStatus, SessionStatus


class Table(BaseModel, SoftDeleteMixin):
    """Represents a physical table in the restaurant."""

    number = models.CharField(_('number'), max_length=10)
    qr_uuid = models.UUIDField(_('QR UUID'), default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=TableStatus.choices,
        default=TableStatus.FREE,
    )

    class Meta:
        verbose_name = _('Table')
        verbose_name_plural = _('Tables')

    def __str__(self):
        return f'{_("Table")} {self.number}'

    @property
    def get_absolute_url_path(self):
        """Returns the URL path component (e.g., /table/a1b2c3d4/)."""
        # It's best practice to use reverse() here if your URL is defined by name
        # If your URL is simple, using f-string is also fine.
        return reverse('table:guest-qr-resolver', args=[str(self.qr_uuid)])

    def get_qr_url(self, request):
        """Constructs the full URL using the request object."""
        # This uses the request object to get the scheme ('http' or 'https') and host
        base_url = request.build_absolute_uri('/')[:-1]  # Gets 'https://www.menuva.com'

        # Now combine the base URL with the path
        return f'{base_url}{self.get_absolute_url_path}'

    @property
    def get_status_color(self):
        return TableStatus.color(self.status)


class TableSession(BaseModel):
    """Represents a customer session at a specific table."""

    id = models.UUIDField(_('ID'), primary_key=True, default=uuid.uuid4, editable=False)
    table = models.ForeignKey(
        Table,
        verbose_name=_('table'),
        related_name='sessions',
        on_delete=models.PROTECT,
    )
    opened_by = models.ForeignKey(
        User,
        verbose_name=_('opened by'),
        related_name='opened_sessions',
        on_delete=models.PROTECT,
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.OPEN,
    )
    opened_at = models.DateTimeField(_('opened at'), auto_now_add=True)
    closed_at = models.DateTimeField(_('closed at'), null=True, blank=True)
    assistance_requested = models.BooleanField(_('assistance requested'), default=False)

    class Meta:
        db_table = 'table_session'
        verbose_name = _('Table Session')
        verbose_name_plural = _('Table Sessions')
        constraints = [
            models.UniqueConstraint(
                fields=['table'],
                condition=models.Q(status=SessionStatus.OPEN),
                name='unique_open_session_per_table',
            )
        ]

    def clean(self):
        """Ensure only one OPEN session per table."""
        if (
            self.status == SessionStatus.OPEN
            and TableSession.objects.filter(table=self.table, status=SessionStatus.OPEN)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(_('Only one open session is allowed per table.'))

    def __str__(self):
        return f'{_("Session")} {self.id} — {_("Table")} {self.table.number}'
