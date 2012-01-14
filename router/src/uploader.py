#!/opt/bin/python2.7

import os
import re
from commands import getstatusoutput as gso
import syslog
import tempfile
from util import run_or_die, OK, FAIL
from Exceptions import UploadException

TEST_FILE = '/etc/passwd'
#URL = "http://falling-stone-8827.herokuapp.com//arp_upload/"
URL = "http://freezing-frost-9935.herokuapp.com/arp_upload/"

def grab_csrf():
    cmd = "curl -c /tmp/cookies.txt %s 2>/dev/null" % URL
    output = run_or_die(cmd)
    matches = re.compile("name='csrfmiddlewaretoken' value='(\S+)'" ).findall(output)
    if not matches:
        syslog.syslog(syslog.LOG_ERR, "Could not detect csrf from server")
        raise UploadException(URL, output)
    return matches[0]

def upload_file(csrf, filename):
    cmd = "curl -b /tmp/cookies.txt -F 'docfile=@%s' "\
          "-F 'csrfmiddlewaretoken=%s' %s 2>/dev/null" % (filename, csrf, URL)
    output = run_or_die(cmd)
    if output == "cool.":
        return OK
    return output
    
def upload(filename):
    csrf = grab_csrf()
    return upload_file(csrf, filename)

def upload_arp_table():
    arp_data = run_or_die('arp -an')
    fd, file_name = tempfile.mkstemp(prefix="arp_")
    open(file_name, 'w').write(arp_data)
    output = upload(file_name)
    if output == OK:
        gso('rm -f %s' % file_name)
        os.close(fd)
        return OK
    os.close(fd)
    syslog.syslog(syslog.LOG_ERR, "Error uploading")
    raise UploadException(URL, output)

if __name__ == "__main__":
    #print "(%s)" % upload(TEST_FILE)
    print "(%s)" % upload_arp_table()
