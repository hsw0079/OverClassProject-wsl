from django.db import models
from django.utils import timezone


class Vehicle(models.Model):
    """车辆档案"""
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
        verbose_name = '车辆档案'
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

    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE,
        verbose_name='车辆', related_name='records'
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
        return f'{self.vehicle.plate_number} {type_label} {self.record_time.strftime("%Y-%m-%d %H:%M")}'


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
