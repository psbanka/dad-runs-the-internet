#!/opt/bin/python2.7

from util import run_or_die, OK
import PolicyMgr
from commands import getstatusoutput as gso
from Exceptions import DownloadException
import json
import optparse
from pprint import pprint
from DaemonBase import DaemonBase

#URL = "http://falling-stone-8827.herokuapp.com//iptables_download/"
#URL = "http://freezing-frost-9935.herokuapp.com/iptables_download/"
IPTABLES_TARGET = "grp_2"

def verify_ip(mac_address, ip_address):
    """
    We have been given IP-address and MAC address combinations.
    We should probably verify that these things are what we think
    they are.
    """
    pass # TODO

def make_rules(configs):
    "Generate iptables rules to run on the system"
    cmds = ['iptables -F %s' % IPTABLES_TARGET]

    for allowed_record in configs['allowed']:
        #mac_address = allowed_record["mac_address"] # should use.
        ip_address = allowed_record["ip_address"]
        cmd = "iptables -I %s -s %s -j ACCEPT" % (IPTABLES_TARGET, ip_address)
        cmds.append(cmd)
    for allowed_record in configs['blocked']:
        # We should verify the mac-address at some point.
        #mac_address = allowed_record["mac_address"]
        ip_address = allowed_record["ip_address"]
        cmd = "iptables -I %s -s %s -j %s" % (IPTABLES_TARGET, ip_address, PolicyMgr.IPTABLES_TARGET)
        cmds.append(cmd)
    return cmds

class Downloader(DaemonBase):

    def __init__(self, options):
        DaemonBase.__init__(self, options)

    def run(self):
        "Perform all necessary actions"
        try:
            configs = self.pull_json_configs()
        except ValueError:
            raise DownloadException(self.options.server_url, "Can't parse data from server")
        cmds = make_rules(configs)
        self.implement_rules(cmds)

    def pull_json_configs(self):
        "Go grab data from the server"
        cmd = "curl %s/iptables_download/ 2>/dev/null" % self.options.server_url
        curl_output = run_or_die(cmd)
        
        configs = {}
        for line in curl_output.split('\n'):
            if line.endswith('&&'):
                line = line[:-2]
            configs.update(json.loads(line))

        if not configs.get('success', False):
            self.log("Error loading configs")
            if self.options.verbose:
                print "Output from the server:"
                pprint(curl_output)
            raise DownloadException(self.options.server_url, curl_output)
        return configs

    def implement_rules(self, cmds):
        "Actually run the rules that we put together"
        if self.options.test:
            print "This script would implement the following rules:"
            for cmd in cmds:
                print "   %s" % cmd
        else:
            for cmd in cmds:
                if self.options.verbose: self.log("Running: [%s]..." % cmd)
                status, output = gso(cmd)
                if status != OK:
                    self.log("COMMAND FAILED: [%s]" % cmd)
                    raise DownloadException(self.options.server_url, output)
                if self.options.verbose: print "SUCCESS"

def main():
    parser = optparse.OptionParser("usage: %prog")
    parser.add_option("-t", "--test", dest="test", action="store_const", const=True,
                      help="Print the rules rather than run them")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_const", const=True,
                      help="Turn on debugging")
    (options, actions) = parser.parse_args()
    downloader = Downloader(options)
    downloader.run()

if __name__ == "__main__":
    main()












