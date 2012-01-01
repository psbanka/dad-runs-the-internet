#!/opt/bin/python2.7

import re
from commands import getstatusoutput as gso
import sys
import tempfile
from util import run_or_die, OK, FAIL

TEST_FILE = '/etc/passwd'
URL = "http://192.168.11.114:8080/arp_upload/"

def grab_csrf():
    cmd = "curl -c /tmp/cookies.txt %s 2>/dev/null" % URL
    output = run_or_die(cmd)
    matches = re.compile("name='csrfmiddlewaretoken' value='(\S+)'" ).findall(output)
    if not matches:
        print "Could not detect csrf from server:"
        #print output
        sys.exit(1)
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
    fh, file_name = tempfile.mkstemp(prefix="arp_")
    open(file_name, 'w').write(arp_data)
    output = upload(file_name)
    if output == OK:
        gso('rm -f %s' % file_name)
        return OK
    return output

if __name__ == "__main__":
    #print "(%s)" % upload(TEST_FILE)
    print "(%s)" % upload_arp_table()
