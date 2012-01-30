#!/opt/bin/python2.7

import os
import re
from commands import getstatusoutput as gso
import tempfile
from util import run_or_die, OK
from Exceptions import UploadException
from DaemonBase import DaemonBase

TEST_FILE = '/etc/passwd'
#URL = "http://falling-stone-8827.herokuapp.com//arp_upload/"
#URL = "http://freezing-frost-9935.herokuapp.com/arp_upload/"

class Uploader(DaemonBase):
    "Handles uploading all information to the central server"

    def __init__(self, options):
        DaemonBase.__init__(self, options)

    def grab_csrf(self):
        """
        We have to pull the CSRF from the website in order to keep the
        server happy.
        """
        cmd = "curl -c /tmp/cookies.txt %s/arp_upload/ 2>/dev/null" % self.options.server_url
        output = run_or_die(cmd)
        matches = re.compile("name='csrfmiddlewaretoken' value='(\S+)'" ).findall(output)
        if not matches:
            self.log("Could not detect csrf from server")
            raise UploadException(self.options.server_url, output)
        return matches[0]

    def _upload_file(self, filename):
        "Take an arbitrary file and sends it to the server"
        csrf = self.grab_csrf()
        cmd = "curl -b /tmp/cookies.txt -F 'docfile=@%s' "\
              "-F 'csrfmiddlewaretoken=%s' %s/arp_upload/ 2>/dev/null" % (filename, csrf, self.options.server_url)
        output = run_or_die(cmd)
        if output == "cool.":
            return OK
        return output
        
    def upload_arp_table(self):
        "Responsible for sending everything of value to the server"
        arp_data = run_or_die('arp -an')
        fd, file_name = tempfile.mkstemp(prefix="arp_")
        open(file_name, 'w').write(arp_data)
        output = self._upload_file(file_name)
        if output == OK:
            gso('rm -f %s' % file_name)
            os.close(fd)
            return OK
        os.close(fd)
        self.log("Error uploading")
        raise UploadException(self.options.server_url, output)

if __name__ == "__main__":
    class Options:
        def __init__(self):
            self.no_daemonize = True
            self.verbose = True
            self.test = True
            self.server_url = "http://127.0.0.1:8000"
    uploader = Uploader(Options())
    print "(%s)" % uploader.upload_arp_table()
