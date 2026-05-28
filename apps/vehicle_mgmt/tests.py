from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.vehicle_mgmt.models import Vehicle, EntryExitRecord, VisitorAppointment
from django.utils.timezone import now, timedelta


class AdminPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('testadmin', 'test@test.com', 'test123')
        today = now()
        cls.v1 = Vehicle.objects.create(plate_number='京A12345', vehicle_type='staff', brand='大众', color='白色', owner_name='张老师')
        Vehicle.objects.create(plate_number='京B67890', vehicle_type='school_bus', brand='宇通', color='黄色', owner_name='校车队')
        Vehicle.objects.create(plate_number='京D66666', vehicle_type='delivery', brand='东风', color='蓝色', owner_name='送货公司', is_blacklisted=True, blacklist_reason='违规')
        EntryExitRecord.objects.create(vehicle=cls.v1, record_type='entry', driver_name='张老师')
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

    def test_vehicle_list(self):
        r = self.client.get('/admin/vehicle_mgmt/vehicle/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '京A12345')

    def test_entryexit_list(self):
        r = self.client.get('/admin/vehicle_mgmt/entryexitrecord/')
        self.assertEqual(r.status_code, 200)

    def test_visitor_list(self):
        r = self.client.get('/admin/vehicle_mgmt/visitorappointment/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '赵先生')

    def test_vehicle_search(self):
        r = self.client.get('/admin/vehicle_mgmt/vehicle/?q=京A12345')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '京A12345')

    def test_entryexit_filter(self):
        r = self.client.get('/admin/vehicle_mgmt/entryexitrecord/?record_type__exact=entry')
        self.assertEqual(r.status_code, 200)

    def test_visitor_filter(self):
        r = self.client.get('/admin/vehicle_mgmt/visitorappointment/?status__exact=pending')
        self.assertEqual(r.status_code, 200)

    def test_blacklist_filter(self):
        r = self.client.get('/admin/vehicle_mgmt/vehicle/?is_blacklisted__exact=1')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '京D66666')

    def test_model_str(self):
        self.assertIn('京A12345', str(self.v1))
        self.assertIn('张老师', str(self.v1))
