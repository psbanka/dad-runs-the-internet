"""
We want to watch the dnsmasq server and determine what IP addresses are being
handed out. We have a list of names that we are allowing and based on that list
of names, we're going to dynamically provide IPTables rules for them.
"""
import re
import time
import syslog
from util import OK
from commands import getstatusoutput as gso
from Exceptions import PolicyMgrException
from DaemonBase import DaemonBase
import select

IPTABLES_TARGET = "grp_2"

class DnsCacheMon(DaemonBase):

    def __init__(self, file_name, allowed_names, options):
        DaemonBase.__init__(self, options)
        self.allowed_names = allowed_names
        self.ip_list = []
        self.match_list_ip = [re.compile(exp + "\sis\s([\d\.]+)") for exp in self.allowed_names]
        self.match_list_cname = [re.compile(exp + "\sis\s(<CNAME>+)") for exp in self.allowed_names]
        self.generic_matcher = re.compile('reply\s(\S+)\sis\s([\d.]+)')
        self.watch_for_cname = False
        self.test = options.test
        self.verbose = options.verbose
        cmds = ['iptables -F %s' % IPTABLES_TARGET,
                "iptables -A %s -j REJECT" % (IPTABLES_TARGET),
               ]
        self.implement_rules(cmds)
        self.file_handle = open(file_name, 'r')
        self.current_position = 0

    def initial_load(self):
        """
        Initial load of the whole log file
        """
        if self.options.test:
            self.log("Skipping initial load due to testing.")
            self.file_handle.seek(0,2) # Seek to end of file
            self.current_position = self.file_handle.tell()
            return 0
        self.log("Pulling in the whole log... ")
        start_time = time.time()
        rules_loaded = 0
        for line in self.file_handle.readlines():
            if self.parse_and_implement(line):
                rules_loaded += 1
        elapsed = time.time() - start_time
        self.log("Loaded %s rules in %s seconds." % (rules_loaded, elapsed))
        return rules_loaded

    def check_for_new_stuff(self, lines = 1):
        """
        Tail our log, seeing if there are any lines to pull out
        """
        new_lines = self.tail()
        for line in new_lines:
            self.parse_and_implement(line)

    def tail(self):
        """Reads 'lines' lines from file_handle.
        The return value is a tuple in the form ``(lines, has_more)`` where
        `has_more` is an indicator that is `True` if there are more lines in the file.
        """
        self.file_handle.seek(self.current_position, 0)
        lines = self.file_handle.read().splitlines()
        if self.options.verbose:
            self.log("position in the file: %s" % self.current_position)
            self.log("number of lines read: %s" % len(lines))
        self.current_position = self.file_handle.tell()
        return lines

    def close(self):
        "close our file handle"
        self.file_handle.close()

    def parse_and_implement(self, line):
        """
        Go through lines read from the log file and implement any new
        iptables rules based on them.
        """
        new_ip = self.parse(line)
        if new_ip:
            cmd = "iptables -I %s -d %s -j ACCEPT" % (IPTABLES_TARGET, new_ip)
            self.implement_rules([cmd])
            return True
        return False

    def parse(self, line):
        "Gather IP addresses from a line of DNSMasq log output"
        if not 'reply' in line:
            return None
        found = False
        for matcher in self.match_list_ip:
            match = matcher.findall(line)
            if match:
                if match[0] not in self.ip_list:
                    self.ip_list.append(match[0])
                    return match[0]
                found = True
                break
        if found: return
        for matcher in self.match_list_cname:
            match = matcher.findall(line)
            if match:
                self.watch_for_cname = True
                found = True
                break
        if found: return
        if self.watch_for_cname:
            match = self.generic_matcher.findall(line)
            if match:
                new_name = match[0][0]
                new_ip = match[0][1]
                self.match_list_ip.append(re.compile(new_name + "\sis\s([\d\.]+)"))
                if new_ip not in self.ip_list:
                    self.ip_list.append(new_ip)
                    return new_ip
            else:
                self.watch_for_cname = False

    def make_all_rules(self):
        "Generate iptables rules to permit the IPs we know about"
        cmds = ['iptables -F %s' % IPTABLES_TARGET]

        for ip_address in self.ip_list:
            cmd = "iptables -I %s -d %s -j ACCEPT" % (IPTABLES_TARGET, ip_address)
            cmds.append(cmd)
        cmds.append("iptables -A %s -j REJECT" % (IPTABLES_TARGET))
        self.implement_rules(cmds)
        return cmds

    # TODO: Refactor with downloader.py
    def implement_rules(self, cmds):
        "Actually run the rules that we put together"
        if self.test:
            print "This script would implement the following rules:"
            for cmd in cmds:
                print "   %s" % cmd
        else:
            for cmd in cmds:
                if self.verbose: self.log("Running: [%s]..." % cmd,)
                status, output = gso(cmd)
                if status != OK:
                    self.log(syslog.LOG_ERR, "COMMAND FAILED: [%s]" % cmd)
                    raise PolicyMgrException(output)
                if self.verbose: print "SUCCESS"

if __name__ == "__main__":
    ALLOWED_NAMES = [".*google\.com", ".*amazonaws\.com", "freezing\-frost\-9935\.herokuapp\.com",
                     "ssl\.gstatic\.com", "lastpass\.com", "ar\.herokuapp\.com", "pbanka\.atlassian\.net",
                     "ajax\.googleapis\.com", "accounts\.youtube\.com"]
    dns_cache_mon = DnsCacheMon("/tmp/dnsmasq.log", ALLOWED_NAMES, False, True)
    dns_cache_mon.check_for_new_stuff(500)
    for i in xrange(1,10):
        print "Checking..."
        dns_cache_mon.check_for_new_stuff()
        time.sleep(1)
    print dns_cache_mon.ip_list
