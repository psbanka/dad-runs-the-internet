OK = 0
FAIL = 1

import syslog
from commands import getstatusoutput as gso
from Exceptions import CommandException

def run_or_die(cmd):
    try:
        status, output = gso(cmd)
        if status != OK:
            raise CommandException(cmd, output)
    except OSError:
        raise CommandException(cmd, str(OSError))
    return output

