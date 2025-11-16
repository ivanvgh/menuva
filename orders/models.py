import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.utils.timesince import timesince
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel, SoftDeleteMixin
from table.models import TableSession
from menu.models import MenuItem
from .enums import OrderStatus, OrderItemStatus


class GuestProfile(models.Model):
    """Stores temporary guest identity per TableSession."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        TableSession, on_delete=models.CASCADE, related_name="guests"
    )
    name = models.CharField(_("Guest name"), max_length=100)
    dni = models.CharField(_("DNI"), max_length=20, null=True, blank=True)
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    guest_token = models.UUIDField(default=uuid.uuid4)
    chat_history = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = _("Guest Profile")
        verbose_name_plural = _("Guest Profiles")

    def __str__(self):
        return f"{self.name} ({self.session.table})"

    def append_message(self, sender, text):
        """Add a chat message to JSON history."""
        message = {
            "sender": sender,
            "text": text,
            "timestamp": timezone.now().isoformat(),
        }
        self.chat_history.append(message)
        self.save(update_fields=["chat_history"])
        return message


class Order(BaseModel, SoftDeleteMixin):
    """Unified order per TableSession."""

    session = models.ForeignKey(
        TableSession, on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(
        _("Status"), max_length=20, choices=OrderStatus.choices, default=OrderStatus.DRAFT
    )
    total_price = models.DecimalField(_("Total"), max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_("Tax amount"), max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return _('Order %(id)s - Table %(number)s [%(status)s]') % {
            'id': self.id,
            'number': self.session.table.number,
            'status': self.status,
        }


class OrderItem(BaseModel, SoftDeleteMixin):
    """Individual menu item linked to an Order and Guest."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    guest = models.ForeignKey(GuestProfile, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_("Quantity"), default=1)
    unit_price = models.DecimalField(_("Unit price"), max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(_("Subtotal"), max_digits=8, decimal_places=2)
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=OrderItemStatus.choices,
        default=OrderItemStatus.PENDING,
    )

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    def save(self, *args, **kwargs):
        self.subtotal = Decimal(self.unit_price) * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.menu_item.item.name} x{self.quantity} by {self.guest.name}"

    def time_since_created(self):
        """Tiempo legible desde que se pidió este ítem."""
        if not self.created_at:
            return ''
        delta = timesince(self.created_at, timezone.now())
        # timesince devuelve "2 minutes", "1 hour, 3 minutes" → solo tomamos la primera parte
        return _('hace %(time)s') % {'time': delta.split(',')[0]}
