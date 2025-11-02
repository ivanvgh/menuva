from django.urls import path
from .views import (
    GuestMenuView,
    GuestOrderSubmitView,
    OrderListView,
    OrderDetailView,
    KitchenDashboardView,
    KitchenDashboardPartialView,
    OrderStatusUpdateView, GuestEntryView, GuestSOSView, GuestChatView, GuestOrdersView,
    GuestReviewView, GuestChatMessagesView,
)

app_name = "orders"

urlpatterns = [
    path("guest/<uuid:table_qr_uuid>/", GuestEntryView.as_view(), name="guest-entry"),
    path("guest/session/<uuid:session_id>/order/", GuestOrderSubmitView.as_view(), name="guest-order"),
    path("guest/<uuid:session_id>/menu/", GuestMenuView.as_view(), name="guest-menu"),
    path("guest/<uuid:session_id>/sos/", GuestSOSView.as_view(), name="guest-sos"),
    path("guest/<uuid:session_id>/chat/", GuestChatView.as_view(), name="guest-chat"),
    path("guest/<uuid:session_id>/chat/messages/", GuestChatMessagesView.as_view(), name="guest-chat-messages"),
    path("guest/<uuid:session_id>/orders/", GuestOrdersView.as_view(), name="guest-orders"),
    path("guest/<uuid:session_id>/review/", GuestReviewView.as_view(), name="guest-review"),

    path("orders/", OrderListView.as_view(), name="orders-list"),
    path("orders/<uuid:order_id>/", OrderDetailView.as_view(), name="order-detail"),
    path("kitchen/", KitchenDashboardView.as_view(), name="kitchen-dashboard"),
    path("kitchen/refresh/", KitchenDashboardPartialView.as_view(), name="kitchen-dashboard-refresh"),
    path("orders/<uuid:order_id>/status/", OrderStatusUpdateView.as_view(), name="order-status-update"),
]

