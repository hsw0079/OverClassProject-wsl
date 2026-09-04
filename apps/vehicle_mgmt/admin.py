import csv

from django.contrib import admin
from django.http import HttpResponse

from apps.vehicle_mgmt.models import SchoolVehicle, ExternalVehicle, EntryExitRecord, VisitorAppointment, NonMotorVehicle


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


def purge_external_vehicles_action(model_admin, request, queryset):
    """立即清空所有外来车辆记录"""
    count, _ = ExternalVehicle.objects.all().delete()
    model_admin.message_user(request, f'已清空 {count} 条外来车辆记录。')

purge_external_vehicles_action.short_description = '⚠ 立即清空所有外来车辆记录'


# ---- 在校车辆档案 Admin ----
@admin.register(SchoolVehicle)
class SchoolVehicleAdmin(admin.ModelAdmin):
    change_list_template = 'admin/school_vehicle_change_list.html'
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


# ---- 外来车辆档案 Admin ----
@admin.register(ExternalVehicle)
class ExternalVehicleAdmin(admin.ModelAdmin):
    change_list_template = 'admin/external_vehicle_change_list.html'
    list_display = ('plate_number', 'owner_name', 'owner_phone', 'created_at')
    search_fields = ('plate_number', 'owner_name', 'owner_phone')
    list_per_page = 20
    ordering = ('-created_at',)
    actions = [export_as_csv, purge_external_vehicles_action]


# ---- 进出记录 Admin ----
@admin.register(EntryExitRecord)
class EntryExitRecordAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        """显式处理自动关联逻辑，确保 Admin 保存时外来车辆自动登记"""
        from apps.vehicle_mgmt.models import SchoolVehicle, ExternalVehicle
        obj.plate_number = (obj.plate_number or '').strip()
        sv = SchoolVehicle.objects.filter(plate_number=obj.plate_number).first()
        if sv:
            obj.school_vehicle = sv
            obj.external_vehicle = None
        else:
            obj.school_vehicle = None
            ev, _ = ExternalVehicle.objects.get_or_create(
                plate_number=obj.plate_number,
                defaults={'owner_name': obj.driver_name, 'owner_phone': obj.driver_phone or ''}
            )
            obj.external_vehicle = ev
        super().save_model(request, obj, form, change)

    list_display = ('plate_number', 'vehicle_source', 'record_type_display', 'record_time',
                    'driver_name', 'driver_phone', 'purpose_short',
                    'passenger_count', 'created_at')
    list_filter = ('record_type', 'record_time')
    search_fields = ('plate_number', 'driver_name', 'driver_phone', 'purpose',
                     'school_vehicle__owner_name', 'external_vehicle__owner_name')
    list_per_page = 20
    ordering = ('-record_time',)
    actions = [export_as_csv]

    fieldsets = (
        ('车辆信息', {'fields': ('plate_number',)}),
        ('进出信息', {'fields': ('record_type', 'record_time')}),
        ('驾驶员信息', {'fields': ('driver_name', 'driver_phone', 'passenger_count')}),
        ('进校详情', {'fields': ('purpose', 'goods_info', 'expected_leave_time', 'approver')}),
        ('其他', {'fields': ('remarks',)}),
    )

    # 图标
    def vehicle_source(self, obj):
        if obj.school_vehicle:
            return f' {obj.school_vehicle.owner_name}'
        if obj.external_vehicle:
            return f' 外来'
        return '—'
    vehicle_source.short_description = '车辆来源'

    def record_type_display(self, obj):
        return '🟢 进校' if obj.record_type == 'entry' else '🔴 出校'
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
                    'status_display', 'approver', 'approval_message', 'created_at')
    list_filter = ('status', 'expected_time', 'host_department')
    search_fields = ('visitor_name', 'visitor_phone', 'plate_number',
                     'host_name', 'host_department', 'purpose')
    list_per_page = 20
    ordering = ('-created_at',)
    actions = [export_as_csv, 'approve_appointments', 'reject_appointments']

    fieldsets = (
        ('访客信息', {'fields': ('visitor_name', 'visitor_phone', 'plate_number')}),
        ('被访信息', {'fields': ('host_name', 'host_department')}),
        ('预约信息', {'fields': ('expected_time', 'purpose', 'status', 'approver')}),
        ('其他', {'fields': ('remarks',)}),
    )

    def approve_appointments(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='approved',
            approver=request.user.username
        )
        self.message_user(request, '已审批通过 {} 条预约。'.format(updated))
    approve_appointments.short_description = '✅ 审批通过'

    def reject_appointments(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='rejected',
            approver=request.user.username
        )
        self.message_user(request, '已拒绝 {} 条预约。'.format(updated))
    reject_appointments.short_description = '❌ 拒绝'

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

    def approval_message(self, obj):
        if obj.status == 'approved':
            return '✅ {} 已通过'.format(obj.approver or '管理员')
        elif obj.status == 'rejected':
            return '❌ {} 已拒绝'.format(obj.approver or '管理员')
        return '—'
    approval_message.short_description = '审批消息'



# ---- 非机动车档案 Admin ----
@admin.register(NonMotorVehicle)
class NonMotorVehicleAdmin(admin.ModelAdmin):
    list_display = ('number_plate', 'vehicle_type', 'owner_name', 'owner_phone', 'created_at')
    list_filter = ('vehicle_type', 'created_at')
    search_fields = ('number_plate', 'owner_name', 'owner_phone')
    list_per_page = 20
    ordering = ('number_plate',)
    actions = [export_as_csv]

    fieldsets = (
        ('基本信息', {'fields': ('number_plate', 'vehicle_type', 'brand', 'color')}),
        ('所属信息', {'fields': ('owner_name', 'owner_phone')}),
        ('其他', {'fields': ('remarks',)}),
    )