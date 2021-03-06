#!/usr/bin/env python

'''
Simple tests for some of the functions in the ss.py script
'''

import unittest
import ss
import collections
from ss import __strip as ssstrip


class TestSystemStatus(unittest.TestCase):
    statvfsout = collections.namedtuple('statvfs_result', ['f_bsize',
                                                           'f_blocks',
                                                           'f_bfree',
                                                           'f_files',
                                                           'f_ffree'])
    dfout_base = ['/dev/sda1', '/', 0, 0, 0, 0]
    dfout_okay = dfout_base + [statvfsout(f_bsize=4096, f_blocks=100,
                                         f_bfree=99, f_files=100,
                                         f_ffree=99)]
    dfout_warn = dfout_base + [statvfsout(f_bsize=4096, f_blocks=100,
                                          f_bfree=15, f_files=100,
                                          f_ffree=99)]
    dfout_err = dfout_base + [statvfsout(f_bsize=4096, f_blocks=100,
                                         f_bfree=1, f_files=100,
                                         f_ffree=99)]
    dfout_noinode = dfout_base + [statvfsout(f_bsize=4096, f_blocks=100,
                                             f_bfree=1, f_files=0,
                                             f_ffree=0)]

    dfout = [dfout_okay, dfout_warn, dfout_err]

    dfout_correct = [
        'Filesystem    Size  Used  Avail  Use% Mounted on\x1b[0m',
        '\x1b[1;32m/dev/sda1     400K    4K   396K    1% /\x1b[0m',
        '\x1b[1;33m/dev/sda1     400K  340K    60K   85% /\x1b[0m',
        '\x1b[1;31m/dev/sda1     400K  396K     4K   99% /\x1b[0m']

    ipoutput = '''1: lo    inet 127.0.0.1/8 scope host lo\       valid_lft forever preferred_lft forever
    1: lo    inet6 ::1/128 scope host \       valid_lft forever preferred_lft forever
    2: eth0    inet 162.242.212.101/24 brd 162.242.212.255 scope global eth0\       valid_lft forever preferred_lft forever
    2: eth0    inet6 2001:4802:7801:102:7eb4:d9f4:ff20:1ba7/64 scope global \       valid_lft forever preferred_lft forever
    2: eth0    inet6 fe80::be76:4eff:fe20:1ba7/64 scope link \       valid_lft forever preferred_lft forever
    3: eth1    inet 10.176.128.123/19 brd 10.176.159.255 scope global eth1\       valid_lft forever preferred_lft forever
    3: eth1    inet6 fe80::be76:4eff:fe20:128d/64 scope link \       valid_lft forever preferred_lft forever
    '''
    good_ip_out = ['eth0    162.242.212.101',
                   'eth0    2001:4802:7801:102:7eb4:d9f4:ff20:1ba7',
                   'eth1    10.176.128.123']

    micromem = '''MemTotal:        8060916 kB
MemFree:          694180 kB
MemWhat:          694180
MemAvailable:    5763740 kB'''

    correctmem = {'MemTotal': '8060916',
                  'MemFree': '694180',
                  'MemWhat': '694180',
                  'MemAvailable': '5763740'}

    ssout = ['Total: 280 (kernel 0)',
             'TCP:   10 (estab 8, closed 0, orphaned 0, synrecv 0, timewait 0/0), ports 0',
             'tcp    LISTEN     0      5                                        127.0.0.1:33265                                           *:*      users:(("weechat",pid=548,fd=14))',
             'tcp    ESTAB      0      0                                      192.168.0.3:55151                              173.194.64.109:993    users:(("offlineimap",pid=20920,fd=9))',
             'tcp    ESTAB      0      0                                      192.168.0.3:55151                              173.194.64.109:993    users:(("offlineimap",pid=20920,fd=9))',
             'tcp    ESTAB      0      0                                      192.168.0.3:55151                              173.194.64.109:993    users:(("offlineimap",pid=20920,fd=9))',
             'tcp    ESTAB      0      0                                        127.0.0.1:42337                                   127.0.0.1:7700   users:(("ncmpcpp",pid=552,fd=3))',
             'tcp    ESTAB      0      0                                        127.0.0.1:42337                                   127.0.0.1:7700   users:(("ncmpcpp",pid=552,fd=3))',
             'tcp    ESTAB      0      0                                      192.168.0.3:46661                             162.242.212.101:5127   users:(("weechat",pid=548,fd=71))',
             'tcp    LISTEN     0      128                                             :::7700                                           :::*      users:(("mpd",pid=558,fd=3),("systemd",pid=353,fd=19))',
             ]

    ssntlp = ['127.0.0.1:33265      0      5 "weechat",pid=548,fd=14',
              ':::7700              0    128 "mpd",pid=558,fd=3, "systemd",pid=353,fd=19']

    ssutn = [['      3 55151', '      2 42337', '      1 46661'],
             ['      3 993', '      2 7700', '      1 5127']]

    utmpbytes = b"\x02\x00\x00\x00\x00\x00\x00\x00~\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00~~\x00\x00reboot\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x003.14.3-1-ARCH\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\xc0kS\xeb'\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    utmpdict = {'Line': '~',
                'addr': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                'ID': '~~', 'Hostname': '3.14.3-1-ARCH', 'unused': '',
                'PID': 0, 'User': 'reboot', 'session': 0, 'time_ms': 600043,
                'type': 2, 'exit_status': 0, 'time_s': 1399570656}

    redhat_release = ['Fedora release 21 (Rawhide)']
    rh_release_dict = {'NAME': 'Fedora', 'VERSION': '21 (Rawhide)'}

    lsb_release = ['DISTRIB_ID=Ubuntu',
                   'DISTRIB_RELEASE=11.10',
                   'DISTRIB_CODENAME=oneiric',
                   'DISTRIB_DESCRIPTION="Ubuntu 11.10"']
    lsb_release_dict = {'NAME': 'Ubuntu', 'VERSION': '11.10 (oneiric)'}

    os_release = ['NAME="Arch Linux"',
                  'ID=arch',
                  'PRETTY_NAME="Arch Linux"',
                  'ANSI_COLOR="0;36"',
                  'HOME_URL="https://www.archlinux.org/"',
                  'SUPPORT_URL="https://bbs.archlinux.org/"',
                  'BUG_REPORT_URL="https://bugs.archlinux.org/"']
    os_release_dict = {'NAME': 'Arch Linux', 'VERSION': 'rolling release'}
    os_rel_fedora = ['NAME=Fedora',
                     'VERSION="21 (Rawhide)"',
                     'ID=fedora',
                     'VERSION_ID=21',
                     'PRETTY_NAME="Fedora 21 (Rawhide)"',
                     'ANSI_COLOR="0;34"',
                     'CPE_NAME="cpe:/o:fedoraproject:fedora:21"',
                     'HOME_URL="https://fedoraproject.org/"',
                     'BUG_REPORT_URL="https://bugzilla.redhat.com/"',
                     'REDHAT_BUGZILLA_PRODUCT="Fedora"',
                     'REDHAT_BUGZILLA_PRODUCT_VERSION=Rawhide',
                     'REDHAT_SUPPORT_PRODUCT="Fedora"',
                     'REDHAT_SUPPORT_PRODUCT_VERSION=Rawhide']
    os_rel_fedora_dict = {'NAME': 'Fedora', 'VERSION': '21 (Rawhide)'}

    def test_format_size(self):
        'This runs format_size, make sure the full output is okay'
        self.assertEqual(ss.format_size(self.dfout), self.dfout_correct)

    def test_format_ip_output(self):
        '''We should get the correct output from parse_ip_output'''
        self.assertEqual(list(ss.format_ip_output(self.ipoutput)),
                         self.good_ip_out)

    def test_strip(self):
        '''Make sure we correctly strip bytes'''
        for s in ((('a', b'\x01\x00'), '\x00', 'b', ('a', '\x01')),
                  (('a', b'\x01\x00'), '\x00', 'a', ('a', b'\x01\x00')),
                  (('a', b'\x01\x00'), '\x02', 'b', ('a', '\x01\x00')),
                  (('a', b'\x01\x02'), '\x02', 'b', ('a', '\x01'))):
            self.assertEqual(ssstrip(s[0], y=s[1], ign=s[2]), s[3])

    def test_parse_mem(self):
        '''Parse different things in /proc/meminfo right'''
        self.assertEqual(ss._parse_mem(self.micromem), self.correctmem)

    def test_ssproc(self):
        '''Get a correctly formatted proc list from ss input'''
        self.assertEqual(list(ss.format_ssntlp(self.ssout)),
                         self.ssntlp)

    def test_ssutn(self):
        '''Test ss -ntu output formatting.'''
        self.assertEqual(
            [list(x) for x in ss.format_ssutn(self.ssout, header=2)],
            self.ssutn)

    def test_parse_utmp(self):
        '''Make sure utmp is working right'''
        self.assertDictEqual(ss._parse_utmp(self.utmpbytes)[0],
                             self.utmpdict)

    def test_parse_utmp_fail(self):
        '''Fail when the bytes are a bad length'''
        with self.assertRaises(ss.UtmpLengthError):
            ss._parse_utmp(b'\x00\x01')

    def test_parse_release_rh(self):
        '''Make sure the different redhat-release files are parsed right'''
        self.assertDictEqual(
            ss.parse_release(self.redhat_release), self.rh_release_dict)

    def test_parse_release_os(self):
        '''Make sure the different os-release files are parsed right'''
        self.assertDictEqual(
            ss.parse_release(self.os_release), self.os_release_dict)

    def test_parse_release_os_fedora(self):
        '''Make sure the different os-release files are parsed right for fedora'''
        self.assertDictEqual(
            ss.parse_release(self.os_rel_fedora),
            self.os_rel_fedora_dict)

    def test_parse_release_lsb(self):
        '''Make sure the different lsb-release files are parsed right'''
        self.assertDictEqual(
            ss.parse_release(self.lsb_release), self.lsb_release_dict)

    # TODO: format_w tests (makes extensive use of time.*)
    # TODO: format_mem and format_swap tests


def main():
    import os
    import sys
    u = unittest.TestLoader().loadTestsFromTestCase(TestSystemStatus)
    with open(os.devnull, 'w') as devnull:
        a = unittest.TextTestRunner(stream=devnull).run(u)
    print(': {x} tests run. {f} failures, {e} errors : {s}'.format(
        x=a.testsRun,
        s={True: 'OK', False: 'FAIL'}[a.wasSuccessful()],
        f=len(a.failures), e=len(a.errors)))
    if a.failures:
        print('{0}\nFAILURES:\n'.format('-' * 75))
        print('\n'.join(['{0}\n{1}'.format(x[0], x[1])
                         for x in a.failures]))
    if a.errors:
        print('{0}\nERRORS:\n'.format('-' * 75))
        print('\n'.join(['{0}\n{1}'.format(x[0], x[1])
                         for x in a.errors]))
    if a.failures or a.errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
