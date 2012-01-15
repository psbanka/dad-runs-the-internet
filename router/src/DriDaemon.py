import syslog
import time
import sys
from downloader import Downloader
from uploader import upload_arp_table
from policy_mgr import DnsCacheMon
from util import log_open_files
import json

from Exceptions import DownloadException, UploadException
from Exceptions import CommandException, PolicyMgrException

MAX_LOOPS = 0
INTER_LOOP_SLEEP = 10
ALLOWED_NAMES = [".*google\.com", ".*amazonaws\.com", "freezing\-frost\-9935\.herokuapp\.com","ssl\.gstatic\.com"
                 "lastpass\.com", "ar\.herokuapp\.com", "pbanka\.atlassian\.net", "ajax\.googleapis\.com", "accounts\.youtube\.com"]

class DriDaemon:

    def __init__(self):
        self.kill_switch = False
        self.loops = 0
        self.downloader = Downloader()
        self.dns_cache_mon = DnsCacheMon("/tmp/dnsmasq.log", ALLOWED_NAMES, False, False)
        self.dns_cache_mon.check_for_new_stuff(500)

    def main_loop(self):
        syslog.syslog('Starting dri...')

        while not self.kill_switch:
            time.sleep(INTER_LOOP_SLEEP)
            if MAX_LOOPS:
                self.loops += 1
                if self.loops > MAX_LOOPS:
                    sys.exit(0)
            try:
                self.downloader.run()
                log_open_files("downloader")
            except (DownloadException, CommandException):
                syslog.syslog('Help! Downloading')
            try:
                upload_arp_table()
                log_open_files("uploader")
            except (UploadException, CommandException):
                syslog.syslog('Help! Uploading')
            try:
                self.dns_cache_mon.check_for_new_stuff()
                log_open_files("policy_mgr")
            except (PolicyMgrException, CommandException):
                syslog.syslog('Help! Policy Manager')
            #print "I LIVE"

    def terminate(self):
        self.kill_switch = True
        print "dying"

