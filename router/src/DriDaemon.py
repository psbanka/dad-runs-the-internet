import time
import sys
from downloader import Downloader
from uploader import Uploader
from PolicyMgr import PolicyMgr
from util import log_open_files
from DaemonBase import DaemonBase

from Exceptions import DownloadException, UploadException
from Exceptions import CommandException, PolicyMgrException

MAX_LOOPS = 0
INTER_LOOP_SLEEP = 10
ALLOWED_NAMES = {
"time": [".*.nist.gov", ".*.pool.ntp.org",],
"google": [".*.google.com", "ssl.gstatic.com",],
"dri": [ ".*amazonaws.com", "freezing-frost-9935.herokuapp.com", "ar.herokuapp.com", ".*.googleapis.com",],
"lastpass": [".*.lastpass.com",],
"dev": [".*.atlassian.net",],
"weather": [ ".*.accuweather.com",],
"learning": [".*.dictionary.com", ".*.wikipedia.org",],
"evernote": [".*.evernote.com",],
"mapping": [".*gpsonextra.net",],
"podcasts": [".*.feedburner.net",],
}

class DriDaemon(DaemonBase):

    """
    Manages all functions that need to take place on the router
    on a regular basis
    """

    def __init__(self, options):
        DaemonBase.__init__(self, options)
        self.kill_switch = False
        self.loops = 0
        self.downloader = Downloader(options)
        self.uploader = Uploader(options)
        self.allowed_traffic = self.downloader.get_allowed_traffic()
        self.policy_mgr = PolicyMgr("/tmp/dnsmasq.log", self.allowed_traffic,
            self.options)
        self.policy_mgr.prep_system()
        self.policy_mgr.initial_load()
        self.policy_mgr.rotate_log()

    def main_loop(self):
        """
        Runs forever. We're a daemon
        """
        self.log('Starting dri...')

        while not self.kill_switch:
            start_time = time.time()
            while time.time() < (start_time + INTER_LOOP_SLEEP):
                try:
                    has_more = self.policy_mgr.check_for_new_stuff()
                    if not has_more:
                        time.sleep(1)
                except (PolicyMgrException, CommandException):
                    self.log('Help! Policy Manager')

            if MAX_LOOPS:
                self.loops += 1
                if self.loops > MAX_LOOPS:
                    sys.exit(0)
            try:
                self.downloader.get_addresses()
                allowed_traffic = self.downloader.get_allowed_traffic()
                self.policy_mgr.process_new_allowed(allowed_traffic)
                log_open_files("downloader")
            except (DownloadException, CommandException):
                self.log('Help! Downloading')
            try:
                self.uploader.upload_arp_table()
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
            self.prep_system = True
            self.max_log_size = 500
            self.no_load = False
            self.server_url = "http://freezing-frost-9935.herokuapp.com"

    DriDaemon(Options()).main_loop()
