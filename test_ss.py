#!/usr/bin/env python

'''
Simple tests for some of the functions in the ss.py script
'''

import unittest
import ss
from ss import __strip as ssstrip


class TestSystemStatus(unittest.TestCase):
    dfout_okay = '/dev/sda1      124780544 14392492 105078100  13% /'
    dfout_warn = '/dev/sda1      124780544 14392492 105078100  85% /'
    dfout_err = '/dev/sda1      124780544 14392492 105078100  99% /'
    dfout_noinode = '/dev/sda1            0     0       0     - /home'

    dfout = ['Filesystem      Size  Used Avail Use% Mounted on',
        dfout_okay, dfout_warn, dfout_err]

    dfout_correct = [
        'Filesystem      Size  Used Avail Use% Mounted on',
        '\x1b[1;32m/dev/sda1      124780544 14392492 105078100  13% /\x1b[0m',
        '\x1b[1;33m/dev/sda1      124780544 14392492 105078100  85% /\x1b[0m',
        '\x1b[1;31m/dev/sda1      124780544 14392492 105078100  99% /\x1b[0m']

    ipoutput = '''2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether bc:76:4e:20:1b:a7 brd ff:ff:ff:ff:ff:ff
    inet 162.242.212.101/24 brd 162.242.212.255 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 2001:4802:7801:102:7eb4:d9f4:ff20:1ba7/64 scope global 
       valid_lft forever preferred_lft forever
    inet6 fe80::be76:4eff:fe20:1ba7/64 scope link
       valid_lft forever preferred_lft forever
    '''
    good_ip_out = ['eth0    162.242.212.101',
                   'global  2001:4802:7801:102:7eb4:d9f4:ff20:1ba7']

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

    ssutn = (['      3 55151', '      2 42337', '      1 46661'],
             ['      3 993', '      2 7700', '      1 5127'])

    utmpbytes = b"\x02\x00\x00\x00\x00\x00\x00\x00~\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00~~\x00\x00reboot\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x003.14.3-1-ARCH\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\xc0kS\xeb'\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    utmpdict = {'Line': '~',
                'addr': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                'ID': '~~', 'Hostname': '3.14.3-1-ARCH', 'unused': '',
                'PID': 0, 'User': 'reboot', 'session': 0, 'time_ms': 600043,
                'type': 2, 'exit_status': 0, 'time_s': 1399570656}

    def test_type_df(self):
        'Make sure that type_df returns the correct values'
        for i in ((self.dfout_okay, ss.bcolors.GREEN),
                  (self.dfout_warn, ss.bcolors.YELLOW),
                  (self.dfout_err, ss.bcolors.RED),
                  (self.dfout_noinode, '')):
            self.assertEqual(ss.type_df(i[0]), i[1])

    def test_format_df(self):
        'This runs the type_df stuff, but make sure the full output is okay'
        self.assertEqual(ss.format_df(self.dfout), self.dfout_correct)

    def test_parse_ip_output(self):
        '''We should get the correct output from parse_ip_output'''
        self.assertEqual(list(ss.parse_ip_output(self.ipoutput)),
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
        self.assertEqual(ss.parse_mem(self.micromem), self.correctmem)

    def test_ssproc(self):
        '''Get a correctly formatted proc list from ss input'''
        self.assertEqual(list(ss.format_ssntlp(self.ssout)),
                         self.ssntlp)

    def test_ssutn(self):
        '''Test ss -ntu output formatting'''
        self.assertEqual(ss.format_ssutn(self.ssout, header=2),
                         self.ssutn)

    def test_parse_utmp(self):
        '''Make sure utmp is working right'''
        self.assertDictEqual(ss.parse_utmp(self.utmpbytes)[0],
                             self.utmpdict)

    def test_parse_utmp_fail(self):
        '''Fail when the bytes are a bad length'''
        with self.assertRaises(ss.utmpLengthError):
            ss.parse_utmp(b'\x00\x01')

    # TODO: format_w tests (makes extensive use of time.*)
    # TODO: format_mem and format_swap tests


if __name__ == '__main__':
    unittest.main()
