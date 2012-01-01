#!/opt/bin/python2.7

import optparse
import sys
from signal import SIGTERM
import os
import traceback
from util import OK, FAIL
import time
import resource
from downloader import Downloader
from uploader import upload_arp_table
import syslog

DEFAULT_PID_DIR = "/opt/var/run"
PID_FILE = "dri_router.pid"
DEBUG_TRACE = True
MAX_LOOPS = 10
MAXFD = 1024

def trace_exit(value):
    "Scratch traceback so we can tell where something exited."
    if DEBUG_TRACE:
        traceback.print_stack()
    sys.exit(value)

def stop_pid_file(file_name, service_name):
    "Stops a service based on the PID file"
    if not os.path.isfile(file_name):
        msg = "Can't stop "+service_name+" (can't find PID file %s)."
        print msg % file_name
        return OK
    pid = open(file_name).read().strip()
    print "Stopping "+service_name+" ("+pid+")...",
    try:
        os.kill(int(pid), SIGTERM)
        print "OK"
        status = OK
    except OSError:
        print "FAILED"
        status = FAIL
    os.system("rm -f %s" % file_name)
    return status

class Daemon:

    def __init__(self):
        self.kill_switch = False
        self.loops = 0
        self.downloader = Downloader()

    def main_loop(self):
        syslog.syslog('Starting dri...')
        #syslog.syslog(syslog.LOG_ERR, 'Processing started')

        while not self.kill_switch:
            time.sleep(1)
            self.loops += 1
            if self.loops > MAX_LOOPS:
                sys.exit(0)
            self.downloader.run()
            upload_arp_table() 
            syslog.syslog(syslog.LOG_INFO, "I LIVE")
            #print "I LIVE"

    def terminate(self):
        self.kill_switch = True
        print "dying"

class Daemonizer:
    "Runs the dri service(s)"

    def __init__(self, options):
        self.opts = options
        self.pid_file = os.path.join(self.opts.pid_dir, PID_FILE)

    def main_process_loop(self):
        "This runs the dispatcher process"

        daemon = Daemon()
        pid = str(os.getpid())
        try:
            open(self.pid_file, 'w').write( "%s\n" % pid )
        except:
            daemon.terminate("not_root")
        daemon.main_loop()

    def refork(self):
        "Inner fork, sets up Dispatcher"
        os.setsid()
        try:
            pid = os.fork()
        except OSError, err:
            raise Exception, "%s [%d]" % (err.strerror, err.errno)

        if (pid != 0):
            pass
            #trace_exit(0)
        else:
            self.main_process_loop()

    def start(self):
        "Create a deamon process"

        if os.path.isfile(self.pid_file):
            print "Cannot start: (%s) already exists" % self.pid_file
            trace_exit(1)

        pid = 0
        try:
            pid = os.fork()
        except OSError, err:
            raise Exception, "%s [%d]" % (err.strerror, err.errno)

        if (pid == 0):
            self.refork()

        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if (maxfd == resource.RLIM_INFINITY):
            maxfd = MAXFD

        for file_descriptor in range(0, maxfd):
            try:
                os.close(file_descriptor)
            except OSError:
                pass
        os.dup2(0, 1)
        os.dup2(0, 2)

    def stop(self):
        "Stop the daemon"
        return stop_pid_file(self.pid_file, "dri_daemon")

def main():
    parser = optparse.OptionParser("usage: %prog")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_const", const=True,
                      help="Turn on debugging")
    parser.add_option("-p", "--pid_dir", dest="pid_dir",
                      help="Set the PID directory (default to %s)" % DEFAULT_PID_DIR, default=DEFAULT_PID_DIR)
    (options, actions) = parser.parse_args()
    if len(actions) != 1:
        print "Please provide an action (e.g. 'start', 'stop')"
        sys.exit(1)

    action = actions[0]
    daemonizer = Daemonizer(options)

    if action == 'start':
        daemonizer.start()
    elif action == 'stop':
        daemonizer.stop()
    else:
        print "Valid actions are: 'start', 'stop'"
        sys.exit(1)

if __name__ == "__main__":
    main()
