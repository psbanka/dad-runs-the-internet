"""
We want to watch the dnsmasq server and determine what IP addresses are being
handed out. We have a list of names that we are allowing and based on that list
of names, we're going to dynamically provide IPTables rules for them.
"""
import re
import syslog
from util import OK
from commands import getstatusoutput as gso
from Exceptions import DownloadException

ALLOWED_NAMES = [".*google\.com", ".*amazonaws\.com", "freezing\-frost\-9935\.herokuapp\.com", "ssl\.gstatic\.com"
                 "lastpass\.com", "ar\.herokuapp\.com", "pbanka\.atlassian\.net", "ajax\.googleapis\.com", "accounts\.youtube\.com"]
#ALLOWED_NAMES = ["accounts\.youtube\.com"]
IPTABLES_TARGET = "grp_2"
URL = "localhost"

class DnsCacheMon(object):

    def __init__(self, allowed_names, test, verbose):
        self.allowed_names = allowed_names
        self.ip_list = []
        self.match_list_ip = [re.compile(exp + "\sis\s([\d\.]+)") for exp in self.allowed_names]
        self.match_list_cname = [re.compile(exp + "\sis\s(<CNAME>+)") for exp in self.allowed_names]
        self.generic_matcher = re.compile('reply\s(\S+)\sis\s([\d.]+)')
        #self.header = None
        #self.header_matcher = re.compile('^(.*\sdnsmasq\[\d+\]:\s).*')
        self.watch_for_cname = False
        self.test = test
        self.verbose = verbose
        cmds = ['iptables -F %s' % IPTABLES_TARGET,
                "iptables -A %s -j REJECT" % (IPTABLES_TARGET),
               ]
        self.implement_rules(cmds)

    def parse_and_implement(self, line):
        new_ip = self.parse(line)
        if new_ip:
            cmd = "iptables -I %s -d %s -j ACCEPT" % (IPTABLES_TARGET, new_ip)
            self.implement_rules([cmd])

    def parse(self, line):
        "Gather IP addresses from a line of DNSMasq log output"
        if not 'reply' in line:
            return None
        #if not self.header:
        #    match = self.header_matcher.findall(line)
        #    if match:
        #        self.header = match[0]
        #if self.header:
        #    if line[len(self.header):len(self.header)+5] != 'reply':
        #        continue
        #else:
        #    print "NO HEADER"
        found = False
        for matcher in self.match_list_ip:
            match = matcher.findall(line)
            if match:
                if match[0] not in self.ip_list:
                    #print "ip:",match[0]
                    self.ip_list.append(match[0])
                    return match[0]
                found = True
                break
        if found: return
        for matcher in self.match_list_cname:
            match = matcher.findall(line)
            if match:
                #print "cname:",match[0]
                self.watch_for_cname = True
                found = True
                break
        if found: return
        if self.watch_for_cname:
            #import pdb;pdb.set_trace()
            #print "line>> ",line.strip()
            match = self.generic_matcher.findall(line)
            if match:
                new_name = match[0][0]
                new_ip = match[0][1]
                self.match_list_ip.append(re.compile(new_name + "\sis\s([\d\.]+)"))
                if new_ip not in self.ip_list:
                    #print "CNAME ip:",new_ip
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
                if self.verbose: syslog.syslog("Running: [%s]..." % cmd,)
                status, output = gso(cmd)
                if status != OK:
                    syslog.syslog(syslog.LOG_ERR, "COMMAND FAILED: [%s]" % cmd)
                    raise DownloadException(URL, output)
                if self.verbose: print "SUCCESS"

if __name__ == "__main__":
    dns_cache_mon = DnsCacheMon(ALLOWED_NAMES, False, True)
    with open("dnsmasq.log", 'r') as file_handle:
        for line in file_handle.readlines():
            dns_cache_mon.parse_and_implement(line)
    print dns_cache_mon.ip_list
