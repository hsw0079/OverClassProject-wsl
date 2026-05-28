import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.timezone import now

from apps.vehicle_mgmt.models import Vehicle, EntryExitRecord, VisitorAppointment


# ---- CSV 导出通用 Action ----
def export_as_csv(model_admin, request, queryset):
    """导出选中数据为 CSV 文件"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'
    response.charset = 'utf-8-sig'
    writer = csv.writer(response)
    field_names = [field.name for field in model_admin.model._meta.fields]
    writer.writerow(field_names)
    for obj in queryset:
        row = []
        for field in field_names:
            val = getattr(obj, field)
            if callable(val):
                val = val()
            row.append(str(val) if val is not None else '')
        writer.writerow(row)
    return response


export_as_csv.short_description = '导出选中数据为 CSV'


# ---- 车辆档案 Admin ----
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'vehicle_type', 'owner_name', 'owner_phone',
                    'is_blacklisted', 'created_at')
    list_filter = ('vehicle_type', 'is_blacklisted', 'created_at')
    search_fields = ('plate_number', 'owner_name', 'owner_phone', 'brand')
    list_per_page = 20
    ordering = ('-created_at',)
    actions = [export_as_csv]

    fieldsets = (
        ('基本信息', {'fields': ('plate_number', 'vehicle_type', 'brand', 'color')}),
        ('所属信息', {'fields': ('owner_name', 'owner_phone')}),
        ('黑名单', {'fields': ('is_blacklisted', 'blacklist_reason')}),
        ('其他', {'fields': ('remarks',)}),
    )

    def save_model(self, request, obj, form, change):
        if obj.is_blacklisted and not obj.blacklist_reason:
            obj.blacklist_reason = '未填写原因'
        super().save_model(request, obj, form, change)


# ---- 进出记录 Admin ----
@admin.register(EntryExitRecord)
class EntryExitRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle_plate', 'record_type_display', 'record_time',
                    'driver_name', 'driver_phone', 'purpose_short',
                    'passenger_count', 'created_at')
    list_filter = ('record_type', 'record_time')
    search_fields = ('vehicle__plate_number', 'driver_name', 'driver_phone', 'purpose')
    list_per_page = 20
    ordering = ('-record_time',)
    actions = [export_as_csv]

    fieldsets = (
        ('进出信息', {'fields': ('vehicle', 'record_type', 'record_time')}),
        ('驾驶员信息', {'fields': ('driver_name', 'driver_phone', 'passenger_count')}),
        ('进校详情', {'fields': ('purpose', 'goods_info', 'expected_leave_time', 'approver')}),
        ('其他', {'fields': ('remarks',)}),
    )

    def vehicle_plate(self, obj):
        return obj.vehicle.plate_number
    vehicle_plate.short_description = '车牌号'
    vehicle_plate.admin_order_field = 'vehicle__plate_number'

    def record_type_display(self, obj):
        if obj.record_type == 'entry':
            return '🟢 进校'
        return '🔴 出校'
    record_type_display.short_description = '进出类型'

    def purpose_short(self, obj):
        if obj.purpose and len(obj.purpose) > 20:
            return obj.purpose[:20] + '...'
        return obj.purpose or '-'
    purpose_short.short_description = '事由'


# ---- 访客预约 Admin ----
@admin.register(VisitorAppointment)
class VisitorAppointmentAdmin(admin.ModelAdmin):
    list_display = ('visitor_name', 'visitor_phone', 'plate_number',
                    'host_name', 'host_department', 'expected_time',
                    'status_display', 'approver', 'created_at')
    list_filter = ('status', 'expected_time', 'host_department')
    search_fields = ('visitor_name', 'visitor_phone', 'plate_number',
                     'host_name', 'host_department', 'purpose')
    list_per_page = 20
    ordering = ('-created_at',)
    actions = [export_as_csv]

    fieldsets = (
        ('访客信息', {'fields': ('visitor_name', 'visitor_phone', 'plate_number')}),
        ('被访信息', {'fields': ('host_name', 'host_department')}),
        ('预约信息', {'fields': ('expected_time', 'purpose', 'status', 'approver')}),
        ('其他', {'fields': ('remarks',)}),
    )

    def status_display(self, obj):
        status_colors = {
            'pending': '🟡 待审批',
            'approved': '🟢 已通过',
            'rejected': '🔴 已拒绝',
            'arrived': '🔵 已到访',
            'left': '⚫ 已离开',
        }
        return status_colors.get(obj.status, obj.status)
    status_display.short_description = '状态'
    status_display.admin_order_field = 'status'
