from django.shortcuts import render_to_response
from django.template import RequestContext
from dojango.decorators import json_response
from forms import DeviceForm
from django.core.context_processors import csrf
from models import DeviceType, Device

def index(request):
    return render_to_response("frontend/index.html", context_instance=RequestContext(request))

@json_response
def known_devices(request):
    output = {}
    for record in Device.objects.all():
        device_type = "Unknown device-type"
        if record.device_type is not None:
            device_type = record.device_type
        device_name = record.mac_address
        if record.name is not None:
            device_name = record.name
        try:
            output[device_type].append(device_name)
        except KeyError:
            output[device_type] = [device_name]
    return {"devices": output}

def edit_device(request, device_name):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
    else:
        form = DeviceForm(initial={"device_name": "Jeremy's iPod"})
    model = {"form": form, "device_name": device_name}
    model.update(csrf(request))
    return render_to_response("frontend/edit_device_form.html", model)
