# Create your views here.
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from dojango.decorators import json_response

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
    model = {"joe": "joe is cool", "devices": devices}
    return render_to_response("frontend/known_devices.html", model)

