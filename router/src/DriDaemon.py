import syslog
import time
import sys
from downloader import Downloader
from uploader import upload_arp_table

from Exceptions import DownloadException, UploadException

MAX_LOOPS = 0

class DriDaemon:

    def __init__(self):
        self.kill_switch = False
        self.loops = 0
        self.downloader = Downloader()

    def main_loop(self):
        syslog.syslog('Starting dri...')

        while not self.kill_switch:
            time.sleep(1)
            if MAX_LOOPS:
                self.loops += 1
                if self.loops > MAX_LOOPS:
                    sys.exit(0)
            try:
                self.downloader.run()
            except DownloadException:
                syslog.syslog('Help! Downloading')
            try:
                upload_arp_table()
            except UploadException:
                syslog.syslog('Help! Uploading')
            syslog.syslog(syslog.LOG_INFO, "I LIVE")
            #print "I LIVE"

    def terminate(self):
        self.kill_switch = True
        print "dying"

