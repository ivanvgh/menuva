from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from table.enum import SessionStatus
from table.models import TableSession, Table
from menu.models import MenuItem, MenuVersion
from table.services import active_session_for_table
from .models import GuestProfile, Order, OrderItem
from .services import create_order, update_order_status, create_review, list_guest_orders, \
    send_chat_message, request_assistance
from .enums import OrderStatus


# Add this helper mixin near the top of views.py
class GuestBaseMixin:
    """Provides shared guest context."""
    active_tab = None

    def get_context_data(self, **kwargs):
        ctx = {"active_tab": self.active_tab}
        ctx.update(kwargs)
        return ctx


class GuestEntryView(View):
    """Handles QR entry flow for guests."""

    def post(self, request, table_qr_uuid):
        """Form submission: register guest and redirect to guest menu."""
        table = get_object_or_404(Table, qr_uuid=table_qr_uuid)
        session = active_session_for_table(table)
        if not session:
            return render(request, 'guest/ask_waiter.html',
                          {"table": table, "error": _("Session is not open yet.")})

        name = request.POST.get("name")
        dni = request.POST.get("dni")
        ip = request.META.get("REMOTE_ADDR")

        guest = GuestProfile.objects.create(
            session=session, name=name, dni=dni, ip_address=ip
        )
        request.session["guest_token"] = str(guest.guest_token)

        return redirect("orders:guest-menu", session_id=session.id)


class GuestMenuView(GuestBaseMixin, View):
    active_tab = "menu"
    template_name = "guest/menu.html"

    def get(self, request, session_id):
        session = get_object_or_404(TableSession, id=session_id)
        guest_token = request.session.get("guest_token")
        if not guest_token:
            return redirect("orders:guest-entry", table_qr_uuid=session.table.qr_uuid)

        guest = GuestProfile.objects.filter(session=session, guest_token=guest_token).first()
        menu_version = MenuVersion.objects.prefetch_related(
            "categories__menu_items__item"
        ).filter(is_active=True).first()

        return render(
            request,
            self.template_name,
            self.get_context_data(session=session, guest=guest, menu_version=menu_version),
        )

    def post(self, request, session_id):
        session = get_object_or_404(TableSession, id=session_id)
        name = request.POST.get("name")
        dni = request.POST.get("dni")
        ip = request.META.get("REMOTE_ADDR")
        guest = GuestProfile.objects.create(session=session, name=name, dni=dni, ip_address=ip)
        request.session["guest_token"] = str(guest.guest_token)
        return redirect("orders:guest-menu", session_id=session.id)


class GuestOrderSubmitView(View):
    def post(self, request, session_id):
        session = get_object_or_404(TableSession, id=session_id)
        guest_token = request.session.get("guest_token")
        guest = get_object_or_404(GuestProfile, guest_token=guest_token, session=session)
        items_data = []
        for key, value in request.POST.items():
            if key.startswith("qty_") and int(value) > 0:
                menu_item = get_object_or_404(MenuItem, id=key.split("_")[1])
                unit_price = menu_item.custom_price or menu_item.item.base_unit_price
                items_data.append(
                    {"menu_item": menu_item, "quantity": int(value), "unit_price": unit_price})

        create_order(session.id, guest, items_data)
        return redirect('orders:guest-orders', session_id=session.id)


class OrderListView(View):
    def get(self, request):
        orders = Order.objects.select_related("session__table").all().order_by("-created_at")
        return render(request, "orders/list.html", {"orders": orders})


class OrderDetailView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        grouped = {}
        for item in order.items.select_related("guest", "menu_item"):
            grouped.setdefault(item.guest.name, []).append(item)
        return render(request, "orders/detail.html", {"order": order, "grouped_items": grouped})


class KitchenDashboardView(View):
    template_name = "kitchen/dashboard.html"

    def get(self, request):
        grouped_orders = self.get_grouped_orders()
        return render(request, self.template_name, {"grouped_orders": grouped_orders})

    def get_grouped_orders(self):
        grouped = {}
        for status in [OrderStatus.QUEUED, OrderStatus.PREPARING, OrderStatus.READY]:
            grouped[status] = Order.objects.filter(status=status).select_related("session__table")
        return grouped


class KitchenDashboardPartialView(KitchenDashboardView):
    template_name = "kitchen/partials/orders_list.html"

    def get(self, request):
        html = render_to_string(self.template_name, {"grouped_orders": self.get_grouped_orders()})
        return HttpResponse(html)


class OrderStatusUpdateView(View):
    def post(self, request, order_id):
        new_status = request.POST.get("status")
        update_order_status(order_id, new_status)
        return HttpResponse(_("Status updated successfully."))


# =====================================================
# 🚨 SOS (Call Waiter)
# =====================================================

@method_decorator(csrf_exempt, name="dispatch")
class GuestSOSView(View):
    """Triggered by floating red SOS button."""

    def post(self, request, session_id):
        session = get_object_or_404(TableSession, id=session_id)
        request_assistance(session.id)
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "ok", "message": _("Waiter called successfully.")})
        return redirect("orders:guest-menu", session_id=session.id)


# =====================================================
# 💬 Chat with Waiter (Fake API)
# =====================================================

class GuestChatView(GuestBaseMixin, View):
    active_tab = "chat"
    template_name = "guest/chat.html"

    def get(self, request, session_id):
        session = get_object_or_404(TableSession, id=session_id)
        guest_token = request.session.get("guest_token")
        guest = get_object_or_404(GuestProfile, guest_token=guest_token, session=session)

        return render(
            request,
            self.template_name,
            self.get_context_data(session=session, guest=guest, messages=guest.chat_history),
        )

    @method_decorator(csrf_exempt)
    def post(self, request, session_id):
        session = get_object_or_404(TableSession, id=session_id)
        guest_token = request.session.get("guest_token")
        guest = get_object_or_404(GuestProfile, guest_token=guest_token, session=session)
        text = request.POST.get("message", "").strip()

        if not text:
            return HttpResponse("", status=204)

        msg = guest.append_message(sender="guest", text=text)
        html = render_to_string("guest/partials/chat_message.html", {"m": msg})
        return HttpResponse(html)


class GuestChatMessagesView(GuestBaseMixin, View):
    """Partial HTML refresh for chat messages"""
    def get(self, request, session_id):
        session = get_object_or_404(TableSession, id=session_id)
        guest_token = request.session.get("guest_token")
        guest = get_object_or_404(GuestProfile, guest_token=guest_token, session=session)
        messages = guest.chat_history
        html = render_to_string("guest/_chat_messages.html", {"messages": messages})
        return HttpResponse(html)

# =====================================================
# 📦 Guest Orders View
# =====================================================

class GuestOrdersView(GuestBaseMixin, View):
    active_tab = "orders"

    def get(self, request, session_id):
        session = get_object_or_404(TableSession, id=session_id)
        items = (
            OrderItem.objects
            .filter(order__session_id=session_id)
            .select_related("guest", "menu_item")
        )

        guest_summaries = {}
        for item in items:
            guest_name = item.guest.name if item.guest else "Unknown Guest"
            guest_summaries.setdefault(guest_name, {"items": [], "total": 0})
            guest_summaries[guest_name]["items"].append(item)
            guest_summaries[guest_name]["total"] += item.subtotal

        total_all = sum(summary["total"] for summary in guest_summaries.values())

        return render(
            request,
            "guest/orders.html",
            self.get_context_data(
                guest_summaries=guest_summaries,
                session=session,
                table_total=total_all,
            ),
        )


# =====================================================
# ⭐ Guest Review View
# =====================================================

class GuestReviewView(GuestBaseMixin, View):
    active_tab = "review"
    template_name = "guest/review.html"

    def get(self, request, session_id):
        session = get_object_or_404(TableSession, id=session_id)
        guest_token = request.session.get("guest_token")
        guest = get_object_or_404(GuestProfile, guest_token=guest_token, session=session)
        return render(
            request,
            self.template_name,
            self.get_context_data(session=session, guest=guest),
        )

    def post(self, request, session_id):
        session = get_object_or_404(TableSession, id=session_id)
        guest_token = request.session.get("guest_token")
        guest = get_object_or_404(GuestProfile, guest_token=guest_token, session=session)
        rating = int(request.POST.get("rating", 5))
        comment = request.POST.get("comment", "")
        data = create_review(session.id, guest, rating, comment)
        return JsonResponse({"status": "ok", "data": data})
