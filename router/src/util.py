OK = 0
FAIL = 1

from commands import getstatusoutput as gso

def run_or_die(cmd):
    status, output = gso(cmd)
    if status != OK:
        print "Error running: %s" % cmd
        sys.exit(1)
    return output

