from django.views.generic import TemplateView, View
from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from orders.models import Order
from menu.models import MenuCategory
from orders.services import update_order_status


class KitchenDashboardView(TemplateView):
    template_name = "kitchen/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = MenuCategory.objects.all().order_by("order")
        context["orders"] = (
            Order.objects.filter(status__in=["QUEUED", "PREPARING", "READY"])
            .select_related("session__table")
            .prefetch_related("items__menu_item__menu_category")
            .order_by("created_at")
        )
        context["statuses"] = ["QUEUED", "PREPARING", "READY", "CANCELED"]
        return context


class KitchenQueuePartialView(TemplateView):
    template_name = "kitchen/partials/orders_queue.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = (
            Order.objects.filter(status__in=["QUEUED", "PREPARING", "READY"])
            .select_related("session__table")
            .prefetch_related("items__menu_item__menu_category")
        )

        categories = self.request.GET.get("category")
        statuses = self.request.GET.get("status")

        if statuses:
            qs = qs.filter(status__in=statuses.split(","))

        orders = qs.distinct().order_by("created_at")

        # Filter visible items per order
        orders_with_items = []
        if categories:
            category_ids = [c for c in categories.split(",") if c]
            for order in orders:
                filtered = [
                    item for item in order.items.all()
                    if str(item.menu_item.menu_category_id) in category_ids
                ]
                if filtered:  # ✅ only keep orders with visible items
                    order.filtered_items = filtered
                    orders_with_items.append(order)
        else:
            for order in orders:
                order.filtered_items = list(order.items.all())
                orders_with_items.append(order)

        context["orders"] = orders_with_items
        return context


class KitchenOrderStatusUpdateView(View):
    def post(self, request, order_id):
        new_status = request.POST.get("status")
        try:
            order = update_order_status(order_id, new_status)
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)
        return render(
            request,
            "kitchen/partials/orders_queue.html",
            {"orders": [order]},
        )
