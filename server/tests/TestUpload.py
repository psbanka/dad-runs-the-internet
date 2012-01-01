import unittest2
from dri_server.web.frontend.views import upload_process
from dri_server.web.frontend.models import Device

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
        self.assertEqual(len(Device.objects.all()), 4)
        upload_process(TEST_ARP_ENTRY)
        self.assertEqual(len(Device.objects.all()), 9)

