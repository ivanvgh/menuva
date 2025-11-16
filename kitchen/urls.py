from django.urls import path
from . import views

app_name = "kitchen"

urlpatterns = [
    path("", views.KitchenDashboardView.as_view(), name="dashboard"),
    path("refresh/", views.KitchenQueuePartialView.as_view(), name="queue-refresh"),
    path("order/<int:order_id>/status/",
         views.KitchenOrderStatusUpdateView.as_view(),
         name="order-status"),
]
