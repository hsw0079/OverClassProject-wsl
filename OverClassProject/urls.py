from django.contrib import admin
from django.urls import path, re_path, include
from django.views.static import serve
from django.shortcuts import redirect
from . import settings
from apps.vehicle_mgmt.views import stats_dashboard, import_excel, download_template, visitor_appointment
from apps.vehicle_mgmt.api_views import RegisterView, appointment_qr, qr_token_info, user_info
from rest_framework.routers import DefaultRouter
from apps.vehicle_mgmt.api_views import AppointmentViewSet
from rest_framework.authtoken.views import obtain_auth_token
from apps.vehicle_mgmt.api_views import csrf_exempt_login

# DRF Router
router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', lambda request: redirect('admin:index')),
    path('appointment/', visitor_appointment, name='visitor_appointment'),

    # ---- API ----
    path('api/auth/register/', RegisterView.as_view(), name='api_register'),
    path('api/auth/login/', csrf_exempt_login, name='api_login'),
    path('api/auth/user/', user_info, name='api_user_info'),
    path('api/appointments/<int:pk>/qr/', appointment_qr, name='api_appointment_qr'),
    path('api/appointments/<int:pk>/qr-info/', qr_token_info, name='api_qr_info'),
    path('api/admin/', include('apps.campus_nav.urls')),
    path('api/', include(router.urls)),

    # ---- Admin ----
    path('admin/stats/', stats_dashboard, name='admin_stats'),
    path('admin/import-excel/', import_excel, name='admin_import_excel'),
    path('admin/download-template/', download_template, name='admin_download_template'),
    path('admin/', admin.site.urls),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]