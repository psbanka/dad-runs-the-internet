import syslog

class DaemonBase(object):

    def __init__(self, options):
        self.options = options

    def log(self, message):
        "Depending on whether we're daemonized, log to screen or syslog"
        if self.options.no_daemonize:
            print(message)
        else:
            syslog.syslog(message)

