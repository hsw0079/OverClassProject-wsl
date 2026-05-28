from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.vehicle_mgmt.models import SchoolVehicle, ExternalVehicle, EntryExitRecord, VisitorAppointment
from django.utils.timezone import now, timedelta


class AdminPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('testadmin', 'test@test.com', 'test123')
        today = now()
        cls.sv1 = SchoolVehicle.objects.create(plate_number='京A12345', vehicle_type='staff', brand='大众', color='白色', owner_name='张老师')
        SchoolVehicle.objects.create(plate_number='京B67890', vehicle_type='school_bus', brand='宇通', color='黄色', owner_name='校车队')
        SchoolVehicle.objects.create(plate_number='京D66666', vehicle_type='delivery', brand='东风', color='蓝色', owner_name='送货公司', is_blacklisted=True, blacklist_reason='违规')
        EntryExitRecord.objects.create(plate_number='京A12345', record_type='entry', driver_name='张老师')
        VisitorAppointment.objects.create(visitor_name='赵先生', visitor_phone='13900000000', plate_number='京E55555', host_name='王主任', expected_time=now()+timedelta(days=1), purpose='交流')

    def setUp(self):
        self.client = Client()
        self.client.login(username='testadmin', password='test123')

    def test_admin_index(self):
        r = self.client.get('/admin/')
        self.assertEqual(r.status_code, 200)

    def test_stats_dashboard(self):
        r = self.client.get('/admin/stats/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '今日进校')

    def test_school_vehicle_list(self):
        r = self.client.get('/admin/vehicle_mgmt/schoolvehicle/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '京A12345')

    def test_external_vehicle_list(self):
        r = self.client.get('/admin/vehicle_mgmt/externalvehicle/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '清空倒计时')

    def test_entryexit_list(self):
        r = self.client.get('/admin/vehicle_mgmt/entryexitrecord/')
        self.assertEqual(r.status_code, 200)

    def test_visitor_list(self):
        r = self.client.get('/admin/vehicle_mgmt/visitorappointment/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '赵先生')

    def test_school_vehicle_search(self):
        r = self.client.get('/admin/vehicle_mgmt/schoolvehicle/?q=京A12345')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '京A12345')

    def test_entryexit_filter(self):
        r = self.client.get('/admin/vehicle_mgmt/entryexitrecord/?record_type__exact=entry')
        self.assertEqual(r.status_code, 200)

    def test_visitor_filter(self):
        r = self.client.get('/admin/vehicle_mgmt/visitorappointment/?status__exact=pending')
        self.assertEqual(r.status_code, 200)

    def test_blacklist_filter(self):
        r = self.client.get('/admin/vehicle_mgmt/schoolvehicle/?is_blacklisted__exact=1')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '京D66666')

    def test_model_str(self):
        self.assertIn('京A12345', str(self.sv1))
        self.assertIn('张老师', str(self.sv1))


class AutoLinkTests(TestCase):
    """测试进出记录自动关联逻辑"""

    def test_school_vehicle_auto_link(self):
        """登记在校车辆 → 自动关联 school_vehicle"""
        sv = SchoolVehicle.objects.create(plate_number='京TEST01', vehicle_type='staff', owner_name='测试老师')
        record = EntryExitRecord.objects.create(
            plate_number='京TEST01', record_type='entry', driver_name='测试司机'
        )
        self.assertEqual(record.school_vehicle, sv)
        self.assertIsNone(record.external_vehicle)

    def test_external_vehicle_auto_create(self):
        """未登记车牌 → 自动创建并关联外来车辆"""
        self.assertEqual(ExternalVehicle.objects.count(), 0)
        record = EntryExitRecord.objects.create(
            plate_number='京OUT001', record_type='entry', driver_name='外来司机', driver_phone='13800000000'
        )
        self.assertIsNone(record.school_vehicle)
        self.assertIsNotNone(record.external_vehicle)
        self.assertEqual(record.external_vehicle.plate_number, '京OUT001')
        self.assertEqual(ExternalVehicle.objects.count(), 1)

    def test_external_vehicle_no_duplicate(self):
        """同一未登记车牌多次进出 → 不重复创建外来车辆"""
        EntryExitRecord.objects.create(plate_number='京OUT002', record_type='entry', driver_name='司机A')
        EntryExitRecord.objects.create(plate_number='京OUT002', record_type='exit', driver_name='司机A')
        self.assertEqual(ExternalVehicle.objects.filter(plate_number='京OUT002').count(), 1)

    def test_school_trumps_external(self):
        """已登记在校的车辆 → 即使有外来记录也关联在校"""
        SchoolVehicle.objects.create(plate_number='京BOTH01', vehicle_type='staff', owner_name='在校老师')
        record = EntryExitRecord.objects.create(plate_number='京BOTH01', record_type='entry', driver_name='司机')
        self.assertIsNotNone(record.school_vehicle)
        self.assertIsNone(record.external_vehicle)
        self.assertEqual(ExternalVehicle.objects.count(), 0)

    def test_owner_name_property(self):
        """owner_name 属性优先返回在校车辆所属人"""
        sv = SchoolVehicle.objects.create(plate_number='京PROP01', vehicle_type='staff', owner_name='产权人')
        record = EntryExitRecord.objects.create(plate_number='京PROP01', record_type='entry', driver_name='驾驶员')
        self.assertEqual(record.owner_name, '产权人')


class PurgeCommandTests(TestCase):
    """测试清空命令"""

    def test_purge_deletes_all_external(self):
        EntryExitRecord.objects.create(plate_number='京OUT99', record_type='entry', driver_name='测试')
        self.assertGreater(ExternalVehicle.objects.count(), 0)

        from django.core.management import call_command
        call_command('purge_external_vehicles')
        self.assertEqual(ExternalVehicle.objects.count(), 0)
