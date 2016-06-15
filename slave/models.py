from django.db import models


# Create your models here.
class BaseInfo(models.Model):
    host_ip = models.GenericIPAddressField()
    host_port = models.IntegerField()
    room_number = models.IntegerField()
    target_temp = models.FloatField()
    current_speed = models.CharField(max_length=20)
    current_temp = models.FloatField()
    mode = models.CharField(max_length=20)
    query_speed = models.CharField(max_length=20)
    power_consump = models.FloatField()
    power_price = models.FloatField()
    total_cost = models.FloatField()
    is_log = models.CharField(max_length=20)
    is_conn = models.CharField(max_length=20)
