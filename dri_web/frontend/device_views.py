"""
Views for examining and modifying devices in the system
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from dojango.decorators import json_response
from forms import DeviceForm
from django.core.context_processors import csrf
from models import DeviceType, Device, Policy, TemporaryApproval
from django.http import HttpResponse
from libs import log_object
import logging

@login_required
@json_response
def get_known_devices(request):
    """
    Used to populate the navigation screen on the left hand side of the
    application to display what hosts are on your network.
    """
    output = {}
    for record in Device.objects.all():
        if record.mac_address == '<incomplete>':
            continue
        output[record.mac_address] = {'name': record.name,
                                      'type': record.device_type,
                                      'policy': record.policy,
                                      'is_allowed': record.is_allowed(),
                                     }
    output['csrf'] = csrf(request)
    return output

@login_required
@json_response
def enable_device(request):
    """
    The user wants to temporarily enable a device
    """
    logger = logging.getLogger('dri.custom')
    output = {"success": True,
              "message": ""}
    if request.method != 'POST':
        output['success'] = False
        output["message"] = "Must use a POST"
        return output
    mac_address = request.POST.get("mac_address")
    provided_duration = request.POST.get("duration", "30")
    logger.info("IN ENABLE-DEVICES: %s" % mac_address)
    try:
        duration = int(provided_duration)
        device = None
        logger.info("Duration: %s" % duration)
        try:
            device = Device.objects.get(mac_address=mac_address)
            logger.info("device found. Device name: %s" % device.name)
        except Device.DoesNotExist:
            return {"success": False,
                    "message": "can't look that record up: (%s)" % mac_address
                   }
        temporary_approval = TemporaryApproval()
        temporary_approval.device = device
        temporary_approval.set_parameters(duration)
        temporary_approval.save()
        output['message'] = "Saved"
        logger.info("Saving approval")
    except ValueError:
        msg = "Bad duration provided: (%s)" % provided_duration
        logger.info(msg)
        output["success"] = False
        output['message'] = msg
    log_object(output, "MY OUTPUT")
    return output

def _save_device(self, request, mac_address):
    """
    A person is trying to save some new settings on a device
    """

    logger = logging.getLogger('dri.custom')
    form = DeviceForm(request.POST)
    log_object(request.POST)
    if not form.errors:
        submitted_policy = request.POST.get('policy')
        submitted_device_type = request.POST.get('device_type')
        submitted_device_name = request.POST.get('device_name')
        try:
            device = Device.objects.get(mac_address=mac_address)
        except Device.DoesNotExist:
            logger.info("NO object! Bailing out!")
            return HttpResponse("Name: (%s) does not exist in the database." % mac_address)

        device.name = submitted_device_name
        try:
            policy = Policy.objects.get(name=submitted_policy)
            device.policy = policy
        except Policy.DoesNotExist:
            logger.info("NO POLICY object! Bailing out!")
            return HttpResponse("POLICY: (%s) does not exist in the database." % submitted_policy)

        try:
            device_type = DeviceType.objects.get(name=submitted_device_type)
            device.device_type = device_type
        except DeviceType.DoesNotExist:
            logger.info("NO DEVICE_TYPE object! Bailing out!")
            return HttpResponse("DEVICE_TYPE: (%s) does not exist in the database." % submitted_device_type)

        device.save()
        return HttpResponse("<h1>SAVED</h1>")

@login_required
def device(request, mac_address):
    """
    The user has been shown a list of devices on his network. He wants
    to edit one: give it a name, assign it a policy, whatever.
    """
    device_name = "Unknown"
    if request.method == 'POST':
        return _save_device(request, mac_address)
    else:
        try:
            device = Device.objects.get(mac_address=mac_address)
            policy = None if not device.policy else device.policy.name
            device_type = None if not device.device_type else device.device_type.name
            form = DeviceForm(initial={"device_name": device.name,
                                       "mac_address": device.mac_address,
                                       "device_type": device_type,
                                       "device_allowed": str(device.is_allowed()),
                                       "policy"     : policy})
            device_name = device.name
        except Device.DoesNotExist:
            return HttpResponse("can't look that record up: (%s)" % mac_address)

    model = {"form": form, "device_name": device_name, "mac_address": mac_address}
    model.update(csrf(request))
    return render_to_response("frontend/edit_device_form.html", model)

