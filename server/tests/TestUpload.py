import unittest2
from dri_server.web.frontend.views import _upload_process, iptables_download, enable_device
from dri_server.web.frontend.models import Device, Policy, TemporaryApproval
import json
from nose.plugins.skip import SkipTest
from mock import Mock


TEST_ARP_ENTRY = '? (192.168.11.149) at 7C:61:93:FD:FE:DA [ether] on br0\n'\
                 '? (192.168.11.114) at 00:0E:35:EC:B9:CB [ether] on br0\n'\
                 '? (192.168.2.1) at 00:0B:82:17:6C:9C [ether] on vlan2\n'\
                 '? (192.168.11.110) at 58:55:CA:31:82:10 [ether] on br0\n'\
                 '? (192.168.11.109) at 58:94:6B:A4:DA:BC [ether] on br0'

class TestUpload(unittest2.TestCase):
    """ Class used by all TNT test cases to test TNT. Not production code """

    def setUp(self):
        "Override base class method"
        pass

    def tearDown(self):
        "Override base class method"
        pass

    def test_upload_process(self):
        raise SkipTest # need more reliable way to set up fixtures
        self.assertEqual(len(Device.objects.all()), 4)
        _upload_process(TEST_ARP_ENTRY)
        self.assertEqual(len(Device.objects.all()), 9)

    def test_download_process(self):
        raise SkipTest # need more reliable way to set up fixtures
        device_1 = Device.objects.get(mac_address="58:94:6b:a4:da:bc")
        device_2 = Device.objects.get(mac_address="48:5b:39:f8:5d:f9")
        device_3 = Device.objects.get(mac_address="58:94:6b:a4:d7:bc")
        device_4 = Device.objects.get(mac_address="48:57:39:78:5d:f9")
        full = Policy.objects.get(name = "full")
        blocked = Policy.objects.get(name = 'blocked')
        device_1.policy = full
        device_1.save()
        device_2.policy = full
        device_2.save()
        device_3.policy = blocked
        device_3.save()
        device_4.policy = blocked
        device_4.save()
        response = iptables_download({})
        response_dict = json.loads(response._get_content()[5:])
        allowed_expected = [
                         {"mac_address": "58:94:6b:a4:da:bc", "ip_address": "192.168.10.2"},
                         {"mac_address": "48:5b:39:f8:5d:f9", "ip_address": "192.168.10.3"},
                       ]
        blocked_expected = [
                         {"mac_address": "58:94:6b:a4:d7:bc", "ip_address": "192.168.10.4"},
                         {"mac_address": "48:57:39:78:5d:f9", "ip_address": "192.168.10.5"},
                       ]
        for item in allowed_expected:
            self.assertIn(item, response_dict['allowed'])
        for item in blocked_expected:
            self.assertIn(item, response_dict['blocked'])

    def test_enabling(self):
        full = Policy.objects.get(name = "full")
        upon_request = Policy.objects.get(name = 'upon-request')

        device_1 = Device.objects.get(mac_address="58:94:6b:a4:da:bc")
        device_1.policy = full
        device_1.save()

        self.assertTrue(device_1.is_allowed()) 

        # Test out partial unblocking
        device_1.policy = upon_request
        device_1.save()

        self.assertFalse(device_1.is_allowed()) 

        # Create an approval, and see that the device is enabled
        ta = TemporaryApproval(device=device_1)
        ta.set_parameters(10)
        ta.save()

        self.assertTrue(device_1.is_allowed()) 

    def test_enable_device(self):
        raise SkipTest # need more reliable way to set up fixtures
        response = iptables_download({})
        response_dict = json.loads(response._get_content()[5:])

        expected_blocked = {"mac_address": "58:94:6b:a4:da:bc", "ip_address": "192.168.10.2"}
        self.assertIn(expected_blocked, response_dict['blocked'])

        request = Mock()
        request.POST = { "device_name": '58:94:6b:a4:da:bc', "duration": 30 }
        request.method = "POST"
        response = enable_device(request)
        response_dict = json.loads(response._get_content()[5:])
        self.assertEqual(response_dict['success'], True)
        self.assertEqual(response_dict['message'], 'Saved')
        
