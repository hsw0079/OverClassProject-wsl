from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from django.shortcuts import redirect
from . import settings
from apps.vehicle_mgmt.views import stats_dashboard, import_excel, download_template, visitor_appointment

urlpatterns = [
    path('', lambda request: redirect('admin:index')),
    path('appointment/', visitor_appointment, name='visitor_appointment'),
    path('admin/stats/', stats_dashboard, name='admin_stats'),
    path('admin/import-excel/', import_excel, name='admin_import_excel'),
    path('admin/download-template/', download_template, name='admin_download_template'),
    path('admin/', admin.site.urls),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
