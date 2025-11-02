from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, DetailView

from table.models import Table, TableSession
from table.services import (
    open_session,
    close_session,
    request_assistance,
    resolve_assistance,
    active_session_for_table,
)
from table.enum import TableStatus, SessionStatus


# ============================================================
# STAFF VIEWS
# ============================================================

class TableGridView(ListView):
    """Main grid showing all tables for waiters/admins."""
    model = Table
    template_name = 'table/grid.html'
    context_object_name = 'tables'
    queryset = Table.objects.all().order_by('number')


class TableGridPartialView(TableGridView):
    """HTMX partial view to refresh the grid content."""
    template_name = 'table/partials/grid_partial.html'


class TableDetailView(DetailView):
    """Detail page for a specific table."""
    model = Table
    template_name = 'table/detail.html'
    context_object_name = 'table'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session'] = active_session_for_table(self.object)
        return context


# ============================================================
# ACTION VIEWS (POST)
# ============================================================

class OpenSessionView(View):
    """Start a new table session."""
    def post(self, request, pk):
        try:
            open_session(pk, request.user)
            messages.success(request, _('Session opened successfully.'))
        except Exception as e:
            messages.error(request, str(e))
        return redirect('table:table-detail', pk=pk)


class CloseSessionView(View):
    """Close an open session."""
    def post(self, request, pk):
        session = active_session_for_table(get_object_or_404(Table, pk=pk))
        if not session:
            messages.warning(request, _('No active session found.'))
            return redirect('table:table-detail', pk=pk)
        try:
            close_session(session.id, request.user)
            messages.success(request, _('Session closed successfully.'))
        except Exception as e:
            messages.error(request, str(e))
        return redirect('table:table-detail', pk=pk)


class AssistanceRequestView(View):
    """Mark a table session as needing help."""
    def post(self, request, pk):
        session = active_session_for_table(get_object_or_404(Table, pk=pk))
        if session:
            request_assistance(session.id)
            messages.info(request, _('Assistance requested.'))
        else:
            messages.warning(request, _('No active session found.'))
        return redirect('table:table-detail', pk=pk)


class AssistanceResolveView(View):
    """Resolve assistance request for a table session."""
    def post(self, request, pk):
        session = active_session_for_table(get_object_or_404(Table, pk=pk))
        if session:
            resolve_assistance(session.id)
            messages.success(request, _('Assistance resolved.'))
        else:
            messages.warning(request, _('No active session found.'))
        return redirect('table:table-detail', pk=pk)


# ============================================================
# GUEST QR VIEWS
# ============================================================

class GuestQRResolverView(View):
    """Resolve a QR URL and redirect the guest accordingly."""
    def get(self, request, qr_uuid):
        table = get_object_or_404(Table, qr_uuid=qr_uuid)
        session = active_session_for_table(table)

        if not session:
            return render(request, 'guest/ask_waiter.html', {'table': table})

        return render(request, 'guest/guest_info.html', {"table": table, "session": session})


class GuestSessionView(DetailView):
    """Guest view for an active session (simple placeholder)."""
    model = TableSession
    template_name = 'table/guest/session.html'
    pk_url_kwarg = 'session_id'
    context_object_name = 'session'

    def get_queryset(self):
        return TableSession.objects.select_related('table', 'opened_by')
