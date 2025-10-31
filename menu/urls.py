from django.urls import path

from menu import views

app_name = 'menu'

urlpatterns = [
    path('preview/<uuid:version_id>/', views.preview_menu, name='preview-version'),
]