from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response
from django.template import RequestContext
from dojango.decorators import json_response
from forms import LoginForm
from django.core.context_processors import csrf
from django.http import HttpResponse
#from libs import log_object
import logging

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
    "Obtain the login form"
    if request.method != 'GET':
        return HttpResponse("Use a GET")

    form = LoginForm()
    model = {"form": form}
    model.update(csrf(request))
    return render_to_response("frontend/login_form.html", model)

@json_response
def login_post(request):
    "Attempt to log in"
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
            model['username'] = user.username
            model['full_name'] = user.get_full_name()
            #model['permissions'] = user.user_permissions
        else:
            model["success"] = False
            model["message"] = "Account disabled"
            logger.info("Disabled account (%s) attempted login" % username)
    else:
        logger.info("Invalid login attempt from (%s)" % username)
        model["success"] = False
        model["message"] = "Invalid username and/or password"
    return model

