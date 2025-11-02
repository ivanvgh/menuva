from django.urls import path
from table import views

app_name = 'table'

urlpatterns = [
    # Grid & detail views
    path('', views.TableGridView.as_view(), name='tables-grid'),
    path('grid-refresh/', views.TableGridPartialView.as_view(), name='tables-grid-refresh'),
    path('<int:pk>/', views.TableDetailView.as_view(), name='table-detail'),

    # Actions
    path('<int:pk>/open/', views.OpenSessionView.as_view(), name='table-open'),
    path('<int:pk>/close/', views.CloseSessionView.as_view(), name='table-close'),
    path('<int:pk>/assist/', views.AssistanceRequestView.as_view(), name='table-assist'),
    path('<int:pk>/resolve/', views.AssistanceResolveView.as_view(), name='table-resolve'),

    # Guest routes
    path('qr/<uuid:qr_uuid>/', views.GuestQRResolverView.as_view(), name='guest-qr-resolver'),
    path('guest/session/<uuid:session_id>/', views.GuestSessionView.as_view(), name='guest-session'),
]
