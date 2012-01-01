from django.shortcuts import render_to_response
from django.template import RequestContext
from dojango.decorators import json_response
from forms import DeviceForm, ArpUploadForm
from models import ArpDocument
from django.core.context_processors import csrf
from models import DeviceType, Device, Policy
from django.http import HttpResponse
import logging
import pprint
import StringIO
import re

def index(request):
    """
    Provides the root page
    """
    return render_to_response("frontend/index.html",
        context_instance=RequestContext(request))

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

def upload_process(arp_data):
    """
    Update the database based on ARP entries
    """
    logger = logging.getLogger('dri.custom')
    matcher = re.compile('\((\d+\.\d+\.\d+.\d+)\) at (\S+) ')
    for line in arp_data.split('\n'):
        match_sets = matcher.findall(line)
        if not match_sets:
            logger.error(">>> NO MATCH (%s) " % line)
            continue
        for match_set in match_sets:
            logger.info( ">>> MATCH %s" % str(match_set))
            ip_address, mac_address = match_set
            records = Device.objects.filter(mac_address = mac_address)
            if len(records) == 0:
                device = Device()
            else:
                if len(records) > 1:
                    logger.error("Too many records for %s" % mac_address)
                device = records[0]
            device.mac_address = mac_address
            device.ip_address = ip_address
            device.save()

def arp_upload(request, filename = None):
    """
    Routers are uploading their ARP tables, accept and process it.
    """
    logger = logging.getLogger('dri.custom')
    if request.method == 'POST':
        form = ArpUploadForm(request.POST, request.FILES)
        if form.is_valid():
            output = StringIO.StringIO()
            for chunk_name, file_chunk in request.FILES.iteritems():
                logger.info("CHUNK: %s" % chunk_name)
                output.write( file_chunk.read() )

            output.seek(0)
            upload_process(output.read())
            return HttpResponse("cool.")
    else:
        form = ArpUploadForm() # A empty, unbound form

    # Load documents for the list page
    documents = ArpDocument.objects.all()

    # Render list page with the documents and the form
    model = {'documents': documents, 'form': form}
    return render_to_response("frontend/arp_upload_form.html", model,
        context_instance=RequestContext(request))


@json_response
def known_devices(request):
    """
    Used to populate the navigation screen on the left hand side of the
    application to display what hosts are on your network.
    """
    output = {}
    for record in Device.objects.all():
        device_description = "Unknown device-type"
        if record.device_type is not None:
            device_description = record.device_type.description
        device_name = record.mac_address
        if record.name is not None:
            device_name = record.name
        try:
            output[device_description].append(device_name)
        except KeyError:
            output[device_description] = [device_name]
    return {"devices": output}

def edit_device(request, device_name):
    """
    The user has been shown a list of devices on his network. He wants
    to edit one: give it a name, assign it a policy, whatever.
    """
    logger = logging.getLogger('dri.custom')
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        log_object(request.POST)
        if not form.errors:
            submitted_mac = request.POST.get("mac_address")
            submitted_policy = request.POST.get('policy')
            submitted_device_type = request.POST.get('device_type')
            try:
                device = Device.objects.get(mac_address=submitted_mac)
            except Exception: # FIXME: catch DoesNotExist
                logger.info("NO object! Bailing out!")
                return HttpResponse("Name: (%s) does not exist in the database." % submitted_mac)

            device.name = request.POST.get('device_name')
            try:
                policy = Policy.objects.get(name=submitted_policy)
                device.policy = policy
            except Exception: # FIXME: catch DoesNotExist
                logger.info("NO POLICY object! Bailing out!")
                return HttpResponse("POLICY: (%s) does not exist in the database." % submitted_policy)

            try:
                device_type = DeviceType.objects.get(name=submitted_device_type)
                device.device_type = device_type
            except Exception: # FIXME: catch DoesNotExist
                logger.info("NO DEVICE_TYPE object! Bailing out!")
                return HttpResponse("DEVICE_TYPE: (%s) does not exist in the database." % submitted_device_type)

            device.save()
            return HttpResponse("<h1>SAVED</h1>")
    else:
        try:
            device = Device.objects.get(mac_address=device_name)
        except Exception: # FIXME catch DoesNotExist
            try:
                device = Device.objects.get(name=device_name)
            except Exception: # FIXME catch DoesNotExist
                return HttpResponse("can't look that record up: (%s)" % device_name)
        policy = None if not device.policy else device.policy.name
        device_type = None if not device.device_type else device.device_type.name
        form = DeviceForm(initial={"device_name": device.name,
                                   "mac_address": device.mac_address,
                                   "device_type": device_type,
                                   "policy"     : policy})
    model = {"form": form, "device_name": device_name}
    model.update(csrf(request))
    return render_to_response("frontend/edit_device_form.html", model)
