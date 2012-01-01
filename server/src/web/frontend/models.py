from django.db import models

class Policy(models.Model):
    name = models.CharField(max_length = 17)
    description = models.CharField(max_length = 150)

class DeviceType(models.Model):
    name = models.CharField(max_length = 20)
    description = models.CharField(max_length = 150)

class Device(models.Model):
    name = models.CharField(max_length = 50, null=True)
    mac_address = models.CharField(max_length = 17)
    ip_address = models.CharField(max_length = 17)
    policy = models.ForeignKey(Policy, null=True)
    device_type = models.ForeignKey(DeviceType, null=True)
 
class ArpDocument(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

