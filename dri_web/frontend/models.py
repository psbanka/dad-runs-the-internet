from django.db import models
from datetime import datetime
import time
import logging

class Policy(models.Model):
    """
    A policy is applied to a device. It indicates how the router should treat
    all traffic from the device
    """
    name = models.CharField(max_length = 17)
    description = models.CharField(max_length = 150)

    def dump_exceptions(self):
        """
        There are exceptions to a policy. This will show them all as a dictionary of lists
        """
        output = {}
        for tp_record in TrafficPolicy.objects.filter(policy = self.id):
            tm_records = TrafficMatcher.objects.filter(traffic_policy = tp_record.id)
            output[tp_record.name] = [rec.regex for rec in tm_records]
        return output

class TrafficPolicy(models.Model):
    """
    Applies a set of filters to be implemented when a policy is in place for
    a set of devices on a home network.
    """
    description = models.CharField(max_length = 50, null=True)
    name = models.CharField(max_length = 20, null=False)
    policy = models.ForeignKey(Policy, null=False)

class TrafficMatcher(models.Model):
    """
    Coupled with TrafficPolicy, this provides a set of regular expressions
    that are used to tag traffic
    """
    regex = models.CharField(max_length = 150)
    traffic_policy = models.ForeignKey(TrafficPolicy, null=False)

class DeviceType(models.Model):
    """
    DeviceTypes provide categorization and documentation for devices.
    """
    name = models.CharField(max_length = 20)
    description = models.CharField(max_length = 150)

class Device(models.Model):
    """
    Devices are things on a network that want to send traffic through the
    home firewall and out to the network.
    """
    name = models.CharField(max_length = 50, null=True)
    mac_address = models.CharField(max_length = 17, primary_key = True)
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
    """
    This is being uploaded from the home router to tell us what MAC addresses
    are live.
    """
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

class TemporaryApproval(models.Model):
    """
    For devices that are not allowed full access to the Internet, it is
    possible to provide temporary access by adding an entry to this table.
    """
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
