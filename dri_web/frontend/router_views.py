"""
Views made available for interfacing directly with routers in homes
"""


from django.shortcuts import render_to_response
from django.template import RequestContext
from dojango.decorators import json_response
from forms import ArpUploadForm
from models import ArpDocument
from models import Device
from django.http import HttpResponse
import logging
import StringIO
import re

def _process_arp_entry(arp_match_sets):
    """
    We received a line of data from the ARP system on a remote router
    """
    logger = logging.getLogger('dri.custom')
    for match_set in arp_match_sets:
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

def _process_dnslease_entry(dnslease_match_sets):
    """
    We received a line of data from the DNSLEASE system on remote router
    """
    logger = logging.getLogger('dri.custom')
    for match_set in dnslease_match_sets:
        timestamp, mac_addr, ip_address, suggested_name, full_mac_addr = match_set
        records = Device.objects.filter(mac_address = mac_addr.upper())
        if len(records) == 0:
            logger.error("No record found in ARP table for %s" % mac_addr)
            continue
        else:
            if len(records) > 1:
                logger.error("Too many records for %s" % mac_addr)
            device = records[0]
        device.suggested_name = suggested_name
        if device.ip_address != ip_address:
            logger.warning("Could be some hanky-panky: %s" % mac_addr)
        device.save()

def _upload_process(upload_data):
    """
    Update the database based on ARP entries
    """
    logger = logging.getLogger('dri.custom')
    arp_matcher = re.compile('\((\d+\.\d+\.\d+.\d+)\) at (\S+) ')
    dnslease_matcher = re.compile('(\d+)\s(\S+)\s(\S+)\s(\S+)\s(\S+)')
    for line in upload_data.split('\n'):
        arp_match_sets = arp_matcher.findall(line)
        if arp_match_sets:
            _process_arp_entry(arp_match_sets)
            continue
        dnslease_match_sets = dnslease_matcher.findall(line)
        if dnslease_match_sets:
            _process_dnslease_entry(dnslease_match_sets)
            continue
        logger.error(">>> UPLOAD: ignoring line (%s) " % line)

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

