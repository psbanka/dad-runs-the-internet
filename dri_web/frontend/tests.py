from django.utils import unittest

from router_views import _upload_process, iptables_download
from device_views import enable_device
from policy_views import get_policies
from models import Device, Policy, TemporaryApproval
import json
from mock import Mock


TEST_ARP_ENTRY = '? (192.168.11.149) at 7C:61:93:FD:FE:DA [ether] on br0\n'\
                 '? (192.168.11.114) at 00:0E:35:EC:B9:CB [ether] on br0\n'\
                 '? (192.168.2.1) at 00:0B:82:17:6C:9C [ether] on vlan2\n'\
                 '? (192.168.11.110) at 58:55:CA:31:82:10 [ether] on br0\n'\
                 '? (192.168.11.125) at 8C:58:77:02:8E:5D [ether] on br0'

TEST_LEASES_ENTRY = '1329759916 8c:58:77:02:8e:5d 192.168.11.125 Kristys-iPhone 01:8c:58:77:02:8e:5d\n'\
                    '1329760542 f0:b4:79:e3:d8:c5 192.168.11.129 Be-The-Spirit 01:f0:b4:79:e3:d8:c5'

class TestUpload(unittest.TestCase):
    """ Class used by all TNT test cases to test TNT. Not production code """

    fixtures = ['initial_data']

    def setUp(self):
        self.full = Policy.objects.get(name = "full")
        self.blocked = Policy.objects.get(name = 'blocked')
        self.device_1 = Device(mac_address="58:94:6B:A4:DA:BC", ip_address="192.168.10.2")
        self.device_1.policy = self.full
        self.device_1.save()
        self.device_2 = Device(mac_address="48:5B:39:F8:5D:F9", ip_address="192.168.10.3")
        self.device_2.policy = self.full
        self.device_2.save()
        self.device_3 = Device(mac_address="58:94:6B:A4:D7:BC", ip_address="192.168.10.4")
        self.device_3.policy = self.blocked
        self.device_3.save()
        self.device_4 = Device(mac_address="8C:58:77:02:8E:5D", ip_address="192.168.11.125")
        self.device_4.policy = self.blocked
        self.device_4.save()

    def tearDown(self):
        self.device_1.delete()
        self.device_2.delete()
        self.device_3.delete()
        self.device_4.delete()

    def test_upload_leases(self):
        _upload_process(TEST_LEASES_ENTRY)
        self.assertEqual(len(Device.objects.all()), 4)
        device = Device.objects.get(mac_address="8C:58:77:02:8E:5D")
        self.assertEqual(device.suggested_name, 'Kristys-iPhone')

    def test_upload_process(self):
        self.assertEqual(len(Device.objects.all()), 4)
        _upload_process(TEST_ARP_ENTRY)
        self.assertEqual(len(Device.objects.all()), 8)

    def test_download_process(self):
        full = Policy.objects.get(name = "full")
        blocked = Policy.objects.get(name = 'blocked')
        self.device_1.policy = full
        self.device_1.save()
        self.device_2.policy = full
        self.device_2.save()
        self.device_3.policy = blocked
        self.device_3.save()
        self.device_4.policy = blocked
        self.device_4.save()
        response = iptables_download({})
        response_dict = json.loads(response._get_content()[5:])
        allowed_expected = [
                         {"mac_address": "58:94:6B:A4:DA:BC", "ip_address": "192.168.10.2"},
                         {"mac_address": "48:5B:39:F8:5D:F9", "ip_address": "192.168.10.3"},
                       ]
        blocked_expected = [
                         {"mac_address": "58:94:6B:A4:D7:BC", "ip_address": "192.168.10.4"},
                         {"mac_address": "8C:58:77:02:8E:5D", "ip_address": "192.168.11.125"},
                       ]
        for item in allowed_expected:
            self.assertIn(item, response_dict['allowed'])
        for item in blocked_expected:
            self.assertIn(item, response_dict['blocked'])

    def test_enabling(self):
        full = Policy.objects.get(name = "full")
        upon_request = Policy.objects.get(name = 'upon-request')

        self.device_1.policy = full
        self.device_1.save()

        self.assertTrue(self.device_1.is_allowed()) 

        # Test out partial unblocking
        self.device_1.policy = upon_request
        self.device_1.save()

        self.assertFalse(self.device_1.is_allowed()) 

        # Create an approval, and see that the device is enabled
        ta = TemporaryApproval(device=self.device_1)
        ta.set_parameters(10)
        ta.save()

        self.assertTrue(self.device_1.is_allowed()) 

    def test_enable_device(self):
        response = iptables_download({})
        response_dict = json.loads(response._get_content()[5:])

        expected_blocked = [{u'ip_address': u'192.168.10.4',
               u'mac_address': u'58:94:6B:A4:D7:BC'},
              {u'ip_address': u'192.168.11.125',
               u'mac_address': u'8C:58:77:02:8E:5D'}]
        self.assertEqual(expected_blocked, response_dict['blocked'])

        request = Mock()
        request.POST = { "mac_address": '58:94:6b:a4:da:bc', "duration": 30 }
        request.method = "POST"
        response = enable_device(request)
        response_dict = json.loads(response._get_content()[5:])
        self.assertEqual(response_dict['success'], True)
        self.assertEqual(response_dict['message'], 'Saved')
        
    def test_download_policy(self):
        request = Mock()
        request.GET = {}
        request.method = "GET"
        response = get_policies(request)
        response_dict = json.loads(response._get_content()[5:])

        expected = {u'dri': [u'freezing-frost-9935.herokuapp.com', u'.*.googleapis.com'],
                    u'google': [u'.*.google.com', u'.*.gstatic.com'],
                    u'learning': [u'.*.dictionary.com', u'.*.wikipedia.org'],
                    u'mapping': [u'.*gpsonextra.net'],
                    u'podcasts': [u'.*.feedburner.net'],
                    u'time': [u'.*.nist.gov', u'.*.pool.ntp.org'],
                    u'utilities': [u'.*.lastpass.com', u'.*.evernote.com'],
                    u'weather': [u'.*.accuweather.com']}
        self.maxDiff = None

        self.assertEqual(response_dict['success'], True)
        self.assertEqual(response_dict['message']['upon-request'], expected)
