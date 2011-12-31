# Create your views here.
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext

def first_page(request):
    return render_to_response("frontend/my_first_page.html", context_instance=RequestContext(request))

def index(request):
    return render_to_response("frontend/index.html", context_instance=RequestContext(request))
