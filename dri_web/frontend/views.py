from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response
from django.template import RequestContext
from dojango.decorators import json_response
from forms import DeviceForm, ArpUploadForm, LoginForm
from models import ArpDocument
from django.core.context_processors import csrf
from models import DeviceType, Device, Policy, TemporaryApproval
from django.http import HttpResponse
from libs import log_object
import logging
import StringIO
import re

def index(request):
    """
    Provides the root page
    """
    model = {}
    if request.user.is_authenticated():
        model['username'] = request.user.username
    else:
        model['username'] = '__ANONYMOUS'
    return render_to_response("frontend/index.html", model,
        context_instance=RequestContext(request))

def login_get(request):
    if request.method != 'GET':
        return HttpResponse("Use a GET")

    form = LoginForm()
    model = {"form": form}
    model.update(csrf(request))
    return render_to_response("frontend/login_form.html", model)

@json_response
def login_post(request):
    if request.method != 'POST':
        return HttpResponse("Use a POST")
    model = {}
    logger = logging.getLogger('dri.custom')
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            model["success"] = True
            model["message"] = ""
        else:
            model["success"] = False
            model["message"] = "Account disabled"
            logger.info("Disabled account (%s) attempted login" % username)
    else:
        logger.info("Invalid login attempt from (%s)" % username)
        model["success"] = False
        model["message"] = "Invalid username and/or password"
    return model

def _upload_process(arp_data):
    """
    Update the database based on ARP entries
    """
    logger = logging.getLogger('dri.custom')
    matcher = re.compile('\((\d+\.\d+\.\d+.\d+)\) at (\S+) ')
    for line in arp_data.split('\n'):
        match_sets = matcher.findall(line)
        if not match_sets:
            logger.error(">>> UPLOAD: ignoring line (%s) " % line)
            continue
        for match_set in match_sets:
            #logger.info( ">>> UPLOAD: processing data: %s" % str(match_set))
            ip_address, mac_address = match_set
            if ip_address == "<incomplete>":
                logger.info( ">>> UPLOAD: Ignoring incomplete-data for: %s" % mac_address)
                continue
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
    #logger = logging.getLogger('dri.custom')
    if request.method == 'POST':
        form = ArpUploadForm(request.POST, request.FILES)
        if form.is_valid():
            output = StringIO.StringIO()
            for chunk_name, file_chunk in request.FILES.iteritems():
                #logger.info("CHUNK: %s" % chunk_name)
                output.write( file_chunk.read() )

            output.seek(0)
            _upload_process(output.read())
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
def iptables_download(request):
    """
    A router wants to know what to do with itself
    """
    response = {"allowed": [],
                "blocked": []
               }
    for device in Device.objects.all():
        section_name = "allowed" if device.is_allowed() else "blocked"
        new_entry = {"mac_address": device.mac_address, "ip_address": device.ip_address}
        response[section_name].append(new_entry)
    return response

#@login_required
@json_response
def known_devices(request):
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
        except Exception: # FIXME catch DoesNotExist
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
    except Exception: # FIXME (does not exist)
        msg = "Bad device name provided: (%s)" % request.POST.get("mac_address")
        logger.info(msg)
        output["success"] = False
        output['message'] = msg
    log_object(output, "MY OUTPUT")
    return output

@login_required
def edit_device(request, mac_address):
    """
    The user has been shown a list of devices on his network. He wants
    to edit one: give it a name, assign it a policy, whatever.
    """
    logger = logging.getLogger('dri.custom')
    device_name = "Unknown"
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        log_object(request.POST)
        if not form.errors:
            submitted_policy = request.POST.get('policy')
            submitted_device_type = request.POST.get('device_type')
            submitted_device_name = request.POST.get('device_name')
            try:
                device = Device.objects.get(mac_address=mac_address)
            except Exception: # FIXME: catch DoesNotExist
                logger.info("NO object! Bailing out!")
                return HttpResponse("Name: (%s) does not exist in the database." % mac_address)

            device.name = submitted_device_name
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
            device = Device.objects.get(mac_address=mac_address)
            policy = None if not device.policy else device.policy.name
            device_type = None if not device.device_type else device.device_type.name
            form = DeviceForm(initial={"device_name": device.name,
                                       "mac_address": device.mac_address,
                                       "device_type": device_type,
                                       "device_allowed": str(device.is_allowed()),
                                       "policy"     : policy})
            device_name = device.name
        except Exception: # FIXME catch DoesNotExist
            return HttpResponse("can't look that record up: (%s)" % mac_address)

    model = {"form": form, "device_name": device_name, "mac_address": mac_address}
    model.update(csrf(request))
    return render_to_response("frontend/edit_device_form.html", model)




