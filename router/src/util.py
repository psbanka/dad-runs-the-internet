import syslog
from commands import getstatusoutput as gso
from Exceptions import CommandException
import glob
import os

OK = 0
FAIL = 1

def run_or_die(cmd):
    try:
        status, output = gso(cmd)
        if status != OK:
            raise CommandException(cmd, output)
    except OSError:
        raise CommandException(cmd, str(OSError))
    return output

def log_open_files(note):
    pid = str(os.getpid())
    open_files = len(glob.glob('/proc/%s/fd/*' % pid))
    syslog.syslog("(%s) my open files: %s" % (note, open_files))
