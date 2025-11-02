from django.contrib import admin
import nested_admin
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem, GuestProfile


class OrderItemInline(nested_admin.NestedTabularInline):
    model = OrderItem
    extra = 0
    fields = ("menu_item", "guest", "quantity", "unit_price", "subtotal", "status")
    readonly_fields = ("subtotal",)


@admin.register(Order)
class OrderAdmin(nested_admin.NestedModelAdmin):
    inlines = [OrderItemInline]
    list_display = ("session", "status", "total_price", "tax_amount")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("session", "status")}),
        (_("Totals"), {"fields": ("total_price", "tax_amount")}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(GuestProfile)
class GuestProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "dni", "ip_address", "session", "created_at")
    search_fields = ("name", "dni", "ip_address")
