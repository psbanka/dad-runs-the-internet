from django.shortcuts import render_to_response
from django.template import RequestContext
from dojango.decorators import json_response
from forms import DeviceForm
from django.core.context_processors import csrf
from models import DeviceType, Device, Policy
from django.http import HttpResponse
import logging
import pprint

def index(request):
    return render_to_response("frontend/index.html", context_instance=RequestContext(request))

def log_object(object, title='', max_lines=0):
    "Sometimes you just have to log an entire object out"
    logger = logging.getLogger('dri.custom')
    if title:
        logger.info(title.upper().ljust(50,'-'))
    current_line = 0
    for line in pprint.pformat(object).split('\n'):
        logger.info(">> %s" % line)
        current_line += 1
        if max_lines:
            if current_line > max_lines:
                break
    if title:
        logger.info(title.upper().ljust(50,'='))

@json_response
def known_devices(request):
    output = {}
    logger = logging.getLogger('dri.custom')
    logger.info("pulling device names")
    for record in Device.objects.all():
        device_description = "Unknown device-type"
        if record.device_type is not None:
            device_description = record.device_type.description
            logger.info("The device has a TYPE!!: (%s)" % record.device_type)
        device_name = record.mac_address
        if record.name is not None:
            logger.info("The device has a name!!: (%s)" % record.name)
            device_name = record.name
        try:
            output[device_description].append(device_name)
        except KeyError:
            output[device_description] = [device_name]
    return {"devices": output}

def edit_device(request, device_name):
    logger = logging.getLogger('dri.custom')
    if request.method == 'POST':
        logger.info("dealing with a POST")
        form = DeviceForm(request.POST)
        log_object(request.POST)
        if not form.errors:
            submitted_mac = request.POST.get("mac_address")
            submitted_policy = request.POST.get('policy')
            submitted_device_type = request.POST.get('device_type')
            try:
                logger.info("fetching object...")
                device = Device.objects.get(mac_address=submitted_mac)
                logger.info("got it!")
            except Exception: # FIXME: catch DoesNotExist
                logger.info("NO object! Bailing out!")
                return HttpResponse("Name: (%s) does not exist in the database." % submitted_mac)

            logger.info("setting stuff...")
            device.name = request.POST.get('device_name')
            try:
                logger.info("fetching policy...")
                policy = Policy.objects.get(name=submitted_policy)
                logger.info("got it!")
                device.policy = policy
            except Exception: # FIXME: catch DoesNotExist
                logger.info("NO POLICY object! Bailing out!")
                return HttpResponse("POLICY: (%s) does not exist in the database." % submitted_policy)

            try:
                logger.info("fetching device_type...")
                device_type = DeviceType.objects.get(name=submitted_device_type)
                logger.info("got it!")
                device.device_type = device_type
            except Exception: # FIXME: catch DoesNotExist
                logger.info("NO DEVICE_TYPE object! Bailing out!")
                return HttpResponse("DEVICE_TYPE: (%s) does not exist in the database." % submitted_device_type)

            logger.info("saving...")
            device.save()
            logger.info("all good")
            return HttpResponse("<h1>SAVED</h1>")
    else:
        try:
            device = Device.objects.get(mac_address=device_name)
        except Exception: # FIXME catch DoesNotExist
            try:
                device = Device.objects.get(name=device_name)
            except Exception: # FIXME catch DoesNotExist
                return HttpResponse("can't look that record up: (%s)" % device_name)
        logger.info("dealing with a GET")
        policy = None if not device.policy else device.policy.name
        device_type = None if not device.device_type else device.device_type.name
        form = DeviceForm(initial={"device_name": device.name,
                                   "mac_address": device.mac_address,
                                   "device_type": device_type,
                                   "policy"     : policy})
    model = {"form": form, "device_name": device_name}
    model.update(csrf(request))
    return render_to_response("frontend/edit_device_form.html", model)
