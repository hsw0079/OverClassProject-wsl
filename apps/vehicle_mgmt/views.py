from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils.timezone import now

from apps.vehicle_mgmt.models import SchoolVehicle, ExternalVehicle, EntryExitRecord, VisitorAppointment, NonMotorVehicle


@staff_member_required
def stats_dashboard(request):
    """系统首页统计看板"""
    today = now().date()

    today_entry_count = EntryExitRecord.objects.filter(
        record_type='entry', record_time__date=today
    ).count()
    today_exit_count = EntryExitRecord.objects.filter(
        record_type='exit', record_time__date=today
    ).count()

    # 当前在校车辆（按车牌号去重）
    entered_today = set(EntryExitRecord.objects.filter(
        record_type='entry', record_time__date=today
    ).values_list('plate_number', flat=True))
    exited_today = set(EntryExitRecord.objects.filter(
        record_type='exit', record_time__date=today
    ).values_list('plate_number', flat=True))
    on_campus_count = len(entered_today - exited_today)

    pending_visitors = VisitorAppointment.objects.filter(status='pending').count()
    blacklisted_count = SchoolVehicle.objects.filter(is_blacklisted=True).count()
    today_arrived = VisitorAppointment.objects.filter(
        status__in=['arrived', 'left']
    ).filter(expected_time__date=today).count()

    recent_records = EntryExitRecord.objects.order_by('-record_time')[:10]

    context = {
        'today_entry_count': today_entry_count,
        'today_exit_count': today_exit_count,
        'on_campus_count': on_campus_count,
        'pending_visitors': pending_visitors,
        'blacklisted_count': blacklisted_count,
        'today_arrived': today_arrived,
        'recent_records': recent_records,
        'total_vehicles': SchoolVehicle.objects.count(),
        'external_vehicles': ExternalVehicle.objects.count(),
        'non_motor_count': NonMotorVehicle.objects.count(),
        'total_records_today': today_entry_count + today_exit_count,
    }
    return render(request, 'admin/stats_dashboard.html', context)
