#!/opt/bin/python2.7

from util import run_or_die, OK, FAIL
from commands import getstatusoutput as gso
import json
import sys
import optparse
from pprint import pprint

URL = "http://192.168.11.114:8080/iptables_download/"
IPTABLES_TARGET = "grp_1"

def pull_json_configs(options):
    "Go grab data from the server"
    cmd = "curl %s 2>/dev/null" % URL
    curl_output = run_or_die(cmd)
    
    configs = {}
    for line in curl_output.split('\n'):
        if line.endswith('&&'):
            line = line[:-2]
        configs.update(json.loads(line))

    if not configs['success']:
        if options.verbose:
            print "Error loading configs"
            print "Output from the server:"
            pprint(output)
        sys.exit(1)
    return configs

def verify_ip(mac_address, ip_address, options):
    """
    We have been given IP-address and MAC address combinations.
    We should probably verify that these things are what we think
    they are.
    """
    pass # TODO

def make_rules(configs, options):
    "Generate iptables rules to run on the system"
    cmds = ['iptables -F %s' % IPTABLES_TARGET]

    for allowed_record in configs['allowed']:
        mac_address = allowed_record["mac_address"]
        ip_address = allowed_record["ip_address"]
        cmd = "iptables -I %s -s %s -j ACCEPT" % (IPTABLES_TARGET, ip_address)
        cmds.append(cmd)
    for allowed_record in configs['blocked']:
        mac_address = allowed_record["mac_address"]
        ip_address = allowed_record["ip_address"]
        cmd = "iptables -I %s -s %s -j REJECT" % (IPTABLES_TARGET, ip_address)
        cmds.append(cmd)

    return cmds

def implement_rules(cmds, options):
    "Actually run the rules that we put together"
    if options.test:
        print "This script would implement the following rules:"
        for cmd in cmds:
            print "   %s" % cmd
    else:
        for cmd in cmds:
            if options.verbose: print "Running: [%s]..." % cmd,
            status, output = gso(cmd)
            if status != OK:
                print "\nCOMMAND FAILED: [%s]" % cmd
                print ">> OUTPUT: (%s)" % output
                sys.exit(1)
            if options.verbose: print "SUCCESS"

def main():
    parser = optparse.OptionParser("usage: %prog")
    parser.add_option("-t", "--test", dest="test", action="store_const", const=True,
                      help="Print the rules rather than run them")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_const", const=True,
                      help="Turn on debugging")
    (options, actions) = parser.parse_args()
    configs = pull_json_configs(options)
    cmds = make_rules(configs, options)
    implement_rules(cmds, options)

if __name__ == "__main__":
    main()












