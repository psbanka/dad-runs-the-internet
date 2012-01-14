from django.shortcuts import render_to_response
from django.template import RequestContext
import logging
#from libs import log_object

def _detect_platform(request):
    """
    Try to determine what kind of device we're being hit with
    """
    output = {"platform": "unknown",
              "mobile": False,
             }
    if "Android" in request.META['HTTP_USER_AGENT']:
        output['mobile'] = True
        output['platform'] = "android"
    elif "iPad" in request.META['HTTP_USER_AGENT']:
        output['mobile'] = True
        output['platform'] = "apple"
    elif "iPhone" in request.META['HTTP_USER_AGENT']:
        output['mobile'] = True
        output['platform'] = "apple"
    elif "iPod" in request.META['HTTP_USER_AGENT']:
        output['mobile'] = True
        output['platform'] = "apple"
    return output

def index(request):
    """
    Provides the root page
    """
    logger = logging.getLogger('dri.custom')
    model = _detect_platform(request)
    logger.info("request from %s" % model['platform'])
    if request.user.is_authenticated():
        model['username'] = request.user.username
    else:
        model['username'] = '__ANONYMOUS'
    return render_to_response("frontend/m.html", model,
        context_instance=RequestContext(request))

