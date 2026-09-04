import json
from django.contrib import admin
from django.utils.html import format_html
from apps.campus_nav.models import CampusLocation


@admin.register(CampusLocation)
class CampusLocationAdmin(admin.ModelAdmin):
    change_list_template = 'admin/campus_nav/change_list.html'
    list_display = ('name', 'coordinates', 'created_at')
    search_fields = ('name',)
    list_per_page = 20

    fieldsets = (
        ('基本信息', {'fields': ('name',)}),
        ('位置信息', {'fields': ('longitude', 'latitude')}),
    )

    def coordinates(self, obj):
        return f'{obj.longitude:.6f}, {obj.latitude:.6f}'
    coordinates.short_description = '坐标'