import syslog
import time
import sys
from downloader import Downloader
from uploader import upload_arp_table
from policy_mgr import DnsCacheMon
from util import log_open_files
import json
from DaemonBase import DaemonBase

from Exceptions import DownloadException, UploadException
from Exceptions import CommandException, PolicyMgrException

MAX_LOOPS = 0
INTER_LOOP_SLEEP = 10
ALLOWED_NAMES = [
".*.nist.gov",
".*.google.com",
".*amazonaws.com",
"freezing-frost-9935.herokuapp.com",
"ssl.gstatic.com",
".*.lastpass.com",
"ar.herokuapp.com",
".*.atlassian.net",
".*.googleapis.com",
".*.pool.ntp.org",
".*.accuweather.com",
".*.dictionary.com",
".*.evernote.com",
".*gpsonextra.net",
".*.feedburner.net",
".*.wikipedia.org",
]

class DriDaemon(DaemonBase):

    def __init__(self, options):
        DaemonBase.__init__(self, options)
        self.kill_switch = False
        self.loops = 0
        self.downloader = Downloader()
        self.dns_cache_mon = DnsCacheMon("/tmp/dnsmasq.log", ALLOWED_NAMES,
            self.options)
        print('Loading initial rules....')
        rules_loaded = self.dns_cache_mon.initial_load()
        print('Loaded %s targets.' % rules_loaded)

    def main_loop(self):
        self.log('Starting dri...')

        while not self.kill_switch:
            start_time = time.time()
            while time.time() < (start_time + INTER_LOOP_SLEEP):
                try:
                    has_more = self.dns_cache_mon.check_for_new_stuff()
                    if not has_more:
                        time.sleep(1)
                except (PolicyMgrException, CommandException):
                    self.log('Help! Policy Manager')

            if MAX_LOOPS:
                self.loops += 1
                if self.loops > MAX_LOOPS:
                    sys.exit(0)
            try:
                self.downloader.run()
                log_open_files("downloader")
            except (DownloadException, CommandException):
                self.log('Help! Downloading')
            try:
                upload_arp_table()
                log_open_files("uploader")
            except (UploadException, CommandException):
                self.log('Help! Uploading')
            #print "I LIVE"

    def terminate(self):
        self.kill_switch = True
        print "dying"

if __name__ == "__main__":
    class Options:
        def __init__(self):
            self.no_daemonize = True
            self.verbose = False
            self.test = False

    DriDaemon(Options()).main_loop()
