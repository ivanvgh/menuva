from django.contrib import admin
from django.urls import path

from .models import Item
from .views import PreviewMenuView

app_name = 'menu'

urlpatterns = [
    path('preview/<int:pk>/', PreviewMenuView.as_view(), name='preview'),
]
