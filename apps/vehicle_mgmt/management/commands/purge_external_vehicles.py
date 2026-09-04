from django.core.management.base import BaseCommand
from apps.vehicle_mgmt.models import ExternalVehicle


class Command(BaseCommand):
    help = '清空本月外来车辆档案记录'

    def handle(self, *args, **kwargs):
        count, _ = ExternalVehicle.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'已清空 {count} 条外来车辆记录'))
