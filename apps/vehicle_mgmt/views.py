from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils.timezone import now

from apps.vehicle_mgmt.models import Vehicle, EntryExitRecord, VisitorAppointment


@staff_member_required
def stats_dashboard(request):
    """系统首页统计看板"""
    today = now().date()

    # 今日进出统计
    today_entry_count = EntryExitRecord.objects.filter(
        record_type='entry', record_time__date=today
    ).count()
    today_exit_count = EntryExitRecord.objects.filter(
        record_type='exit', record_time__date=today
    ).count()

    # 当前在校车辆
    entered_today = EntryExitRecord.objects.filter(
        record_type='entry', record_time__date=today
    ).values_list('vehicle_id', flat=True)
    exited_today = EntryExitRecord.objects.filter(
        record_type='exit', record_time__date=today
    ).values_list('vehicle_id', flat=True)
    on_campus_ids = set(entered_today) - set(exited_today)
    on_campus_count = len(on_campus_ids)

    # 待审批访客
    pending_visitors = VisitorAppointment.objects.filter(status='pending').count()

    # 黑名单车辆
    blacklisted_count = Vehicle.objects.filter(is_blacklisted=True).count()

    # 今日到访
    today_arrived = VisitorAppointment.objects.filter(
        status__in=['arrived', 'left']
    ).filter(expected_time__date=today).count()

    # 最近10条进出记录
    recent_records = EntryExitRecord.objects.select_related('vehicle').order_by('-record_time')[:10]

    context = {
        'today_entry_count': today_entry_count,
        'today_exit_count': today_exit_count,
        'on_campus_count': on_campus_count,
        'pending_visitors': pending_visitors,
        'blacklisted_count': blacklisted_count,
        'today_arrived': today_arrived,
        'recent_records': recent_records,
        'total_vehicles': Vehicle.objects.count(),
        'total_records_today': today_entry_count + today_exit_count,
    }
    return render(request, 'admin/stats_dashboard.html', context)
