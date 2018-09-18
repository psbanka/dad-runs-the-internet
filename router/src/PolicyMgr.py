"""
We want to watch the dnsmasq server and determine what IP addresses are being
handed out. We have a list of names that we are allowing and based on that list
of names, we're going to dynamically provide IPTables rules for them.
"""

import re
import sys
import time
import os, stat
from util import OK
from commands import getstatusoutput as gso
from Exceptions import PolicyMgrException
from DaemonBase import DaemonBase

IPTABLES_TARGET = "grp_3"
MAX_LOG_SIZE = 700 # KB

def _add_item(dictionary, key, value):
    "Safe append to dictionary key"
    try:
        dictionary[key].append(value)
    except KeyError:
        dictionary[key] = [value]

class AllowedSite(object):
    """
    Retains information about what IP addresses and regex are associated with
    a certain Internet destination    
    """

    def __init__(self, name, regex_strings, options):
        self.name = name
        self.original_regex = set(regex_strings)
        self.regex_set = set([re.compile(regex_str) for regex_str in regex_strings])
        self.options = options
        self.ip_addresses = set([])
        self.cnames = set()

    def check_regex_against_server(self, server_regex):
        """
        We are getting a new list of regex from the server. Is it the same
        as what we've been given before?
        """
        output = True
        if set(server_regex) != self.original_regex:
            output = False
        return output

    def new_cname(self, cname, actual_name):
        """
        There is a new cname found, e.g. 'www.google.com' is also known as
        'www.l.g1.google.com'. If we care about the cname, then we now care
        about the actual_name as well.
        """
        found = False
        if actual_name not in self.cnames:
            if any([regex.findall(cname) for regex in self.regex_set]):
                self.regex_set.update([re.compile(actual_name)])
                self.cnames.update([actual_name])
                found = True
            if cname in self.cnames:
                # CNAME of a CNAME
                self.regex_set.update([re.compile(actual_name)])
                self.cnames.update([actual_name])
                found = True
        return found

    def new_address(self, name, address):
        """
        A new IP address was found. Do we care about it?
        """
        if address not in self.ip_addresses:
            if any([regex.findall(name) for regex in self.regex_set]):
                self.ip_addresses.update([address])

    def build_data(self, ip_cache, cname_cache):
        """
        We need to go through the entire cache and build the list of
        ip addresses that we care about.
        """
        found = True
        while found:
            found = False
            for cname, actual_name in cname_cache.iteritems():
                new_found = self.new_cname(cname, actual_name)
                if new_found == True:
                    found = True

        for name, addresses in ip_cache.iteritems():
            for address in addresses:
                self.new_address(name, address)

class PolicyMgr(DaemonBase):

    "Manages IP addresses for sites we're interested in granting access to"

    def __init__(self, file_name, allowed_names, options):
        """
        @param allowed_names: a dictionary of name: regex_list values from
            the server. This gets turned into a dictionary of AllowedSite
            objects
        """
        DaemonBase.__init__(self, options)
        self.max_log_size = options.max_log_size
        self.file_name = file_name
        self.allowed_names = allowed_names
        self.allowed_sites = {}
        from pprint import pprint;pprint(allowed_names)
        for name, regex_strings in allowed_names.iteritems():
            self.allowed_sites[name] = AllowedSite(name, regex_strings, options)

        self.generic_matcher = re.compile('reply\s(\S+)\sis\s([<CNAME>\d\.]+)')
        self.watch_for_cname = None
        self.options = options
        cmds = ['iptables -F %s' % IPTABLES_TARGET,
                "iptables -A %s -j REJECT" % (IPTABLES_TARGET),
               ]
        self._implement_rules(cmds)
        self.current_position = 0

        self.ip_cache = {}
        self.cname_cache = {}
        self.published_ips = set()
        self.file_handle = None
        if options.prep_system:
            self.prep_system()
        self._open_file()

    def prep_system(self):
        """
        Need to be able to make a few system changes so we can manage the
        system
        """
        # Responsible for making sure the old dnsmasq is run
        os.system("rm -f /tmp/cron.d/check_ps")
        # Must get rid of the old dnsmasq
        os.system("killall dnsmasq")
        cmd  = "LD_PRELOAD=/opt/lib/libuClibc-0.9.28.so "
        cmd += "/opt/sbin/dnsmasq -C "
        cmd += "/opt/home/dev/work/dri/router/dnsmasq.conf"
        os.system(cmd)
        while not os.path.isfile('/tmp/dnsmasq.log'):
            print("waiting for /tmp/dnsmasq.log to show up...")
            time.sleep(1)

    def _open_file(self):
        """Get our file handle working"""
        if not self.file_handle:
            self.file_handle = open(self.file_name, 'r')

    def _close_file(self):
        "close it"
        if self.file_handle:
            self.file_handle.close()
        self.file_handle = None

    # Tested
    def rotate_log(self, wait_for_log_file = True):
        """
        We have a need to rotate logs periodically or the system will
        run out of disk space
        """
        size = os.stat(self.file_name)[stat.ST_SIZE] / 1024.0
        if size < self.max_log_size: # Don't rotate...
            return False
        self._close_file()
        self.log("Rotating log... (%s MB)" % (size ))
        os.system('rm -f %s' % self.file_name)
        os.system('killall -s USR2 dnsmasq 2> /dev/null')
        os.system('touch %s' % self.file_name)
        if wait_for_log_file:
            while not os.path.isfile(self.file_name):
                time.sleep(1)
                self.log("Waiting for log file to be created...")
        self._open_file()
        self.current_position = 0
        return True

    # Tested
    def initial_load(self):
        """
        Initial load of the whole log file
        """
        if self.options.no_load:
            self.log("Skipping initial load due to testing.")
            self.file_handle.seek(0, 2) # Seek to end of file
            self.current_position = self.file_handle.tell()
            return 0
        self.log("Pulling in the whole log... ")
        start_time = time.time()
        rules_loaded = 0
        new_line = "INITIALIZE"
        while new_line != '':
            new_line = self.file_handle.readline()
            rules_loaded += self._parse_and_implement(new_line)
        elapsed = time.time() - start_time
        self.log("Loaded %s rules in %s seconds." % (rules_loaded, elapsed))
        return rules_loaded

    # Tested
    def check_for_new_stuff(self):
        """
        Tail our log, seeing if there are any lines to pull out
        """
        new_lines = self._tail()
        new_rules = 0
        for line in new_lines:
            new_rules += self._parse_and_implement(line)
        return new_rules

    # Tested
    def _tail(self):
        """
        Reads a line from self.file_handle
        """
        self.file_handle.seek(self.current_position, 0)
        lines = self.file_handle.read().splitlines()
        if self.options.verbose:
            self.log("position in the file: %s" % self.current_position)
            self.log("number of lines read: %s" % len(lines))
        self.current_position = self.file_handle.tell()
        self.rotate_log()
        return lines

    # Tested
    def _parse_and_implement(self, line):
        """
        Go through lines read from the log file and implement any new
        iptables rules based on them.
        """
        self._parse(line)
        return self._build_new_rules()

    # Tested
    def _build_new_rules(self):
        """
        Try to find any new rules to create
        """
        all_allowed_ips = set()
        for allowed_site in self.allowed_sites.values():
            all_allowed_ips.update(allowed_site.ip_addresses)

        new_ips = all_allowed_ips - self.published_ips

        for new_ip in new_ips:
            cmd = "iptables -I %s -d %s -j ACCEPT" % (IPTABLES_TARGET, new_ip)
            self._implement_rules([cmd])
            self.published_ips.update([new_ip])
        return len(new_ips)

    # Tested
    def remove_site(self, site_name):
        "If we decide there is a site we no longer want to have..."
        current_ips = set()
        removed_ips = 0
        del self.allowed_sites[site_name]
        for allowed_site in self.allowed_sites.values():
            current_ips.update(allowed_site.ip_addresses)
        deleted_ips = self.published_ips - current_ips
        for deleted_ip in deleted_ips:
            cmd = "iptables -D %s -d %s -j ACCEPT" % (IPTABLES_TARGET, deleted_ip)
            self._implement_rules([cmd])
            self.published_ips.remove(deleted_ip)
            removed_ips += 1
        return removed_ips

    # Tested
    def add_site(self, site_name, regex_strings):
        "We would like to add a site after the fact"
        self.allowed_sites[site_name] = AllowedSite(site_name, regex_strings, self.options)
        self.allowed_sites[site_name].build_data(self.ip_cache, self.cname_cache)
        return self._build_new_rules()

    # Tested
    def process_new_allowed(self, allowed_names):
        """
        We have been handed a new list of allowed names from the server.
        Determine if it's different from what we had, if so deal with it.
        """
        server_names = set(allowed_names.keys())
        local_names = set(self.allowed_sites.keys())
        names_to_remove = local_names - server_names
        names_to_add    = server_names - local_names

        for name in names_to_remove:
            self.remove_site(name)
        for name in names_to_add:
            self.add_site(name, allowed_names[name])

        for site_name, server_regex in allowed_names.iteritems():
            if not self.allowed_sites[site_name].check_regex_against_server(server_regex):
                print("server regex list has changed...")
                self.remove_site(site_name)
                self.add_site(site_name, server_regex)
        return names_to_add, names_to_remove

    # Tested
    def _parse(self, line):
        """
        Gather IP addresses from a line of DNSMasq log output.
        Modifies self.cname_cache and self.ip_cache.
        """
        if not 'reply' in line:
            self.watch_for_cname = None
            return
        matches = self.generic_matcher.findall(line)
        if not matches:
            self.watch_for_cname = None
            return

        for match in matches:
            name, address = match
            print(">> ", line)
            print(">> name: %s / address: %s / watch: %s" % (name, address, self.watch_for_cname))
            if address == "<CNAME>":
                if self.watch_for_cname != None: # cname points to a cname
                    self.cname_cache[self.watch_for_cname] = name
                    for allowed_site in self.allowed_sites.values():
                        allowed_site.new_cname(self.watch_for_cname, name)
                self.watch_for_cname = name
                try:
                    del self.cname_cache[self.watch_for_cname]
                except KeyError:
                    pass
                continue
            if self.watch_for_cname:
                if self.watch_for_cname in self.cname_cache.keys():
                    _add_item(self.ip_cache, name, address)
                    for allowed_site in self.allowed_sites.values():
                        allowed_site.new_address(name, address)
                else:
                    self.cname_cache[self.watch_for_cname] = name
                    _add_item(self.ip_cache, name, address)
                    print("Adding a cname AND an IP")
                    for allowed_site in self.allowed_sites.values():
                        allowed_site.new_cname(self.watch_for_cname, name)
                        allowed_site.new_address(name, address)
            else:
                _add_item(self.ip_cache, name, address)
                print("Adding an a-record")
                for allowed_site in self.allowed_sites.values():
                    allowed_site.new_address(name, address)

    # TODO: Refactor with downloader.py
    # Tested
    def _implement_rules(self, cmds):
        "Actually run the rules that we put together"
        if self.options.test:
            if self.options.verbose:
                print("This script would implement the following rules:")
                for cmd in cmds:
                    print("   %s" % cmd)
        else:
            for cmd in cmds:
                if self.options.verbose:
                    self.log("Running: [%s]..." % cmd,)
                status, output = gso(cmd)
                if status != OK:
                    self.log("COMMAND FAILED: [%s]" % cmd)
                    raise PolicyMgrException(output)
                if self.options.verbose:
                    self.log("SUCCESS")

    def dump(self):
        "Show off what's going on"
        print(">>> A-Records:")
        for key, value in self.ip_cache.iteritems():
            print("A:: %20s: %d" % (key, len(value)))
        print(">>> cname_cache:")
        for key, value in self.cname_cache.iteritems():
            print("CNAME: %20s: %s" % (key, value))
        pprint(self.ip_cache)

def main():
    class Options:
        def __init__(self):
            self.no_daemonize = True
            self.verbose = True
            self.test = True
            self.no_load = False
            self.max_log_size = 700
    allowed_names = {"google": [".*google\.com", "ssl\.gstatic\.com",],
                     "dri": ["freezing\-frost\-9935\.herokuapp\.com",
                             "ajax\.googleapis\.com",],
                     "lastpass": [ "lastpass\.com"],
                     "dev": ["pbanka\.atlassian\.net"],
                     "info": ["www.wikipedia.org"],
                     "productivity": ["www.canva.com"],
                    }
    file_name = sys.argv[1]
    tmpfile_name = "tmp_dnsmasq.log"
    os.system('cp %s %s' % (file_name, tmpfile_name))
    policy_mgr = PolicyMgr(tmpfile_name, allowed_names, Options())
    policy_mgr.initial_load()

    print('---------------------------------------------------- initial')
    policy_mgr.dump()
    print('---------------------------------------------------- add youtube')
    allowed_names["youtube"] = ["accounts\.youtube\.com"]
    policy_mgr.process_new_allowed(allowed_names)
    policy_mgr.dump()

    print('---------------------------------------------------- remove dri')
    del allowed_names["dri"]
    policy_mgr.process_new_allowed(allowed_names)
    policy_mgr.dump()

    print('---------------------------------------------------- modify google')
    allowed_names['google'] = [".*google\.com"]
    policy_mgr.process_new_allowed(allowed_names)
    policy_mgr.dump()

    for i in xrange(1,10):
        print("Checking...")
        policy_mgr.check_for_new_stuff()
        time.sleep(1)
    policy_mgr.dump()
    #policy_mgr.remove_site("dri")
    ##policy_mgr.remove_site("lastpass")
    ##policy_mgr.add_site("lastpass", [ "lastpass\.com"])
    #policy_mgr.add_site('dri', ["freezing\-frost\-9935\.herokuapp\.com",
    #                         "ajax\.googleapis\.com",])

if __name__ == "__main__":
    main()
