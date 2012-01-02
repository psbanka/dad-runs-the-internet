from django.db import models
from datetime import datetime
import time
import logging

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

    def is_allowed(self):
        "Should this system be allowed or blocked right now?"
        logger = logging.getLogger('dri.custom')
        output = None
        if self.policy is None:
            output = True
            logger.info("device: %s has NO POLICY" % self.mac_address)
        elif self.policy.name == "full":
            output = True
        elif self.policy.name == "blocked":
            output = False
        elif self.policy.name == "upon-request":
            output = False
            for temporary_approval in TemporaryApproval.objects.filter(device=self):
                logger.info("checking approval: %s" % temporary_approval.end_time)
                if temporary_approval.is_current():
                    logger.info("it's current")
                    output = True
                    break        
            logger.info("approval-based node is: %s" % output)
        else:
            logger.error("Unknown policy (%s) in the system for: %s" % (self.policy.name, self.name))
            output = False
        return output
 
class ArpDocument(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

class TemporaryApproval(models.Model):
    device = models.ForeignKey(Device)
    start_time = models.DateTimeField(editable=False)
    end_time = models.DateTimeField()

    def set_parameters(self, duration_minutes):
        "Generate a record based on number of minutes"
        self.start_time = datetime.now()
        now_timestamp = time.time()
        end_timestamp = now_timestamp + (duration_minutes * 60.0)
        self.end_time = datetime.fromtimestamp(end_timestamp)

    def is_current(self):
        """
        Determine if my record still applies
        """
        return self.end_time >= datetime.now()
