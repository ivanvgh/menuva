from uuid import uuid4
from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Table, TableSession
from .enum import TableStatus, SessionStatus
from .services import generate_qr_zip_response


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    """Admin configuration for restaurant tables."""

    list_display = ('id', 'number', 'qr_uuid', 'status_colored', 'qr_url')
    list_filter = ('status',)
    search_fields = ('number', 'qr_uuid')
    readonly_fields = ('qr_uuid',)
    actions = ['regenerate_qr_uuid', 'download_qr_images']

    def changelist_view(self, request, extra_context=None):
        self._request = request  # Store the request object
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description=_('QR URL'))
    def qr_url(self, obj):
        try:
            # This is the line that will fail without the request object
            full_url = obj.get_qr_url(self._request)
            return format_html('<a href="{}">{}</a>', full_url, obj.qr_uuid)
        except AttributeError:
            # Fallback if _request is not available (e.g., in a background job context)
            return format_html('<span>(URL requires Request Context)</span>')

    @admin.display(description=_('Status'))
    def status_colored(self, obj):
        """Display status text with color based on TableStatus enum."""
        color = TableStatus.color(obj.status)
        label = obj.get_status_display()
        return format_html(f'<strong style="color:{color}">{label}</strong>')

    @admin.action(description=_('Regenerate QR UUID'))
    def regenerate_qr_uuid(self, request, queryset):
        """Generate a new QR UUID for each selected table."""
        for table in queryset:
            if table.status != TableStatus.FREE:
                messages.error(
                    request,
                    _(f'Table {table.number} is not free. Cannot regenerate QR UUID.'),
                )
                continue
            table.qr_uuid = uuid4()
            table.save(update_fields=['qr_uuid'])
            messages.success(request, _(f'QR UUID for Table {table.number} regenerated successfully.'))

    @admin.action(description=_("Generate and download QR images for selected tables"))
    def download_qr_images(self, request, queryset):
        return generate_qr_zip_response(queryset, request)


@admin.register(TableSession)
class TableSessionAdmin(admin.ModelAdmin):
    """Admin configuration for table sessions."""

    list_display = (
        'table',
        'opened_by',
        'status_colored',
        'assistance_requested',
        'opened_at',
        'closed_at',
    )
    list_filter = ('status', 'assistance_requested')
    search_fields = ('table__number', 'opened_by__username')
    readonly_fields = ('opened_at', 'closed_at')
    actions = ['close_selected_sessions']

    @admin.display(description=_('Status'))
    def status_colored(self, obj):
        """Display colored session status using SessionStatus enum."""
        color = SessionStatus.color(obj.status)
        label = obj.get_status_display()
        return format_html(f'<strong style="color:{color}">{label}</strong>')

    @admin.action(description=_('Close selected sessions'))
    def close_selected_sessions(self, request, queryset):
        """Close all selected open sessions."""
        updated = queryset.filter(status=SessionStatus.OPEN).update(
            status=SessionStatus.CLOSED
        )
        messages.success(
            request,
            _(f'{updated} session(s) closed successfully.'),
        )
