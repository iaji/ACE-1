# vim: sw=4:ts=4:et

import unittest

from saq.constants import *
from saq.test import *
from saq.observables import *

# expected values
EV_OBSERVABLE_ASSET = 'localhost'
EV_OBSERVABLE_SNORT_SIGNATURE = '2809768'
EV_OBSERVABLE_EMAIL_ADDRESS = 'jwdavison@valvoline.com'
EV_OBSERVABLE_FILE = 'var/test.txt'
EV_OBSERVABLE_FILE_LOCATION = r'PCN31337@C:\users\lol.txt'
EV_OBSERVABLE_FILE_NAME = 'evil.exe'
EV_OBSERVABLE_FILE_PATH = r'C:\windows\system32\notepod.exe'
EV_OBSERVABLE_FQDN = 'evil.com'
EV_OBSERVABLE_HOSTNAME = 'adserver'
EV_OBSERVABLE_INDICATOR = '5a1463a6ad951d7088c90de4'
EV_OBSERVABLE_IPV4 = '1.2.3.4'
EV_OBSERVABLE_MD5 = 'f233d34c98f6bb32bb3b3ce7e740eb84'
EV_OBSERVABLE_SHA1 = '0b2ca11540b830ae37f4125c9387f8c18c8f86af'
EV_OBSERVABLE_SHA256 = '2206014de326cf3151bcebcfa89bd380c06339680989cd85f3791e81424b27ec'
EV_OBSERVABLE_URL = 'http://www.evil.com/blah.exe'
EV_OBSERVABLE_USER = 'a420539'
EV_OBSERVABLE_YARA_RULE = 'CRITS_URIURL'
EV_OBSERVABLE_MESSAGE_ID = '<E07DC80D-9F7E-4B7D-8338-82D37ACBC80A@burtbrothers.com>'
EV_OBSERVABLE_PROCESS_GUID = '00000043-0000-2c8c-01d3-63e9f520f17c'

EV_OBSERVABLE_VALUE_MAP = {
    F_ASSET: EV_OBSERVABLE_ASSET,
    F_SNORT_SIGNATURE: EV_OBSERVABLE_SNORT_SIGNATURE,
    F_EMAIL_ADDRESS: EV_OBSERVABLE_EMAIL_ADDRESS,
    F_FILE: EV_OBSERVABLE_FILE,
    F_FILE_LOCATION: EV_OBSERVABLE_FILE_LOCATION,
    F_FILE_NAME: EV_OBSERVABLE_FILE_NAME,
    F_FILE_PATH: EV_OBSERVABLE_FILE_PATH,
    F_FQDN: EV_OBSERVABLE_FQDN,
    F_HOSTNAME: EV_OBSERVABLE_HOSTNAME,
    F_INDICATOR: EV_OBSERVABLE_INDICATOR,
    F_IPV4: EV_OBSERVABLE_IPV4,
    F_MD5: EV_OBSERVABLE_MD5,
    F_SHA1: EV_OBSERVABLE_SHA1,
    F_SHA256: EV_OBSERVABLE_SHA256,
    F_URL: EV_OBSERVABLE_URL,
    F_USER: EV_OBSERVABLE_USER,
    F_YARA_RULE: EV_OBSERVABLE_YARA_RULE,
    F_MESSAGE_ID: EV_OBSERVABLE_MESSAGE_ID,
    F_PROCESS_GUID: EV_OBSERVABLE_PROCESS_GUID
}

class ObservableTestCase(ACEBasicTestCase):
    def add_observables(self, root):
        for o_type in EV_OBSERVABLE_VALUE_MAP.keys():
            root.add_observable(o_type, EV_OBSERVABLE_VALUE_MAP[o_type])
        
    def test_add_observable(self):
        root = create_root_analysis()
        self.add_observables(root)

    def test_add_invalid_observables(self):
        root = create_root_analysis()
        o = root.add_observable(F_IPV4, '1.2.3.4.5')
        self.assertIsNone(o)
        o = root.add_observable(F_URL, '\xFF')
        self.assertIsNone(o)
        o = root.add_observable(F_FILE, '')
        self.assertIsNone(o)

    def test_observable_storage(self):
        root = create_root_analysis()
        self.add_observables(root)
        root.save()

        root = create_root_analysis()
        root.load()

        for o_type in EV_OBSERVABLE_VALUE_MAP.keys():
            o = root.get_observable_by_type(o_type)
            self.assertIsNotNone(o)
            self.assertEquals(o.type, o_type)
            self.assertEquals(o.value, EV_OBSERVABLE_VALUE_MAP[o_type])

    def test_caseless_observables(self):
        root = create_root_analysis()
        o1 = root.add_observable(F_HOSTNAME, 'abc')
        o2 = root.add_observable(F_HOSTNAME, 'ABC')
        # the second should return the same object
        self.assertIs(o1, o2)
        self.assertEquals(o2.value, 'abc')

    def test_file_type_observables(self):
        root = create_root_analysis()
        o1 = root.add_observable(F_FILE, 'sample.txt')
        o2 = root.add_observable(F_FILE_NAME, 'sample.txt')

        # the second should NOT return the same object
        self.assertIsNot(o1, o2)

    def test_ipv6_observable(self):
        root = create_root_analysis()
        # this should not add an observable since this is an ipv6 address
        o1 = root.add_observable(F_IPV4, '::1')
        self.assertIsNone(o1)

    def test_add_invalid_message_id(self):
        root = create_root_analysis()
        observable = root.add_observable(F_MESSAGE_ID, 'CANTOGZtOdse1SqNtFRs2o22ohrWpbddWfCzkzn+iy1SEHxt2pg@mail.gmail.com')
        self.assertEquals(observable.value, '<CANTOGZtOdse1SqNtFRs2o22ohrWpbddWfCzkzn+iy1SEHxt2pg@mail.gmail.com>')

    def test_add_invalid_email_delivery_message_id(self):
        root = create_root_analysis()
        observable = root.add_observable(F_EMAIL_DELIVERY, create_email_delivery('CANTOGZtOdse1SqNtFRs2o22ohrWpbddWfCzkzn+iy1SEHxt2pg@mail.gmail.com', 'test@localhost.com'))
        self.assertEquals(observable.value, '<CANTOGZtOdse1SqNtFRs2o22ohrWpbddWfCzkzn+iy1SEHxt2pg@mail.gmail.com>|test@localhost.com')

    def test_valid_mac_observable(self):
        root = create_root_analysis()
        observable = root.add_observable(F_MAC_ADDRESS, '001122334455')
        self.assertIsNotNone(observable)
        self.assertEquals(observable.value, '001122334455')
        self.assertEquals(observable.mac_address(), '00:11:22:33:44:55')
        self.assertEquals(observable.mac_address(sep='-'), '00-11-22-33-44-55')

        observable = root.add_observable(F_MAC_ADDRESS, '00:11:22:33:44:55')
        self.assertIsNotNone(observable)
        self.assertEquals(observable.value, '00:11:22:33:44:55')
        self.assertEquals(observable.mac_address(sep=''), '001122334455')

    def test_invalid_mac_observable(self):
        root = create_root_analysis()
        observable = root.add_observable(F_MAC_ADDRESS, '00112233445Z')
        self.assertIsNone(observable)
