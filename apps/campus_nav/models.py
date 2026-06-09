from django.db import models

class CampusLocation(models.Model):
    """校内地点标注"""
    name = models.CharField('地点名称', max_length=100)
    longitude = models.FloatField('经度')
    latitude = models.FloatField('纬度')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '校内地点'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name