from django.db import models

class Policy(models.Model):
    name = models.CharField(max_length = 17)
    description = models.CharField(max_length = 150)

class DeviceType(models.Model):
    name = models.CharField(max_length = 20)
    description = models.CharField(max_length = 150)

class Device(models.Model):
    mac_address = models.CharField(max_length = 17)
    name = models.CharField(max_length = 50, null=True)
    policy = models.ForeignKey(Policy, null=True)
    device_type = models.ForeignKey(DeviceType, null=True)

