from django.db import models

class Policy(models.Model):
    name = models.CharField(max_length = 17)

class Device(models.Model):
    mac_address = models.CharField(max_length = 17)
    name = models.CharField(max_length = 50)
    policy = models.ForeignKey(Policy)

