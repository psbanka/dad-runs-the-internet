from django.shortcuts import render_to_response
from django.template import RequestContext
from dojango.decorators import json_response
from forms import DeviceForm
from django.core.context_processors import csrf

def index(request):
    return render_to_response("frontend/index.html", context_instance=RequestContext(request))

@json_response
def known_devices(request):
    devices = { "Windows computers" : [
                    "58:94:6b:a4:da:bc",
                    "48:5b:39:f8:5d:f9",
                ],
                "Apple mobile devices": [
                    "58:94:6b:a4:d7:bc",
                    "48:57:39:78:5d:f9",
                ]
              }
    return {"devices": devices}

def edit_device(request, device_name):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
    else:
        form = DeviceForm(initial={"device_name": "Jeremy's iPod"})
    model = {"form": form, "device_name": device_name}
    model.update(csrf(request))
    return render_to_response("frontend/edit_device_form.html", model)
