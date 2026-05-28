from django.core.management.base import BaseCommand
from apps.vehicle_mgmt.models import Vehicle, EntryExitRecord, VisitorAppointment
from django.utils.timezone import now, timedelta


class Command(BaseCommand):
    help = '播种测试数据'

    def handle(self, *args, **kwargs):
        today = now()

        v1 = Vehicle.objects.get_or_create(plate_number='京A12345', defaults={'vehicle_type': 'staff', 'brand': '大众', 'color': '白色', 'owner_name': '张老师', 'owner_phone': '13800001111'})[0]
        v2 = Vehicle.objects.get_or_create(plate_number='京B67890', defaults={'vehicle_type': 'school_bus', 'brand': '宇通', 'color': '黄色', 'owner_name': '校车队', 'owner_phone': '13800002222'})[0]
        v3 = Vehicle.objects.get_or_create(plate_number='京C11111', defaults={'vehicle_type': 'visitor', 'brand': '丰田', 'color': '黑色', 'owner_name': '访客登记', 'owner_phone': '13800003333'})[0]
        Vehicle.objects.get_or_create(plate_number='京D66666', defaults={'vehicle_type': 'delivery', 'brand': '东风', 'color': '蓝色', 'owner_name': '送货公司', 'owner_phone': '13800004444', 'is_blacklisted': True, 'blacklist_reason': '多次违规停放'})

        EntryExitRecord.objects.get_or_create(vehicle=v1, record_type='entry', record_time=today.replace(hour=8, minute=30), defaults={'driver_name': '张老师', 'driver_phone': '13800001111', 'passenger_count': 1, 'purpose': '上班', 'expected_leave_time': today.replace(hour=17, minute=0)})
        EntryExitRecord.objects.get_or_create(vehicle=v2, record_type='entry', record_time=today.replace(hour=9, minute=0), defaults={'driver_name': '李师傅', 'driver_phone': '13800002222', 'passenger_count': 30, 'purpose': '接送学生'})
        EntryExitRecord.objects.get_or_create(vehicle=v3, record_type='entry', record_time=today.replace(hour=10, minute=15), defaults={'driver_name': '王先生', 'driver_phone': '13800003333', 'passenger_count': 2, 'purpose': '拜访教务处', 'expected_leave_time': today.replace(hour=12, minute=0), 'approver': '李主任'})

        tomorrow = now() + timedelta(days=1)
        VisitorAppointment.objects.get_or_create(visitor_name='赵先生', visitor_phone='13900005555', defaults={'plate_number': '京E55555', 'host_name': '王主任', 'host_department': '教务处', 'expected_time': tomorrow, 'purpose': '学术交流', 'status': 'pending'})
        VisitorAppointment.objects.get_or_create(visitor_name='钱女士', visitor_phone='13900006666', defaults={'plate_number': '京F66666', 'host_name': '李校长', 'host_department': '校办', 'expected_time': today, 'purpose': '考察访问', 'status': 'approved'})

        entered = set(EntryExitRecord.objects.filter(record_type='entry', record_time__date=today.date()).values_list('vehicle_id', flat=True))
        exited = set(EntryExitRecord.objects.filter(record_type='exit', record_time__date=today.date()).values_list('vehicle_id', flat=True))
        on_campus = entered - exited

        self.stdout.write(self.style.SUCCESS('测试数据已就绪'))
        self.stdout.write(f'  车辆: {Vehicle.objects.count()} | 黑名单: {Vehicle.objects.filter(is_blacklisted=True).count()}')
        self.stdout.write(f'  进出记录: {EntryExitRecord.objects.count()}')
        self.stdout.write(f'  访客预约: {VisitorAppointment.objects.count()} | 待审批: {VisitorAppointment.objects.filter(status="pending").count()}')
        self.stdout.write(f'  当前在校车辆: {len(on_campus)}')
