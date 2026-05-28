from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from django.shortcuts import redirect
from . import settings
from apps.vehicle_mgmt.views import stats_dashboard

urlpatterns = [
    path('', lambda request: redirect('admin:index')),
    path('admin/stats/', stats_dashboard, name='admin_stats'),
    path('admin/', admin.site.urls),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
