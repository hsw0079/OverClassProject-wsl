import re
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class SchoolVehicle(models.Model):
    """在校车辆档案"""
    VEHICLE_TYPE_CHOICES = [
        ('school_bus', '校车'),
        ('staff', '教职工车辆'),
        ('official', '公务车辆'),
        ('visitor', '访客车辆'),
        ('delivery', '送货车辆'),
    ]

    plate_number = models.CharField('车牌号', max_length=20, unique=True)
    vehicle_type = models.CharField('车辆类型', max_length=20, choices=VEHICLE_TYPE_CHOICES, default='staff')
    brand = models.CharField('品牌', max_length=50, blank=True, null=True)
    color = models.CharField('颜色', max_length=20, blank=True, null=True)
    owner_name = models.CharField('所属人/部门', max_length=100)
    owner_phone = models.CharField('联系电话', max_length=20, blank=True, null=True)
    is_blacklisted = models.BooleanField('是否黑名单', default=False)
    blacklist_reason = models.TextField('拉黑原因', blank=True, null=True)
    remarks = models.TextField('备注', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '在校车辆档案'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.plate_number}（{self.owner_name}）'


class ExternalVehicle(models.Model):
    """外来车辆档案（每月月底清空）"""
    plate_number = models.CharField('车牌号', max_length=20, unique=True)
    owner_name = models.CharField('所属人', max_length=100)
    owner_phone = models.CharField('联系电话', max_length=20, blank=True, null=True)
    created_at = models.DateTimeField('首次登记时间', auto_now_add=True)

    class Meta:
        verbose_name = '外来车辆档案'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.plate_number}（{self.owner_name}）'


class EntryExitRecord(models.Model):
    """进出记录"""
    RECORD_TYPE_CHOICES = [
        ('entry', '进校'),
        ('exit', '出校'),
    ]

    plate_number = models.CharField('车牌号', max_length=20)
    school_vehicle = models.ForeignKey(
        SchoolVehicle, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='在校车辆', related_name='records'
    )
    external_vehicle = models.ForeignKey(
        ExternalVehicle, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='外来车辆', related_name='records'
    )
    record_type = models.CharField('进出类型', max_length=10, choices=RECORD_TYPE_CHOICES)
    record_time = models.DateTimeField('进出时间', default=timezone.now)
    driver_name = models.CharField('驾驶员姓名', max_length=50)
    driver_phone = models.CharField('驾驶员电话', max_length=20, blank=True, null=True)
    passenger_count = models.PositiveIntegerField('同行人数', default=1)
    goods_info = models.TextField('货物信息', blank=True, null=True)
    purpose = models.TextField('事由', blank=True, null=True)
    expected_leave_time = models.DateTimeField('预计离校时间', blank=True, null=True)
    approver = models.CharField('审批人', max_length=50, blank=True, null=True)
    remarks = models.TextField('备注', blank=True, null=True)
    created_at = models.DateTimeField('登记时间', auto_now_add=True)

    class Meta:
        verbose_name = '进出记录'
        verbose_name_plural = verbose_name
        ordering = ['-record_time']
        indexes = [
            models.Index(fields=['-record_time']),
            models.Index(fields=['record_type']),
        ]

    def __str__(self):
        type_label = '进校' if self.record_type == 'entry' else '出校'
        return f'{self.plate_number} {type_label} {self.record_time.strftime("%Y-%m-%d %H:%M")}'

    def save(self, *args, **kwargs):
        # 自动关联：先查在校车辆，未命中则创建/关联外来车辆
        self.plate_number = (self.plate_number or '').strip()
        sv = SchoolVehicle.objects.filter(plate_number=self.plate_number).first()
        if sv:
            self.school_vehicle = sv
            self.external_vehicle = None
        else:
            self.school_vehicle = None
            ev, _ = ExternalVehicle.objects.get_or_create(
                plate_number=self.plate_number,
                defaults={
                    'owner_name': self.driver_name,
                    'owner_phone': self.driver_phone or '',
                }
            )
            self.external_vehicle = ev
        super().save(*args, **kwargs)

    @property
    def owner_name(self):
        """获取所属人名称（在校 > 外来 > 驾驶员）"""
        if self.school_vehicle:
            return self.school_vehicle.owner_name
        if self.external_vehicle:
            return self.external_vehicle.owner_name
        return self.driver_name


class VisitorAppointment(models.Model):
    """访客预约"""
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
        ('arrived', '已到访'),
        ('left', '已离开'),
    ]

    visitor_name = models.CharField('访客姓名', max_length=50)
    visitor_phone = models.CharField('访客电话', max_length=20)
    plate_number = models.CharField('车牌号', max_length=20)
    host_name = models.CharField('被访人', max_length=50)
    host_department = models.CharField('被访部门', max_length=100, blank=True, null=True)
    expected_time = models.DateTimeField('预计进校时间')
    purpose = models.TextField('事由')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    approver = models.CharField('审批人', max_length=50, blank=True, null=True)
    remarks = models.TextField('备注', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '访客预约'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.visitor_name} - {self.plate_number}（{self.get_status_display()}）'


class NonMotorVehicle(models.Model):
    """非机动车档案"""
    TYPE_CHOICES = [
        ('bicycle', '自行车'),
        ('ebike', '电动车'),
        ('tricycle', '三轮车'),
        ('other', '其他'),
    ]

    number_plate = models.CharField('编号牌', max_length=3, unique=True, help_text='范围 001~999，必须3位数字')
    vehicle_type = models.CharField('车辆类型', max_length=20, choices=TYPE_CHOICES, default='ebike')
    owner_name = models.CharField('所属人', max_length=100)
    owner_phone = models.CharField('联系电话', max_length=20, blank=True, null=True)
    brand = models.CharField('品牌', max_length=50, blank=True, null=True)
    color = models.CharField('颜色', max_length=20, blank=True, null=True)
    remarks = models.TextField('备注', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '非机动车档案'
        verbose_name_plural = verbose_name
        ordering = ['number_plate']

    def __str__(self):
        return f'{self.number_plate}（{self.owner_name}）'

    def clean(self):
        super().clean()
        if not re.match(r'^(00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})$', self.number_plate):
            raise ValidationError({'number_plate': '编号牌必须为 001~999 的3位数字（如 001、050、999）'})
