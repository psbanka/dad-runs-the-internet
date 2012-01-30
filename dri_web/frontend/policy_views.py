"""
Views for examining and modifying policies in the system
"""

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from dojango.decorators import json_response
from django.core.context_processors import csrf
from models import Policy, TrafficPolicy, TrafficMatcher
from libs import log_object
import logging

@json_response
def get_policies(request):
    """
    Obtain a list of current allowed websites for low-privilege users
    """
    output = {}
    for policy in Policy.objects.all():
        output[policy.name] = policy.dump_exceptions()
    return {'message': output, 'success': True}

def _purge_traffic_matchers(traffic_policy):
    """
    Need to get rid of existing traffic_matcher entries to make way for a new set
    """
    traffic_matchers = TrafficMatcher.objects.filter(traffic_policy = traffic_policy.id)
    for traffic_matcher in traffic_matchers:
        traffic_matcher.delete()

def _save_policy(request, traffic_policy_name):
    """
    A user is saving changes to a traffic_policy
    """
    logger = logging.getLogger('dri.custom')
    log_object(request.POST)
    description = request.POST.get('description')
    try:
        traffic_policy = TrafficPolicy.objects.get(name=traffic_policy_name)
    except TrafficPolicy.DoesNotExist:
        logger.info("NO object! Bailing out!")
        msg = "Name: (%s) does not exist in the database." % traffic_policy_name
        return {"success": False,
                "message": msg,
               }

    traffic_policy.description = description
    _purge_traffic_matchers(traffic_policy)
    for index in xrange(0, len(request.POST.keys())):
        object_name = "regex_%d" % index
        if object_name in request.POST.keys():
            logger.info("Post: %s // %s" % (object_name, request.POST.get(object_name)))
            regex = request.POST.get(object_name).strip()
            if regex:
                traffic_matcher = TrafficMatcher(regex = regex, traffic_policy=traffic_policy)
                traffic_matcher.save()
    traffic_policy.save()
    return {"success": True,
            "message": "Saved",
           }

@login_required
@json_response
def edit_traffic_policy(request, traffic_policy_name):
    """
    The user has been shown a list of devices on his network. He wants
    to edit one: give it a name, assign it a policy, whatever.
    """
    #logger = logging.getLogger('dri.custom')
    if request.method == 'POST':
        return _save_policy(request, traffic_policy_name)
    else:
        try:
            traffic_policy = TrafficPolicy.objects.get(name=traffic_policy_name)
            description = traffic_policy.description
            traffic_matchers = TrafficMatcher.objects.filter(traffic_policy = traffic_policy.id)
            model = {"traffic_policy": traffic_policy.name,
                     "description": description,
                     "traffic_matchers": [tm.regex for tm in traffic_matchers]}
            model.update(csrf(request))
            return model
        except TrafficPolicy.DoesNotExist:
            return HttpResponse("can't look that record up: (%s)" % traffic_policy_name)


