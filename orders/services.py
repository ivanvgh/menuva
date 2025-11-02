from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from table.enum import TableStatus, SessionStatus
from .models import Order, OrderItem, GuestProfile
from .enums import OrderStatus, OrderItemStatus, TAX_RATE
from table.models import TableSession


# -------------------------------
#  ORDER CREATION / CALCULATION
# -------------------------------

@transaction.atomic
def create_order(session_id, guest, item_data):
    order = Order.objects.create(session_id=session_id, status=OrderStatus.DRAFT)

    for data in item_data:
        OrderItem.objects.create(
            order=order,
            guest=guest,
            menu_item=data["menu_item"],
            quantity=data["quantity"],
            unit_price=data["unit_price"],
            subtotal=data["unit_price"] * data["quantity"],
        )

    calculate_totals(order)
    order.status = OrderStatus.QUEUED
    order.save()
    return order



def calculate_totals(order):
    subtotal = sum(i.subtotal for i in order.items.all())
    tax = subtotal * TAX_RATE
    order.tax_amount = tax
    order.total_price = subtotal + tax
    order.save()
    return order


def update_order_status(order_id, new_status):
    order = Order.objects.get(id=order_id)
    order.status = new_status
    order.save()
    return order


def mark_item_delivered(item_id):
    item = OrderItem.objects.get(id=item_id)
    item.status = OrderItemStatus.DELIVERED
    item.save()
    order = item.order
    if not order.items.exclude(status=OrderItemStatus.DELIVERED).exists():
        order.status = OrderStatus.SERVED
        order.save()
    return item


# -------------------------------
#  GUEST / ASSISTANCE (SOS)
# -------------------------------
@transaction.atomic
def request_assistance(session_id: UUID) -> None:
    """Flag a table as needing assistance."""
    session = TableSession.objects.select_related('table').get(pk=session_id)

    if session.status != SessionStatus.OPEN:
        raise ValidationError(_('Cannot request assistance for a closed session.'))

    session.assistance_requested = True
    session.save(update_fields=['assistance_requested'])

    session.table.status = TableStatus.NEEDS_HELP
    session.table.save(update_fields=['status'])

@transaction.atomic
def resolve_assistance(session_id: UUID) -> None:
    """Mark assistance request as resolved and revert table to occupied."""
    session = TableSession.objects.select_related('table').get(pk=session_id)

    if session.status != SessionStatus.OPEN:
        raise ValidationError(_('Cannot resolve assistance for a closed session.'))

    session.assistance_requested = False
    session.save(update_fields=['assistance_requested'])

    session.table.status = TableStatus.OCCUPIED
    session.table.save(update_fields=['status'])

# -------------------------------
#  GUEST ORDERS & REVIEWS
# -------------------------------

def list_guest_orders(session_id, guest_id):
    """Return all orders for a given guest within a table session."""
    return (
        OrderItem.objects
        .filter(order__session_id=session_id, guest_id=guest_id)
        .select_related("menu_item", "order")
        .order_by("-created_at")
    )


def create_review(session_id, guest: GuestProfile, rating: int, comment: str):
    """Save a simple feedback entry (placeholder for real model)."""
    # NOTE: You can later move this into a Review model
    print(f"[REVIEW] Session {session_id} by {guest.name}: {rating}★ - {comment}")
    # In production, persist to Review model or external service
    return {"session_id": session_id, "guest": guest.name, "rating": rating, "comment": comment}


# -------------------------------
#  CHAT (FAKE ENDPOINT FOR NOW)
# -------------------------------

def send_chat_message(session_id, guest: GuestProfile, message: str):
    """
    Append a message from the guest to their chat history.
    """
    new_message = guest.append_message(sender="guest", text=message)

    # In future, waiter messages can also append with sender="waiter"
    fake_response = {
        "status": "ok",
        "message": new_message,
        "all_messages": guest.chat_history,
    }
    return fake_response

