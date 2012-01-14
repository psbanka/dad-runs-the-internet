import syslog
import time
import sys
from downloader import Downloader
from uploader import upload_arp_table
from util import log_open_files

from Exceptions import DownloadException, UploadException, CommandException

MAX_LOOPS = 0
INTER_LOOP_SLEEP = 10

class DriDaemon:

    def __init__(self):
        self.kill_switch = False
        self.loops = 0
        self.downloader = Downloader()

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
            syslog.syslog(syslog.LOG_INFO, "I LIVE")
            #print "I LIVE"

    def terminate(self):
        self.kill_switch = True
        print "dying"

